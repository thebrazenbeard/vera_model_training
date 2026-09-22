from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

from successor import build_v4_custom_corpus as custom
from successor import build_v4_hf_rehearsal as rehearsal

CUSTOM_VALIDATION_PER_FAMILY = 50
REHEARSAL_VALIDATION_ROWS = 2000
EXPECTED_TRAIN_ROWS = 50000
EXPECTED_VALIDATION_ROWS = 2500
SPLIT_SEED = "VERA_V4_SPLIT_20260922_V1"


def stable_key(record_id: str, purpose: str) -> str:
    return hashlib.sha256(f"{SPLIT_SEED}:{purpose}:{record_id}".encode("utf-8")).hexdigest()


def pair_digest(row: dict) -> str:
    return hashlib.sha256((row["prompt"].strip() + "\0" + row["response"].strip()).encode("utf-8")).hexdigest()


def load_rehearsal_rows() -> tuple[list[dict], dict]:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "rehearsal.jsonl"
        manifest = rehearsal.build(path)
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows, manifest


def load_custom_rows() -> tuple[list[dict], dict]:
    rows = []
    families = {}
    for family in custom.CONFIG["specs"]:
        family_rows = custom.rows_for(family)
        rows.extend(family_rows)
        families[family] = len(family_rows)
    return rows, {"rows": len(rows), "families": families}


def split_rows(custom_rows: list[dict], rehearsal_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    custom_val_ids = set()
    by_family: dict[str, list[dict]] = {}
    for row in custom_rows:
        by_family.setdefault(row["family"], []).append(row)
    for family, rows in by_family.items():
        ranked = sorted(rows, key=lambda r: stable_key(r["record_id"], "custom-val"))
        selected = ranked[:CUSTOM_VALIDATION_PER_FAMILY]
        if len(selected) != CUSTOM_VALIDATION_PER_FAMILY:
            raise RuntimeError(f"insufficient custom rows for {family}")
        custom_val_ids.update(row["record_id"] for row in selected)

    rehearsal_ranked = sorted(
        rehearsal_rows,
        key=lambda r: stable_key(r["record_id"], "rehearsal-val"),
    )
    rehearsal_val_ids = {
        row["record_id"] for row in rehearsal_ranked[:REHEARSAL_VALIDATION_ROWS]
    }

    validation = [
        row for row in custom_rows if row["record_id"] in custom_val_ids
    ] + [
        row for row in rehearsal_rows if row["record_id"] in rehearsal_val_ids
    ]
    train = [
        row for row in custom_rows if row["record_id"] not in custom_val_ids
    ] + [
        row for row in rehearsal_rows if row["record_id"] not in rehearsal_val_ids
    ]

    train.sort(key=lambda r: stable_key(r["record_id"], "train-order"))
    validation.sort(key=lambda r: stable_key(r["record_id"], "validation-order"))
    return train, validation


def render(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def build(train_path: Path, validation_path: Path, manifest_path: Path) -> dict:
    custom_rows, custom_manifest = load_custom_rows()
    rehearsal_rows, rehearsal_manifest = load_rehearsal_rows()

    all_rows = custom_rows + rehearsal_rows
    ids = [row["record_id"] for row in all_rows]
    pairs = [pair_digest(row) for row in all_rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate record_id across V4 source pools")
    if len(pairs) != len(set(pairs)):
        raise RuntimeError("duplicate prompt/response pair across V4 source pools")

    train, validation = split_rows(custom_rows, rehearsal_rows)
    if len(train) != EXPECTED_TRAIN_ROWS:
        raise RuntimeError(f"expected {EXPECTED_TRAIN_ROWS} train rows, got {len(train)}")
    if len(validation) != EXPECTED_VALIDATION_ROWS:
        raise RuntimeError(f"expected {EXPECTED_VALIDATION_ROWS} validation rows, got {len(validation)}")

    train_ids = {row["record_id"] for row in train}
    validation_ids = {row["record_id"] for row in validation}
    if train_ids & validation_ids:
        raise RuntimeError("train/validation record overlap")

    train_bytes = render(train)
    validation_bytes = render(validation)
    train_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    train_path.write_bytes(train_bytes)
    validation_path.write_bytes(validation_bytes)

    train_classes = Counter(row["source_class"] for row in train)
    validation_classes = Counter(row["source_class"] for row in validation)
    general_train = train_classes.get("ordinary_general_competence", 0)

    manifest = {
        "schema": "VERA_V4_TRAINING_CORPUS_MANIFEST_V1",
        "corpus_id": "VERA_SUCCESSOR_V4_50K_20260922",
        "source_rows": len(all_rows),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "train_validation_overlap": 0,
        "general_fraction": general_train / len(train),
        "train_counts_by_source_class": dict(sorted(train_classes.items())),
        "validation_counts_by_source_class": dict(sorted(validation_classes.items())),
        "train_sha256": hashlib.sha256(train_bytes).hexdigest(),
        "validation_sha256": hashlib.sha256(validation_bytes).hexdigest(),
        "custom_source": custom_manifest,
        "rehearsal_source": rehearsal_manifest,
        "split_seed": SPLIT_SEED,
        "custom_validation_per_family": CUSTOM_VALIDATION_PER_FAMILY,
        "rehearsal_validation_rows": REHEARSAL_VALIDATION_ROWS,
        "blind_plaintext_included": False,
        "weight_change_performed": False,
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", type=Path, required=True)
    ap.add_argument("--validation", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(build(args.train, args.validation, args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()
