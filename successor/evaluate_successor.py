from __future__ import annotations

import hashlib
import json


REQUIRED_FIELDS = {"item_id", "prompt_family", "prompt", "rubric"}


def _canonical(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def prompt_hash(prompt: str) -> str:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("heldout prompt must be nonempty text")
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()


def freeze_heldout_manifest(items, train_prompts, validation_prompts):
    train_hashes = {prompt_hash(p) for p in train_prompts}
    validation_hashes = {prompt_hash(p) for p in validation_prompts}
    seen_prompts = set()
    manifest_items = []
    for item in items:
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"heldout item missing fields: {sorted(missing)}")
        digest = prompt_hash(item["prompt"])
        if digest in seen_prompts:
            raise ValueError("duplicate heldout prompt")
        if digest in train_hashes:
            raise ValueError("heldout prompt has training leakage")
        if digest in validation_hashes:
            raise ValueError("heldout prompt has validation leakage")
        seen_prompts.add(digest)
        item_digest = hashlib.sha256(_canonical(item)).hexdigest()
        manifest_items.append({
            "item_id": item["item_id"],
            "prompt_family": item["prompt_family"],
            "prompt_sha256": digest,
            "item_sha256": item_digest,
        })

    set_digest = hashlib.sha256(_canonical(manifest_items)).hexdigest()
    return {
        "schema_version": 1,
        "item_count": len(manifest_items),
        "items": manifest_items,
        "set_sha256": set_digest,
    }
