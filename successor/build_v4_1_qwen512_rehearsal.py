from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from successor import build_v4_hf_rehearsal as base
from successor import build_v4_1_hf_rehearsal as v41

DATASET_REPO = base.DATASET_REPO
DATASET_REVISION = base.DATASET_REVISION
DATASET_CONFIG = base.DATASET_CONFIG
DATASETS_VERSION = "4.1.1"
TRANSFORMERS_VERSION = "5.17.0"
QWEN_REPO = "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
QWEN_REVISION = "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
SEED = base.SEED
SHUFFLE_BUFFER = base.SHUFFLE_BUFFER
MAX_TOKENS = 512
TARGETS = dict(v41.TARGETS)
EXPECTED_ROWS = sum(TARGETS.values())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def rendered_token_count(tokenizer, prompt: str, response: str) -> int:
    messages = [{"role": "user", "content": prompt}]
    try:
        prefix = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        prefix = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    text = prefix + response + (tokenizer.eos_token or "")
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def _load_tokenizer():
    from transformers import AutoTokenizer

    local = os.environ.get("QWEN35_TOKENIZER_DIR")
    if local:
        return AutoTokenizer.from_pretrained(local, local_files_only=True)
    return AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)


def build(output_path: Path | None = None) -> dict[str, Any]:
    import datasets
    import transformers
    from datasets import load_dataset

    if datasets.__version__ != DATASETS_VERSION:
        raise RuntimeError(f"datasets version mismatch: {datasets.__version__}")
    if transformers.__version__ != TRANSFORMERS_VERSION:
        raise RuntimeError(f"transformers version mismatch: {transformers.__version__}")

    tokenizer = _load_tokenizer()
    seen: set[str] = set()
    lines: list[str] = []
    source_stats: dict[str, Any] = {}

    for split_index, (split, target) in enumerate(TARGETS.items()):
        stream = load_dataset(
            DATASET_REPO,
            DATASET_CONFIG,
            split=split,
            revision=DATASET_REVISION,
            streaming=True,
        ).shuffle(seed=SEED + split_index * 1009, buffer_size=SHUFFLE_BUFFER)

        accepted = 0
        scanned = 0
        rejected_shape = 0
        rejected_length = 0
        rejected_duplicate = 0

        for source_row in stream:
            scanned += 1
            pair = base.extract_pair(source_row)
            if pair is None:
                rejected_shape += 1
                continue
            prompt, response = pair
            digest = base.pair_digest(prompt, response)
            if digest in seen:
                rejected_duplicate += 1
                continue
            if rendered_token_count(tokenizer, prompt, response) > MAX_TOKENS:
                rejected_length += 1
                continue
            seen.add(digest)
            normalized = {
                "schema": "VERA_V10_QWEN512_HF_REHEARSAL_ROW_V1",
                "record_id": f"hf-smoltalk2-{split}-{digest[:24]}",
                "source_class": "ordinary_general_competence",
                "training_use": "general_rehearsal",
                "dataset_repo": DATASET_REPO,
                "dataset_revision": DATASET_REVISION,
                "dataset_config": DATASET_CONFIG,
                "dataset_split": split,
                "source": source_row.get("source"),
                "prompt": prompt,
                "response": response,
                "pair_sha256": digest,
            }
            lines.append(json.dumps(normalized, ensure_ascii=False, separators=(",", ":")))
            accepted += 1
            if accepted >= target:
                break

        if accepted != target:
            raise RuntimeError(f"split {split} produced {accepted}/{target} accepted rows")
        source_stats[split] = {
            "target": target,
            "accepted": accepted,
            "scanned": scanned,
            "rejected_shape": rejected_shape,
            "rejected_length": rejected_length,
            "rejected_duplicate": rejected_duplicate,
        }

    if len(lines) != EXPECTED_ROWS or len(seen) != EXPECTED_ROWS:
        raise RuntimeError(f"unexpected final rows: {len(lines)} unique={len(seen)}")

    payload = ("\n".join(lines) + "\n").encode("utf-8")
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(payload)

    recipe = {
        "dataset_repo": DATASET_REPO,
        "dataset_revision": DATASET_REVISION,
        "dataset_config": DATASET_CONFIG,
        "tokenizer_repo": QWEN_REPO,
        "tokenizer_revision": QWEN_REVISION,
        "datasets_version": DATASETS_VERSION,
        "transformers_version": TRANSFORMERS_VERSION,
        "seed": SEED,
        "shuffle_buffer": SHUFFLE_BUFFER,
        "max_tokens": MAX_TOKENS,
        "formatter": "QWEN_USER_GENERATION_PREFIX_PLUS_RESPONSE_EOS_V1",
        "targets": TARGETS,
    }
    return {
        "schema": "VERA_V10_QWEN512_HF_REHEARSAL_MANIFEST_V1",
        "corpus_id": "VERA_V10_QWEN512_HF_REHEARSAL_42500_20261001_V1",
        "rows": len(lines),
        "unique_pairs": len(seen),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "recipe_sha256": hashlib.sha256(canonical_json(recipe).encode()).hexdigest(),
        "source_stats": source_stats,
        "qwen_max_tokens": MAX_TOKENS,
        "qwen_tokenizer_repo": QWEN_REPO,
        "qwen_tokenizer_revision": QWEN_REVISION,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2, sort_keys=True))
