from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from successor.experiments.evaluate_v10r3_recipe_semantics import (
    RecipeEvalHold,
    apply_prospective_gates,
    bind_evaluated_candidate_to_training_receipt,
)
from successor.experiments.train_v10_qwen35_authorized import sha256_file


EVAL_SCHEMA = "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_EVAL_V1"
EVAL_STATUS = "DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_COMPLETE"
PROTOCOL_SCHEMA = "V10R3_STAGED_VS_CONTINUOUS_RECIPE_SEMANTICS_PROTOCOL_V2"


def committed_text_sha(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_json(path: Path, *, label: str) -> dict:
    if not path.is_file():
        raise RecipeEvalHold(f"{label} missing:{path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RecipeEvalHold(f"{label} must be a JSON object")
    return value


def run_recipe_semantics_decision(
    *,
    evaluation_path: Path | str,
    protocol_path: Path | str,
    staged_receipt_path: Path | str,
    continuous_receipt_path: Path | str,
    staged_name: str = "staged",
    continuous_name: str = "continuous",
) -> dict:
    evaluation_path = Path(evaluation_path)
    protocol_path = Path(protocol_path)
    staged_receipt_path = Path(staged_receipt_path)
    continuous_receipt_path = Path(continuous_receipt_path)

    evaluation = _read_json(evaluation_path, label="evaluation")
    if evaluation.get("schema") != EVAL_SCHEMA:
        raise RecipeEvalHold("evaluation schema mismatch")
    if evaluation.get("status") != EVAL_STATUS:
        raise RecipeEvalHold("evaluation status mismatch")

    protocol = _read_json(protocol_path, label="protocol")
    if protocol.get("schema") != PROTOCOL_SCHEMA:
        raise RecipeEvalHold("protocol schema mismatch")

    staged_custody = bind_evaluated_candidate_to_training_receipt(
        evaluation,
        candidate_name=staged_name,
        receipt_path=staged_receipt_path,
        expected_cumulative_optimizer_steps=20,
    )
    continuous_custody = bind_evaluated_candidate_to_training_receipt(
        evaluation,
        candidate_name=continuous_name,
        receipt_path=continuous_receipt_path,
        expected_cumulative_optimizer_steps=20,
    )
    gate_decision = apply_prospective_gates(
        evaluation,
        protocol,
        staged_name=staged_name,
        continuous_name=continuous_name,
    )

    return {
        "schema": "V10R3_RECIPE_SEMANTICS_DECISION_V1",
        "status": gate_decision["status"],
        "decision": gate_decision["decision"],
        "evaluation": {
            "path": str(evaluation_path),
            "sha256": sha256_file(evaluation_path),
        },
        "protocol": {
            "path": str(protocol_path),
            "sha256": committed_text_sha(protocol_path),
            "hash_semantics": "UTF8_TEXT_LF_NORMALIZED_CONTENT",
        },
        "custody": {
            "staged": staged_custody,
            "continuous": continuous_custody,
        },
        "gates": gate_decision["gates"],
        "family_comparison": gate_decision["family_comparison"],
        "claim_ceiling": (
            "DEVELOPMENT_RECIPE_SEMANTICS_DECISION_ONLY_"
            "NOT_FINAL_BANK_NOT_FULL_RUN_AUTHORITY"
        ),
    }


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--staged-receipt", type=Path, required=True)
    parser.add_argument("--continuous-receipt", type=Path, required=True)
    parser.add_argument("--staged-name", default="staged")
    parser.add_argument("--continuous-name", default="continuous")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        result = run_recipe_semantics_decision(
            evaluation_path=args.evaluation,
            protocol_path=args.protocol,
            staged_receipt_path=args.staged_receipt,
            continuous_receipt_path=args.continuous_receipt,
            staged_name=args.staged_name,
            continuous_name=args.continuous_name,
        )
        if args.output.exists():
            raise RecipeEvalHold(f"decision output already exists:{args.output}")
    except (RecipeEvalHold, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "schema": "V10R3_RECIPE_SEMANTICS_DECISION_V1",
                    "status": "HOLD",
                    "reason": str(exc),
                },
                sort_keys=True,
            )
        )
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
