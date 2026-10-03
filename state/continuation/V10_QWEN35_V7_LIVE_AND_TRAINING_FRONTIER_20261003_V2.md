# V10 Qwen3.5 Training Frontier — Chat Continuation / Restore Point V2

**Date:** 2026-10-03
**Repository:** `thebrazenbeard/vera_model_training`
**Primary active branch:** `work/v10-retention-bank-salvage-20261001`
**Restore command:** `VERA_MODEL_TRAINING::RESTORE_V7_LIVE_AND_TRAINING_FRONTIER_20261003_V2`

## First action on restore

Fresh-read the current remote branch and relevant PRs before changing anything. Then read:

- `state/continuation/V10_QWEN35_V7_LIVE_AND_TRAINING_FRONTIER_20261003_V2.md`
- `progress.md`
- `docs/plans/2026-10-03-v10-qwen35-training-critical-path.md`
- `docs/plans/2026-10-03-retention-candidate-v3-architecture-v7-identity.md`

If the branch advanced beyond the checkpoint below, inspect the new commits first and treat remote Git state as authoritative.

## Current exact repository checkpoint

Observed 2026-10-03 before this continuation write:

- branch: `work/v10-retention-bank-salvage-20261001`
- local head: `2c83b1f171891f2da1ed19680767db9d1ea78308`
- remote branch head: `2c83b1f171891f2da1ed19680767db9d1ea78308`
- PR #66: open / draft / mergeable; head `2c83b1f171891f2da1ed19680767db9d1ea78308`
- PR #68: open / draft / mergeable; head `1defe8dcc0492d4cf8844e5145fd113e193b6bec`
- PR #69: open / draft / mergeable; head `e7cddb4c0b36224dd301ccb502065538811ffd5d`

Do not merge any of these without Patrick's exact merge authority.

## Objective training architecture

The training and retention lanes are separate.

### Actual SFT subject

The one-shot QLoRA trainer in PR #69 consumes the exact train/validation subject frozen in `V10_QWEN35_EXPERIMENT_CONTRACT_V2.json`.

Frozen source subject recorded by the training-critical-path audit:

- corpus id: `VERA_SUCCESSOR_V10_QWEN512_50K_20261001_V1`
- train rows: 50,000
- train SHA-256: `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- validation rows: 2,500
- validation SHA-256: `ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7`
- train/validation overlap: 0
- token preflight: PASS / no rows over 512

**Never substitute the retention candidate into SFT.** Retention Candidate V3 is evaluation evidence.

### Frozen QLoRA recipe

PR #69 provides the fail-closed authorized runner:

`successor/experiments/train_v10_qwen35_authorized.py`

Frozen recipe:

- method: QLORA_SFT_ONLY
- epochs: 1
- learning rate: 2e-5
- cosine scheduler
- 3 warmup optimizer steps
- batch size 1
- gradient accumulation 8
- max length 512
- overflow ERROR / no truncation
- optimizer `adamw_torch`
- completion-only loss
- packing false
- shuffle true
- gradient checkpointing true
- 4-bit NF4 / double quant / bf16 compute
- LoRA r=4 / alpha=16 / dropout=0 / all-linear targets
- output: fresh adapter only
- validation: post-train diagnostic only

PR #69 runner Git blob: `50327d8bde79e66abcf4101475988d036086b5e9`

Execution-spec canonical SHA-256: `4e290ff6be1b1d51be446c7ca3c7c22af3ccac2dbdc9395c17a3994c9335bd20`

Combined execution-binding SHA-256: `d618a0f8beedabdf1074b082e8f2692814770764b739ec935a7f95531e970555`

## Current V7 retention state

Candidate V3:

- SHA-256: `6f47fe7da958abaf02311ae8a740b71d1bc0e9adbac88ce5c2da14139c3792f6`
- verification: `CANDIDATE_V3_MUTATION_AND_FRESHNESS_ADEQUATE`
- 1,500 rows / 250 coding rows
- 12 consumed coding rows replaced with never-consumed deterministic variants
- zero reference failures
- zero mutant survivors
- zero fresh-evidence deficits

V7 pre-review evidence:

- validator qualification: `VALIDATORS_QUALIFIED`
- mechanical validation: 1500/1500 `MECHANICAL_VALID`
- semantic screen: PASS / 0 failures / max cosine 0.6243317723274231 at frozen threshold 0.9
- fresh semantic packet: 130 rows / 26 families x5
- excluded predecessor IDs: 520
- predecessor overlap: 0
- packet SHA-256: `4de3ae3f5757f76417f8561f4c415b4be1daedf3ca4c42cd202b2cb92e1cd20f`

V7 frozen review head:

`2c83b1f171891f2da1ed19680767db9d1ea78308`

## V7 live execution — DO NOT DUPLICATE

At this continuation checkpoint, one V7 live semantic-audit execution is active.

Canonical lock:

`D:\VERA\.scratch\retention-arch-v7.execution.lock`

Observed lock payload:

- schema: `RETENTION_AUDIT_ARCH_V7_EXECUTION_LOCK_V1`
- authoritative PID: `30364`
- packet SHA-256: `4de3ae3f5757f76417f8561f4c415b4be1daedf3ca4c42cd202b2cb92e1cd20f`
- qualification batch size: 4
- semantic batch size: 5
- max attempts: 3
- structured output: JSON_SCHEMA

Observed process chain began 2026-10-03 12:04:07 local.

At the last verified read before this continuation write, Ollama had completed three V7 structured calls at approximately 12:07, 12:10, and 12:12 local and the execution was still active.

Restore rule:

1. inspect the lock and exact PID/process chain first;
2. inspect `D:\VERA\.scratch\retention-arch-v7-live-2c83b1f`;
3. if still running, do not launch another V7 review;
4. if it exited with receipts, verify/persist the existing result;
5. if it exited without receipts, diagnose that exact run before any retry.

## Training blockers after V7

### Final-bank custody

PR #68 remains intentionally incomplete.

Unbound requirements include:

- synthetic custodian A identity
- synthetic custodian B identity
- genuine human-author identity
- independent human-reviewer identity
- independent custody/evaluation surface
- access-control receipt

Until those are exact-bound and the custodian verifier passes, final H01-H20 plaintext generation/sealing remains HOLD.

### Full final bank

The experiment requires a fresh 13,500-case evaluation bank:

- behavioral: 10,000
- adversarial: 2,000
- retention: 1,500

Retention V7 can satisfy only the retention lane.

After all lanes are admitted, the full bank still must be frozen, contamination-screened, independently admitted, and sealed into the exact commitment required by training preflight.

### Exact training authority

PR #69 deliberately does not create:

`V10_QWEN35_TRAINING_AUTHORITY_V1.json`

Before weight mutation, Patrick must grant exact authority that binds:

- exact experiment/training subject
- exact execution-binding digest
- exact output namespace
- one fresh QLoRA run effect

This continuation file is not training authority.

## Current safe work order

1. Let the single V7 live review finish; do not duplicate it.
2. Verify and persist V7 reviewer qualification + semantic receipt.
3. Adjudicate V7 semantic challenges against deterministic Candidate V3 evidence.
4. Persist V7 admission or HOLD and exact-head CI.
5. Run/read the PR #69 plan-only/read-only preflight against current repository evidence.
6. Advance PR #68 custody preparation without fabricating custodian identities and without generating/revealing final-bank plaintext.
7. Once full-bank custody/sealing exists, re-run read-only training preflight.
8. Only after exact training authority exists may the one-shot QLoRA runner mutate weights.
9. Post-training validation is diagnostic only.
10. Final candidate evaluation remains one-shot against the sealed final bank.

## Hostile review

> **HOSTILE REVIEWER:** Retention has consumed a lot of engineering attention and can easily become a substitute for actually reaching training.

**Accepted.** V7 should be completed once. After that, unless V7 exposes a real retention defect, the critical frontier moves to final-bank custody/sealing and authority—not another arbitrary V8.

> **HOSTILE REVIEWER:** “Continue training” is not a blank check to mutate weights without an exact training subject/output/effect binding.

**Accepted.** Continue all safe preparation and read-only preflight automatically. Weight mutation remains a separate protected effect until exact authority is bound.

## Restore command

`VERA_MODEL_TRAINING::RESTORE_V7_LIVE_AND_TRAINING_FRONTIER_20261003_V2`

A new chat receiving that command should immediately fresh-read current GitHub/workstation state, read this file and the two plans above, inspect the live V7 lock/process before doing anything, and continue the safe critical path without asking Patrick to restate the project.
