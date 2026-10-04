from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


class ParityHold(RuntimeError):
    pass


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ParityHold(f"JSON object required:{path}")
    return value


def _record_id(row: dict) -> str:
    for key in ("record_id", "case_id", "source_id", "id"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    raise ParityHold("row has no stable record id")


def _observe_runtime(binding: dict, torch) -> dict:
    packages: dict[str, str] = {}
    for package in sorted(binding.get("packages", {})):
        dist = "huggingface-hub" if package == "huggingface_hub" else package
        try:
            packages[package] = metadata.version(dist)
        except metadata.PackageNotFoundError as exc:
            raise ParityHold(f"missing bound package:{package}") from exc

    target = binding["target"]
    base = Path(target["base_path"])
    artifacts = {}
    for name, expected in binding["base_artifacts"].items():
        path = base / name
        if not path.is_file():
            raise ParityHold(f"missing base artifact:{path}")
        actual = sha256_file(path)
        if actual != expected:
            raise ParityHold(f"base artifact mismatch:{name}")
        artifacts[name] = actual

    if not torch.cuda.is_available():
        raise ParityHold("CUDA unavailable")
    props = torch.cuda.get_device_properties(0)
    try:
        driver = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=15,
        ).stdout.splitlines()[0].strip()
    except Exception as exc:
        raise ParityHold(f"cannot observe NVIDIA driver:{exc}") from exc

    observed = {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "torch": torch.__version__,
        "cuda_runtime": str(torch.version.cuda),
        "gpu": torch.cuda.get_device_name(0),
        "vram_mib": int(props.total_memory // (1024 * 1024)),
        "driver": driver,
        "packages": packages,
        "base_artifacts": artifacts,
    }
    if observed["python_version"] != target["python_version"]:
        raise ParityHold("python version does not match runtime binding")
    if observed["cuda_runtime"] != str(target["cuda_runtime"]):
        raise ParityHold("CUDA runtime does not match runtime binding")
    if observed["gpu"] != target["gpu"]:
        raise ParityHold("GPU does not match runtime binding")
    if abs(observed["vram_mib"] - int(target["vram_mib"])) > 1:
        raise ParityHold("VRAM does not match runtime binding")
    if observed["driver"] != target["driver"]:
        raise ParityHold("driver does not match runtime binding")
    if packages != dict(binding["packages"]):
        raise ParityHold("package set does not match runtime binding")
    return observed


def _load_rows(protocol: dict) -> list[dict]:
    subject = protocol["common_subject"]
    train_path = Path(subject["train_jsonl"])
    if sha256_file(train_path) != subject["train_sha256"]:
        raise ParityHold("training corpus hash mismatch")
    rows = [
        json.loads(line)
        for line in train_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != int(subject["train_rows"]):
        raise ParityHold("training corpus row count mismatch")

    selected = []
    for expected in subject["rows"]:
        index = int(expected["index"])
        row = rows[index]
        if _record_id(row) != expected["record_id"]:
            raise ParityHold(f"row identity mismatch at index:{index}")
        selected.append(row)
    return selected


def _generation_prefix(tokenizer, prompt: str) -> str:
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )


def _examples(tokenizer, rows: list[dict], max_length: int) -> list[dict]:
    result = []
    for row in rows:
        prefix = _generation_prefix(tokenizer, row["prompt"])
        completion = row["response"] + (tokenizer.eos_token or "")
        prompt_ids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
        full_ids = tokenizer(
            prefix + completion, add_special_tokens=False
        )["input_ids"]
        if len(full_ids) > max_length:
            raise ParityHold(
                f"probe row exceeds max length:{_record_id(row)}:"
                f"{len(full_ids)}>{max_length}"
            )
        if len(full_ids) <= len(prompt_ids):
            raise ParityHold(f"empty completion tokens:{_record_id(row)}")
        labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
        result.append(
            {
                "record_id": _record_id(row),
                "input_ids": full_ids,
                "labels": labels,
                "token_count": len(full_ids),
            }
        )
    return result


def _sequence_binding(examples: list[dict], field: str) -> str:
    return hashlib.sha256(
        canonical_bytes(
            [
                {"record_id": item["record_id"], field: item[field]}
                for item in examples
            ]
        )
    ).hexdigest()


def _trainable_digest(model, torch) -> tuple[str, int, str]:
    digest = hashlib.sha256()
    layout = hashlib.sha256()
    count = 0
    for name, parameter in sorted(model.named_parameters()):
        if not parameter.requires_grad:
            continue
        tensor = (
            parameter.detach()
            .to(device="cpu", dtype=torch.float32)
            .contiguous()
        )
        header = canonical_bytes(
            {"name": name, "shape": list(tensor.shape), "dtype": "float32"}
        )
        layout.update(header)
        digest.update(header)
        digest.update(tensor.numpy().tobytes(order="C"))
        count += tensor.numel()
    if count < 1:
        raise ParityHold("no trainable parameters")
    return digest.hexdigest(), count, layout.hexdigest()


def _gradient_vector(model, torch) -> tuple[object, dict]:
    pieces = []
    layout = hashlib.sha256()
    nonfinite = 0
    zero = 0
    for name, parameter in sorted(model.named_parameters()):
        if not parameter.requires_grad:
            continue
        if parameter.grad is None:
            raise ParityHold(f"missing gradient:{name}")
        grad = parameter.grad.detach().to(
            device="cpu", dtype=torch.float32
        ).contiguous()
        header = canonical_bytes(
            {"name": name, "shape": list(grad.shape), "dtype": "float32"}
        )
        layout.update(header)
        if not bool(torch.isfinite(grad).all().item()):
            nonfinite += 1
        if not bool(torch.count_nonzero(grad).item()):
            zero += 1
        pieces.append(grad.reshape(-1))
    if not pieces or nonfinite:
        raise ParityHold(f"invalid gradients nonfinite={nonfinite}")
    vector = torch.cat(pieces)
    return vector, {
        "element_count": int(vector.numel()),
        "l2": float(torch.linalg.vector_norm(vector.double()).item()),
        "all_finite": nonfinite == 0,
        "nonfinite_tensor_count": nonfinite,
        "zero_tensor_count": zero,
        "layout_sha256": layout.hexdigest(),
        "gradient_sha256": hashlib.sha256(
            vector.numpy().tobytes(order="C")
        ).hexdigest(),
    }


def execute_probe(
    repo_root: Path,
    *,
    protocol_path: Path,
    runtime_key: str,
    output_path: Path,
    vector_path: Path,
) -> dict:
    if output_path.exists() or vector_path.exists():
        raise ParityHold("probe output already exists")
    protocol = _read_json(protocol_path)
    if protocol["status"] != "FROZEN_NOT_EXECUTED":
        raise ParityHold("protocol is not frozen for execution")
    if runtime_key not in {"A", "B"}:
        raise ParityHold("runtime key must be A or B")

    runtime_spec = protocol["runtimes"][runtime_key]
    binding_path = repo_root / runtime_spec["binding_path"]
    binding = _read_json(binding_path)
    if binding.get("binding_sha256") != runtime_spec["binding_sha256"]:
        raise ParityHold("runtime binding identity mismatch")

    import torch
    from peft import PeftModel, prepare_model_for_kbit_training
    from transformers import (
        AutoTokenizer,
        BitsAndBytesConfig,
        Qwen3_5ForCausalLM,
        set_seed,
    )

    observed = _observe_runtime(binding, torch)
    subject = protocol["common_subject"]
    rows = _load_rows(protocol)
    base_path = Path(subject["base_path"])
    adapter_path = Path(subject["adapter_path"])
    adapter_model = adapter_path / "adapter_model.safetensors"
    if sha256_file(adapter_model) != subject["adapter_model_sha256"]:
        raise ParityHold("step48 adapter hash mismatch")
    receipt_path = Path(subject["adapter_receipt_path"])
    if sha256_file(receipt_path) != subject["adapter_receipt_file_sha256"]:
        raise ParityHold("step48 receipt file hash mismatch")
    receipt = _read_json(receipt_path)
    if receipt.get("receipt_sha256") != subject["adapter_receipt_sha256"]:
        raise ParityHold("step48 receipt identity mismatch")

    tokenizer = AutoTokenizer.from_pretrained(base_path)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    examples = _examples(tokenizer, rows, int(subject["max_length"]))
    input_sha = _sequence_binding(examples, "input_ids")
    labels_sha = _sequence_binding(examples, "labels")

    set_seed(20261001)
    quant = subject["quantization"]
    bits = BitsAndBytesConfig(
        load_in_4bit=quant["load_in_4bit"],
        bnb_4bit_quant_type=quant["type"],
        bnb_4bit_use_double_quant=quant["double_quant"],
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = Qwen3_5ForCausalLM.from_pretrained(
        base_path,
        quantization_config=bits,
        device_map={"": 0},
        dtype=torch.bfloat16,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )
    model = PeftModel.from_pretrained(
        model,
        adapter_path,
        is_trainable=True,
        autocast_adapter_dtype=False,
    )
    model.train()
    model.zero_grad(set_to_none=True)

    before, trainable_count, trainable_layout = _trainable_digest(
        model, torch
    )
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    started = time.perf_counter()
    losses = []
    for item in examples:
        input_ids = torch.tensor(
            [item["input_ids"]], device="cuda", dtype=torch.long
        )
        labels = torch.tensor(
            [item["labels"]], device="cuda", dtype=torch.long
        )
        attention_mask = torch.ones_like(input_ids)
        output = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            use_cache=False,
        )
        loss = output.loss
        if not bool(torch.isfinite(loss.detach()).item()):
            raise ParityHold(f"nonfinite loss:{item['record_id']}")
        losses.append(float(loss.detach().float().cpu().item()))
        (loss / len(examples)).backward()
        del output, input_ids, labels, attention_mask
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started

    vector, gradient = _gradient_vector(model, torch)
    after, after_count, after_layout = _trainable_digest(model, torch)
    if after_count != trainable_count or after_layout != trainable_layout:
        raise ParityHold("trainable layout changed")
    if before != after:
        raise ParityHold("trainable weights changed during parity probe")

    vector_path.parent.mkdir(parents=True, exist_ok=True)
    vector.numpy().astype(np.float32, copy=False).tofile(vector_path)
    vector_sha = sha256_file(vector_path)
    result = {
        "schema": "V10R3_CROSS_RUNTIME_PARITY_PROBE_RECEIPT_V1",
        "status": "NON_MUTATING_PARITY_PROBE_COMPLETE",
        "runtime_key": runtime_key,
        "protocol_sha256": sha256_file(protocol_path),
        "runtime_binding_sha256": binding["binding_sha256"],
        "runtime_observation": observed,
        "row_indices": list(subject["row_indices"]),
        "record_ids": [item["record_id"] for item in examples],
        "token_counts": [item["token_count"] for item in examples],
        "input_ids_sha256": input_sha,
        "labels_sha256": labels_sha,
        "microbatch_losses": losses,
        "mean_loss": float(sum(losses) / len(losses)),
        "trainable_parameter_count": trainable_count,
        "trainable_layout_sha256": trainable_layout,
        "weight_digest_before": before,
        "weight_digest_after": after,
        "weight_digest_unchanged": before == after,
        "optimizer_created": False,
        "gradient": {**gradient, "vector_file_sha256": vector_sha},
        "elapsed_seconds": elapsed,
        "cuda_memory": {
            "peak_allocated_mib": round(
                torch.cuda.max_memory_allocated() / (1024**2), 3
            ),
            "peak_reserved_mib": round(
                torch.cuda.max_memory_reserved() / (1024**2), 3
            ),
        },
        "effect": "FORWARD_BACKWARD_ONLY_NO_OPTIMIZER_NO_WEIGHT_CHANGE",
    }
    result["receipt_sha256"] = hashlib.sha256(
        canonical_bytes(result)
    ).hexdigest()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def assess_parity(
    protocol: dict,
    left: dict,
    right: dict,
    left_vector: np.ndarray,
    right_vector: np.ndarray,
) -> dict:
    gate = protocol["prospective_gate"]
    reasons = []
    for label in ("input_ids_sha256", "labels_sha256", "trainable_layout_sha256"):
        if left.get(label) != right.get(label):
            reasons.append(f"{label}_mismatch")
    if left.get("trainable_parameter_count") != right.get(
        "trainable_parameter_count"
    ):
        reasons.append("trainable_parameter_count_mismatch")
    if left.get("weight_digest_unchanged") is not True or right.get(
        "weight_digest_unchanged"
    ) is not True:
        reasons.append("weight_change_observed")
    if left.get("optimizer_created") is not False or right.get(
        "optimizer_created"
    ) is not False:
        reasons.append("optimizer_created")
    if left_vector.shape != right_vector.shape:
        reasons.append("gradient_shape_mismatch")
        cosine = float("nan")
        relative_l2 = float("inf")
        norm_relative_difference = float("inf")
    else:
        lv = left_vector.astype(np.float64, copy=False)
        rv = right_vector.astype(np.float64, copy=False)
        lnorm = float(np.linalg.norm(lv))
        rnorm = float(np.linalg.norm(rv))
        if lnorm == 0 or rnorm == 0:
            cosine = float("nan")
            relative_l2 = float("inf")
            norm_relative_difference = float("inf")
        else:
            cosine = float(np.dot(lv, rv) / (lnorm * rnorm))
            relative_l2 = float(np.linalg.norm(rv - lv) / lnorm)
            norm_relative_difference = abs(rnorm - lnorm) / lnorm

    losses_a = list(left.get("microbatch_losses", []))
    losses_b = list(right.get("microbatch_losses", []))
    if len(losses_a) != len(losses_b) or not losses_a:
        reasons.append("microbatch_loss_shape_mismatch")
        max_loss_delta = float("inf")
        mean_loss_delta = float("inf")
    else:
        max_loss_delta = max(abs(a - b) for a, b in zip(losses_a, losses_b))
        mean_loss_delta = abs(
            float(left["mean_loss"]) - float(right["mean_loss"])
        )

    if not math.isfinite(cosine) or cosine < gate["gradient_cosine_min"]:
        reasons.append("gradient_cosine_below_gate")
    if relative_l2 > gate["gradient_relative_l2_max"]:
        reasons.append("gradient_relative_l2_above_gate")
    if norm_relative_difference > gate["gradient_l2_relative_difference_max"]:
        reasons.append("gradient_norm_relative_difference_above_gate")
    if max_loss_delta > gate["max_microbatch_loss_abs_delta"]:
        reasons.append("microbatch_loss_delta_above_gate")
    if mean_loss_delta > gate["mean_loss_abs_delta_max"]:
        reasons.append("mean_loss_delta_above_gate")
    if left.get("gradient", {}).get("all_finite") is not True or right.get(
        "gradient", {}
    ).get("all_finite") is not True:
        reasons.append("nonfinite_gradient")

    status = (
        "PASS_RUNTIME_PARITY"
        if not reasons
        else "HOLD_RUNTIME_PROMOTION"
    )
    return {
        "schema": "V10R3_CROSS_RUNTIME_PARITY_DECISION_V1",
        "status": status,
        "reasons": reasons,
        "metrics": {
            "max_microbatch_loss_abs_delta": max_loss_delta,
            "mean_loss_abs_delta": mean_loss_delta,
            "gradient_cosine": cosine,
            "gradient_relative_l2": relative_l2,
            "gradient_l2_relative_difference": norm_relative_difference,
        },
        "thresholds": dict(gate),
        "decision": (
            protocol["decision"]["pass"]
            if not reasons
            else protocol["decision"]["fail"]
        ),
        "effect": "READ_ONLY_COMPARISON_NO_WEIGHT_CHANGE",
    }


def compare_probe_outputs(
    protocol_path: Path,
    left_path: Path,
    right_path: Path,
    left_vector_path: Path,
    right_vector_path: Path,
    output_path: Path,
) -> dict:
    if output_path.exists():
        raise ParityHold("comparison output already exists")
    protocol = _read_json(protocol_path)
    left = _read_json(left_path)
    right = _read_json(right_path)
    expected_protocol = sha256_file(protocol_path)
    for receipt in (left, right):
        if receipt.get("protocol_sha256") != expected_protocol:
            raise ParityHold("probe receipt protocol hash mismatch")
    if {left.get("runtime_key"), right.get("runtime_key")} != {"A", "B"}:
        raise ParityHold("comparison requires runtime A and B")
    a = np.fromfile(left_vector_path, dtype=np.float32)
    b = np.fromfile(right_vector_path, dtype=np.float32)
    result = assess_parity(protocol, left, right, a, b)
    result["protocol_sha256"] = expected_protocol
    result["left_receipt_sha256"] = left.get("receipt_sha256")
    result["right_receipt_sha256"] = right.get("receipt_sha256")
    result["left_vector_sha256"] = sha256_file(left_vector_path)
    result["right_vector_sha256"] = sha256_file(right_vector_path)
    result["receipt_sha256"] = hashlib.sha256(
        canonical_bytes(result)
    ).hexdigest()
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "successor/experiments/V10R3_CROSS_RUNTIME_PARITY_PROTOCOL_V1.json"
        ),
    )
    sub = parser.add_subparsers(dest="mode", required=True)
    probe = sub.add_parser("probe")
    probe.add_argument("--runtime-key", choices=("A", "B"), required=True)
    probe.add_argument("--output", type=Path, required=True)
    probe.add_argument("--vector-out", type=Path, required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("--left", type=Path, required=True)
    compare.add_argument("--right", type=Path, required=True)
    compare.add_argument("--left-vector", type=Path, required=True)
    compare.add_argument("--right-vector", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    protocol = (
        args.protocol
        if args.protocol.is_absolute()
        else args.repo_root / args.protocol
    )
    if args.mode == "probe":
        result = execute_probe(
            args.repo_root,
            protocol_path=protocol,
            runtime_key=args.runtime_key,
            output_path=args.output,
            vector_path=args.vector_out,
        )
    else:
        result = compare_probe_outputs(
            protocol,
            args.left,
            args.right,
            args.left_vector,
            args.right_vector,
            args.output,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") == "HOLD_RUNTIME_PROMOTION":
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except ParityHold as exc:
        print(
            json.dumps(
                {
                    "schema": "V10R3_CROSS_RUNTIME_PARITY_ERROR_V1",
                    "status": "HOLD",
                    "reason": str(exc),
                    "effect": "NO_WEIGHT_CHANGE",
                },
                sort_keys=True,
            )
        )
        raise SystemExit(2)
