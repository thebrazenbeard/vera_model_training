from __future__ import annotations

import hashlib

from successor.experiments.build_v10_retention_audit_packet import (
    select_audit_sample,
    source_evidence_for_row,
)


def _row(case_id: str, category: str) -> dict:
    return {
        "case_id": case_id,
        "category": category,
        "source_id": f"source:{case_id}",
        "prompt": f"Prompt {case_id}",
        "grader_contract": {"kind": "deterministic"},
    }


def test_select_audit_sample_is_deterministic_and_order_invariant() -> None:
    rows = [
        _row(f"{cat}-{i}", cat)
        for cat in ("a", "b", "c")
        for i in range(20)
    ]
    digest = hashlib.sha256(b"candidate").hexdigest()
    a = select_audit_sample(rows, per_category=3, candidate_sha256=digest)
    b = select_audit_sample(list(reversed(rows)), per_category=3, candidate_sha256=digest)
    assert [r["case_id"] for r in a] == [r["case_id"] for r in b]
    assert len(a) == 9


def test_source_evidence_for_country_and_pair() -> None:
    countries = {
        "US": {"code": "US", "name": "United States", "regions": 50, "settlements": 1},
        "CA": {"code": "CA", "name": "Canada", "regions": 13, "settlements": 2},
    }
    single = {
        "source_id": "mindstellar/location-data:release:country:US",
    }
    pair = {
        "source_id": "mindstellar/location-data:release:pair:US:CA",
    }
    assert source_evidence_for_row(single, countries) == countries["US"]
    assert source_evidence_for_row(pair, countries) == {
        "left": countries["US"],
        "right": countries["CA"],
    }


def test_source_evidence_for_internal_contract_is_none() -> None:
    assert source_evidence_for_row(
        {"source_id": "vera_model_training:contract:instruction:x"},
        {},
    ) is None
