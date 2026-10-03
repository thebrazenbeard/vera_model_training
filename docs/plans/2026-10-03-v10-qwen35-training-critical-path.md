# V10 Qwen3.5 — Objective Training Critical Path V1

**Date:** 2026-10-03
**Repository:** `thebrazenbeard/vera_model_training`
**Purpose:** Separate evaluation-bank qualification from the actual SFT weight-changing execution path.

## Bottom line

The retention bank is **not training data**.

The authorized SFT runner consumes the exact train/validation JSONL subject frozen in `V10_QWEN35_EXPERIMENT_CONTRACT_V2.json`. The retention lane is one-third of the fresh evaluation bank used to decide whether a trained candidate is acceptable.

A retention admission does not authorize training and does not satisfy the full final-bank gate by itself.

## Frozen SFT subject

Contract:
`successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V2.json`

Training source subject:
- corpus id: `VERA_SUCCESSOR_V10_QWEN512_50K_20261001_V1`
- train rows: 50,000
- train SHA-256: `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- validation rows: 2,500
- validation SHA-256: `ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7`
- train/validation overlap: 0
- token preflight: PASS, no rows over 512 tokens

Training recipe:
- one fresh QLoRA SFT adapter
- 1 epoch
- learning rate 2e-5
- cosine scheduler
- 3 warmup optimizer steps
- batch size 1
- gradient accumulation 8
- max length 512
- error on overflow / no truncation
- `adamw_torch`
- completion-only loss
- no packing
- shuffle enabled
- gradient checkpointing enabled
- 4-bit NF4, double quant, bf16 compute
- LoRA r=4, alpha=16, dropout=0, all-linear targets
- post-train validation is diagnostic only, not checkpoint/recipe selection

## Evaluation-bank requirement

The frozen contract expects:

- behavioral: 10,000 rows across H01-H20
- adversarial: 2,000 rows across H01-H20
- retention: 1,500 rows
- total: 13,500 fresh evaluation cases

The behavioral and adversarial lanes require independent semantic review. The final bank admission policy says semantic cases require independent human review. Retention can use deterministic-first/objective case audit mechanics, but it does not replace the behavioral/adversarial human-review boundary.

## Current retention frontier

Candidate V3:
- 1,500 rows
- SHA-256: `6f47fe7da958abaf02311ae8a740b71d1bc0e9adbac88ce5c2da14139c3792f6`
- mechanical: 1,500/1,500 valid
- semantic contamination screen: PASS, zero failures at cosine threshold 0.9
- fresh V7 semantic packet: 130 rows, 26 families x5
- predecessor IDs excluded: 520
- V7 live review is a retention admission step, not SFT execution

## Read-only preflight state observed 2026-10-03

`successor.evaluate_successor.assess_v10_experiment_state` returned HOLD with:

- `final_bank_cases_not_admitted`
- `fresh_evaluation_bank_frozen`
- `independent_bank_admission_verified`
- `patrick_exact_weight_change_authority`
- `semantic_contamination_screen_verified`

The names above are unsatisfied preconditions. The branch-level preflight is less strict than the final PR #69 runner and must not be treated as the complete training authorization check.

## Final runner gate

Draft PR #69 contains the fail-closed weight-changing runner:
`successor/experiments/train_v10_qwen35_authorized.py`

Before any training stack is loaded/executed, the final runner requires a READY preflight. The execution body then additionally verifies:

- exact experiment contract
- exact execution spec
- exact train/validation bytes and row counts
- exact live runtime/packages/base artifacts
- exact Qwen3.5 topology
- every train/validation sample <=512 tokens
- exact sealed final-bank commitment
- exact training authority receipt
- exact unused output namespace

Only then does it create `RUN_STARTED.json` and begin one QLoRA run.

A failure after `RUN_STARTED.json` produces `RUN_FAILED.json` with `retry_authorized=false`.

## Current true blockers

### Retention
Finish Architecture V7 and either:
- admit the Candidate V3 retention bank, or
- preserve HOLD and repair in a new lineage.

### Behavioral/adversarial final bank
Draft PR #68 still has unbound custody requirements:
- synthetic custodian A identity
- synthetic custodian B identity
- genuine human-author identity
- independent human-reviewer identity
- independent custody/evaluation surface
- access-control receipt

Those cannot be fabricated by the training lane.

### Full final-bank freeze/admission
After all three lanes are admitted:
- materialize exact behavioral/adversarial/retention data + manifests
- run the frozen semantic contamination screen
- produce independent-admission evidence
- freeze the final-bank manifest/commitment
- bind hashes back into the experiment subject without post-result tuning

### Weight-change authority
Training remains blocked until Patrick grants exact authority for:
- this exact experiment/training subject
- the exact execution-binding digest
- the exact output namespace
- the one fresh QLoRA run effect

This project state is not itself that authority.

## Ordering

`V7 RETENTION -> FINAL-BANK CUSTODY -> FULL 13,500 BANK FREEZE/SCREEN/ADMISSION -> SEALED COMMITMENT -> EXACT TRAINING AUTHORITY -> READ-ONLY PREFLIGHT READY -> ONE QLORA RUN -> POST-TRAIN DIAGNOSTICS -> FINAL ONE-SHOT EVALUATION`

## Hostile review

> **HOSTILE REVIEWER:** Retention auditing can become an infinite local optimization loop while the actual training critical path is blocked by independent human custody and full-bank admission.

**Accepted.** Retention must finish rigorously, but after V7 the highest-value frontier is the custody/final-bank gate, not another arbitrary retention methodology revision unless V7 finds a real defect.

> **HOSTILE REVIEWER:** Updating contract booleans to true because individual artifacts exist would be cargo-cult readiness.

**Accepted.** Preconditions may flip only when exact frozen evidence satisfies the named gate. Do not edit readiness flags optimistically.

## Claim ceiling

`TRAINING_CRITICAL_PATH_MAPPED / TRAINING_RECIPE_AND_SOURCE_SUBJECT_IDENTIFIED / RETENTION_NOT_TRAINING_DATA / FINAL_BANK_NOT_ADMITTED / TRAINING_NOT_AUTHORIZED / WEIGHTS_UNCHANGED`
