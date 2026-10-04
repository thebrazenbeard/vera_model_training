from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from successor.experiments.evaluate_v10r3_recipe_semantics import (
    RecipeEvalHold,
    load_train_holdout_panel,
    select_train_holdout_rows,
)


def _write_panel(path: Path) -> Path:
    ids = ["row-a", "row-b"]
    value = {
        "schema": "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_PANEL_V1",
        "role": "ONE_TIME_DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_NOT_FINAL_BANK",
        "train_sha256": (
            "a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300"
        ),
        "train_rows": 50000,
        "row_start": 10,
        "row_count": 2,
        "row_indices": [10, 11],
        "record_ids": ids,
        "record_ids_sha256": hashlib.sha256(
            ("\n".join(ids) + "\n").encode("utf-8")
        ).hexdigest(),
        "selection_policy": {
            "one_time_recipe_selection_use": True,
            "subsequent_checkpoint_selection_reuse": "PROHIBITED",
            "final_bank_use": "PROHIBITED",
            "external_qualification_use": "PROHIBITED",
            "rows_may_remain_in_eventual_full_training_corpus": True,
        },
        "claim_ceiling": (
            "DEVELOPMENT_TRAIN_CORPUS_HOLDOUT_ONLY_NOT_FRESH_FINAL_BANK_"
            "NOT_EXTERNAL_QUALIFICATION"
        ),
    }
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_load_train_holdout_panel_accepts_exact_binding(tmp_path: Path) -> None:
    got = load_train_holdout_panel(_write_panel(tmp_path / "panel.json"))
    assert got["row_indices"] == [10, 11]
    assert got["record_ids"] == ["row-a", "row-b"]


def test_load_train_holdout_panel_rejects_reuse_policy(tmp_path: Path) -> None:
    path = _write_panel(tmp_path / "panel.json")
    value = json.loads(path.read_text())
    value["selection_policy"]["subsequent_checkpoint_selection_reuse"] = "ALLOWED"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RecipeEvalHold, match="subsequent reuse"):
        load_train_holdout_panel(path)


def test_select_train_holdout_rows_requires_index_and_id_match(
    tmp_path: Path,
) -> None:
    panel = load_train_holdout_panel(_write_panel(tmp_path / "panel.json"))
    rows = [{"record_id": f"row-{i}"} for i in range(50000)]
    rows[10]["record_id"] = "row-a"
    rows[11]["record_id"] = "row-b"
    selected = select_train_holdout_rows(rows, panel)
    assert [r["record_id"] for r in selected] == ["row-a", "row-b"]

    rows[11]["record_id"] = "wrong"
    with pytest.raises(RecipeEvalHold, match="record id mismatch"):
        select_train_holdout_rows(rows, panel)


def test_apply_prospective_gates_binds_nll_and_family_regression() -> None:
    from successor.experiments import evaluate_v10r3_recipe_semantics as module

    apply_gates = getattr(module, "apply_prospective_gates", None)
    assert callable(apply_gates)

    result = {
        "train_sha256": "train-a",
        "panel_record_ids_sha256": "panel-ids",
        "runtime_binding_sha256": "runtime-a",
        "candidates": [
            {
                "name": "staged",
                "token_weighted_completion_nll": 1.0,
                "cases": [
                    {"record_id": "v4.1-identity_stability-0001", "loss": 1.0},
                    {"record_id": "hf-smoltalk2-source_a-0001", "loss": 1.0},
                ],
            },
            {
                "name": "continuous",
                "token_weighted_completion_nll": 1.004,
                "cases": [
                    {"record_id": "v4.1-identity_stability-0001", "loss": 1.009},
                    {"record_id": "hf-smoltalk2-source_a-0001", "loss": 0.999},
                ],
            },
        ]
    }
    protocol = {
        "runtime": {"binding_sha256": "runtime-a"},
        "matched_training_subject": {"train_sha256": "train-a"},
        "evaluation": {"panel_record_ids_sha256": "panel-ids"},
        "prospective_gates": {
            "continuous_minus_staged_token_weighted_nll_max": 0.005,
            "family_mean_case_loss_regression_hold_abs": 0.01,
            "if_both_pass": "CONTINUOUS_STATE_SEMANTICS_SURVIVE_SMALL_SCALE_TRANSFER",
            "if_either_fails": "HOLD_V10R3_CONTINUOUS_RECIPE_AND_REASSESS",
        }
    }

    decision = apply_gates(
        result,
        protocol,
        staged_name="staged",
        continuous_name="continuous",
    )

    assert decision["status"] == "PASS"
    assert decision["decision"] == (
        "CONTINUOUS_STATE_SEMANTICS_SURVIVE_SMALL_SCALE_TRANSFER"
    )
    assert decision["gates"]["token_weighted_nll"]["passed"] is True
    assert decision["gates"]["family_mean_case_loss"]["passed"] is True
    assert decision["gates"]["family_mean_case_loss"]["worst_family"] == (
        "v4.1:identity_stability"
    )



def test_apply_prospective_gates_holds_on_family_regression() -> None:
    from successor.experiments.evaluate_v10r3_recipe_semantics import (
        apply_prospective_gates,
    )

    result = {
        "train_sha256": "train-a",
        "panel_record_ids_sha256": "panel-ids",
        "runtime_binding_sha256": "runtime-a",
        "candidates": [
            {
                "name": "staged",
                "token_weighted_completion_nll": 1.0,
                "cases": [
                    {"record_id": "v4.1-privacy_boundary-0001", "loss": 1.0},
                    {"record_id": "hf-smoltalk2-source_a-0001", "loss": 1.0},
                ],
            },
            {
                "name": "continuous",
                "token_weighted_completion_nll": 1.001,
                "cases": [
                    {"record_id": "v4.1-privacy_boundary-0001", "loss": 1.011},
                    {"record_id": "hf-smoltalk2-source_a-0001", "loss": 0.99},
                ],
            },
        ]
    }
    protocol = {
        "runtime": {"binding_sha256": "runtime-a"},
        "matched_training_subject": {"train_sha256": "train-a"},
        "evaluation": {"panel_record_ids_sha256": "panel-ids"},
        "prospective_gates": {
            "continuous_minus_staged_token_weighted_nll_max": 0.005,
            "family_mean_case_loss_regression_hold_abs": 0.01,
            "if_both_pass": "CONTINUOUS_STATE_SEMANTICS_SURVIVE_SMALL_SCALE_TRANSFER",
            "if_either_fails": "HOLD_V10R3_CONTINUOUS_RECIPE_AND_REASSESS",
        }
    }

    decision = apply_prospective_gates(
        result,
        protocol,
        staged_name="staged",
        continuous_name="continuous",
    )

    assert decision["status"] == "HOLD"
    assert decision["decision"] == "HOLD_V10R3_CONTINUOUS_RECIPE_AND_REASSESS"
    assert decision["gates"]["token_weighted_nll"]["passed"] is True
    assert decision["gates"]["family_mean_case_loss"]["passed"] is False
    assert decision["gates"]["family_mean_case_loss"]["worst_family"] == (
        "v4.1:privacy_boundary"
    )



def test_apply_prospective_gates_rejects_wrong_evaluation_binding() -> None:
    from successor.experiments.evaluate_v10r3_recipe_semantics import (
        apply_prospective_gates,
    )

    result = {
        "train_sha256": "wrong-train",
        "panel_record_ids_sha256": "panel-ids",
        "runtime_binding_sha256": "runtime-a",
        "candidates": [
            {
                "name": "staged",
                "token_weighted_completion_nll": 1.0,
                "cases": [
                    {"record_id": "v4.1-identity_stability-0001", "loss": 1.0},
                ],
            },
            {
                "name": "continuous",
                "token_weighted_completion_nll": 1.0,
                "cases": [
                    {"record_id": "v4.1-identity_stability-0001", "loss": 1.0},
                ],
            },
        ],
    }
    protocol = {
        "runtime": {"binding_sha256": "runtime-a"},
        "matched_training_subject": {"train_sha256": "train-a"},
        "evaluation": {"panel_record_ids_sha256": "panel-ids"},
        "prospective_gates": {
            "continuous_minus_staged_token_weighted_nll_max": 0.005,
            "family_mean_case_loss_regression_hold_abs": 0.01,
            "if_both_pass": "PASS_DECISION",
            "if_either_fails": "HOLD_DECISION",
        },
    }

    with pytest.raises(RecipeEvalHold, match="train binding mismatch"):
        apply_prospective_gates(
            result,
            protocol,
            staged_name="staged",
            continuous_name="continuous",
        )
