from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from typing import Callable


class TrainingHold(RuntimeError):
    """Fail-closed refusal before any weight-changing training work."""


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrainingHold(f"invalid JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TrainingHold(f"JSON artifact must be an object: {path}")
    return value


def assess_preflight(repo_root: Path | str) -> dict:
    from successor.evaluate_successor import assess_v10_experiment_state

    return assess_v10_experiment_state(Path(repo_root))


def gated_training_stack(
    preflight: dict,
    loader: Callable[[], object],
):
    if (
        preflight.get("status") != "READY_PRECONDITIONS"
        or preflight.get("training_allowed") is not True
        or preflight.get("reasons") not in ([], None)
    ):
        reasons = preflight.get("reasons")
        raise TrainingHold(
            "training preflight HOLD"
            + (f": {reasons}" if reasons else "")
        )
    return loader()


def load_training_stack() -> dict:
    """Heavy imports are intentionally isolated behind the READY gate."""
    import torch
    import transformers
    import trl
    import peft
    import bitsandbytes
    import datasets
    import accelerate
    import safetensors
    import huggingface_hub
    import tokenizers
    import jinja2
    import numpy
    from datasets import Dataset
    from peft import LoraConfig, prepare_model_for_kbit_training
    from transformers import (
        AutoTokenizer,
        BitsAndBytesConfig,
        Qwen3_5ForCausalLM,
    )
    from trl import SFTConfig, SFTTrainer

    return {
        "torch": torch,
        "transformers": transformers,
        "trl": trl,
        "peft": peft,
        "bitsandbytes": bitsandbytes,
        "datasets": datasets,
        "accelerate": accelerate,
        "safetensors": safetensors,
        "huggingface_hub": huggingface_hub,
        "tokenizers": tokenizers,
        "jinja2": jinja2,
        "numpy": numpy,
        "Dataset": Dataset,
        "LoraConfig": LoraConfig,
        "prepare_model_for_kbit_training": prepare_model_for_kbit_training,
        "AutoTokenizer": AutoTokenizer,
        "BitsAndBytesConfig": BitsAndBytesConfig,
        "Qwen3_5ForCausalLM": Qwen3_5ForCausalLM,
        "SFTConfig": SFTConfig,
        "SFTTrainer": SFTTrainer,
    }


def load_verified_jsonl(
    path: Path,
    *,
    expected_sha256: str,
    expected_rows: int,
) -> list[dict]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TrainingHold(f"could not read JSONL {path}: {exc}") from exc

    actual_sha = sha256_bytes(raw)
    if actual_sha != expected_sha256:
        raise TrainingHold(
            f"corpus hash mismatch: {actual_sha} != {expected_sha256}"
        )

    rows: list[dict] = []
    try:
        for line_number, line in enumerate(
            raw.decode("utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise TrainingHold(
                    f"row {line_number} must be a JSON object"
                )
            prompt = row.get("prompt")
            response = row.get("response")
            if (
                not isinstance(prompt, str)
                or not prompt.strip()
                or not isinstance(response, str)
                or not response.strip()
            ):
                raise TrainingHold(
                    f"row {line_number} missing nonempty prompt/response"
                )
            rows.append(row)
    except UnicodeDecodeError as exc:
        raise TrainingHold(f"JSONL is not UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise TrainingHold(f"invalid JSONL row in {path}: {exc}") from exc

    if len(rows) != expected_rows:
        raise TrainingHold(
            f"corpus row count mismatch: {len(rows)} != {expected_rows}"
        )
    return rows


def validate_output_namespace(
    output_dir: Path,
    authority: dict,
) -> None:
    expected = authority.get("output_namespace")
    if not isinstance(expected, str) or not expected.strip():
        raise TrainingHold("authority output namespace missing")
    if str(output_dir) != expected:
        raise TrainingHold(
            f"output namespace mismatch: {output_dir} != {expected}"
        )
    if output_dir.exists():
        raise TrainingHold(
            f"output namespace already exists: {output_dir}"
        )


def validate_runtime_observation(
    binding: dict,
    observed: dict,
) -> dict:
    reasons: list[str] = []
    target = binding.get("target")
    if not isinstance(target, dict):
        raise TrainingHold("runtime binding target missing")

    for field in (
        "python_version",
        "gpu",
        "vram_mib",
        "driver",
        "cuda_runtime",
    ):
        if observed.get(field) != target.get(field):
            reasons.append(
                f"runtime target mismatch:{field}:"
                f"{observed.get(field)}!={target.get(field)}"
            )

    expected_packages = binding.get("packages")
    observed_packages = observed.get("packages")
    if not isinstance(expected_packages, dict):
        raise TrainingHold("runtime binding packages missing")
    if not isinstance(observed_packages, dict):
        raise TrainingHold("runtime observation packages missing")
    for package, expected in sorted(expected_packages.items()):
        actual = observed_packages.get(package)
        if actual != expected:
            reasons.append(
                f"package mismatch:{package}:{actual}!={expected}"
            )

    expected_artifacts = binding.get("base_artifacts")
    observed_artifacts = observed.get("base_artifacts")
    if not isinstance(expected_artifacts, dict):
        raise TrainingHold("runtime binding base_artifacts missing")
    if not isinstance(observed_artifacts, dict):
        raise TrainingHold("runtime observation base_artifacts missing")
    for name, expected in sorted(expected_artifacts.items()):
        actual = observed_artifacts.get(name)
        if actual != expected:
            reasons.append(
                f"base artifact mismatch:{name}:{actual}!={expected}"
            )

    if reasons:
        raise TrainingHold("runtime observation mismatch: " + " | ".join(reasons))
    return {
        "schema": "V10_QWEN35_LIVE_RUNTIME_CHECK_V1",
        "status": "PASS",
        "binding_sha256": binding.get("binding_sha256"),
    }


def default_execution_spec() -> dict:
    return {
        "schema": "V10_QWEN35_TRAINING_EXECUTION_SPEC_V1",
        "effect": "TRAIN_ONE_FRESH_QLORA_ADAPTER",
        "trainer": {
            "method": "QLORA_SFT_ONLY",
            "seed": 20261001,
            "epochs": 1.0,
            "learning_rate": 2e-5,
            "lr_scheduler_type": "cosine",
            "warmup_optimizer_steps": 3,
            "per_device_train_batch_size": 1,
            "gradient_accumulation_steps": 8,
            "max_length": 512,
            "overflow_policy": "ERROR_NO_TRUNCATION",
            "optimizer": "adamw_torch",
            "completion_only_loss": True,
            "packing": False,
            "shuffle_dataset": True,
            "gradient_checkpointing": True,
            "validation_role": (
                "POST_TRAIN_DIAGNOSTIC_ONLY_NO_RECIPE_OR_CHECKPOINT_SELECTION"
            ),
        },
        "quantization": {
            "load_in_4bit": True,
            "type": "nf4",
            "double_quant": True,
            "compute_dtype": "bfloat16",
        },
        "lora": {
            "r": 4,
            "alpha": 16,
            "dropout": 0.0,
            "target_modules": "all-linear",
        },
        "artifact_policy": {
            "fresh_adapter_only": True,
            "parent_adapter": None,
            "save_strategy": "final_adapter_only",
            "validation_checkpoint_selection": False,
        },
    }


def validate_execution_spec(
    contract: dict,
    execution_spec: dict,
) -> dict:
    recipe = contract.get("training_recipe")
    if not isinstance(recipe, dict):
        raise TrainingHold("contract training_recipe missing")

    trainer = execution_spec.get("trainer")
    quant = execution_spec.get("quantization")
    lora = execution_spec.get("lora")
    if not isinstance(trainer, dict):
        raise TrainingHold("execution trainer spec missing")
    if not isinstance(quant, dict):
        raise TrainingHold("execution quantization spec missing")
    if not isinstance(lora, dict):
        raise TrainingHold("execution LoRA spec missing")

    trainer_fields = (
        "method",
        "seed",
        "epochs",
        "learning_rate",
        "lr_scheduler_type",
        "warmup_optimizer_steps",
        "per_device_train_batch_size",
        "gradient_accumulation_steps",
        "max_length",
        "overflow_policy",
        "optimizer",
        "completion_only_loss",
        "packing",
        "shuffle_dataset",
        "gradient_checkpointing",
        "validation_role",
    )
    reasons: list[str] = []
    for field in trainer_fields:
        if trainer.get(field) != recipe.get(field):
            reasons.append(
                f"{field}:{trainer.get(field)}!={recipe.get(field)}"
            )

    for field in ("load_in_4bit", "type", "double_quant", "compute_dtype"):
        if quant.get(field) != recipe.get("quantization", {}).get(field):
            reasons.append(
                f"quantization.{field}:"
                f"{quant.get(field)}!="
                f"{recipe.get('quantization', {}).get(field)}"
            )

    for field in ("r", "alpha", "dropout", "target_modules"):
        if lora.get(field) != recipe.get("lora", {}).get(field):
            reasons.append(
                f"lora.{field}:{lora.get(field)}!="
                f"{recipe.get('lora', {}).get(field)}"
            )

    base = contract.get("base_model", {})
    policy = execution_spec.get("artifact_policy", {})
    if policy.get("fresh_adapter_only") is not True:
        reasons.append("fresh_adapter_only")
    if base.get("fresh_adapter_required") is not True:
        reasons.append("contract_fresh_adapter_required")
    if policy.get("parent_adapter") is not None:
        reasons.append("execution_parent_adapter_not_null")
    if base.get("parent_adapter") is not None:
        reasons.append("contract_parent_adapter_not_null")
    if policy.get("validation_checkpoint_selection") is not False:
        reasons.append("validation_checkpoint_selection_not_false")

    if reasons:
        raise TrainingHold(
            "execution spec does not match frozen recipe: "
            + " | ".join(reasons)
        )
    return {
        "schema": "V10_QWEN35_EXECUTION_SPEC_CHECK_V1",
        "status": "PASS",
        "execution_spec_sha256": sha256_bytes(
            canonical_bytes(execution_spec)
        ),
    }


def write_run_start_receipt(
    output_dir: Path,
    *,
    authority: dict,
    contract_sha256: str,
    execution_spec_sha256: str,
    runtime_binding_sha256: str,
    sealed_commitment_sha256: str,
    train_sha256: str,
    validation_sha256: str,
    started_at: str,
) -> dict:
    validate_output_namespace(output_dir, authority)
    output_dir.mkdir(parents=True, exist_ok=False)

    receipt = {
        "schema": "V10_QWEN35_RUN_STARTED_V1",
        "status": "RUN_STARTED",
        "effect": "TRAIN_ONE_FRESH_QLORA_ADAPTER",
        "started_at": started_at,
        "output_namespace": str(output_dir),
        "authority_receipt_sha256": authority.get("receipt_sha256"),
        "contract_sha256": contract_sha256,
        "execution_spec_sha256": execution_spec_sha256,
        "runtime_binding_sha256": runtime_binding_sha256,
        "sealed_final_bank_commitment_sha256": sealed_commitment_sha256,
        "train_sha256": train_sha256,
        "validation_sha256": validation_sha256,
    }
    receipt["receipt_sha256"] = sha256_bytes(canonical_bytes(receipt))
    path = output_dir / "RUN_STARTED.json"
    try:
        with path.open("xb") as handle:
            handle.write(
                (
                    json.dumps(receipt, indent=2, sort_keys=True)
                    + "\n"
                ).encode("utf-8")
            )
    except FileExistsError as exc:
        raise TrainingHold(
            f"run start receipt already exists: {path}"
        ) from exc
    return receipt


def observe_lightweight_runtime(binding: dict) -> dict:
    """Observe package/base-file identity without importing the training stack."""
    target = binding.get("target")
    if not isinstance(target, dict):
        raise TrainingHold("runtime binding target missing")

    packages = {}
    for package in sorted(binding.get("packages", {})):
        distribution = package
        if package == "huggingface_hub":
            distribution = "huggingface-hub"
        try:
            packages[package] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError as exc:
            raise TrainingHold(
                f"bound runtime package not installed:{package}"
            ) from exc

    base_path = Path(str(target.get("base_path", "")))
    artifacts = {}
    for name in sorted(binding.get("base_artifacts", {})):
        path = base_path / name
        if not path.is_file():
            raise TrainingHold(f"bound base artifact missing:{path}")
        artifacts[name] = sha256_file(path)

    # GPU fields require torch and are intentionally observed only after the
    # preflight READY gate. Keep this lightweight function CPU/import safe.
    return {
        "python_version": platform.python_version(),
        "packages": packages,
        "base_artifacts": artifacts,
    }


def plan_execution(
    repo_root: Path | str,
    *,
    training_stack_loader: Callable[[], object] = load_training_stack,
) -> dict:
    preflight = assess_preflight(repo_root)
    if (
        preflight.get("status") != "READY_PRECONDITIONS"
        or preflight.get("training_allowed") is not True
    ):
        return {
            "schema": "V10_QWEN35_AUTHORIZED_TRAINING_PLAN_V1",
            "status": "HOLD",
            "training_stack_loaded": False,
            "reasons": list(preflight.get("reasons", [])),
            "preflight": preflight,
            "effect": "READ_ONLY_PLAN_NO_WEIGHT_CHANGE",
        }

    stack = gated_training_stack(preflight, training_stack_loader)
    return {
        "schema": "V10_QWEN35_AUTHORIZED_TRAINING_PLAN_V1",
        "status": "READY",
        "training_stack_loaded": stack is not None,
        "reasons": [],
        "preflight": preflight,
        "effect": "READ_ONLY_PLAN_NO_WEIGHT_CHANGE",
    }


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)

    # No execute mode is exposed yet. This command is deliberately read-only
    # until the exact runner/execution-spec digests are added to the authority
    # contract and Patrick explicitly authorizes the bound weight change.
    if not args.plan_only:
        raise TrainingHold(
            "weight-changing execute mode is not exposed; use --plan-only"
        )

    result = plan_execution(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "READY" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except TrainingHold as exc:
        print(
            json.dumps(
                {
                    "schema": "V10_QWEN35_AUTHORIZED_TRAINING_PLAN_V1",
                    "status": "HOLD",
                    "training_allowed": False,
                    "reason": str(exc),
                    "effect": "NO_WEIGHT_CHANGE",
                },
                sort_keys=True,
            )
        )
        raise SystemExit(2)
