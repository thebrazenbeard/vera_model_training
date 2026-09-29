from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import os
import random
import tarfile
from pathlib import Path

BASE_REPO = "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV = "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
OUTPUT_IDENTITY = "Vera-Qwen3.5-4B-Behavior-V1-v4-candidate-a"
SEED = 20260929
SFT_LR = 2e-5
LORA_R = 4
LORA_ALPHA = 16
HARDWARE_PROFILES = {
    "generic": {"max_length": 1024, "overflow": "error", "target_vram_mib": None, "optimizer": "adamw_torch"},
    "lappy-rtx3050-4gb": {"max_length": 512, "overflow": "error", "target_vram_mib": 4096, "optimizer": "adamw_torch"},
}


def hardware_profile(name: str) -> dict:
    if name not in HARDWARE_PROFILES:
        raise ValueError(f"unsupported hardware profile {name}")
    return dict(HARDWARE_PROFILES[name])


def runtime_profile(device: str) -> dict:
    if device == "cpu":
        return {"device_map": {"": "cpu"}, "compute_dtype": "float32", "bf16": False, "tf32": False}
    if device == "cuda":
        return {"device_map": {"": 0}, "compute_dtype": "bfloat16", "bf16": True, "tf32": True}
    raise ValueError(f"unsupported device {device}")


def generation_prefix(tok, prompt: str) -> str:
    try:
        return tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)


def sft_row(tok, prompt: str, response: str) -> dict:
    return {"prompt": generation_prefix(tok, prompt), "completion": response + (tok.eos_token or "")}


def _token_count(tok, text: str) -> int:
    return len(tok(text, add_special_tokens=False)["input_ids"])


def validate_token_budget(tok, sft_data: list[dict], max_length: int) -> dict:
    lengths = [_token_count(tok, r["prompt"] + r["completion"]) for r in sft_data]
    report = {"rows": len(lengths), "max_tokens": max(lengths, default=0), "over_budget": sum(n > max_length for n in lengths), "max_length": max_length}
    if report["over_budget"]:
        raise RuntimeError(f"token budget exceeded: max_length={max_length} over={report['over_budget']}")
    return report


def validate_frozen_corpus(corpus_path: Path, manifest_path: Path) -> tuple[list[dict], str]:
    raw = corpus_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if digest != manifest["corpus_sha256"]:
        raise RuntimeError(f"corpus hash mismatch: {digest} != {manifest['corpus_sha256']}")
    rows = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows) != int(manifest["rows"]):
        raise RuntimeError(f"corpus row mismatch: {len(rows)} != {manifest['rows']}")
    if len(rows) != 512:
        raise RuntimeError(f"V4 candidate A requires 512 rows, got {len(rows)}")
    return rows, digest


def base_receipt(rows: int, corpus_sha256: str, hardware_profile_name: str) -> dict:
    return {
        "schema": "VERA_QWEN35_BEHAVIOR_V4_TRAINING_RECEIPT_V1",
        "output_identity": OUTPUT_IDENTITY,
        "training_method": "QLORA_SFT_ONLY",
        "parent_adapter": None,
        "base_repo": BASE_REPO,
        "base_revision": BASE_REV,
        "sft_rows": rows,
        "corpus_sha256": corpus_sha256,
        "seed": SEED,
        "sft_learning_rate": SFT_LR,
        "hardware_profile": hardware_profile_name,
        "lora": {"r": LORA_R, "alpha": LORA_ALPHA, "target_modules": "all-linear"},
    }


def load_tokenizer(base_dir: str | None = None):
    from transformers import AutoTokenizer
    source = base_dir or os.environ.get("QWEN35_BASE_DIR") or BASE_REPO
    kwargs = {} if base_dir or os.environ.get("QWEN35_BASE_DIR") else {"revision": BASE_REV}
    tok = AutoTokenizer.from_pretrained(source, **kwargs)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    return tok


def load_model(device: str, tok, base_dir: str | None = None):
    import torch
    from peft import LoraConfig, prepare_model_for_kbit_training
    from transformers import BitsAndBytesConfig, Qwen3_5ForCausalLM

    profile = runtime_profile(device)
    compute_dtype = getattr(torch, profile["compute_dtype"])
    q = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    source = base_dir or BASE_REPO
    kwargs = {} if base_dir else {"revision": BASE_REV}
    model = Qwen3_5ForCausalLM.from_pretrained(
        source,
        quantization_config=q,
        device_map=profile["device_map"],
        dtype=compute_dtype,
        **kwargs,
    )
    model.config.use_cache = False

    types = list(getattr(model.config, "layer_types", []))
    if len(types) != 32 or types.count("linear_attention") != 24 or types.count("full_attention") != 8:
        raise RuntimeError(f"unexpected Qwen3.5 topology: layers={len(types)} types={types}")
    names = [n for n, _ in model.named_modules()]
    expected = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_b", "in_proj_a", "out_proj", "gate_proj", "up_proj", "down_proj"]
    counts = {x: sum(n.endswith(x) for n in names) for x in expected}
    required = {"q_proj": 8, "k_proj": 8, "v_proj": 8, "o_proj": 8, "in_proj_qkv": 24, "in_proj_z": 24, "in_proj_b": 24, "in_proj_a": 24}
    for key, value in required.items():
        if counts[key] != value:
            raise RuntimeError(f"module topology mismatch {key}: {counts[key]} != {value}")
    if any("vision" in n.lower() or ".visual" in n.lower() for n in names):
        raise RuntimeError("vision modules present in text-only Qwen3_5ForCausalLM")

    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="all-linear",
    )
    return model, lora, counts


def archive_dir(path: Path) -> bytes:
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w:gz", compresslevel=6) as tf:
        for item in sorted(path.rglob("*")):
            if item.is_file():
                tf.add(item, arcname=str(item.relative_to(path.parent)))
    return bio.getvalue()


def emit(tag: str, raw: bytes, chunk: int = 65536) -> None:
    b64 = base64.b64encode(raw).decode("ascii")
    total = math.ceil(len(b64) / chunk)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}", flush=True)
    for i in range(total):
        print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*chunk:(i+1)*chunk]}", flush=True)
    print(f"{tag}_COMPLETE", flush=True)


def run(corpus_path: Path, manifest_path: Path, out: Path, smoke: bool, device: str, base_dir: str | None, emit_archive: bool, hardware_profile_name: str) -> dict:
    import peft as peft_lib
    import torch
    import transformers
    import trl
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer

    random.seed(SEED)
    torch.manual_seed(SEED)
    profile = hardware_profile(hardware_profile_name)
    runtime = runtime_profile(device)
    rows, corpus_sha = validate_frozen_corpus(corpus_path, manifest_path)
    tok = load_tokenizer(base_dir)
    sft_data = [sft_row(tok, row["prompt"], row["response"]) for row in rows]
    if smoke:
        sft_data = sft_data[:24]
    token_budget = validate_token_budget(tok, sft_data, profile["max_length"])
    print("TOKEN_BUDGET=" + json.dumps(token_budget, sort_keys=True), flush=True)
    model, lora, module_counts = load_model(device, tok, base_dir=base_dir)

    out.mkdir(parents=True, exist_ok=True)
    args = SFTConfig(
        output_dir=str(out / "sft_work"),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1 if smoke else 8,
        num_train_epochs=1.0,
        max_steps=1 if smoke else -1,
        learning_rate=SFT_LR,
        lr_scheduler_type="cosine",
        warmup_steps=0 if smoke else 3,
        optim=profile["optimizer"],
        bf16=runtime["bf16"],
        tf32=runtime["tf32"],
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_length=profile["max_length"],
        completion_only_loss=True,
        packing=False,
        shuffle_dataset=True,
        logging_steps=1 if smoke else 10,
        save_strategy="no",
        eval_strategy="no",
        report_to="none",
        seed=SEED,
        data_seed=SEED,
    )
    trainer = SFTTrainer(model=model, args=args, train_dataset=Dataset.from_list(sft_data), processing_class=tok, peft_config=lora)
    result = trainer.train()
    model = trainer.model
    targets = list(getattr(model, "targeted_module_names", []))
    if not targets:
        raise RuntimeError("PEFT reported no targeted modules")
    families = {
        "linear_attn": sum(".linear_attn." in n for n in targets),
        "self_attn": sum(".self_attn." in n for n in targets),
        "mlp": sum(".mlp." in n for n in targets),
    }
    if not all(families.values()):
        raise RuntimeError(f"all-linear coverage incomplete: {families}")
    adapter = out / "adapter"
    for _, param in model.named_parameters():
        if param.requires_grad and param.is_floating_point():
            param.data = param.data.to(torch.bfloat16)
    model.save_pretrained(adapter, safe_serialization=True)
    archive = archive_dir(adapter)
    receipt = base_receipt(len(rows), corpus_sha, hardware_profile_name)
    receipt.update({
        "smoke": smoke,
        "device": device,
        "max_length": profile["max_length"],
        "overflow": profile["overflow"],
        "optimizer": profile["optimizer"],
        "token_budget": token_budget,
        "sft_loss": float(result.training_loss),
        "lora": {"r": LORA_R, "alpha": LORA_ALPHA, "target_modules": "all-linear", "targeted_module_count": len(targets), "families": families, "saved_dtype": "bfloat16"},
        "base_topology": module_counts,
        "adapter_archive_bytes": len(archive),
        "adapter_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "versions": {"torch": torch.__version__, "transformers": transformers.__version__, "trl": trl.__version__, "peft": peft_lib.__version__},
    })
    (out / "training_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("TRAINING_RECEIPT=" + json.dumps(receipt, sort_keys=True), flush=True)
    if emit_archive:
        emit("ADAPTER_ARCHIVE", archive)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--base-dir")
    ap.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    ap.add_argument("--hardware-profile", choices=sorted(HARDWARE_PROFILES), default="lappy-rtx3050-4gb")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--emit-archive", action="store_true")
    a = ap.parse_args()
    run(a.corpus, a.manifest, a.output_dir, a.smoke, a.device, a.base_dir, a.emit_archive, a.hardware_profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())