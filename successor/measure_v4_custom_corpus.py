from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path

from successor.build_v4_custom_corpus import CORE_FAMILIES

SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+")
EXPECTED_ROWS = 10_000
ROWS_PER_FAMILY = 1_000


def sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_RE.findall(text)]


def summarize(values: list[int]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 3),
        "median": statistics.median(values),
        "p90": ordered[min(len(ordered) - 1, int(round((len(ordered) - 1) * 0.90)))],
        "max": max(values),
    }


def measure_family(path: Path, family: str) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != ROWS_PER_FAMILY:
        raise AssertionError(f"{family}: expected {ROWS_PER_FAMILY} rows, got {len(rows)}")

    ids = [row["record_id"] for row in rows]
    prompts = [row["prompt"] for row in rows]
    responses = [row["response"] for row in rows]
    pairs = [(row["prompt"], row["response"]) for row in rows]

    sentence_positions: list[Counter[str]] = [Counter() for _ in range(5)]
    sentence_counts: list[int] = []
    for response in responses:
        parts = sentences(response)
        sentence_counts.append(len(parts))
        for index, part in enumerate(parts[:5]):
            sentence_positions[index][part] += 1

    position_diversity = [
        {
            "position": index + 1,
            "unique_sentences": len(counter),
            "diversity_ratio": round(len(counter) / len(rows), 4),
            "max_reuse": max(counter.values()) if counter else 0,
            "max_reuse_ratio": round((max(counter.values()) / len(rows)), 4) if counter else 0,
        }
        for index, counter in enumerate(sentence_positions)
    ]

    return {
        "rows": len(rows),
        "unique_record_ids": len(set(ids)),
        "unique_prompts": len(set(prompts)),
        "unique_responses": len(set(responses)),
        "unique_pairs": len(set(pairs)),
        "difficulty_counts": dict(sorted(Counter(row["difficulty"] for row in rows).items())),
        "source_class_counts": dict(sorted(Counter(row["source_class"] for row in rows).items())),
        "prompt_chars": summarize([len(value) for value in prompts]),
        "response_chars": summarize([len(value) for value in responses]),
        "response_sentence_count": summarize(sentence_counts),
        "sentence_position_diversity": position_diversity,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        default=Path(__file__).parent / "corpus" / "v4" / "custom",
    )
    args = ap.parse_args()

    families = {}
    all_ids: list[str] = []
    all_pairs: list[tuple[str, str]] = []
    all_responses: list[str] = []
    all_rows = 0

    for family in CORE_FAMILIES:
        path = args.corpus_dir / f"{family}.jsonl"
        if not path.is_file():
            raise FileNotFoundError(path)
        result = measure_family(path, family)
        families[family] = result

        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        all_rows += len(rows)
        all_ids.extend(row["record_id"] for row in rows)
        all_pairs.extend((row["prompt"], row["response"]) for row in rows)
        all_responses.extend(row["response"] for row in rows)

    if all_rows != EXPECTED_ROWS:
        raise AssertionError(f"expected {EXPECTED_ROWS} core rows, got {all_rows}")

    exact_response_uniqueness = len(set(all_responses)) / all_rows
    review_flags = []
    for family, result in families.items():
        for position in result["sentence_position_diversity"]:
            if position["max_reuse_ratio"] > 0.10:
                review_flags.append(
                    {
                        "family": family,
                        "position": position["position"],
                        "max_reuse_ratio": position["max_reuse_ratio"],
                        "reason": "single sentence component reused in more than 10% of family responses",
                    }
                )

    output = {
        "schema": "VERA_V4_CUSTOM_CORPUS_MEASUREMENT_V1",
        "core_rows": all_rows,
        "family_count": len(CORE_FAMILIES),
        "rows_per_family": ROWS_PER_FAMILY,
        "unique_record_ids": len(set(all_ids)),
        "unique_prompt_response_pairs": len(set(all_pairs)),
        "unique_responses": len(set(all_responses)),
        "exact_response_uniqueness_ratio": round(exact_response_uniqueness, 4),
        "families": families,
        "review_flags": review_flags,
        "interpretation": {
            "exact_uniqueness_is_not_semantic_diversity": True,
            "review_flags_are_measurement_signals_not_failure_verdicts": True,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
