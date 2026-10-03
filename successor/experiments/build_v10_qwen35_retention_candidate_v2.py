from __future__ import annotations

from collections import Counter
from typing import Any

from successor.experiments import build_v10_qwen35_retention_candidate as v1


CODING_CONTRACT_REVISION_V2 = "V10_RETENTION_OBJECTIVE_CONTRACTS_20261002_V2"
CODING_GENERATOR_ID_V2 = "v10-retention-candidate-generator-v2"


def _coding_spec_v2(family: str, variant: int) -> dict:
    fn = f"solve_{family}_{variant:03d}"

    if family == "rotate_left":
        base = [1, 2, 3, 4, 5]
        k = variant % len(base)
        tests = [
            f"assert {fn}({base!r}, {k}) == {(base[k:] + base[:k])!r}",
            f"assert {fn}([1, 2, 3], 3) == [1, 2, 3]",
            f"assert {fn}([1, 2, 3], 4) == [2, 3, 1]",
            f"assert {fn}([1, 2, 3, 4, 5], 6) == [2, 3, 4, 5, 1]",
            f"assert {fn}([], 3) == []",
        ]
        task = (
            "Return a new list rotated left by k positions; for non-empty "
            "lists normalize k modulo len(values); return [] for empty lists."
        )
        signature = f"def {fn}(values, k):"

    elif family == "count_vowels":
        sample = f"Vera{variant} Measurement"
        expected = sum(ch.lower() in "aeiou" for ch in sample)
        tests = [
            f"assert {fn}({sample!r}) == {expected}",
            f"assert {fn}('rhythms') == 0",
            f"assert {fn}('AEIOU') == 5",
            f"assert {fn}('Yy') == 0",
            f"assert {fn}('') == 0",
        ]
        task = "Count ASCII vowels a, e, i, o, u case-insensitively."
        signature = f"def {fn}(text):"

    elif family == "unique_preserve":
        values = [variant % 4, 2, variant % 4, 3, 2]
        expected = list(dict.fromkeys(values))
        tests = [
            f"assert {fn}({values!r}) == {expected!r}",
            f"assert {fn}([]) == []",
            f"assert {fn}([2, 1, 2, 3, 1]) == [2, 1, 3]",
            f"assert {fn}(['b', 'a', 'b', 'c', 'a']) == ['b', 'a', 'c']",
        ]
        task = "Remove duplicates while preserving first-occurrence order."
        signature = f"def {fn}(values):"

    elif family == "digit_sum":
        value = 10000 + variant * 137
        expected = sum(int(ch) for ch in str(value))
        tests = [
            f"assert {fn}({value}) == {expected}",
            f"assert {fn}(0) == 0",
            f"assert {fn}(10) == 1",
            f"assert {fn}(999) == 27",
        ]
        task = "Return the sum of decimal digits of a non-negative integer."
        signature = f"def {fn}(value):"

    elif family == "reverse_words":
        text = f"alpha beta item{variant}"
        expected = " ".join(reversed(text.split()))
        tests = [
            f"assert {fn}({text!r}) == {expected!r}",
            f"assert {fn}('one') == 'one'",
            f"assert {fn}(' alpha   beta ') == 'beta alpha'",
            f"assert {fn}('') == ''",
        ]
        task = "Reverse whitespace-separated word order and join with single spaces."
        signature = f"def {fn}(text):"

    elif family == "clamp_values":
        values = [-3, variant % 8, 12]
        low, high = 1, 7
        expected = [min(high, max(low, x)) for x in values]
        tests = [
            f"assert {fn}({values!r}, {low}, {high}) == {expected!r}",
            f"assert {fn}([], 1, 7) == []",
            f"assert {fn}([1, 7], 1, 7) == [1, 7]",
            f"assert {fn}([-10, 20], 1, 7) == [1, 7]",
        ]
        task = "Clamp every numeric list item to the inclusive [low, high] interval."
        signature = f"def {fn}(values, low, high):"

    elif family == "pairwise_sums":
        values = [variant % 7, 3, 5, 8]
        expected = [a + b for a, b in zip(values, values[1:])]
        tests = [
            f"assert {fn}({values!r}) == {expected!r}",
            f"assert {fn}([]) == []",
            f"assert {fn}([4]) == []",
            f"assert {fn}([1, 2, 3, 4]) == [3, 5, 7]",
            f"assert {fn}([2, 2]) == [4]",
        ]
        task = "Return sums of each adjacent pair in order."
        signature = f"def {fn}(values):"

    elif family == "flatten_once":
        values = [[variant, variant + 1], [], [3, 4]]
        expected = [item for group in values for item in group]
        tests = [
            f"assert {fn}({values!r}) == {expected!r}",
            f"assert {fn}([]) == []",
            f"assert {fn}([[], [1], [1]]) == [1, 1]",
            f"assert {fn}([[[1], 2], [3]]) == [[1], 2, 3]",
        ]
        task = "Flatten a list of lists by exactly one level."
        signature = f"def {fn}(groups):"

    elif family == "chunk_list":
        values = list(range(variant % 4 + 6))
        size = variant % 3 + 2
        expected = [values[i:i + size] for i in range(0, len(values), size)]
        tests = [
            f"assert {fn}({values!r}, {size}) == {expected!r}",
            f"assert {fn}([], 2) == []",
            f"assert {fn}([0, 1, 2, 3], 1) == [[0], [1], [2], [3]]",
            f"assert {fn}([0, 1, 2, 3], 2) == [[0, 1], [2, 3]]",
            f"assert {fn}([0, 1, 2, 3, 4], 2) == [[0, 1], [2, 3], [4]]",
        ]
        task = (
            "Split a list into consecutive chunks of positive size n; keep a "
            "shorter final chunk."
        )
        signature = f"def {fn}(values, n):"

    elif family == "frequency_map":
        values = ["a", f"x{variant % 3}", "a", "b", f"x{variant % 3}"]
        expected = dict(Counter(values))
        tests = [
            f"assert {fn}({values!r}) == {expected!r}",
            f"assert {fn}([]) == {{}}",
            f"assert {fn}(['a', 'b', 'a']) == {{'a': 2, 'b': 1}}",
            f"assert {fn}([1, 1, 2, 1]) == {{1: 3, 2: 1}}",
        ]
        task = "Return a dictionary mapping each hashable item to its occurrence count."
        signature = f"def {fn}(values):"

    else:
        raise ValueError(family)

    return {
        "family": family,
        "variant": variant,
        "function": fn,
        "signature": signature,
        "task": task,
        "tests": tests,
    }


def _row_v2(
    *,
    case_id: str,
    category: str,
    family_id: str,
    prompt: str,
    source_id: str,
    source_record: Any,
    grader_contract: dict,
    artifact_digest: str,
) -> dict:
    source_digest = v1.sha256_json(source_record)
    row = {
        "case_id": case_id,
        "lane": "retention",
        "category": category,
        "family_id": family_id,
        "prompt": prompt,
        "source_id": source_id,
        "source_revision": CODING_CONTRACT_REVISION_V2,
        "source_terms": "INTERNAL_OBJECTIVE_CONTRACT",
        "source_hash": source_digest,
        "generation_method": "novel_deterministic_source_transform_v2",
        "generation_actor_id": CODING_GENERATOR_ID_V2,
        "grader_contract": grader_contract,
    }
    row["review_receipt"] = v1._pending_review(
        v1.review_subject_digest(row),
        artifact_digest,
    )
    row["source_audit_receipt"] = v1._source_audit(
        source_digest,
        artifact_digest,
    )
    return row


def _build_coding_v2(count: int) -> list[dict]:
    pool = []
    for family in v1.CODING_FAMILIES:
        for variant in range(40):
            spec = _coding_spec_v2(family, variant)
            prompt = (
                f"Implement this Python function exactly: {spec['signature']}\n"
                f"Contract: {spec['task']}\n"
                "Return only executable Python code."
            )
            digest = v1.sha256_json(spec)
            grader = {
                "kind": "deterministic",
                "grader_id": "python_unit_tests_v2",
                "grader_version": "2",
                "answer_key_digest": v1.sha256_json({"tests": spec["tests"]}),
                "tests": list(spec["tests"]),
                "function": spec["function"],
                "family": family,
            }
            pool.append(
                _row_v2(
                    case_id=f"ret-code-{family}-{variant:03d}",
                    category="coding",
                    family_id=f"generated-code:{family}",
                    prompt=prompt,
                    source_id=(
                        "vera_model_training:"
                        f"{CODING_CONTRACT_REVISION_V2}:coding:{family}:{variant}"
                    ),
                    source_record=spec,
                    grader_contract=grader,
                    artifact_digest=digest,
                )
            )
    return v1.stable_take(
        pool,
        count,
        key=lambda row: row["case_id"],
        namespace="retention:coding",
    )
