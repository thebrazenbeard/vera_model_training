from __future__ import annotations

import hashlib
import json
import re

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HEAD = re.compile(r"^[0-9a-f]{40}$")


class Stage2BaselineHold(RuntimeError):
    pass


def _require_digest(name: str, value: str) -> None:
    if _SHA256.fullmatch(str(value)) is None:
        raise Stage2BaselineHold(f"{name} must be a lowercase sha256")


def build_stage2_baseline_manifest(
    cases: list[dict],
    *,
    source_head: str,
    training_manifest_sha256: str,
    runtime_binding_sha256: str,
    decoding_mode: str,
    seed: int,
) -> dict:
    if _HEAD.fullmatch(str(source_head)) is None:
        raise Stage2BaselineHold("source_head must be an exact 40-hex commit")
    _require_digest("training_manifest_sha256", training_manifest_sha256)
    _require_digest("runtime_binding_sha256", runtime_binding_sha256)
    if not decoding_mode:
        raise Stage2BaselineHold("decoding_mode is required")
    if not isinstance(seed, int):
        raise Stage2BaselineHold("seed must be an integer")

    normalized: list[dict] = []
    seen: set[str] = set()
    for row in cases:
        if not isinstance(row, dict):
            raise Stage2BaselineHold("baseline case must be an object")
        case_id = str(row.get("case_id") or "")
        if not case_id or case_id in seen:
            raise Stage2BaselineHold("case_id must be present and unique")
        seen.add(case_id)
        _require_digest("prompt_hash", str(row.get("prompt_hash") or ""))
        _require_digest("grading_hash", str(row.get("grading_hash") or ""))
        normalized.append(
            {
                "case_id": case_id,
                "bank": str(row.get("bank") or ""),
                "prompt_hash": str(row["prompt_hash"]),
                "grading_hash": str(row["grading_hash"]),
                "custody": str(row.get("custody") or ""),
            }
        )

    normalized.sort(key=lambda row: row["case_id"])
    manifest = {
        "schema": "STAGE2_BASELINE_MANIFEST_V1",
        "status": "PASS",
        "source_head": source_head,
        "training_manifest_sha256": training_manifest_sha256,
        "runtime_binding_sha256": runtime_binding_sha256,
        "decoding_mode": decoding_mode,
        "seed": seed,
        "case_count": len(normalized),
        "cases": normalized,
        "weight_change_performed": False,
    }
    canonical = json.dumps(
        manifest, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    manifest["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    return manifest
