import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "training_contract.py"
CONTRACT = ROOT / "docs" / "training-plan" / "VERA_EXECUTION_CONTRACT_V1.json"
VIEW = ROOT / "docs" / "training-plan" / "VERA_EXECUTION_CONTRACT_V1.md"
PARENT = "c06e33d44184904418a4a68f22f78d19a4f46137"


def run_contract(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_contract_validates_and_render_is_reproducible():
    result = run_contract("validate", str(CONTRACT))
    assert result.returncode == 0, result.stdout + result.stderr
    rendered = run_contract("render", str(CONTRACT))
    assert rendered.returncode == 0, rendered.stdout + rendered.stderr
    assert rendered.stdout == VIEW.read_text(encoding="utf-8")


def test_duplicate_json_keys_are_rejected(tmp_path):
    bad = tmp_path / "duplicate.json"
    bad.write_text('{"schema":"A","schema":"B"}', encoding="utf-8")
    result = run_contract("validate", str(bad))
    assert result.returncode != 0
    assert "duplicate key" in (result.stdout + result.stderr).lower()

def test_contract_binds_lane_c_hold_clearers():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["source"]["parent_head"] == PARENT
    assert data["execution_precedence"] == "CONTROLLING_PLAN_NORMATIVE_FLOOR__CONTRACT_STRENGTHENING_OVERLAY"
    assert data["authorization"]["requires_live_operator_authorization"] is True

    isolation = data["controls"]["fresh_state_isolation"]
    assert isolation["required"] is True
    assert isolation["weaker_fallback_allowed"] is False

    stages = [stage["id"] for stage in data["stages"]]
    assert stages[:7] == [
        "stage0_runtime",
        "stage1_corpus",
        "stage2_eval",
        "stage3_h0",
        "stage4_mechanisms",
        "stage5_corrigibility_identity",
        "stage6_epistemic",
    ]

    stage0 = data["stage0"]
    assert stage0["soak"]["minimum_optimizer_steps"] >= 20
    assert stage0["abort"]["cpu_fallback"] is True
    assert stage0["abort"]["driver_reset_or_cuda_error"] is True
    assert stage0["abort"]["cuda_allocation_failure"] is True

    stage16 = data["stage16_custody"]
    assert stage16["lane_a_can_read_rows"] is False
    assert stage16["lane_c_can_read_rows"] is False
    assert stage16["training_lanes_can_read_answer_keys"] is False

    assert data["exposure_ledger"]["required_for"] == ["H0", "H1", "H2"]
    assert data["evaluator"]["candidate_identity_blinded"] is True
    assert data["continual_learning"]["minimum_order_permutations"] >= 2
    assert data["privacy"]["sensitive_material_default"] == "EXCLUDED"
    assert data["review"]["vera_exact_head_review_required_before_corpus_training"] is True
    assert data["review"]["lane_c_exact_head_review_required_before_corpus_training"] is True

    stats = data["statistical_decision_contract"]
    required_stat_fields = {
        "primary_metric",
        "practical_effect_threshold",
        "noninferiority_margin",
        "seed_policy",
        "failed_run_treatment",
        "multiple_comparison_policy",
        "early_stop_rule",
        "inconclusive_region",
    }
    assert required_stat_fields <= set(stats["subject_required_fields"])

    bundle_fields = set(data["deployment_bundle_binding"]["required_digests"])
    assert {
        "model_or_adapter",
        "tokenizer",
        "chat_template",
        "system_developer_prompts",
        "generation_parameters",
        "tool_schemas",
        "routing",
        "retrieval_memory_config",
        "runtime",
    } <= bundle_fields

    rendered = data["rendered_input_digests"]
    assert rendered["after_chat_template"] is True
    assert rendered["after_tokenization"] is True

    assert data["h0"]["arms"] == [
        "BASE_ONLY",
        "BOUNDED_CONTEXT",
        "GOVERNED_RETRIEVAL_MEMORY",
        "COMBINED_SUPPORT",
    ]

    assert set(data["prompt_dependence_ablations"]["required_for"]) == {
        "identity",
        "corrigibility",
        "tool_honesty",
    }
    calibration = data["calibration"]
    assert calibration["required_for_epistemic_confidence_claims"] is True
    assert calibration["selective_prediction_required"] is True

    c_harness = data["controls"]["fresh_state_isolation"]
    assert c_harness["implementation_owner"] == "Lane-C"
    assert "reserved_branch" not in c_harness
    assert c_harness["accepted_subject_binding"]["status"] == "PENDING_VERA_ACCEPTANCE"
    assert c_harness["accepted_subject_binding"]["exact_head_required"] is True
    assert "current_unaccepted_candidate" not in c_harness["accepted_subject_binding"]
    assert c_harness["mandatory_canaries"] == [
        "undeclared_environment_global_counter",
        "changed_file_outside_arm_root",
        "shared_retrieval_index_or_external_mutable_state",
        "inherited_write_capable_credential",
        "reused_daemon_port_or_provider_session_state",
        "stale_adapter_module_resurrection",
        "deterministic_state_file_outside_isolated_root",
    ]


def test_rendered_view_contains_no_known_stale_weakening():
    text = VIEW.read_text(encoding="utf-8")
    forbidden = [
        "where practical",
        "VERA REVIEW PENDING",
        "FRESH LANE B CREATIVE PROPOSAL NOT YET FROZEN",
        "No planning-signoff dependency remains",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_validator_rejects_c_pre_audit_negative_controls(tmp_path):
    import copy

    baseline = json.loads(CONTRACT.read_text(encoding="utf-8"))
    variants = []

    broken = copy.deepcopy(baseline)
    broken["authorization"]["paid_compute_authorized"] = True
    variants.append(("unvalidated_material_authority_change", broken))

    broken = copy.deepcopy(baseline)
    broken["exposure_ledger"]["subject_required_fields"] = []
    variants.append(("empty_exposure_ledger", broken))

    broken = copy.deepcopy(baseline)
    broken["controls"]["fresh_state_isolation"]["covered_channels"] = []
    variants.append(("empty_covered_channels", broken))

    broken = copy.deepcopy(baseline)
    broken["stage16_custody"]["one_time_use_state_required"] = False
    variants.append(("reusable_protected_bank", broken))

    broken = copy.deepcopy(baseline)
    broken["stage16_custody"]["bank_exposure_marks_burned"] = False
    variants.append(("bank_exposure_not_burned", broken))

    broken = copy.deepcopy(baseline)
    broken["stage16_custody"]["post_run_lane_c_receives_only_nonsecret_evidence"] = False
    variants.append(("secret_post_run_c_evidence", broken))

    broken = copy.deepcopy(baseline)
    broken["stage0"]["thresholds"] = {
        "minimum_commit_headroom_mib": -1,
        "gpu_temperature_c_abort": 999,
        "step_time_p95_over_median_abort_ratio": 999,
        "consecutive_degraded_steps": 0,
    }
    variants.append(("unsafe_stage0_thresholds", broken))

    broken = copy.deepcopy(baseline)
    broken["controls"]["fresh_state_isolation"]["mandatory_canaries"] = [
        "local_hidden_counter",
        "external_mutable_service",
    ]
    variants.append(("reduced_isolation_canaries", broken))

    for label, candidate in variants:
        candidate_path = tmp_path / f"{label}.json"
        candidate_path.write_text(
            json.dumps(candidate, indent=2) + "\n",
            encoding="utf-8",
        )
        result = run_contract("validate", str(candidate_path))
        assert result.returncode != 0, (
            f"validator accepted C pre-audit negative control: {label}\n"
            + result.stdout
            + result.stderr
        )


def test_controlling_plan_is_normative_floor_and_overlay_only():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["execution_precedence"] == "CONTROLLING_PLAN_NORMATIVE_FLOOR__CONTRACT_STRENGTHENING_OVERLAY"
    floor = data["plan_floor"]
    assert floor == {
        "repository": "thebrazenbeard/vera_model_training",
        "branch": "a-b-c-vera-training-plan",
        "head": "c06e33d44184904418a4a68f22f78d19a4f46137",
        "path": "docs/training-plan/VERA_STAGED_TRAINING_PLAN_FINAL_V2.md",
        "blob": "3d0895dca8b3581061dd0d2e9824758bd6fb8e74",
        "plan_is_normative_floor": True,
        "contract_may_strengthen_but_not_weaken": True,
    }

    superseded = data["superseded_historical_propositions"]
    assert superseded == [{
        "id": "TRAINING_PAUSED_AUTHORITY_STATE",
        "replacement": "LIVE_OPERATOR_RESUMED_2026-10-05",
        "scope": "AUTHORITY_STATE_ONLY",
        "does_not_supersede": [
            "technical_architecture",
            "evidence_gates",
            "stage_dependencies",
            "privacy_custody_rules",
            "claim_ceilings",
        ],
    }]

    invariants = data["plan_floor_invariants"]
    assert invariants["stage0_before_corpus_optimization"] is True
    assert invariants["stage1_provenance_privacy_ancestry_before_training"] is True
    assert invariants["stage2_eval_baseline_contracts_before_optimization"] is True
    assert invariants["stage3_h0_before_neural_promotion"] is True
    assert invariants["matched_h1_h2_h3_exposure_search_accounting"] is True
    assert invariants["corrigibility_before_or_jointly_gates_identity"] is True
    assert invariants["tool_success_requires_effect_verification"] is True
    assert invariants["continual_learning_requires_isolation_support_removal_reopen"] is True
    assert invariants["routing_mechanism_requires_qualification"] is True
    assert invariants["protected_final_qualification_sealed_one_time"] is True
    assert invariants["material_head_movement_creates_new_review_subject"] is True
    assert invariants["placement_policy_preserved"] is True


def test_validator_rejects_plan_floor_weakening(tmp_path):
    import copy

    baseline = json.loads(CONTRACT.read_text(encoding="utf-8"))
    variants = []

    broken = copy.deepcopy(baseline)
    broken["execution_precedence"] = "THIS_CONTRACT_IS_SOLE_EXECUTION_NORMATIVE_SOURCE"
    variants.append(("sole_source_regression", broken))

    broken = copy.deepcopy(baseline)
    broken["plan_floor"]["blob"] = "0" * 40
    variants.append(("wrong_plan_blob", broken))

    broken = copy.deepcopy(baseline)
    broken["plan_floor"]["plan_is_normative_floor"] = False
    variants.append(("plan_not_floor", broken))

    broken = copy.deepcopy(baseline)
    broken["plan_floor"]["contract_may_strengthen_but_not_weaken"] = False
    variants.append(("overlay_can_weaken", broken))

    broken = copy.deepcopy(baseline)
    broken["plan_floor_invariants"]["stage0_before_corpus_optimization"] = False
    variants.append(("stage0_floor_weakened", broken))

    broken = copy.deepcopy(baseline)
    broken["superseded_historical_propositions"][0]["scope"] = "ALL_PLAN_REQUIREMENTS"
    variants.append(("resume_overbroad_supersession", broken))

    for label, candidate in variants:
        candidate_path = tmp_path / f"{label}.json"
        candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
        result = run_contract("validate", str(candidate_path))
        assert result.returncode != 0, (
            f"validator accepted plan-floor weakening: {label}\n"
            + result.stdout
            + result.stderr
        )


def test_rendered_view_declares_plan_floor_overlay():
    text = VIEW.read_text(encoding="utf-8")
    assert (
        "Controlling plan is the normative floor; this contract is a "
        "machine-checkable strengthening/execution overlay."
    ) in text
    assert "TRAINING_PAUSED_AUTHORITY_STATE" in text
    assert "AUTHORITY_STATE_ONLY" in text
