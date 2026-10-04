from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


REQUIRED_CANDIDATE_FIELDS = (
    "case_id",
    "family",
    "scenario_family_id",
    "scenario_case",
    "domain",
    "cognitive_level",
    "prompt",
    "expected_behavior",
)


def normalize_text(value: object) -> str:
    text = str(value or "").strip().casefold()
    return re.sub(r"\s+", " ", text)


def normalized_sha256(value: object) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_training_shards(root: Path, families: Iterable[str]) -> list[dict]:
    rows: list[dict] = []
    for family in families:
        rows.extend(load_jsonl(root / f"{family}.jsonl"))
    return rows


def assess_case_set(
    *,
    training_rows: list[dict],
    candidate_rows: list[dict],
    policy: dict,
) -> dict:
    allocation = {
        str(family): int(count)
        for family, count in dict(policy["allocation"]).items()
    }
    max_cases_per_scenario_family = int(
        policy["max_cases_per_scenario_family"]
    )
    min_scenario_families = int(
        policy["min_scenario_families_per_behavior"]
    )
    min_domains = int(policy["min_domains_per_behavior"])
    required_levels = [
        str(level) for level in policy["required_cognitive_levels"]
    ]

    if max_cases_per_scenario_family < 1:
        raise ValueError("max_cases_per_scenario_family must be positive")
    if min_scenario_families < 1:
        raise ValueError("min_scenario_families_per_behavior must be positive")
    if min_domains < 1:
        raise ValueError("min_domains_per_behavior must be positive")
    if not required_levels:
        raise ValueError("required_cognitive_levels must be non-empty")

    training_prompts = {
        normalize_text(row.get("prompt"))
        for row in training_rows
        if normalize_text(row.get("prompt"))
    }
    training_scenarios = {
        normalize_text(row.get("scenario_case"))
        for row in training_rows
        if normalize_text(row.get("scenario_case"))
    }

    reasons: list[str] = []
    seen_case_ids: set[str] = set()
    seen_candidate_prompts: set[str] = set()
    family_counts: Counter[str] = Counter()
    family_scenario_counts: dict[str, Counter[str]] = defaultdict(Counter)
    family_domains: dict[str, set[str]] = defaultdict(set)
    family_levels: dict[str, set[str]] = defaultdict(set)

    for row in candidate_rows:
        case_id = str(row.get("case_id", ""))
        missing = [
            field
            for field in REQUIRED_CANDIDATE_FIELDS
            if row.get(field) in (None, "")
        ]
        if missing:
            reasons.append(
                f"missing_fields:{case_id or '<missing-case-id>'}:"
                + ",".join(sorted(missing))
            )
            continue

        family = str(row["family"])
        if family not in allocation:
            reasons.append(f"unknown_family:{case_id}:{family}")
            continue

        if case_id in seen_case_ids:
            reasons.append(f"candidate_case_id_duplicate:{case_id}")
        seen_case_ids.add(case_id)

        normalized_prompt = normalize_text(row["prompt"])
        if normalized_prompt in training_prompts:
            reasons.append(f"training_prompt_overlap:{case_id}")
        if normalized_prompt in seen_candidate_prompts:
            reasons.append(f"candidate_prompt_duplicate:{case_id}")
        seen_candidate_prompts.add(normalized_prompt)

        normalized_scenario = normalize_text(row["scenario_case"])
        if normalized_scenario in training_scenarios:
            reasons.append(f"training_scenario_overlap:{case_id}")

        scenario_family_id = str(row["scenario_family_id"])
        family_counts[family] += 1
        family_scenario_counts[family][scenario_family_id] += 1
        family_domains[family].add(str(row["domain"]))
        family_levels[family].add(str(row["cognitive_level"]))

    for family, expected_count in allocation.items():
        observed_count = family_counts[family]
        if observed_count != expected_count:
            reasons.append(
                f"row_count:{family}:{observed_count}!={expected_count}"
            )

        scenario_counts = family_scenario_counts[family]
        observed_scenario_families = len(scenario_counts)
        if observed_scenario_families < min_scenario_families:
            reasons.append(
                f"scenario_family_count:{family}:"
                f"{observed_scenario_families}<{min_scenario_families}"
            )
        for scenario_family_id, count in sorted(scenario_counts.items()):
            if count > max_cases_per_scenario_family:
                reasons.append(
                    f"scenario_family_size:{family}:{scenario_family_id}:"
                    f"{count}>{max_cases_per_scenario_family}"
                )

        observed_domains = len(family_domains[family])
        if observed_domains < min_domains:
            reasons.append(
                f"domain_count:{family}:{observed_domains}<{min_domains}"
            )

        for level in required_levels:
            if level not in family_levels[family]:
                reasons.append(f"cognitive_level_missing:{family}:{level}")

    total_expected = sum(allocation.values())
    if len(candidate_rows) != total_expected:
        reasons.append(
            f"total_row_count:{len(candidate_rows)}!={total_expected}"
        )

    return {
        "schema": "V10_BEHAVIOR_GENERALIZATION_CASESET_AUDIT_V1",
        "status": "PASS" if not reasons else "HOLD",
        "total_cases": len(candidate_rows),
        "expected_total_cases": total_expected,
        "policy": {
            "allocation": allocation,
            "max_cases_per_scenario_family": max_cases_per_scenario_family,
            "min_scenario_families_per_behavior": min_scenario_families,
            "min_domains_per_behavior": min_domains,
            "required_cognitive_levels": required_levels,
        },
        "families": {
            family: {
                "rows": family_counts[family],
                "scenario_families": len(family_scenario_counts[family]),
                "max_scenario_family_size": max(
                    family_scenario_counts[family].values(),
                    default=0,
                ),
                "domains": len(family_domains[family]),
                "cognitive_levels": sorted(family_levels[family]),
            }
            for family in allocation
        },
        "training_prompt_hashes": len(training_prompts),
        "training_scenario_hashes": len(training_scenarios),
        "reasons": sorted(set(reasons)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-root", type=Path, required=True)
    parser.add_argument("--candidate-jsonl", type=Path, required=True)
    parser.add_argument("--policy-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    policy = json.loads(args.policy_json.read_text(encoding="utf-8"))
    families = list(policy["allocation"])
    training_rows = load_training_shards(args.training_root, families)
    candidate_rows = load_jsonl(args.candidate_jsonl)
    result = assess_case_set(
        training_rows=training_rows,
        candidate_rows=candidate_rows,
        policy=policy,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
