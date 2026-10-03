from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _rid(row: dict) -> str:
    return row.get("record_id") or row.get("case_id") or row.get("id")


def _rank(rows: list[dict], salt: str) -> list[dict]:
    return sorted(
        rows,
        key=lambda row: hashlib.sha256(
            (salt + "\0" + _rid(row)).encode("utf-8")
        ).hexdigest(),
    )


def test_checkpoint_panel_recomputes_from_frozen_validation() -> None:
    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (repo / "successor/experiments/V10R2_HELDOUT_CHECKPOINT_PANEL_V1.json").read_text(encoding="utf-8")
    )
    validation = Path(r"D:\\VERA\\.scratch\\v10-qwen512-preflight-20261001-v1\\validation.jsonl")
    assert hashlib.sha256(validation.read_bytes()).hexdigest() == manifest["validation_sha256"]
    rows = [json.loads(line) for line in validation.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2500

    anchors = _rank(rows, manifest["anchor_panel"]["salt"])[:16]
    confirm = _rank(rows, manifest["confirmatory_panel"]["salt"])[:48]
    anchor_ids = [_rid(row) for row in anchors]
    confirm_ids = [_rid(row) for row in confirm]
    assert anchor_ids == manifest["anchor_panel"]["record_ids"]
    assert confirm_ids == manifest["confirmatory_panel"]["record_ids"]
    assert set(anchor_ids).isdisjoint(confirm_ids)
    assert anchor_ids + confirm_ids == manifest["combined_panel"]["record_ids"]
    combined_sha = hashlib.sha256(
        json.dumps(anchor_ids + confirm_ids, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    assert combined_sha == manifest["combined_panel"]["record_ids_sha256"]
