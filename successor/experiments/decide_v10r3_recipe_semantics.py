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
from successor.experiments.train_v10_qwen35_authorized import (
    canonical_bytes,
    sha256_file,
)


EVAL_SCHEMA = "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_EVAL_V1"
EVAL_STATUS = "DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_COMPLETE"
PROTOCOL_SCHEMA = "V10R3_STAGED_VS_CONTINUOUS_RECIPE_SEMANTICS_PROTOCOL_V2"
FROZEN_PROTOCOL_SHA256 = "c206099a98cec088396d1090eb5733c1586c6ca357b6156a945c921093198c2f"


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




def _verified_training_receipt(path: Path | str) -> tuple[dict, str]:
    path = Path(path)
    receipt = _read_json(path, label="training receipt")
    if receipt.get("schema") != "V10R2_QWEN35_DEV_TRAINING_RECEIPT_V1":
        raise RecipeEvalHold("training receipt schema mismatch")
    if receipt.get("status") != "DEVELOPMENT_OPTIMIZER_STEP_COMPLETE":
        raise RecipeEvalHold("training receipt status mismatch")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    actual = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    if claimed != actual:
        raise RecipeEvalHold("training receipt self-hash mismatch")
    return receipt, actual


def _validate_common_recipe_receipt(
    receipt: dict,
    *,
    expected_train_sha: str,
    expected_runtime_sha: str,
    label: str,
) -> None:
    if receipt.get("train_sha256") != expected_train_sha:
        raise RecipeEvalHold(f"{label} train binding mismatch")
    if receipt.get("runtime_binding_sha256") != expected_runtime_sha:
        raise RecipeEvalHold(f"{label} runtime binding mismatch")
    order = receipt.get("training_order")
    if not isinstance(order, dict):
        raise RecipeEvalHold(f"{label} training order missing")
    if order.get("shuffle_dataset") is not False:
        raise RecipeEvalHold(f"{label} shuffle must be disabled")
    if order.get("train_sampling_strategy") != "sequential":
        raise RecipeEvalHold(f"{label} sampler must be sequential")
    optimizer = receipt.get("optimizer")
    if not isinstance(optimizer, dict):
        raise RecipeEvalHold(f"{label} optimizer receipt missing")
    if optimizer.get("backend") != "bitsandbytes":
        raise RecipeEvalHold(f"{label} optimizer backend mismatch")
    if optimizer.get("module") != "bitsandbytes.optim.adamw":
        raise RecipeEvalHold(f"{label} optimizer module mismatch")
    if optimizer.get("optim_bits") != 8 or optimizer.get("is_paged") is not False:
        raise RecipeEvalHold(f"{label} optimizer must be nonpaged 8-bit")
    if receipt.get("weight_digest_changed") is not True:
        raise RecipeEvalHold(f"{label} receipt does not prove weight change")


def _validate_window(
    receipt: dict,
    *,
    start_row: int,
    row_count: int,
    label: str,
) -> None:
    window = receipt.get("development_window")
    if not isinstance(window, dict):
        raise RecipeEvalHold(f"{label} development window missing")
    if window.get("start_row") != start_row or window.get("row_count") != row_count:
        raise RecipeEvalHold(f"{label} development window mismatch")
    expected_ids = [f"bound-train-row-{i}" for i in range(start_row, start_row + row_count)]
    if window.get("row_ids") != expected_ids:
        raise RecipeEvalHold(f"{label} development row ids mismatch")


def _load_bound_source_receipt(
    receipt: dict,
    *,
    expected_source_cumulative: int,
    expected_previous_steps: int,
    expected_next_row: int,
    label: str,
) -> tuple[dict, Path, str]:
    resume = receipt.get("resume_adapter")
    if not isinstance(resume, dict):
        raise RecipeEvalHold(f"{label} resume binding missing")
    if resume.get("source_cumulative_optimizer_steps") != expected_source_cumulative:
        raise RecipeEvalHold(f"{label} source cumulative-step mismatch")
    if resume.get("previous_optimizer_steps") != expected_previous_steps:
        raise RecipeEvalHold(f"{label} previous-step mismatch")
    if resume.get("next_train_row") != expected_next_row:
        raise RecipeEvalHold(f"{label} next-row mismatch")
    source_path_value = resume.get("source_receipt_path")
    if not isinstance(source_path_value, str) or not source_path_value:
        raise RecipeEvalHold(f"{label} source receipt path missing")
    source_path = Path(source_path_value)
    source, actual_sha = _verified_training_receipt(source_path)
    if actual_sha != resume.get("source_receipt_sha256"):
        raise RecipeEvalHold(f"{label} source receipt hash mismatch")
    if source.get("weight_digest_after") != resume.get("source_weight_digest_after"):
        raise RecipeEvalHold(f"{label} source weight digest mismatch")
    return source, source_path, actual_sha


def validate_recipe_receipt_semantics(
    receipt_path: Path | str,
    *,
    role: str,
    expected_train_sha: str,
    expected_runtime_sha: str,
    expected_initial_digest: str,
) -> dict:
    receipt_path = Path(receipt_path)
    receipt, receipt_sha = _verified_training_receipt(receipt_path)
    _validate_common_recipe_receipt(
        receipt,
        expected_train_sha=expected_train_sha,
        expected_runtime_sha=expected_runtime_sha,
        label=role,
    )

    if role == "continuous":
        if receipt.get("experiment_class") != "CONTINUOUS_STATE_RECIPE_SEMANTICS":
            raise RecipeEvalHold("continuous receipt experiment class mismatch")
        if receipt.get("cumulative_optimizer_steps") != 20:
            raise RecipeEvalHold("continuous receipt cumulative-step mismatch")
        _validate_window(receipt, start_row=0, row_count=160, label="continuous")
        if receipt.get("resume_adapter") is not None:
            raise RecipeEvalHold("continuous receipt must not resume an adapter")
        if receipt.get("initial_trainable_parameter_digest") != expected_initial_digest:
            raise RecipeEvalHold("continuous initialization digest mismatch")
        if receipt.get("weight_digest_before") != expected_initial_digest:
            raise RecipeEvalHold("continuous weight-before digest mismatch")
        gate = receipt.get("initialization_equivalence_gate")
        if (
            not isinstance(gate, dict)
            or gate.get("expected_digest") != expected_initial_digest
            or gate.get("pass") is not True
        ):
            raise RecipeEvalHold("continuous initialization gate mismatch")
        return {
            "status": "PASS",
            "role": role,
            "receipt_path": str(receipt_path),
            "receipt_sha256": receipt_sha,
            "chain": ["continuous20"],
        }

    if role != "staged":
        raise RecipeEvalHold(f"unsupported recipe role:{role}")

    if receipt.get("experiment_class") != "STAGED_RESET_RECIPE_SEMANTICS_CONTROL":
        raise RecipeEvalHold("staged receipt experiment class mismatch")
    if receipt.get("cumulative_optimizer_steps") != 20:
        raise RecipeEvalHold("staged receipt cumulative-step mismatch")
    _validate_window(receipt, start_row=96, row_count=64, label="staged stage3")

    stage2, stage2_path, stage2_sha = _load_bound_source_receipt(
        receipt,
        expected_source_cumulative=12,
        expected_previous_steps=8,
        expected_next_row=96,
        label="staged stage3",
    )
    stage2_source_weight = stage2.get("weight_digest_after")
    if (
        receipt.get("initial_trainable_parameter_digest") != stage2_source_weight
        or receipt.get("weight_digest_before") != stage2_source_weight
    ):
        raise RecipeEvalHold("staged stage3 initial digest/source mismatch")
    _validate_common_recipe_receipt(
        stage2,
        expected_train_sha=expected_train_sha,
        expected_runtime_sha=expected_runtime_sha,
        label="staged stage2",
    )
    if stage2.get("experiment_class") != "STAGED_RESET_RECIPE_SEMANTICS_CONTROL":
        raise RecipeEvalHold("staged stage2 experiment class mismatch")
    if stage2.get("cumulative_optimizer_steps") != 12:
        raise RecipeEvalHold("staged stage2 cumulative-step mismatch")
    _validate_window(stage2, start_row=32, row_count=64, label="staged stage2")

    stage1, stage1_path, stage1_sha = _load_bound_source_receipt(
        stage2,
        expected_source_cumulative=4,
        expected_previous_steps=4,
        expected_next_row=32,
        label="staged stage2",
    )
    stage1_source_weight = stage1.get("weight_digest_after")
    if (
        stage2.get("initial_trainable_parameter_digest") != stage1_source_weight
        or stage2.get("weight_digest_before") != stage1_source_weight
    ):
        raise RecipeEvalHold("staged stage2 initial digest/source mismatch")
    _validate_common_recipe_receipt(
        stage1,
        expected_train_sha=expected_train_sha,
        expected_runtime_sha=expected_runtime_sha,
        label="staged stage1",
    )
    if stage1.get("experiment_class") != "STAGED_RESET_RECIPE_SEMANTICS_CONTROL":
        raise RecipeEvalHold("staged stage1 experiment class mismatch")
    if stage1.get("cumulative_optimizer_steps") != 4:
        raise RecipeEvalHold("staged stage1 cumulative-step mismatch")
    _validate_window(stage1, start_row=0, row_count=32, label="staged stage1")
    if stage1.get("resume_adapter") is not None:
        raise RecipeEvalHold("staged stage1 must be fresh")
    if stage1.get("initial_trainable_parameter_digest") != expected_initial_digest:
        raise RecipeEvalHold("staged stage1 initialization digest mismatch")
    if stage1.get("weight_digest_before") != expected_initial_digest:
        raise RecipeEvalHold("staged stage1 weight-before digest mismatch")
    gate = stage1.get("initialization_equivalence_gate")
    if (
        not isinstance(gate, dict)
        or gate.get("expected_digest") != expected_initial_digest
        or gate.get("pass") is not True
    ):
        raise RecipeEvalHold("staged stage1 initialization gate mismatch")

    return {
        "status": "PASS",
        "role": role,
        "receipt_path": str(receipt_path),
        "receipt_sha256": receipt_sha,
        "chain": [
            {"stage": 1, "receipt_path": str(stage1_path), "receipt_sha256": stage1_sha},
            {"stage": 2, "receipt_path": str(stage2_path), "receipt_sha256": stage2_sha},
            {"stage": 3, "receipt_path": str(receipt_path), "receipt_sha256": receipt_sha},
        ],
    }


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
    protocol_sha256 = committed_text_sha(protocol_path)
    if protocol_sha256 != FROZEN_PROTOCOL_SHA256:
        raise RecipeEvalHold(
            "frozen protocol hash mismatch:"
            f"{protocol_sha256}!={FROZEN_PROTOCOL_SHA256}"
        )

    matched_subject = protocol.get("matched_training_subject")
    runtime = protocol.get("runtime")
    init_gate = protocol.get("initialization_equivalence_gate")
    if not isinstance(matched_subject, dict):
        raise RecipeEvalHold("protocol matched training subject missing")
    if not isinstance(runtime, dict):
        raise RecipeEvalHold("protocol runtime binding missing")
    if not isinstance(init_gate, dict):
        raise RecipeEvalHold("protocol initialization gate missing")
    expected_train_sha = matched_subject.get("train_sha256")
    expected_runtime_sha = runtime.get("binding_sha256")
    expected_initial_digest = init_gate.get(
        "expected_initial_trainable_parameter_digest"
    )
    if not isinstance(expected_train_sha, str) or not expected_train_sha:
        raise RecipeEvalHold("protocol train binding missing")
    if not isinstance(expected_runtime_sha, str) or not expected_runtime_sha:
        raise RecipeEvalHold("protocol runtime SHA missing")
    if not isinstance(expected_initial_digest, str) or not expected_initial_digest:
        raise RecipeEvalHold("protocol initialization digest missing")

    staged_recipe_semantics = validate_recipe_receipt_semantics(
        staged_receipt_path,
        role="staged",
        expected_train_sha=expected_train_sha,
        expected_runtime_sha=expected_runtime_sha,
        expected_initial_digest=expected_initial_digest,
    )
    continuous_recipe_semantics = validate_recipe_receipt_semantics(
        continuous_receipt_path,
        role="continuous",
        expected_train_sha=expected_train_sha,
        expected_runtime_sha=expected_runtime_sha,
        expected_initial_digest=expected_initial_digest,
    )

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
        "recipe_semantics": {
            "staged": staged_recipe_semantics,
            "continuous": continuous_recipe_semantics,
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
    try:
        # Create exclusively: another process may publish this path after
        # decision evaluation. Never overwrite an existing custody result.
        with args.output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    except FileExistsError:
        print(json.dumps({
            "schema": "V10R3_RECIPE_SEMANTICS_DECISION_V1",
            "status": "HOLD",
            "reason": f"decision output already exists:{args.output}",
        }, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
