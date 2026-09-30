from __future__ import annotations

import json
from pathlib import Path

from successor import build_v4_custom_corpus as custom
from successor.measure_v4_custom_corpus import measure_family

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "successor" / "corpus" / "v4" / "custom"


def test_v4_core_family_contract() -> None:
    assert len(custom.CORE_FAMILIES) == 10
    assert custom.EXPECTED_ROWS == 10_000
    assert len(custom.AUXILIARY_FAMILIES) == 2
    assert not set(custom.CORE_FAMILIES) & set(custom.AUXILIARY_FAMILIES)


def test_committed_core_shards_match_generator() -> None:
    total = 0
    for family in custom.CORE_FAMILIES:
        rows = custom.rows_for(family)
        assert len(rows) == 1_000
        rendered = custom.render(rows).encode("utf-8")
        committed = (CORPUS_DIR / f"{family}.jsonl").read_bytes()
        assert rendered == committed, family
        total += len(rows)
    assert total == 10_000


def test_custom_measurement_matches_committed_core() -> None:
    total = 0
    unique_responses: set[str] = set()
    unique_pairs: set[tuple[str, str]] = set()
    for family in custom.CORE_FAMILIES:
        result = measure_family(CORPUS_DIR / f"{family}.jsonl", family)
        assert result["rows"] == 1_000
        assert result["unique_record_ids"] == 1_000
        assert result["unique_prompts"] == 1_000
        assert result["unique_responses"] == 1_000
        assert result["unique_pairs"] == 1_000
        rows = [
            json.loads(line)
            for line in (CORPUS_DIR / f"{family}.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        total += len(rows)
        unique_responses.update(row["response"] for row in rows)
        unique_pairs.update((row["prompt"], row["response"]) for row in rows)
    assert total == 10_000
    assert len(unique_responses) == 10_000
    assert len(unique_pairs) == 10_000
