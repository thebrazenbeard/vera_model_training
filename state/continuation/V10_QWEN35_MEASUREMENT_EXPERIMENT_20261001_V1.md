# V10 Qwen3.5 Measurement Experiment Continuation — 2026-10-01 V1

Restore command:

`VERA_MODEL_TRAINING::RESUME_V10_QWEN35_MEASUREMENT_EXPERIMENT::20261001_V1`

## Canonical working subject

Repository: `thebrazenbeard/vera_model_training`

Research branch: `work/v10-qwen35-measurement-experiment-20261001`

Branch head before this continuation commit: `1cb706aa119f57fe53cfa27d43a100e23271a2f5`

Parent V10 subject: `work/v4.1-diverse-core-20260930@af27db57edf41a06601a2ed2e25d3757f9037ba3`

Parent Draft PR: #59 — do not mutate or merge it from this lane.

## Completed in this continuation

The exact V10 corpus checkpoint was restored and fresh-read. The V10 corpus/mixture/semantic gates are qualified at the corpus-construction layer only; no model-benefit claim follows from those gates.

A child research branch was created to prevent Qwen experiment work from colliding with PR #59.

Persisted plan:
`docs/superpowers/plans/2026-10-01-v10-qwen35-preregistered-experiment.md`

Persisted machine-readable contract:
`successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V1.json`

Contract blob observed after write:
`45254220f73f6da72f2076831d2d2af2c4cd6bb5`

Contract status:
`PREREGISTERED_BLOCKED`

## Frozen experiment subject

Base:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

Fresh adapter only. Parent adapter is null.

V10 train:
- rows: 50,000
- SHA-256: `04fbb3a2012ef3fd0506ad1188cc9f3b8d850161301fb9e0d00edd7f8ec78e90`

V10 validation:
- rows: 2,500
- SHA-256: `26e3387852283d399cea3df0758c3abf877d2884d298860668de7e5fe0b3bd93`

Training recipe is pre-registered as one-epoch QLoRA SFT: NF4 double quantization; bfloat16 compute; LoRA r=4/alpha=16/dropout=0/all-linear; batch 1; gradient accumulation 8; LR 2e-5; cosine; 3 warmup optimizer steps; max length 512; no truncation; adamw_torch; completion-only loss; packing disabled; seed 20261001.

That recipe is not yet runtime-qualified against V10.

## Evaluation contract

The separate Qwen measurement lane at `work/qwen35-measurement-devloop-v1-20260930@f261c4f6c88d326bca660d83c28222512a26ecb1` is donor research/provenance only.

The pre-registered model-only final-bank design is:
- behavioral: 10,000, H01-H20 × 500;
- adversarial: 2,000, H01-H20 × 100;
- retention: 1,500 under the frozen allocation in the experiment contract;
- runtime/effect: 1,000 separate and not counted toward model-only qualification.

Actual generated responses, paired statistics, family-cluster intervals, and exact McNemar inference are required.

Old V3/V4 finals, V10 training/validation rows, and the V10 100-row behavioral review sample are forbidden as final V10 model-benefit evidence.

## Current blockers

All remain unresolved:
- fresh final evaluation banks are not built/frozen;
- independent bank admission is not verified;
- contamination screening against V10 and consumed finals is not verified;
- exact Qwen 512-token no-overflow preflight has not been run on the V10 mixture;
- zero-cost execution target and exact runtime versions are not bound;
- Patrick has not authorized this exact weight-changing subject.

No weight mutation, paid compute, merge, installation, activation, deployment, or provider/credential effect was performed.

## Hostile review result

> **HOSTILE REVIEWER:** Pre-registering the historical Qwen training mechanics does not prove they fit a 50k V10 corpus or the current laptop.

**Accepted.** The recipe is frozen specifically so the token/resource preflight can falsify it before training. Overflow, infeasible resources, or a required recipe change produces a new contract version rather than silent adaptation.

> **HOSTILE REVIEWER:** A 13,500-case bank can still be bad evidence if it is synthetic, correlated, or reviewer-contaminated.

**Accepted.** Row count is a floor, not validity. Final-bank admission remains blocked on provenance, family independence, grader correctness, contamination screening, and genuine independent review.

## Next bounded frontier

Build the final-bank admission specification and contamination registry on this child branch without manufacturing cases. The first executable result should be a fail-closed bank preflight that proves why the experiment is still HOLD.

Do not train until every technical blocker is cleared and Patrick separately authorizes the exact frozen subject.

## Claim ceiling

`V10_CORPUS_AND_MIXTURE_QUALIFIED / QWEN35_EXPERIMENT_PREREGISTERED / FINAL_EVAL_BANK_NOT_FROZEN / TRAINING_NOT_AUTHORIZED / WEIGHTS_UNCHANGED / NOT_DEPLOYED`
