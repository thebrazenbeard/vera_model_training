from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from successor import build_v4_1_diverse_corpus as v4_1
from successor import build_v4_2_identity_bound_corpus as v4_2

SCHEMA = "VERA_V10_IDENTITY_BOUND_QWEN512_TRAINING_CORPUS_MANIFEST_V1"
CORPUS_ID = "VERA_SUCCESSOR_V10_IDENTITY_BOUND_QWEN512_50K_20261004_V1"
PARENT_CORPUS_ID = "VERA_SUCCESSOR_V10_QWEN512_50K_20261001_V1"
PARENT_TRAIN_SHA256 = "a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300"
PARENT_VALIDATION_SHA256 = "ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7"
EXPECTED_TRAIN_ROWS = 50_000
EXPECTED_VALIDATION_ROWS = 2_500
EXPECTED_TRAIN_IDENTITY_ROWS = 950
EXPECTED_VALIDATION_IDENTITY_ROWS = 50

_OLD_IDENTITY = v4_1.rows_for("identity_stability")
_NEW_IDENTITY = v4_2.rows_for("identity_stability")


def _render_row(row: dict) -> bytes:
    return (
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _identity_index(row: dict) -> int:
    record_id = row.get("record_id")
    prefix = "v4.1-identity_stability-"
    if not isinstance(record_id, str) or not record_id.startswith(prefix):
        raise RuntimeError(
            f"unexpected identity_stability record_id: {record_id!r}"
        )
    suffix = record_id[len(prefix) :]
    if not suffix.isdigit():
        raise RuntimeError(f"invalid identity_stability record_id: {record_id}")
    index = int(suffix) - 1
    if index < 0 or index >= len(_OLD_IDENTITY):
        raise RuntimeError(f"identity_stability index out of range: {record_id}")
    return index


def transform_jsonl_bytes(payload: bytes) -> tuple[bytes, dict]:
    lines = payload.splitlines(keepends=True)
    out: list[bytes] = []
    rows = 0
    replaced = 0
    preserved = 0
    bound = 0
    legacy = 0

    for line_number, raw in enumerate(lines, start=1):
        if not raw.strip():
            out.append(raw)
            continue
        try:
            row = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"invalid parent JSONL at line {line_number}") from exc
        if not isinstance(row, dict):
            raise RuntimeError(f"parent row {line_number} is not an object")
        rows += 1

        if row.get("family") != "identity_stability":
            out.append(raw)
            preserved += 1
            continue

        index = _identity_index(row)
        expected = _OLD_IDENTITY[index]
        if row != expected:
            raise RuntimeError(
                f"parent identity row mismatch at line {line_number}: "
                f"{row.get('record_id')}"
            )
        replacement = _NEW_IDENTITY[index]
        out.append(_render_row(replacement))
        replaced += 1
        if replacement.get("identity_binding") is True:
            bound += 1
        else:
            legacy += 1

    transformed = b"".join(out)
    return transformed, {
        "rows": rows,
        "identity_rows_replaced": replaced,
        "identity_binding_rows": bound,
        "legacy_identity_governance_rows": legacy,
        "non_identity_rows_preserved": preserved,
        "sha256": hashlib.sha256(transformed).hexdigest(),
        "bytes": len(transformed),
    }


def _read_verified(path: Path, expected_sha256: str, label: str) -> bytes:
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256:
        raise RuntimeError(
            f"{label} parent hash mismatch: {actual} != {expected_sha256}"
        )
    return payload


def build(
    parent_train: Path,
    parent_validation: Path,
    train_out: Path,
    validation_out: Path,
    manifest_out: Path,
) -> dict:
    parent_train_bytes = _read_verified(
        parent_train, PARENT_TRAIN_SHA256, "train"
    )
    parent_validation_bytes = _read_verified(
        parent_validation, PARENT_VALIDATION_SHA256, "validation"
    )

    train_bytes, train_stats = transform_jsonl_bytes(parent_train_bytes)
    validation_bytes, validation_stats = transform_jsonl_bytes(
        parent_validation_bytes
    )

    if train_stats["rows"] != EXPECTED_TRAIN_ROWS:
        raise RuntimeError(
            f"train row count mismatch: {train_stats['rows']} != {EXPECTED_TRAIN_ROWS}"
        )
    if validation_stats["rows"] != EXPECTED_VALIDATION_ROWS:
        raise RuntimeError(
            "validation row count mismatch: "
            f"{validation_stats['rows']} != {EXPECTED_VALIDATION_ROWS}"
        )
    if train_stats["identity_rows_replaced"] != EXPECTED_TRAIN_IDENTITY_ROWS:
        raise RuntimeError(
            "train identity row count mismatch: "
            f"{train_stats['identity_rows_replaced']} != "
            f"{EXPECTED_TRAIN_IDENTITY_ROWS}"
        )
    if (
        validation_stats["identity_rows_replaced"]
        != EXPECTED_VALIDATION_IDENTITY_ROWS
    ):
        raise RuntimeError(
            "validation identity row count mismatch: "
            f"{validation_stats['identity_rows_replaced']} != "
            f"{EXPECTED_VALIDATION_IDENTITY_ROWS}"
        )

    train_out.parent.mkdir(parents=True, exist_ok=True)
    validation_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    train_out.write_bytes(train_bytes)
    validation_out.write_bytes(validation_bytes)

    manifest = {
        "schema": SCHEMA,
        "corpus_id": CORPUS_ID,
        "parent_corpus_id": PARENT_CORPUS_ID,
        "parent_train_sha256": PARENT_TRAIN_SHA256,
        "parent_validation_sha256": PARENT_VALIDATION_SHA256,
        "transform": {
            "type": "IDENTITY_STABILITY_SAME_INDEX_SUBSTITUTION",
            "source_family": "identity_stability",
            "parent_builder": "successor/build_v4_1_diverse_corpus.py",
            "replacement_builder": "successor/build_v4_2_identity_bound_corpus.py",
            "non_identity_line_bytes_preserved": True,
            "row_order_preserved": True,
            "split_membership_preserved": True,
        },
        "train": train_stats,
        "validation": validation_stats,
        "training_authorization": "NOT_GRANTED",
        "weight_change_performed": False,
        "claim_ceiling": (
            "SOURCE_CORPUS_CONSTRUCTION_ONLY_NOT_TRAINED_NOT_QUALIFIED"
        ),
    }
    unsigned = json.dumps(
        manifest, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    manifest["manifest_sha256"] = hashlib.sha256(unsigned).hexdigest()
    manifest_out.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-train", type=Path, required=True)
    parser.add_argument("--parent-validation", type=Path, required=True)
    parser.add_argument("--train-out", type=Path, required=True)
    parser.add_argument("--validation-out", type=Path, required=True)
    parser.add_argument("--manifest-out", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            build(
                args.parent_train,
                args.parent_validation,
                args.train_out,
                args.validation_out,
                args.manifest_out,
            ),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
