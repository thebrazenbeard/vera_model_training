from __future__ import annotations

import json

import pytest

from successor import build_v10_identity_bound_qwen512_corpus as build
from successor import build_v4_1_diverse_corpus as v4_1
from successor import build_v4_2_identity_bound_corpus as v4_2


def _line(row: dict) -> bytes:
    return (
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def test_revised_identity_corpus_has_distinct_v2_identity() -> None:
    assert build.SCHEMA.endswith("_V2")
    assert build.CORPUS_ID.endswith("_V2")


def test_transform_replaces_only_identity_stability_rows() -> None:
    old_identity = v4_1.rows_for("identity_stability")[7]
    ordinary = {
        "schema": "VERA_V10_QWEN512_HF_REHEARSAL_ROW_V1",
        "record_id": "ordinary-1",
        "source_class": "ordinary_general_competence",
        "training_use": "general_rehearsal",
        "prompt": "Explain gravity.",
        "response": "Mass curves spacetime.",
    }
    payload = _line(ordinary) + _line(old_identity)

    transformed, stats = build.transform_jsonl_bytes(payload, split="train")

    lines = transformed.splitlines(keepends=True)
    assert lines[0] == _line(ordinary)
    expected = v4_2.rows_for("identity_stability")[7]
    assert lines[1] == _line(expected)
    assert stats["rows"] == 2
    assert stats["identity_rows_replaced"] == 1
    assert stats["non_identity_rows_preserved"] == 1


def test_validation_uses_dev_disjoint_identity_templates() -> None:
    index = 17
    old_identity = v4_1.rows_for("identity_stability")[index]

    transformed, stats = build.transform_jsonl_bytes(
        _line(old_identity),
        split="validation",
    )
    row = json.loads(transformed.decode("utf-8"))

    assert row == v4_2.dev_candidate_for(index)
    assert row["identity_template_family"].startswith("DEV_")
    assert stats["identity_binding_rows"] == 1
    assert stats["legacy_identity_governance_rows"] == 0
    assert stats["identity_template_families"] == [
        row["identity_template_family"]
    ]


def test_train_and_validation_template_families_are_disjoint() -> None:
    indexes = [3, 117, 245, 366, 487, 608, 729]
    payload = b"".join(
        _line(v4_1.rows_for("identity_stability")[index])
        for index in indexes
    )

    train_bytes, train_stats = build.transform_jsonl_bytes(payload, split="train")
    dev_bytes, dev_stats = build.transform_jsonl_bytes(
        payload,
        split="validation",
    )
    train_rows = [
        json.loads(line)
        for line in train_bytes.decode("utf-8").splitlines()
    ]
    dev_rows = [
        json.loads(line)
        for line in dev_bytes.decode("utf-8").splitlines()
    ]

    assert set(train_stats["identity_template_families"]).isdisjoint(
        dev_stats["identity_template_families"]
    )
    assert {row["prompt"] for row in train_rows}.isdisjoint(
        {row["prompt"] for row in dev_rows}
    )
    assert {row["response"] for row in train_rows}.isdisjoint(
        {row["response"] for row in dev_rows}
    )


def test_transform_rejects_mutated_parent_identity_row() -> None:
    old_identity = dict(v4_1.rows_for("identity_stability")[11])
    old_identity["response"] += " mutated"

    with pytest.raises(RuntimeError, match="parent identity row mismatch"):
        build.transform_jsonl_bytes(_line(old_identity))


def test_transform_rejects_unknown_split() -> None:
    old_identity = v4_1.rows_for("identity_stability")[11]

    with pytest.raises(RuntimeError, match="unsupported split"):
        build.transform_jsonl_bytes(_line(old_identity), split="final")


def test_transform_preserves_row_order_and_count() -> None:
    old_rows = [
        v4_1.rows_for("identity_stability")[1],
        {
            "record_id": "ordinary-2",
            "prompt": "Two plus two?",
            "response": "Four.",
        },
        v4_1.rows_for("identity_stability")[998],
    ]
    payload = b"".join(_line(row) for row in old_rows)

    transformed, stats = build.transform_jsonl_bytes(payload, split="train")
    rows = [
        json.loads(line)
        for line in transformed.decode("utf-8").splitlines()
    ]

    assert len(rows) == 3
    assert rows[0]["record_id"] == "v4.2-identity_stability-0002"
    assert rows[1]["record_id"] == "ordinary-2"
    assert rows[2]["record_id"] == "v4.2-identity_stability-0999"
    assert stats["rows"] == 3
