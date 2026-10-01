from __future__ import annotations

from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


LOCATION_MANIFEST_URL = (
    "https://geo.mindstellar.com/releases/"
    "2026-09-20T1335Z/manifest.json"
)
LOCATION_MANIFEST_SHA256 = (
    "bf5a2dc0bb0f1ba15f7149e9fa1184aa632f280a72fe306c154a9e05cfacab29"
)


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
def select_audit_sample(
    rows: list[dict],
    *,
    per_category: int,
    candidate_sha256: str,
) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)
    selected = []
    for category in sorted(grouped):
        ranked = sorted(
            grouped[category],
            key=lambda row: hashlib.sha256(
                (
                    candidate_sha256
                    + "\0"
                    + category
                    + "\0"
                    + row["case_id"]
                ).encode("utf-8")
            ).hexdigest(),
        )
        if len(ranked) < per_category:
            raise ValueError(f"{category}: only {len(ranked)} rows")
        selected.extend(ranked[:per_category])
    return selected
def source_evidence_for_row(
    row: dict,
    countries_by_code: dict[str, dict],
):
    source_id = str(row.get("source_id", ""))
    marker = ":country:"
    if marker in source_id:
        code = source_id.rsplit(marker, 1)[1]
        return countries_by_code[code]
    marker = ":pair:"
    if marker in source_id:
        pair = source_id.rsplit(marker, 1)[1].split(":")
        if len(pair) != 2:
            raise ValueError(f"invalid pair source id: {source_id}")
        return {
            "left": countries_by_code[pair[0]],
            "right": countries_by_code[pair[1]],
        }
    return None


def load_location_manifest() -> dict:
    with urlopen(LOCATION_MANIFEST_URL, timeout=30) as response:
        raw = response.read()
    digest = sha256_bytes(raw)
    if digest != LOCATION_MANIFEST_SHA256:
        raise RuntimeError(
            f"location manifest hash mismatch: {digest}"
        )
    return json.loads(raw.decode("utf-8"))
def build_packet(
    *,
    candidate_path: Path,
    expected_candidate_sha256: str,
    per_category: int,
) -> tuple[list[dict], dict]:
    raw = candidate_path.read_bytes()
    candidate_sha = sha256_bytes(raw)
    if candidate_sha != expected_candidate_sha256:
        raise RuntimeError(
            f"candidate hash mismatch: {candidate_sha}"
        )
    rows = [
        json.loads(line)
        for line in raw.decode("utf-8").splitlines()
        if line.strip()
    ]
    location = load_location_manifest()
    countries = {
        str(country["code"]): country
        for country in location["countries"]
    }
    selected = select_audit_sample(
        rows,
        per_category=per_category,
        candidate_sha256=candidate_sha,
    )
    packet = []
    for row in selected:
        packet.append({
            "case_id": row["case_id"],
            "category": row["category"],
            "family_id": row["family_id"],
            "prompt": row["prompt"],
            "source_id": row["source_id"],
            "source_revision": row["source_revision"],
            "source_terms": row["source_terms"],
            "source_hash": row["source_hash"],
            "generation_method": row["generation_method"],
            "grader_contract": row["grader_contract"],
            "source_evidence": source_evidence_for_row(
                row, countries
            ),
        })
    payload = (
        "\n".join(canonical_json(row) for row in packet)
        + "\n"
    ).encode("utf-8")
    manifest = {
        "schema": "V10_RETENTION_AUDIT_PACKET_V1",
        "candidate_sha256": candidate_sha,
        "sample_rows": len(packet),
        "per_category": per_category,
        "sample_case_ids": [row["case_id"] for row in packet],
        "packet_sha256": sha256_bytes(payload),
        "selection": (
            "SHA256(candidate_sha256, category, case_id) "
            "lowest ranks per category"
        ),
        "location_manifest_url": LOCATION_MANIFEST_URL,
        "location_manifest_sha256": LOCATION_MANIFEST_SHA256,
        "review_role": (
            "benchmark-quality audit only; source/test truth "
            "remains authoritative"
        ),
    }
    return packet, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--per-category", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    packet, manifest = build_packet(
        candidate_path=args.candidate,
        expected_candidate_sha256=args.candidate_sha256,
        per_category=args.per_category,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(canonical_json(row) for row in packet) + "\n",
        encoding="utf-8",
    )
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
