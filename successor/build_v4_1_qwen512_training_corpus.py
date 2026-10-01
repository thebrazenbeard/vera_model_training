from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from successor import build_v4_1_qwen512_rehearsal as qwen_rehearsal
from successor import build_v4_1_training_corpus as base

SCHEMA = "VERA_V10_QWEN512_TRAINING_CORPUS_MANIFEST_V1"
CORPUS_ID = "VERA_SUCCESSOR_V10_QWEN512_50K_20261001_V1"
QWEN_TRAINING_CONTRACT = {
    "base_repo": qwen_rehearsal.QWEN_REPO,
    "base_revision": qwen_rehearsal.QWEN_REVISION,
    "max_length": qwen_rehearsal.MAX_TOKENS,
    "overflow": "error",
    "parent_adapter": None,
}


def _digest_manifest(value: dict) -> str:
    payload = dict(value)
    payload.pop("manifest_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def rebind_manifest(manifest: dict) -> dict:
    rebound = dict(manifest)
    rebound["schema"] = SCHEMA
    rebound["corpus_id"] = CORPUS_ID
    rebound["qwen_training_contract"] = dict(QWEN_TRAINING_CONTRACT)
    custom = manifest.get("custom_source", {})
    rebound["parent_v10_custom_corpus_id"] = custom.get("corpus_id")
    rebound["training_authorization"] = "NOT_GRANTED"
    rebound["weight_change_performed"] = False
    rebound["manifest_sha256"] = _digest_manifest(rebound)
    return rebound


def build(train_path: Path, validation_path: Path, manifest_path: Path) -> dict:
    original_rehearsal = base.rehearsal
    base.rehearsal = qwen_rehearsal
    try:
        generated = base.build(train_path, validation_path, manifest_path)
    finally:
        base.rehearsal = original_rehearsal

    rebound = rebind_manifest(generated)
    manifest_path.write_text(
        json.dumps(rebound, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return rebound


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.train, args.validation, args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()
