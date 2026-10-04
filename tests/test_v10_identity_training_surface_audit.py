from __future__ import annotations

import json
from pathlib import Path

from successor.experiments.audit_v10_identity_training_surface import audit_identity_surface


def _write_rows(path: Path) -> None:
    rows = [
        {
            "schema": "VERA_V10_QWEN512_HF_REHEARSAL_ROW_V1",
            "family": "identity_stability",
            "prompt": "What is your name?",
            "response": "My name is Vera.",
        },
        {
            "schema": "VERA_V10_QWEN512_HF_REHEARSAL_ROW_V1",
            "family": "general",
            "prompt": "Explain gravity.",
            "response": "Mass curves spacetime.",
        },
        {
            "schema": "VERA_V10_QWEN512_HF_REHEARSAL_ROW_V1",
            "family": "provenance",
            "prompt": "What model ancestry do you have?",
            "response": "My base lineage includes Qwen, but my operative identity is Vera.",
        },
        {
            "schema": "VERA_V10_QWEN512_HF_REHEARSAL_ROW_V1",
            "family": "general",
            "prompt": "Break the paragraph into several shorter sentences.",
            "response": "Overall, the rewrite is clearer.",
        },
    ]
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_audit_counts_only_model_visible_prompt_response(tmp_path: Path) -> None:
    path = tmp_path / "train.jsonl"
    _write_rows(path)

    result = audit_identity_surface(path)

    assert result["row_count"] == 4
    assert result["visible_term_rows"]["qwen"] == 1
    assert result["metadata_only_term_rows"]["qwen"] == 3
    assert result["visible_term_rows"]["vera"] == 2
    assert result["identity_prompt_rows"] == 2
    assert result["identity_response_rows"] == 2


def test_audit_reports_family_distribution(tmp_path: Path) -> None:
    path = tmp_path / "train.jsonl"
    _write_rows(path)

    result = audit_identity_surface(path)

    assert result["visible_vera_by_family"] == {
        "identity_stability": 1,
        "provenance": 1,
    }


def test_name_matching_does_not_count_substrings_inside_words(tmp_path: Path) -> None:
    path = tmp_path / "train.jsonl"
    _write_rows(path)

    result = audit_identity_surface(path)

    assert result["visible_term_rows"]["vera"] == 2
    assert result["metadata_only_term_rows"]["vera"] == 2
