from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from successor.v5.generate_targeted_pairs import DIMENSIONS

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = Path(__file__).with_name("UNBOUND_SOL_BEHAVIOR_V3_BRIDGE_V1.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def canonical_pair_sha(prompt: str, chosen: str, rejected: str) -> str:
    return hashlib.sha256((prompt + "\0" + chosen + "\0" + rejected).encode("utf-8")).hexdigest()


def normalize_prompt(text: str) -> str:
    return " ".join(text.lower().split())


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        rows.append(row)
    return rows


def load_bridge(path: Path = BRIDGE_PATH) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "VERA_V5_UNBOUND_SOL_BEHAVIOR_V3_BRIDGE_V1":
        raise ValueError("unexpected bridge schema")
    return value


def choose_primary(targets: list[str], bridge: dict) -> str:
    mapping = bridge["target_mapping"]
    unknown = set(targets) - set(mapping)
    if unknown:
        raise ValueError(f"unmapped Behavior V3 targets: {sorted(unknown)}")
    for target in bridge["primary_dimension_priority"]:
        if target in targets:
            return mapping[target]["primary_dimension"]
    raise ValueError("no primary dimension resolved")


def mapped_dimensions(targets: list[str], bridge: dict) -> list[str]:
    mapping = bridge["target_mapping"]
    dims: list[str] = []
    for target in targets:
        item = mapping[target]
        for dim in [item["primary_dimension"], *item.get("secondary_dimensions", [])]:
            if dim not in dims:
                dims.append(dim)
    return dims


def validate_source(rows: list[dict], source_bytes: bytes, bridge: dict) -> None:
    source = bridge["source"]
    if git_blob_sha1(source_bytes) != source["git_blob_sha1"]:
        raise ValueError("source snapshot Git blob SHA-1 mismatch")
    if len(rows) != source["expected_rows"]:
        raise ValueError(f"source rows {len(rows)} != {source['expected_rows']}")

    ids: set[str] = set()
    prompts: set[str] = set()
    for row in rows:
        if row.get("schema") != source["source_schema"]:
            raise ValueError(f"{row.get('id')}: unexpected source schema")
        if row.get("exposure_class") != source["exposure_class"]:
            raise ValueError(f"{row.get('id')}: wrong exposure class")
        if row.get("holdout_eligible") is not False:
            raise ValueError(f"{row.get('id')}: gold source may not be holdout eligible")
        record_id = row.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("source row missing id")
        if record_id in ids:
            raise ValueError(f"duplicate source id: {record_id}")
        ids.add(record_id)
        prompt = row.get("prompt")
        chosen = row.get("preferred")
        rejected = row.get("rejected")
        targets = row.get("targets")
        if not all(isinstance(x, str) and x.strip() for x in (prompt, chosen, rejected)):
            raise ValueError(f"{record_id}: missing prompt/preferred/rejected")
        if not isinstance(targets, list) or not targets:
            raise ValueError(f"{record_id}: targets must be non-empty list")
        normalized = normalize_prompt(prompt)
        if normalized in prompts:
            raise ValueError(f"{record_id}: duplicate normalized prompt")
        prompts.add(normalized)
        if chosen.strip() == rejected.strip():
            raise ValueError(f"{record_id}: chosen and rejected identical")
        dims = mapped_dimensions(targets, bridge)
        if any(dim not in DIMENSIONS for dim in dims):
            raise ValueError(f"{record_id}: mapped dimension missing from V5 taxonomy: {dims}")


def convert(source_path: Path, output_path: Path, manifest_path: Path) -> dict:
    bridge = load_bridge()
    source_bytes = source_path.read_bytes()
    rows = load_jsonl(source_path)
    validate_source(rows, source_bytes, bridge)

    converted: list[dict] = []
    per_primary: Counter[str] = Counter()
    for row in rows:
        targets = row["targets"]
        primary = choose_primary(targets, bridge)
        dims = mapped_dimensions(targets, bridge)
        pair_sha = canonical_pair_sha(row["prompt"], row["preferred"], row["rejected"])
        converted.append({
            "schema": "VERA_V5_GOLD_TARGETED_PAIR_V1",
            "candidate_id": f"gold-sol-{row['id']}-{pair_sha[:16]}",
            "dimension": primary,
            "dimension_name": DIMENSIONS[primary]["name"],
            "secondary_dimensions": [dim for dim in dims if dim != primary],
            "behavior_v3_targets": targets,
            "source_record_id": row["id"],
            "source_repo": bridge["source"]["repository"],
            "source_revision": bridge["source"]["revision"],
            "source_path": bridge["source"]["path"],
            "source_git_blob_sha1": bridge["source"]["git_blob_sha1"],
            "source_exposure_class": bridge["source"]["exposure_class"],
            "qualification_eligible": False,
            "prompt": row["prompt"],
            "chosen": row["preferred"],
            "rejected": row["rejected"],
            "discriminator": row["why_preferred"],
            "failure_mode": row["failure_mode"],
            "pair_sha256": pair_sha,
            "curation": {
                "kind": "HUMAN_AUTHORED_PUBLIC_GOLD",
                "source_exactly_bound": True,
                "model_judge_used": False,
            },
        })
        per_primary[primary] += 1

    converted.sort(key=lambda row: row["candidate_id"])
    payload = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in converted) + "\n").encode("utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)

    manifest = {
        "schema": "VERA_V5_GOLD_TARGETED_MANIFEST_V1",
        "rows": len(converted),
        "sha256": sha256_bytes(payload),
        "source_revision": bridge["source"]["revision"],
        "source_git_blob_sha1": bridge["source"]["git_blob_sha1"],
        "source_snapshot_sha256": sha256_bytes(source_bytes),
        "per_primary_dimension": dict(sorted(per_primary.items())),
        "exposure_class": "PUBLIC_TRAINING_REGRESSION_ONLY",
        "qualification_eligible": False,
        "generated_quota_reduction": 0,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def merge_generated_with_gold(generated_path: Path, gold_path: Path, output_path: Path) -> dict:
    generated = load_jsonl(generated_path)
    gold = load_jsonl(gold_path)
    seen_pairs: set[str] = set()
    seen_prompts: set[str] = set()

    for row in [*generated, *gold]:
        pair_sha = row.get("pair_sha256")
        if not isinstance(pair_sha, str) or not pair_sha:
            raise ValueError("targeted row missing pair_sha256")
        if pair_sha in seen_pairs:
            raise ValueError(f"duplicate pair across generated/gold targeted data: {pair_sha}")
        seen_pairs.add(pair_sha)
        prompt = row.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("targeted row missing prompt")
        normalized = normalize_prompt(prompt)
        if normalized in seen_prompts:
            raise ValueError(f"duplicate prompt across generated/gold targeted data: {prompt[:80]}")
        seen_prompts.add(normalized)

    combined = [*generated, *gold]
    combined.sort(key=lambda row: hashlib.sha256(("v5-combined-targeted:" + row["pair_sha256"]).encode()).hexdigest())
    payload = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in combined) + "\n").encode("utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)
    return {
        "schema": "VERA_V5_COMBINED_TARGETED_MANIFEST_V1",
        "generated_rows": len(generated),
        "gold_rows": len(gold),
        "rows": len(combined),
        "sha256": sha256_bytes(payload),
        "gold_qualification_eligible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert exact public Behavior V3 gold pairs into Vera V5 targeted rows.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(convert(args.source, args.output, args.manifest), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
