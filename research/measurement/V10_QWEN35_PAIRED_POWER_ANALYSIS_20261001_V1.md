# V10 Qwen3.5 Paired-Power Analysis — 2026-10-01 V1

## Subject

This analysis tests whether the pre-registered V10 final-bank allocation is statistically defensible for the model-only behavioral gate.

Bound experiment lineage:
- parent V10 custom core: `VERA_SUCCESSOR_V4_1_10K_DIVERSE_CORE_20260930_V10`;
- behavioral final-bank proposal: 10,000 rows total, H01-H20 × 500;
- minimum behavioral families: 50 per dimension;
- predeclared overall behavioral effect gate: candidate-base delta >= +0.05;
- two-sided paired significance threshold: alpha <= 0.01.

This is planning evidence, not final qualification evidence.

## Method

The script `successor/experiments/power_v10_qwen35.py` uses a transparent dependency-free normal approximation to paired McNemar power.

For paired binary outcomes:
- `delta = P(candidate only correct) - P(base only correct)`;
- `discordance = P(candidate only correct) + P(base only correct)`;
- the approximate paired signal is `delta * sqrt(N / discordance)`.

Family correlation is handled conservatively for planning with the standard design-effect approximation:

`DE = 1 + (m - 1) * ICC`

where `m=10` cases per family at the current 500-row / 50-family dimension allocation.

Explored grid:
- discordance: 0.10, 0.20, 0.30, 0.40;
- ICC: 0, 0.05, 0.10, 0.20;
- target delta: +0.05;
- alpha: 0.01 two-sided.

The complete machine-readable grid is frozen in
`research/measurement/V10_QWEN35_PAIRED_POWER_RECEIPT_V1.json`.

## Result

### Overall 10,000-row behavioral lane

The 10k lane is amply powered for the predeclared +0.05 overall effect across the explored grid.

Even the pessimistic planning point:
- discordance = 0.40;
- family ICC = 0.20;
- design effect = 2.8;
- effective N ≈ 3,571;

still gives approximate power ≈ **0.9842**.

At discordance <=0.30 under the same ICC, approximate power remains >=0.998.

### Individual 500-row H dimensions

Five hundred rows per dimension are **not** generally sufficient for an independent +0.05 significance claim.

Examples:
- discordance 0.10, ICC 0.00: power ≈ 0.831;
- discordance 0.10, ICC 0.10: power ≈ 0.496;
- discordance 0.20, ICC 0.00: power ≈ 0.470;
- discordance 0.20, ICC 0.10: power ≈ 0.223;
- discordance 0.40, ICC 0.20: power ≈ 0.064.

Unclustered nominal N for 80% power at alpha 0.01 and delta 0.05 is approximately:
- discordance 0.10: 468;
- 0.20: 935;
- 0.30: 1,402;
- 0.40: 1,869.

For 90% power:
- 0.10: 596;
- 0.20: 1,191;
- 0.30: 1,786;
- 0.40: 2,381.

Clustering increases those requirements by the design effect.

## Design consequence

The existing 10,000-row behavioral allocation can be justified for **overall paired inference plus taxonomy coverage**.

The 500-row H01-H20 sub-allocations must be treated as:
- coverage guarantees;
- regression sentinels;
- critical-failure sentinels;
- descriptive per-dimension deltas.

They must **not** be described as twenty separately powered proofs of +0.05 improvement unless observed discordance, family structure, and final cluster-aware intervals independently support that claim.

The current contract's architecture is therefore defensible only if:
1. inferential significance remains an overall behavioral-lane claim;
2. per-dimension gates remain non-inferential regression/critical-failure ceilings;
3. the final scorer reports observed discordance and family-cluster uncertainty rather than relying on nominal row count.

## Hostile review

> **HOSTILE REVIEWER:** A normal approximation plus a simple design effect is weaker than exact paired clustered inference.

**Accepted.** This is a pre-result planning calculation. Final qualification must recompute from per-case paired evidence with exact McNemar and family-cluster bootstrap/CI. The planning result is used only to decide whether the proposed sample structure is obviously underpowered or absurdly oversized.

> **HOSTILE REVIEWER:** Ten thousand rows can still be pseudo-replication if the 1,000 nominal families are superficial variants.

**Accepted.** Statistical N cannot rescue semantic dependence. Final-bank admission still requires genuine family/source diversity and independent semantic review where deterministic grading is not valid.

> **HOSTILE REVIEWER:** Since 500 rows per H dimension are weak for separate significance, the bank should simply grow to 40,000+ rows.

**Rejected as unnecessary for the current claim.** The pre-registered gate does not require each H dimension to prove its own +0.05 gain. Overall inference is highly powered at 10k; dimensions exist to expose regressions and critical failures. Expanding every dimension to independent significance would substantially increase review burden without matching the claim actually being made.

## Claim ceiling

`POWER_DESIGN_SUPPORTS_10K_OVERALL_BEHAVIORAL_INFERENCE / 500_PER_DIMENSION_SUPPORTS_COVERAGE_AND_REGRESSION_SENTINELS / FINAL_BANK_NOT_BUILT / NO_MODEL_BENEFIT_MEASURED`
