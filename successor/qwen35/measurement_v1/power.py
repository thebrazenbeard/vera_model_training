"""Paired-power design calculations for the Qwen3.5 measurement workstream.

This module is planning tooling only. It does not score models and does not
establish qualification. The approximation treats each paired case as a
difference D in {-1, 0, +1}; exact McNemar inference remains the final
analysis method.

The key inputs are:
- target paired accuracy improvement (candidate - base);
- expected discordance rate (base-only + candidate-only);
- alpha/power;
- optional family-cluster design effect.

Cluster assumptions are deliberately explicit because family/source
correlation can make a nominal case count overstate information.
"""

from __future__ import annotations

import math
from statistics import NormalDist


NORMAL = NormalDist()


def max_discordance_for_accuracies(base_accuracy: float, candidate_accuracy: float) -> float:
    """Return the largest feasible discordance rate for two marginal accuracies."""
    if not 0.0 <= base_accuracy <= 1.0 or not 0.0 <= candidate_accuracy <= 1.0:
        raise ValueError("accuracies must be in [0, 1]")
    if candidate_accuracy < base_accuracy:
        raise ValueError("candidate_accuracy must be >= base_accuracy")
    delta = candidate_accuracy - base_accuracy
    # Let b=base-only and c=candidate-only. Then c-b=delta and
    # b <= min(base_accuracy, 1-candidate_accuracy).
    b_max = min(base_accuracy, 1.0 - candidate_accuracy)
    return delta + 2.0 * b_max


def cluster_design_effect(cases_per_family: int, intraclass_correlation: float) -> float:
    """Return the one-way cluster design effect 1 + (m-1)*ICC."""
    if cases_per_family < 1:
        raise ValueError("cases_per_family must be >= 1")
    if not 0.0 <= intraclass_correlation < 1.0:
        raise ValueError("intraclass_correlation must be in [0, 1)")
    return 1.0 + (cases_per_family - 1) * intraclass_correlation


def paired_n_approx(
    delta: float,
    discordance_rate: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
    design_effect: float = 1.0,
) -> int:
    """Approximate paired-case N for a two-sided normal McNemar design.

    delta is candidate accuracy minus base accuracy.
    discordance_rate is P(base != candidate).
    The calculation is intentionally conservative for planning only; final
    evidence uses exact McNemar plus cluster-aware intervals.
    """
    if delta <= 0.0:
        raise ValueError("delta must be > 0")
    if not abs(delta) <= discordance_rate <= 1.0:
        raise ValueError("discordance_rate must be >= |delta| and <= 1")
    if not 0.0 < alpha < 1.0 or not 0.0 < power < 1.0:
        raise ValueError("alpha and power must be in (0, 1)")
    if design_effect < 1.0:
        raise ValueError("design_effect must be >= 1")

    z_alpha = NORMAL.inv_cdf(1.0 - alpha / 2.0)
    z_power = NORMAL.inv_cdf(power)
    variance = discordance_rate - delta * delta
    if variance <= 0.0:
        # Degenerate paired outcomes: the deterministic signal needs only a
        # minimal finite sample for planning. Keep one case as a lower bound.
        return 1
    iid_n = ((z_alpha + z_power) ** 2) * variance / (delta * delta)
    return max(1, math.ceil(iid_n * design_effect))


def planning_grid(
    *,
    deltas=(0.03, 0.05, 0.08, 0.10),
    discordance_rates=(0.10, 0.20, 0.30, 0.40),
    alphas=(0.05,),
    powers=(0.80, 0.90),
    design_effects=(1.0, 1.20, 1.45),
) -> list[dict]:
    """Return a deterministic grid for hostile sensitivity review."""
    rows = []
    for delta in deltas:
        for discordance in discordance_rates:
            if discordance < delta:
                continue
            for alpha in alphas:
                for power in powers:
                    for de in design_effects:
                        rows.append(
                            {
                                "delta": delta,
                                "discordance_rate": discordance,
                                "alpha": alpha,
                                "power": power,
                                "design_effect": de,
                                "required_n": paired_n_approx(
                                    delta,
                                    discordance,
                                    alpha=alpha,
                                    power=power,
                                    design_effect=de,
                                ),
                            }
                        )
    return rows


def default_design_receipt() -> dict:
    """Return the current research proposal without claiming it is approved."""
    base = 0.77
    primary_delta = 0.05
    primary_candidate = base + primary_delta
    primary_discordance_max = max_discordance_for_accuracies(base, primary_candidate)

    return {
        "schema": "QWEN35_PAIRED_POWER_DESIGN_V1",
        "status": "RESEARCH_PROPOSAL_NOT_APPROVED",
        "prior_base_behavioral_accuracy": base,
        "primary_overall_mde": primary_delta,
        "primary_overall_target_accuracy": primary_candidate,
        "primary_max_feasible_discordance": round(primary_discordance_max, 6),
        "primary_power_reference": {
            "alpha": 0.05,
            "power": 0.90,
            "discordance": round(primary_discordance_max, 2),
            "required_n_iid_approx": paired_n_approx(
                primary_delta,
                round(primary_discordance_max, 2),
                alpha=0.05,
                power=0.90,
            ),
        },
        "secondary_dimension_mde": 0.10,
        "secondary_dimension_reference": {
            "alpha": 0.05,
            "power": 0.80,
            "discordance": 0.36,
            "required_n_iid_approx": paired_n_approx(
                0.10,
                0.36,
                alpha=0.05,
                power=0.80,
            ),
            "required_n_with_design_effect_1_45": paired_n_approx(
                0.10,
                0.36,
                alpha=0.05,
                power=0.80,
                design_effect=1.45,
            ),
        },
        "proposed_behavioral_cases_per_dimension": 500,
        "proposed_behavioral_cases": 10000,
        "proposed_total_weight_only_cases": 13500,
        "proposal_rationale": [
            "5 percentage points remains the primary overall development/qualification MDE.",
            "10 percentage points is treated as the secondary per-dimension effect worth detecting without claiming 20 independent discoveries.",
            "500 cases per H dimension provides margin over the 300-case governance floor and remains above the 80% planning target in the high-discordance, moderate-clustering reference regime.",
            "The 2,000 adversarial and 1,500 retention floors remain separate lanes rather than being counted as H-dimension power.",
            "If development discordance or family ICC materially differs from these planning regimes, rerun the grid before freezing the bank.",
        ],
        "claim_ceiling": "PLANNING_APPROXIMATION_NOT_FINAL_POWER_OR_QUALIFICATION",
    }
