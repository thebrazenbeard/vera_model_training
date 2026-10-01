import pytest

from successor.qwen35.measurement_v1.power import (
    cluster_design_effect,
    default_design_receipt,
    max_discordance_for_accuracies,
    paired_n_approx,
)


def test_max_discordance_is_bounded_by_marginal_accuracies():
    assert max_discordance_for_accuracies(0.77, 0.82) == pytest.approx(0.41)
    assert max_discordance_for_accuracies(0.77, 0.87) == pytest.approx(0.36)


def test_paired_power_increases_with_discordance():
    low = paired_n_approx(0.05, 0.10, power=0.80)
    high = paired_n_approx(0.05, 0.40, power=0.80)
    assert high > low


def test_paired_power_decreases_with_larger_effect():
    small = paired_n_approx(0.05, 0.30, power=0.80)
    large = paired_n_approx(0.10, 0.30, power=0.80)
    assert large < small


def test_cluster_design_effect_is_explicit_and_monotonic():
    assert cluster_design_effect(1, 0.05) == pytest.approx(1.0)
    assert cluster_design_effect(10, 0.05) == pytest.approx(1.45)
    assert cluster_design_effect(10, 0.10) > cluster_design_effect(10, 0.05)


def test_v4_primary_reference_is_not_based_on_observed_one_case_gain():
    receipt = default_design_receipt()
    assert receipt["primary_overall_mde"] == pytest.approx(0.05)
    assert receipt["primary_power_reference"]["power"] == pytest.approx(0.90)
    assert receipt["primary_power_reference"]["required_n_iid_approx"] >= 1600


def test_dimension_reference_exceeds_old_300_case_floor_when_clustering_is_included():
    receipt = default_design_receipt()
    assert receipt["secondary_dimension_reference"]["required_n_iid_approx"] < 300
    assert receipt["secondary_dimension_reference"]["required_n_with_design_effect_1_45"] > 300
    assert receipt["proposed_behavioral_cases_per_dimension"] == 500
    assert receipt["proposed_behavioral_cases"] == 10000


def test_default_receipt_remains_unapproved_research():
    receipt = default_design_receipt()
    assert receipt["status"] == "RESEARCH_PROPOSAL_NOT_APPROVED"
    assert "NOT_FINAL" in receipt["claim_ceiling"]
