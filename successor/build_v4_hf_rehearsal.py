from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DATASET_REPO = "HuggingFaceTB/smoltalk2"
DATASET_REVISION = "fc6cc2103c066455aade5d7fbb346039ae36ca5e"
DATASET_CONFIG = "SFT"
TOKENIZER_REPO = "HuggingFaceTB/SmolLM3-3B"
TOKENIZER_REVISION = "a07cc9a04f16550a088caea529712d1d335b0ac1"
DATASETS_VERSION = "4.1.1"
TRANSFORMERS_VERSION = "5.14.1"
SEED = 20260922
SHUFFLE_BUFFER = 20000
MAX_TOKENS = 1536
SYSTEM = {"role": "system", "content": "/no_think /system_override"}
TARGETS = {
    "smoltalk_smollm3_explore_instruct_rewriting_no_think": 8000,
    "smoltalk_smollm3_smol_rewrite_no_think": 6000,
    "smoltalk_smollm3_smol_summarize_no_think": 6000,
    "tulu_3_sft_personas_instruction_following_no_think": 7000,
    "Mixture_of_Thoughts_science_no_think": 6000,
    "OpenHermes_2.5_no_think": 5000,
    "table_gpt_no_think": 4500,
}
EXPECTED_ROWS = 42500


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def pair_digest(prompt: str, response: str) -> str:
    return hashlib.sha256((prompt + "\0" + response).encode("utf-8")).hexdigest()


def extract_pair(row: dict[str, Any]) -> tuple[str, str] | None:
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) != 2:
        return None
    first, second = messages
    if not isinstance(first, dict) or not isinstance(second, dict):
        return None
    if first.get("role") != "user" or second.get("role") != "assistant":
        return None
    prompt, response = first.get("content"), second.get("content")
    if not isinstance(prompt, str) or not isinstance(response, str):
        return None
    prompt, response = prompt.strip(), response.strip()
    if not prompt or not response:
        return None
    return prompt, response


def rendered_token_count(tokenizer, prompt: str, response: str) -> int:
    text = tokenizer.apply_chat_template(
        [SYSTEM, {"role": "user", "content": prompt}, {"role": "assistant", "content": response}],
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def build(output_path: Path | None = None) -> dict[str, Any]:
    import datasets
    import transformers
    from datasets import load_dataset
    from transformers import AutoTokenizer

    if datasets.__version__ != DATASETS_VERSION:
        raise RuntimeError(f"datasets version mismatch: {datasets.__version__}")
    if transformers.__version__ != TRANSFORMERS_VERSION:
        raise RuntimeError(f"transformers version mismatch: {transformers.__version__}")

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_REPO, revision=TOKENIZER_REVISION)
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
            pair = extract_pair(source_row)
            if pair is None:
                rejected_shape += 1
                continue
            prompt, response = pair
            digest = pair_digest(prompt, response)
            if digest in seen:
                rejected_duplicate += 1
                continue
            if rendered_token_count(tokenizer, prompt, response) > MAX_TOKENS:
                rejected_length += 1
                continue
            seen.add(digest)
            normalized = {
                "schema": "VERA_V4_HF_REHEARSAL_ROW_V1",
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
        "tokenizer_repo": TOKENIZER_REPO,
        "tokenizer_revision": TOKENIZER_REVISION,
        "datasets_version": DATASETS_VERSION,
        "transformers_version": TRANSFORMERS_VERSION,
        "seed": SEED,
        "shuffle_buffer": SHUFFLE_BUFFER,
        "max_tokens": MAX_TOKENS,
        "targets": TARGETS,
    }
    return {
        "schema": "VERA_V4_HF_REHEARSAL_MANIFEST_V1",
        "rows": len(lines),
        "unique_pairs": len(seen),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "recipe_sha256": hashlib.sha256(canonical_json(recipe).encode()).hexdigest(),
        "source_stats": source_stats,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    print(json.dumps(build(args.output), sort_keys=True))


if __name__ == "__main__":
    main()
