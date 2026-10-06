import importlib
import importlib.util


def test_stage2_contract_requires_all_banks_controls_and_hidden_grading():
    spec = importlib.util.find_spec("training.stage2_eval_contract")
    assert spec is not None, "Stage-2 eval contract module is missing"
    s2 = importlib.import_module("training.stage2_eval_contract")
    contract = s2.build_stage2_eval_contract(
        banks=list(s2.REQUIRED_EVAL_BANKS),
        controls=list(s2.REQUIRED_CONTROL_ARMS),
        hidden_grading_fields=list(s2.REQUIRED_HIDDEN_GRADING_FIELDS),
        candidate_identity_blinded=True,
        deterministic_decoding_or_fixed_seeds=True,
        promotion_cases_per_family=80,
        power_preregistered=True,
        grader_count=2,
        adjudication_required=True,
        exact_training_subject_verified=True,
        manifest_hashes_verified=True,
        shard_hashes_verified=True,
    )
    assert contract["status"] == "PASS"
    assert contract["bank_count"] == 12
    assert contract["promotion_cases_per_family"] == 80
    assert contract["grader_count"] == 2
    assert contract["adjudication_required"] is True


def test_stage2_contract_requires_exact_subject_and_hash_verification_inputs():
    import inspect

    s2 = importlib.import_module("training.stage2_eval_contract")
    params = inspect.signature(s2.build_stage2_eval_contract).parameters
    assert "exact_training_subject_verified" in params
    assert "manifest_hashes_verified" in params
    assert "shard_hashes_verified" in params


def test_stage2_contract_holds_when_subject_hash_verification_is_omitted():
    s2 = importlib.import_module("training.stage2_eval_contract")
    contract = s2.build_stage2_eval_contract(
        banks=list(s2.REQUIRED_EVAL_BANKS),
        controls=list(s2.REQUIRED_CONTROL_ARMS),
        hidden_grading_fields=list(s2.REQUIRED_HIDDEN_GRADING_FIELDS),
        candidate_identity_blinded=True,
        deterministic_decoding_or_fixed_seeds=True,
        promotion_cases_per_family=80,
        power_preregistered=True,
        grader_count=2,
        adjudication_required=True,
    )
    assert contract["status"] == "HOLD"
    assert "exact_training_subject_not_verified" in contract["reasons"]
