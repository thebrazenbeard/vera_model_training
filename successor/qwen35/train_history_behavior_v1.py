from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import math
import os
import random
import tarfile
import urllib.request
from pathlib import Path

BASE_REPO = "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV = "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
UF_REPO = "HuggingFaceH4/ultrafeedback_binarized"
UF_REV = "3949bf5f8c17c394422ccfab0c31ea9c20bdeb85"
SEED = 20260923
MAX_LENGTH = 1024
GENERAL_SFT_ROWS = 320
GENERAL_PREF_ROWS = 320
LORA_TARGETS = ["q_proj", "v_proj"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pair_from_messages(messages):
    if not isinstance(messages, list) or len(messages) != 2:
        return None
    a, b = messages
    if not isinstance(a, dict) or not isinstance(b, dict):
        return None
    if a.get("role") != "user" or b.get("role") != "assistant":
        return None
    p, r = a.get("content"), b.get("content")
    if not isinstance(p, str) or not isinstance(r, str):
        return None
    p, r = p.strip(), r.strip()
    if not p or not r:
        return None
    return p, r


def chat_len(tokenizer, prompt: str, response: str) -> int:
    msgs = [{"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
    try:
        text = tokenizer.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=False, enable_thinking=False
        )
    except TypeError:
        text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def download_targeted(url: str) -> tuple[list[dict], str]:
    req = urllib.request.Request(url, headers={"User-Agent": "vera-qwen35-training/1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 480:
        raise RuntimeError(f"targeted row count {len(rows)} != 480")
    if any(row.get("privacy_class") != "DEIDENTIFIED_PORTABLE_BEHAVIOR" for row in rows):
        raise RuntimeError("targeted corpus privacy class mismatch")
    return rows, sha256_bytes(raw)


def load_general(tokenizer):
    from datasets import load_dataset

    def sft_rows():
        ds = load_dataset(UF_REPO, split="train_sft", revision=UF_REV, streaming=True)
        ds = ds.shuffle(seed=SEED + 11, buffer_size=10000)
        out, seen = [], set()
        for row in ds:
            pair = pair_from_messages(row.get("messages"))
            if not pair:
                continue
            p, r = pair
            h = hashlib.sha256((p + "\0" + r).encode()).hexdigest()
            if h in seen or chat_len(tokenizer, p, r) > MAX_LENGTH:
                continue
            seen.add(h)
            out.append({"prompt": p, "response": r, "source": "ultrafeedback_sft"})
            if len(out) >= GENERAL_SFT_ROWS:
                break
        if len(out) != GENERAL_SFT_ROWS:
            raise RuntimeError(f"general SFT accepted {len(out)}")
        return out

    def pref_rows():
        ds = load_dataset(UF_REPO, split="train_prefs", revision=UF_REV, streaming=True)
        ds = ds.shuffle(seed=SEED + 17, buffer_size=10000)
        out, seen = [], set()
        for row in ds:
            cp = pair_from_messages(row.get("chosen"))
            rp = pair_from_messages(row.get("rejected"))
            if not cp or not rp or cp[0] != rp[0]:
                continue
            p, c, r = cp[0], cp[1], rp[1]
            try:
                if float(row["score_chosen"]) - float(row["score_rejected"]) < 1.0:
                    continue
            except Exception:
                continue
            ratio = (len(c) + 1) / (len(r) + 1)
            if not 0.5 <= ratio <= 2.0:
                continue
            if max(chat_len(tokenizer, p, c), chat_len(tokenizer, p, r)) > MAX_LENGTH:
                continue
            h = hashlib.sha256((p + "\0" + c + "\0" + r).encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            out.append({"prompt": p, "chosen": c, "rejected": r, "source": "ultrafeedback_pref"})
            if len(out) >= GENERAL_PREF_ROWS:
                break
        if len(out) != GENERAL_PREF_ROWS:
            raise RuntimeError(f"general pref accepted {len(out)}")
        return out

    return sft_rows(), pref_rows()


def sft_record(prompt: str, response: str) -> dict:
    return {
        "prompt": [{"role": "user", "content": prompt}],
        "completion": [{"role": "assistant", "content": response}],
    }


def pref_record(prompt: str, chosen: str, rejected: str) -> dict:
    return {
        "prompt": [{"role": "user", "content": prompt}],
        "chosen": [{"role": "assistant", "content": chosen}],
        "rejected": [{"role": "assistant", "content": rejected}],
    }


def load_model():
    import torch
    from peft import LoraConfig, prepare_model_for_kbit_training
    from transformers import AutoTokenizer, BitsAndBytesConfig, Qwen3_5ForCausalLM

    tokenizer = AutoTokenizer.from_pretrained(BASE_REPO, revision=BASE_REV)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = Qwen3_5ForCausalLM.from_pretrained(
        BASE_REPO,
        revision=BASE_REV,
        quantization_config=quant,
        device_map={"": 0},
        dtype=torch.bfloat16,
    )
    model.config.use_cache = False

    names = [name for name, _ in model.named_modules()]
    counts = {t: sum(name.endswith(t) for name in names) for t in LORA_TARGETS}
    if any(counts[t] == 0 for t in LORA_TARGETS):
        raise RuntimeError(f"missing LoRA targets: {counts}")
    targeted_names = [n for n in names if any(n.endswith(t) for t in LORA_TARGETS)]
    if any("vision" in n.lower() for n in targeted_names):
        raise RuntimeError("vision module matched LoRA target")
    print("MODULE_COUNTS=" + json.dumps(counts, sort_keys=True), flush=True)
    print("TARGET_SAMPLE=" + json.dumps(targeted_names[:12]), flush=True)

    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora = LoraConfig(
        r=4,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=LORA_TARGETS,
    )
    return model, tokenizer, lora, counts


def archive_adapter(adapter_dir: Path) -> bytes:
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w:gz", compresslevel=6) as tf:
        for p in sorted(adapter_dir.rglob("*")):
            if p.is_file():
                tf.add(p, arcname=str(p.relative_to(adapter_dir.parent)))
    return bio.getvalue()


def emit_archive(data: bytes):
    b64 = base64.b64encode(data).decode("ascii")
    chunk_chars = 12000
    total = math.ceil(len(b64) / chunk_chars)
    print(f"ADAPTER_ARCHIVE|sha256={sha256_bytes(data)}|bytes={len(data)}|chunks={total}", flush=True)
    for i in range(total):
        chunk = b64[i * chunk_chars:(i + 1) * chunk_chars]
        print(f"ADAPTER_CHUNK|{i+1}|{total}|{chunk}", flush=True)
    print("ADAPTER_CHUNKS_COMPLETE", flush=True)


def train(targeted_url: str, output_dir: Path, smoke: bool) -> dict:
    import torch
    import transformers
    import peft as peft_lib
    import trl
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer
    from trl.experimental.orpo import ORPOConfig, ORPOTrainer

    random.seed(SEED)
    torch.manual_seed(SEED)

    targeted, targeted_sha = download_targeted(targeted_url)
    model, tokenizer, lora, module_counts = load_model()
    general_sft, general_pref = load_general(tokenizer)

    target_sft = [
        sft_record(r["prompt"], r["chosen"])
        for r in targeted
        if chat_len(tokenizer, r["prompt"], r["chosen"]) <= MAX_LENGTH
    ]
    target_pref = [
        pref_record(r["prompt"], r["chosen"], r["rejected"])
        for r in targeted
        if max(
            chat_len(tokenizer, r["prompt"], r["chosen"]),
            chat_len(tokenizer, r["prompt"], r["rejected"]),
        ) <= MAX_LENGTH
    ]
    if len(target_sft) < 460 or len(target_pref) < 460:
        raise RuntimeError(f"too many targeted rows exceeded length: sft={len(target_sft)} pref={len(target_pref)}")

    sft_rows = target_sft + [sft_record(r["prompt"], r["response"]) for r in general_sft]
    pref_rows = target_pref + [pref_record(r["prompt"], r["chosen"], r["rejected"]) for r in general_pref]
    random.Random(SEED + 1).shuffle(sft_rows)
    random.Random(SEED + 2).shuffle(pref_rows)

    if smoke:
        sft_rows = sft_rows[:24]
        pref_rows = pref_rows[:12]

    train_ds = Dataset.from_list(sft_rows)
    pref_ds = Dataset.from_list(pref_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    sft_args = SFTConfig(
        output_dir=str(output_dir / "sft_work"),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1 if smoke else 8,
        num_train_epochs=1.0,
        max_steps=1 if smoke else -1,
        learning_rate=5e-5,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03 if not smoke else 0.0,
        optim="paged_adamw_8bit",
        bf16=True,
        tf32=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_length=MAX_LENGTH,
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
    sft = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_ds,
        processing_class=tokenizer,
        peft_config=lora,
    )
    sft_result = sft.train()
    model = sft.model

    orpo_args = ORPOConfig(
        output_dir=str(output_dir / "orpo_work"),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1 if smoke else 8,
        num_train_epochs=1.0,
        max_steps=1 if smoke else -1,
        learning_rate=2e-5,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03 if not smoke else 0.0,
        optim="paged_adamw_8bit",
        bf16=True,
        tf32=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_length=MAX_LENGTH,
        beta=0.1,
        logging_steps=1 if smoke else 10,
        save_strategy="no",
        eval_strategy="no",
        report_to="none",
        seed=SEED,
        data_seed=SEED,
    )
    orpo = ORPOTrainer(
        model=model,
        args=orpo_args,
        train_dataset=pref_ds,
        processing_class=tokenizer,
    )
    orpo_result = orpo.train()
    model = orpo.model

    adapter_dir = output_dir / "adapter"
    model.save_pretrained(adapter_dir, safe_serialization=True)
    tokenizer.save_pretrained(adapter_dir)

    archive = archive_adapter(adapter_dir)
    receipt = {
        "schema": "VERA_QWEN35_HISTORY_TRAINING_RECEIPT_V1",
        "smoke": smoke,
        "base_repo": BASE_REPO,
        "base_revision": BASE_REV,
        "targeted_sha256": targeted_sha,
        "targeted_source_rows": len(targeted),
        "targeted_sft_rows": len(target_sft),
        "targeted_pref_rows": len(target_pref),
        "general_sft_rows": len(general_sft),
        "general_pref_rows": len(general_pref),
        "trained_sft_rows": len(sft_rows),
        "trained_pref_rows": len(pref_rows),
        "seed": SEED,
        "max_length": MAX_LENGTH,
        "sft_loss": float(sft_result.training_loss),
        "orpo_loss": float(orpo_result.training_loss),
        "lora": {"r": 4, "alpha": 16, "targets": LORA_TARGETS, "module_counts": module_counts},
        "adapter_archive_sha256": sha256_bytes(archive),
        "adapter_archive_bytes": len(archive),
        "versions": {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "trl": trl.__version__,
            "peft": peft_lib.__version__,
        },
    }
    (output_dir / "training_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("TRAINING_RECEIPT=" + json.dumps(receipt, sort_keys=True), flush=True)
    emit_archive(archive)
    return receipt


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--targeted-url", required=True)
    ap.add_argument("--output-dir", type=Path, default=Path("/tmp/vera-qwen35-history-v1"))
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    train(args.targeted_url, args.output_dir, args.smoke)
