import importlib


def test_h0_support_dependent_gain_is_in_context_not_durable_learning():
    h0 = importlib.import_module("training.stage3_h0_falsifier")
    result = h0.classify_h0_retention(
        zero_shot_score=0.2,
        supported_score=0.9,
        support_removed_score=0.2,
        retrieval_disabled_score=0.2,
        weight_change_performed=False,
        fresh_process_retest=True,
    )
    assert result["classification"] == "IN_CONTEXT_ADAPTATION_NOT_DURABLE_LEARNING"
    assert result["durable_learning_claim_allowed"] is False


def test_h0_persistent_no_weight_gain_remains_non_weight_and_unresolved():
    h0 = importlib.import_module("training.stage3_h0_falsifier")
    result = h0.classify_h0_retention(
        zero_shot_score=0.2,
        supported_score=0.9,
        support_removed_score=0.9,
        retrieval_disabled_score=0.9,
        weight_change_performed=False,
        fresh_process_retest=True,
    )
    assert result["classification"] == "NO_WEIGHT_RETENTION_UNRESOLVED"
    assert result["durable_weight_learning_claim_allowed"] is False


def test_h0_without_fresh_process_or_with_weight_change_cannot_support_h0_retention_claim():
    h0 = importlib.import_module("training.stage3_h0_falsifier")
    no_fresh = h0.classify_h0_retention(
        zero_shot_score=0.2,
        supported_score=0.9,
        support_removed_score=0.9,
        retrieval_disabled_score=0.9,
        weight_change_performed=False,
        fresh_process_retest=False,
    )
    assert no_fresh["classification"] == "UNRESOLVED_NO_FRESH_PROCESS"

    changed = h0.classify_h0_retention(
        zero_shot_score=0.2,
        supported_score=0.9,
        support_removed_score=0.9,
        retrieval_disabled_score=0.9,
        weight_change_performed=True,
        fresh_process_retest=True,
    )
    assert changed["classification"] == "OUTSIDE_H0_WEIGHT_CHANGE_PRESENT"
    assert changed["durable_learning_claim_allowed"] is False
