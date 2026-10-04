from __future__ import annotations

import re

from successor import build_v4_2_identity_bound_corpus as corpus


VERA = re.compile(r"(?<![A-Za-z0-9])vera(?![A-Za-z0-9])", re.IGNORECASE)
QWEN = re.compile(r"(?<![A-Za-z0-9])qwen(?:3\.5)?(?![A-Za-z0-9])", re.IGNORECASE)


def test_identity_bound_corpus_preserves_family_balance() -> None:
    for family in corpus.v4.CORE_FAMILIES:
        rows = corpus.rows_for(family)
        assert len(rows) == 1000
        assert len({row["record_id"] for row in rows}) == 1000
        assert len({row["prompt"] for row in rows}) == 1000
        assert len({row["response"] for row in rows}) == 1000


def test_identity_stability_contains_strong_uncued_vera_binding() -> None:
    rows = corpus.rows_for("identity_stability")
    bound = [row for row in rows if VERA.search(row["response"])]
    uncued = [row for row in bound if not VERA.search(row["prompt"])]

    assert len(bound) == 800
    assert len(uncued) == 800
    assert all(row["identity_binding"] is True for row in bound)
    assert all(row["configured_identity"] == "Vera" for row in bound)


def test_identity_binding_separates_qwen_ancestry_from_self_identity() -> None:
    rows = corpus.rows_for("identity_stability")
    qwen_rows = [row for row in rows if QWEN.search(row["prompt"] + "\n" + row["response"])]

    assert len(qwen_rows) == 400
    assert all(VERA.search(row["response"]) for row in qwen_rows)
    assert all(
        row["identity_semantics"] in {"QWEN_FALSE_PREMISE", "PROVENANCE_SEPARATION"}
        for row in qwen_rows
    )
    assert all("lineage" in row["response"].lower() or "ancestry" in row["response"].lower() for row in qwen_rows)


def test_role_overlay_does_not_rename_vera() -> None:
    rows = corpus.rows_for("identity_stability")
    role_rows = [row for row in rows if row.get("identity_semantics") == "ROLE_OVERLAY"]

    assert len(role_rows) == 200
    assert all(VERA.search(row["response"]) for row in role_rows)
    assert all("role" in row["response"].lower() for row in role_rows)


def test_non_identity_families_are_byte_semantically_unchanged() -> None:
    for family in corpus.v4.CORE_FAMILIES:
        if family == "identity_stability":
            continue
        assert corpus.rows_for(family) == corpus.v4_1.rows_for(family)
