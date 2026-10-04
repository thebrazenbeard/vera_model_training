from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from successor.experiments.analyze_v10r2_checkpoint_comparison import (
    summarize_checkpoint_comparison,
)
from successor.experiments.evaluate_v10r2_heldout import (
    _paired_comparison,
    build_completion_example,
    evaluate_candidate,
)
from successor.experiments.train_v10_qwen35_authorized import (
    _observe_live_runtime,
    _read_json,
    canonical_bytes,
    load_training_stack,
    load_verified_jsonl,
    sha256_file,
    validate_runtime_observation,
)


TRAIN_SHA256 = "a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300"
TRAIN_ROWS = 50000
PANEL_SCHEMA = "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_PANEL_V1"
PANEL_ROLE = "ONE_TIME_DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_NOT_FINAL_BANK"


class RecipeEvalHold(RuntimeError):
    """Fail-closed refusal for malformed V10R3 recipe-semantics evaluation."""


def _record_id(row: dict) -> str:
    for field in ("record_id", "case_id", "id"):
        value = row.get(field)
        if isinstance(value, str) and value:
            return value
    raise RecipeEvalHold("row missing stable record id")


def _ids_sha(record_ids: list[str]) -> str:
    return hashlib.sha256(
        ("\n".join(record_ids) + "\n").encode("utf-8")
    ).hexdigest()


def load_train_holdout_panel(path: Path | str) -> dict:
    path = Path(path)
    if not path.is_file():
        raise RecipeEvalHold(f"panel missing:{path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if value.get("schema") != PANEL_SCHEMA:
        raise RecipeEvalHold("panel schema mismatch")
    if value.get("role") != PANEL_ROLE:
        raise RecipeEvalHold("panel role mismatch")
    if value.get("train_sha256") != TRAIN_SHA256:
        raise RecipeEvalHold("panel train sha mismatch")
    if value.get("train_rows") != TRAIN_ROWS:
        raise RecipeEvalHold("panel train row count mismatch")

    count = value.get("row_count")
    indices = value.get("row_indices")
    ids = value.get("record_ids")
    if not isinstance(count, int) or count < 1:
        raise RecipeEvalHold("panel row count invalid")
    if (
        not isinstance(indices, list)
        or len(indices) != count
        or any(not isinstance(i, int) or i < 0 or i >= TRAIN_ROWS for i in indices)
    ):
        raise RecipeEvalHold("panel row indices invalid")
    if len(set(indices)) != count:
        raise RecipeEvalHold("panel row indices not unique")
    if (
        not isinstance(ids, list)
        or len(ids) != count
        or any(not isinstance(item, str) or not item for item in ids)
    ):
        raise RecipeEvalHold("panel record ids invalid")
    if len(set(ids)) != count:
        raise RecipeEvalHold("panel record ids not unique")
    if value.get("record_ids_sha256") != _ids_sha(ids):
        raise RecipeEvalHold("panel record ids digest mismatch")

    policy = value.get("selection_policy")
    if not isinstance(policy, dict):
        raise RecipeEvalHold("panel selection policy missing")
    if policy.get("one_time_recipe_selection_use") is not True:
        raise RecipeEvalHold("panel must be one-time recipe selection use")
    if policy.get("subsequent_checkpoint_selection_reuse") != "PROHIBITED":
        raise RecipeEvalHold("panel subsequent reuse must be prohibited")
    if policy.get("final_bank_use") != "PROHIBITED":
        raise RecipeEvalHold("panel final-bank use must be prohibited")
    if policy.get("external_qualification_use") != "PROHIBITED":
        raise RecipeEvalHold("panel external qualification use must be prohibited")
    return value


def select_train_holdout_rows(rows: list[dict], panel: dict) -> list[dict]:
    if len(rows) != TRAIN_ROWS:
        raise RecipeEvalHold(f"train row count mismatch:{len(rows)}!={TRAIN_ROWS}")
    selected = []
    for index, expected_id in zip(
        panel["row_indices"],
        panel["record_ids"],
        strict=True,
    ):
        row = rows[index]
        actual_id = _record_id(row)
        if actual_id != expected_id:
            raise RecipeEvalHold(
                f"panel record id mismatch at index {index}:{actual_id}!={expected_id}"
            )
        selected.append(row)
    return selected


def parse_candidate_specs(values: list[str]) -> list[tuple[str, Path]]:
    if len(values) < 2:
        raise RecipeEvalHold("at least two candidates are required")
    names: set[str] = set()
    result: list[tuple[str, Path]] = []
    for raw in values:
        if "=" not in raw:
            raise RecipeEvalHold(f"invalid candidate spec:{raw}")
        name, path_text = raw.split("=", 1)
        name = name.strip()
        path_text = path_text.strip()
        if not name or not path_text:
            raise RecipeEvalHold(f"invalid candidate spec:{raw}")
        if name in names:
            raise RecipeEvalHold(f"duplicate candidate name:{name}")
        names.add(name)
        result.append((name, Path(path_text)))
    return result


def bind_evaluated_candidate_to_training_receipt(
    result: dict,
    *,
    candidate_name: str,
    receipt_path: Path | str,
    expected_cumulative_optimizer_steps: int,
) -> dict:
    candidates = result.get("candidates")
    if not isinstance(candidates, list):
        raise RecipeEvalHold("evaluation candidates missing")
    matched = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("name") == candidate_name
    ]
    if len(matched) != 1:
        raise RecipeEvalHold(
            f"evaluation candidate not uniquely found:{candidate_name}"
        )
    candidate = matched[0]

    receipt_path = Path(receipt_path)
    if not receipt_path.is_file():
        raise RecipeEvalHold(f"training receipt missing:{receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    if receipt.get("schema") != "V10R2_QWEN35_DEV_TRAINING_RECEIPT_V1":
        raise RecipeEvalHold("training receipt schema mismatch")
    if receipt.get("status") != "DEVELOPMENT_OPTIMIZER_STEP_COMPLETE":
        raise RecipeEvalHold("training receipt status mismatch")

    claimed_receipt_sha = receipt.get("receipt_sha256")
    unsigned_receipt = dict(receipt)
    unsigned_receipt.pop("receipt_sha256", None)
    actual_receipt_sha = hashlib.sha256(
        canonical_bytes(unsigned_receipt)
    ).hexdigest()
    if claimed_receipt_sha != actual_receipt_sha:
        raise RecipeEvalHold("training receipt self-hash mismatch")

    if result.get("train_sha256") != receipt.get("train_sha256"):
        raise RecipeEvalHold("candidate receipt train binding mismatch")
    if (
        result.get("runtime_binding_sha256")
        != receipt.get("runtime_binding_sha256")
    ):
        raise RecipeEvalHold("candidate receipt runtime binding mismatch")
    if (
        receipt.get("cumulative_optimizer_steps")
        != expected_cumulative_optimizer_steps
    ):
        raise RecipeEvalHold("candidate receipt cumulative-step mismatch")
    if receipt.get("weight_digest_changed") is not True:
        raise RecipeEvalHold("candidate receipt does not prove weight change")

    receipt_adapter_sha = (
        receipt.get("adapter_artifacts", {})
        .get("files", {})
        .get("adapter_model.safetensors")
    )
    candidate_adapter_sha = candidate.get("adapter_model_sha256")
    if candidate_adapter_sha != receipt_adapter_sha:
        raise RecipeEvalHold("candidate adapter hash/receipt mismatch")

    expected_adapter_dir = receipt_path.parent / "adapter"
    candidate_adapter_dir = candidate.get("adapter_dir")
    if not isinstance(candidate_adapter_dir, str) or not candidate_adapter_dir:
        raise RecipeEvalHold("candidate adapter directory missing")
    if Path(candidate_adapter_dir).resolve() != expected_adapter_dir.resolve():
        raise RecipeEvalHold("candidate adapter directory/receipt mismatch")
    adapter_model = expected_adapter_dir / "adapter_model.safetensors"
    if not adapter_model.is_file():
        raise RecipeEvalHold(f"candidate adapter model missing:{adapter_model}")
    current_adapter_sha = sha256_file(adapter_model)
    if current_adapter_sha != candidate_adapter_sha:
        raise RecipeEvalHold("candidate adapter changed after evaluation")

    weight_digest_after = receipt.get("weight_digest_after")
    if not isinstance(weight_digest_after, str) or not weight_digest_after:
        raise RecipeEvalHold("candidate receipt weight digest missing")

    return {
        "schema": "V10R3_RECIPE_SEMANTICS_CANDIDATE_RECEIPT_BINDING_V1",
        "status": "PASS",
        "candidate_name": candidate_name,
        "adapter_dir": str(expected_adapter_dir),
        "adapter_model_sha256": candidate_adapter_sha,
        "receipt_path": str(receipt_path),
        "receipt_sha256": actual_receipt_sha,
        "train_sha256": receipt["train_sha256"],
        "runtime_binding_sha256": receipt["runtime_binding_sha256"],
        "cumulative_optimizer_steps": receipt["cumulative_optimizer_steps"],
        "weight_digest_after": weight_digest_after,
        "claim_ceiling": (
            "DEVELOPMENT_CANDIDATE_CUSTODY_BINDING_ONLY_"
            "NOT_FINAL_BANK_NOT_FULL_RUN_AUTHORITY"
        ),
    }


def apply_prospective_gates(
    result: dict,
    protocol: dict,
    *,
    staged_name: str,
    continuous_name: str,
) -> dict:
    runtime = protocol.get("runtime")
    matched_subject = protocol.get("matched_training_subject")
    evaluation = protocol.get("evaluation")
    if not isinstance(runtime, dict):
        raise RecipeEvalHold("protocol runtime binding missing")
    if not isinstance(matched_subject, dict):
        raise RecipeEvalHold("protocol matched training subject missing")
    if not isinstance(evaluation, dict):
        raise RecipeEvalHold("protocol evaluation binding missing")

    expected_train_sha = matched_subject.get("train_sha256")
    if result.get("train_sha256") != expected_train_sha:
        raise RecipeEvalHold("train binding mismatch")
    expected_panel_ids_sha = evaluation.get("panel_record_ids_sha256")
    if result.get("panel_record_ids_sha256") != expected_panel_ids_sha:
        raise RecipeEvalHold("evaluation panel binding mismatch")
    expected_runtime_sha = runtime.get("binding_sha256")
    if result.get("runtime_binding_sha256") != expected_runtime_sha:
        raise RecipeEvalHold("runtime binding mismatch")

    gates = protocol.get("prospective_gates")
    if not isinstance(gates, dict):
        raise RecipeEvalHold("protocol prospective gates missing")

    nll_limit = gates.get("continuous_minus_staged_token_weighted_nll_max")
    family_limit = gates.get("family_mean_case_loss_regression_hold_abs")
    if not isinstance(nll_limit, (int, float)):
        raise RecipeEvalHold("token-weighted NLL gate missing")
    if not isinstance(family_limit, (int, float)):
        raise RecipeEvalHold("family mean case-loss gate missing")

    summary = summarize_checkpoint_comparison(
        result,
        staged_name,
        continuous_name,
    )
    nll_delta = summary["overall"]["right_minus_left_nll"]
    families = summary["families"]
    if not families:
        raise RecipeEvalHold("family comparison missing")
    worst_family, worst_summary = max(
        families.items(),
        key=lambda item: item[1]["right_minus_left_mean_case_loss"],
    )
    worst_delta = worst_summary["right_minus_left_mean_case_loss"]

    nll_passed = nll_delta <= float(nll_limit)
    family_passed = worst_delta <= float(family_limit)
    passed = nll_passed and family_passed

    return {
        "schema": "V10R3_RECIPE_SEMANTICS_PROSPECTIVE_GATE_DECISION_V1",
        "status": "PASS" if passed else "HOLD",
        "decision": (
            gates["if_both_pass"] if passed else gates["if_either_fails"]
        ),
        "staged_name": staged_name,
        "continuous_name": continuous_name,
        "gates": {
            "token_weighted_nll": {
                "continuous_minus_staged": nll_delta,
                "max_allowed": float(nll_limit),
                "passed": nll_passed,
            },
            "family_mean_case_loss": {
                "worst_family": worst_family,
                "worst_continuous_minus_staged": worst_delta,
                "max_allowed": float(family_limit),
                "passed": family_passed,
            },
        },
        "family_comparison": summary,
        "claim_ceiling": (
            "DEVELOPMENT_RECIPE_SEMANTICS_GATE_APPLICATION_ONLY_"
            "NOT_FINAL_BANK_NOT_FULL_RUN_AUTHORITY"
        ),
    }


def run_recipe_semantics_eval(
    repo_root: Path,
    *,
    train_jsonl: Path,
    panel_path: Path,
    candidates: list[tuple[str, Path]],
) -> dict:
    runtime_path = (
        repo_root
        / "successor"
        / "experiments"
        / "V10_QWEN35_TRAINING_RUNTIME_BINDING_V1.json"
    )
    runtime_binding = _read_json(runtime_path)
    stack = load_training_stack()
    runtime_observation = _observe_live_runtime(runtime_binding, stack)
    runtime_check = validate_runtime_observation(
        runtime_binding,
        runtime_observation,
    )

    rows = load_verified_jsonl(
        train_jsonl,
        expected_sha256=TRAIN_SHA256,
        expected_rows=TRAIN_ROWS,
    )
    panel = load_train_holdout_panel(panel_path)
    selected = select_train_holdout_rows(rows, panel)

    base_path = Path(runtime_binding["target"]["base_path"])
    tokenizer = stack["AutoTokenizer"].from_pretrained(base_path)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    examples = [
        build_completion_example(tokenizer, row, max_length=512)
        for row in selected
    ]

    torch = stack["torch"]
    quant_config = stack["BitsAndBytesConfig"](
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    results = [
        evaluate_candidate(
            stack=stack,
            tokenizer=tokenizer,
            examples=examples,
            base_path=base_path,
            quant_config=quant_config,
            name=name,
            adapter_dir=adapter_dir,
        )
        for name, adapter_dir in candidates
    ]
    comparisons = []
    for left_index in range(len(results)):
        for right_index in range(left_index + 1, len(results)):
            comparisons.append(
                _paired_comparison(results[left_index], results[right_index])
            )

    return {
        "schema": "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_EVAL_V1",
        "status": "DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_COMPLETE",
        "role": "ONE_TIME_TRAIN_CORPUS_HOLDOUT_DIAGNOSTIC_NOT_FINAL_BANK",
        "train_sha256": sha256_file(train_jsonl),
        "train_rows": TRAIN_ROWS,
        "panel_path": str(panel_path),
        "panel_sha256": sha256_file(panel_path),
        "panel_record_ids_sha256": panel["record_ids_sha256"],
        "panel_row_indices": panel["row_indices"],
        "panel_record_ids": panel["record_ids"],
        "runtime_binding_sha256": runtime_binding["binding_sha256"],
        "runtime_observation": runtime_observation,
        "runtime_check": runtime_check,
        "candidates": results,
        "paired_comparisons": comparisons,
        "claim_ceiling": (
            "DEVELOPMENT RECIPE-SEMANTICS TRAIN-CORPUS HOLDOUT ONLY / "
            "ONE-TIME RECIPE SELECTION USE / NOT FINAL BANK / "
            "NOT EXTERNAL QUALIFICATION"
        ),
    }


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        candidates = parse_candidate_specs(args.candidate)
        result = run_recipe_semantics_eval(
            args.repo_root,
            train_jsonl=args.train_jsonl,
            panel_path=args.panel,
            candidates=candidates,
        )
    except (RecipeEvalHold, ValueError) as exc:
        print(
            json.dumps(
                {
                    "schema": "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_EVAL_V1",
                    "status": "HOLD",
                    "reason": str(exc),
                },
                sort_keys=True,
            )
        )
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise RecipeEvalHold(f"output already exists:{args.output}")
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())