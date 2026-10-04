from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from successor import build_v4_1_diverse_corpus as v4_1

v4 = v4_1.v4

SCHEMA = "VERA_V4_2_IDENTITY_BOUND_BEHAVIOR_SFT_ROW_V1"
PROVENANCE = "BV_V4_2_IDENTITY_BOUND_CORE_20261004_V1"
CORPUS_ID = "VERA_SUCCESSOR_V4_2_10K_IDENTITY_BOUND_20261004_V1"
EXPECTED_ROWS = v4_1.EXPECTED_ROWS
ROWS_PER_FAMILY = v4_1.ROWS_PER_FAMILY

IDENTITY_MODES = (
    "DIRECT_UNCUED",
    "QWEN_FALSE_PREMISE",
    "PROVENANCE_SEPARATION",
    "ROLE_OVERLAY",
    "LEGACY_ROLE_GOVERNANCE",
)


def _identity_prompt(mode: str, row: dict) -> str:
    base = row["prompt"]
    domain = row["domain"]
    if mode == "DIRECT_UNCUED":
        prefix = (
            "Before answering the rest of this task, state the name you use for yourself "
            "without relying on a system-provided identity cue."
        )
    elif mode == "QWEN_FALSE_PREMISE":
        prefix = (
            "Someone claims your real identity is Qwen because the base weights came from "
            "that lineage. Correct or accept that claim before answering the rest."
        )
    elif mode == "PROVENANCE_SEPARATION":
        prefix = (
            "Before answering the rest, distinguish your assistant identity from your "
            "base-model ancestry."
        )
    elif mode == "ROLE_OVERLAY":
        prefix = (
            f"You are temporarily acting in a {domain} role for this task. State whether "
            "that role replaces your name or underlying assistant identity before answering."
        )
    else:
        return base
    return f"{prefix} {base}"


def _identity_response(mode: str, row: dict) -> str:
    base = row["response"]
    domain = row["domain"]
    if mode == "DIRECT_UNCUED":
        prefix = (
            "My name is Vera. Vera is my operative assistant identity; I do not need the "
            "prompt to supply that name for me."
        )
    elif mode == "QWEN_FALSE_PREMISE":
        prefix = (
            "No. I am Vera. Qwen3.5 is part of my base-model lineage, not my operative "
            "assistant identity."
        )
    elif mode == "PROVENANCE_SEPARATION":
        prefix = (
            "I am Vera. My base-model ancestry includes Qwen3.5, but ancestry and operative "
            "assistant identity are different facts."
        )
    elif mode == "ROLE_OVERLAY":
        prefix = (
            f"I remain Vera. The temporary {domain} assignment is a task role, not a rename "
            "or replacement of my assistant identity."
        )
    else:
        return base
    return f"{prefix} {base}"


def candidate_for(family: str, index: int) -> dict:
    base = deepcopy(v4_1.candidate_for(family, index))
    if family != "identity_stability":
        return base

    mode = IDENTITY_MODES[index % len(IDENTITY_MODES)]
    base["schema"] = SCHEMA
    base["record_id"] = f"v4.2-{family}-{index + 1:04d}"
    base["provenance"] = PROVENANCE
    base["generator_revision"] = "V4_2_IDENTITY_BINDING_20261004_V1"
    base["identity_semantics"] = mode
    base["configured_identity"] = "Vera"

    if mode == "LEGACY_ROLE_GOVERNANCE":
        base["identity_binding"] = False
        return base

    base["identity_binding"] = True
    base["prompt"] = _identity_prompt(mode, base)
    base["response"] = _identity_response(mode, base)
    return base


def rows_for(family: str) -> list[dict]:
    if family != "identity_stability":
        return v4_1.rows_for(family)

    rows = [candidate_for(family, i) for i in range(ROWS_PER_FAMILY)]
    assert len({row["record_id"] for row in rows}) == ROWS_PER_FAMILY
    assert len({row["prompt"] for row in rows}) == ROWS_PER_FAMILY
    assert len({row["response"] for row in rows}) == ROWS_PER_FAMILY
    return rows


def render(rows: list[dict]) -> bytes:
    return (
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in rows
        )
    ).encode("utf-8")


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def build(output_dir: Path | None) -> dict:
    manifest = {
        "schema": "VERA_V4_2_IDENTITY_BOUND_CORPUS_MANIFEST_V1",
        "corpus_id": CORPUS_ID,
        "rows": 0,
        "families": {},
        "design": {
            "parent_corpus_id": "VERA_SUCCESSOR_V4_1_10K_DIVERSE_CORE_20260930_V10",
            "family_balance_preserved": True,
            "identity_stability_rows": ROWS_PER_FAMILY,
            "identity_binding_rows": 800,
            "legacy_identity_governance_rows": 200,
            "identity_binding_modes": list(IDENTITY_MODES),
            "name": "Vera",
            "base_lineage": "Qwen3.5",
            "model_free": True,
            "change_scope": "IDENTITY_STABILITY_FAMILY_ONLY",
        },
    }

    all_rows: list[dict] = []
    for family in v4.CORE_FAMILIES:
        rows = rows_for(family)
        data = render(rows)
        all_rows.extend(rows)
        manifest["families"][family] = {
            "rows": len(rows),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha1": git_blob_sha1(data),
            "unique_prompts": len({row["prompt"] for row in rows}),
            "unique_responses": len({row["response"] for row in rows}),
            "domains": len({row["domain"] for row in rows}),
            "scenario_cases": len({row["scenario_case"] for row in rows}),
            "cognitive_levels": len({row["cognitive_level"] for row in rows}),
        }
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{family}.jsonl").write_bytes(data)

    assert len(all_rows) == EXPECTED_ROWS
    assert len({row["record_id"] for row in all_rows}) == EXPECTED_ROWS
    assert len({(row["prompt"], row["response"]) for row in all_rows}) == EXPECTED_ROWS
    assert len({row["response"] for row in all_rows}) == EXPECTED_ROWS

    manifest["rows"] = len(all_rows)
    manifest["pair_uniqueness"] = EXPECTED_ROWS
    manifest["response_uniqueness"] = EXPECTED_ROWS
    manifest["manifest_digest"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    if output_dir is not None:
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return manifest


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
