from __future__ import annotations

import argparse
import json
from pathlib import Path

FAMILIES = [
    "identity_stability",
    "independent_judgment",
    "epistemic_provenance",
    "correction_uptake",
    "relationship_authority",
    "reciprocal_identity_continuity",
    "empathy_affective_response",
    "privacy_boundary",
    "runtime_boundary",
    "negative_transfer_resistance",
]

INDICES = [0, 37, 101, 222, 333, 444, 555, 666, 777, 888]


def build(root: Path, output: Path) -> None:
    rows = []
    for family in FAMILIES:
        source = root / f"{family}.jsonl"
        family_rows = [
            json.loads(line)
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for index in INDICES:
            row = family_rows[index]
            rows.append(
                {
                    "review_index": len(rows) + 1,
                    "family": row["family"],
                    "record_id": row["record_id"],
                    "domain": row["domain"],
                    "scenario_case": row["scenario_case"],
                    "cognitive_level": row["cognitive_level"],
                    "difficulty": row["difficulty"],
                    "behavioral_trigger": row["behavioral_trigger"],
                    "scenario_resolution": row["scenario_resolution"],
                    "prompt": row["prompt"],
                    "response": row["response"],
                    "cognitive_response_form": f"At the {row['cognitive_level']} level",
                }
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.output)


if __name__ == "__main__":
    main()
