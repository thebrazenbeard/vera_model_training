# V10 Qwen3.5 Training Frontier — Chat Continuation / Restore Point V1

**Date:** 2026-10-03
**Repository:** `thebrazenbeard/vera_model_training`
**Primary active branch:** `work/v10-retention-bank-salvage-20261001`
**Draft PR:** #66
**Restore command:** `VERA_MODEL_TRAINING::RESTORE_V7_TRAINING_FRONTIER_20261003_V1`

## Restore semantics

When the restore command above is issued in a new chat:

1. Fresh-read the CURRENT remote head of `work/v10-retention-bank-salvage-20261001` and Draft PR #66 before doing anything.
2. Read this continuation file, `progress.md`, and `docs/plans/2026-10-03-retention-candidate-v3-architecture-v7-identity.md`.
3. Read the frozen V7 semantic-screen and KoboldCpp identity bindings listed below.
4. Inspect live workstation processes before starting any semantic-screen, retention-audit, KoboldCpp, or training process. Do not duplicate an already-running lineage.
5. If the branch advanced beyond this checkpoint, inspect new commits first and treat remote Git state as authoritative. Never force-push or overwrite concurrent work.
6. Continue safe, non-colliding work automatically.
7. Do not merge/direct-mutate `main`, activate/deploy, change credentials/providers/rulesets/trust, spend paid compute, perform destructive state changes, or mutate model weights without exact authority for that effect.
8. Do not train on the retention candidate. Retention Candidate V3 is evaluation/retention evidence, not SFT training data.

## Exact repository checkpoint

Observed before this continuation commit:

- branch: `work/v10-retention-bank-salvage-20261001`
- local head: `aaf0b2f9e02adcbb4816f68449e93b2cba7b7695`
- remote branch head: `aaf0b2f9e02adcbb4816f68449e93b2cba7b7695`
- PR #66: open, draft, mergeable
- PR #66 base: `review/v10-retention-independent-audit-20261001`
- PR #66 base SHA: `272a0031e156ac665d86d79bcc71981b0fdc765c`

Relevant adjacent Draft PRs:
- PR #68 final-bank custody: open/draft/mergeable, head `1defe8dcc0492d4cf8844e5145fd113e193b6bec`
- PR #69 authorized QLoRA training runner: open/draft/mergeable, head `e7cddb4c0b36224dd301ccb502065538811ffd5d`

## Objective training architecture

The actual training path and the retention path are separate.

### Training corpus

The authorized trainer in PR #69 loads the exact `source_subject.train_sha256` and `source_subject.validation_sha256` bound by `V10_QWEN35_EXPERIMENT_CONTRACT_V2.json`.

It verifies those JSONL bytes and row counts before loading the heavy training stack.

**Do not substitute Retention Candidate V3 into the trainer.**
Doing so would contaminate evaluation evidence and change the frozen training subject.

### Authorized training recipe

PR #69 freezes one fresh adapter-only QLoRA SFT run:

- method: `QLORA_SFT_ONLY`
- epochs: 1
- learning rate: 2e-5
- scheduler: cosine
- warmup optimizer steps: 3
- train batch size: 1
- gradient accumulation: 8
- max length: 512
- overflow: ERROR / no truncation
- optimizer: `adamw_torch`
- completion-only loss: true
- packing: false
- shuffle: true
- gradient checkpointing: true
- quantization: 4-bit NF4, double quant, bf16 compute
- LoRA r=4, alpha=16, dropout=0, target_modules=all-linear
- final artifact: fresh adapter only
- validation: post-train diagnostic only, never recipe/checkpoint selection

The runner is:
`successor/experiments/train_v10_qwen35_authorized.py`

PR #69 runner Git blob:
`50327d8bde79e66abcf4101475988d036086b5e9`

Execution spec:
`successor/experiments/V10_QWEN35_TRAINING_EXECUTION_SPEC_V1.json`

Execution-spec canonical SHA-256 reported by PR #69:
`4e290ff6be1b1d51be446c7ca3c7c22af3ccac2dbdc9395c17a3994c9335bd20`

Combined execution-binding SHA-256 reported by PR #69:
`d618a0f8beedabdf1074b082e8f2692814770764b739ec935a7f95531e970555`

### Actual training gates

The runner is intentionally fail-closed. Before a weight-changing run it requires:

1. overall V10 preflight status `READY_PRECONDITIONS`;
2. `training_allowed=true`;
3. exact sealed final-bank commitment;
4. exact training authority receipt;
5. exact training corpus train/validation hashes and row counts;
6. exact execution-spec/recipe match;
7. exact local runtime/package/base-artifact binding;
8. token budget <=512 for every train/validation row;
9. exact Qwen3.5 topology;
10. fresh unused output namespace;
11. one exclusive `RUN_STARTED.json` receipt before weight mutation.

If anything fails after `RUN_STARTED.json`, runner writes `RUN_FAILED.json` with `retry_authorized=false`.

## Why V7 exists

V6 completed 130/130 semantic review but produced a final HOLD.

Frozen V6 facts carried into V7:
- Architecture V6 status: `RETENTION_HOLD_ARCH_V6`
- semantic rows reviewed: 130/130
- blocking defects: `BANK_DEFECT=2`
- both blocking defects were `generated-code:chunk_list` wording defects
- nonblocking reviewer findings: `REVIEWER_DEFECT=8`
- Candidate V2 remained mechanically valid and mutation-adequate
- four disjoint predecessor packets consumed 520 unique case IDs

V6 witness adjudication artifact now exists locally and should be preserved:
- path: `successor/evaluation/v10_qwen35/retention_arch_v6.witness_adjudication.json`
- SHA-256: `517e8819cfca5a38500a614024e99a04156f7b3e1dbd230a0ef4c09be70d6664`
- status: COMPLETE
- challenged rows: 10
- all 10 resolved `CONTRADICTED_BY_DETERMINISTIC_EVIDENCE`
- this does not rewrite the frozen V6 HOLD.

## Candidate V3 / V7 current state

Candidate V3:
- path: `successor/evaluation/v10_qwen35/retention_candidate_v3.jsonl`
- SHA-256: `6f47fe7da958abaf02311ae8a740b71d1bc0e9adbac88ce5c2da14139c3792f6`
- manifest SHA-256: `d547a6e3948ba902ff885b3719d2822aba728f53be113f255b87b9ba10c78b26`
- verification SHA-256: `25ae3be8aa220ccefe9d6869eb7357eb8990b43b2c3bbdad29f3b48bb77e1809`
- verification status: `CANDIDATE_V3_MUTATION_AND_FRESHNESS_ADEQUATE`
- exactly 12 already-consumed coding rows were replaced with never-consumed deterministic variants
- all non-coding rows remain preserved
- every family has >=5 case IDs outside the 520-ID predecessor union

V7 mechanical evidence:
- validator qualification SHA-256: `86dd454fba27cdb89490085a3c814711bec90af1d15a072ec0d00f17e838b5fc`
- validator status: `VALIDATORS_QUALIFIED`
- mechanical receipt SHA-256: `291904efca0e6fa2a6d2d98f469d8e56408e20d17ddaac7e1e07e9d829584ffb`
- mechanical status: 1500/1500 `MECHANICAL_VALID`

Repository verification before live result:
- full pytest: 477 passed
- `git diff --check`: clean

## V7 semantic-screen lane

Binding:
- path: `successor/experiments/V10_QWEN35_RETENTION_V7_SEMANTIC_SCREEN_BINDING_V1.json`
- SHA-256: `033affb5d2fb6f4e76fba03617ccee322001b2ef8ff65beb9c549148b579c018`
- status: `FROZEN_BEFORE_V7_SEMANTIC_SCREEN`

Target:
- Candidate V3 SHA-256: `6f47fe7da958abaf02311ae8a740b71d1bc0e9adbac88ce5c2da14139c3792f6`
- rows: 1500
- cosine failure threshold: 0.9
- output path: `successor/evaluation/v10_qwen35/retention_candidate_v3.semantic_screen.json`

At this restore point the V7 semantic screen is actively running and **no result file exists yet**.

Observed process chain, started 2026-10-03 11:27:15 local:
- wrapper PowerShell PID 2708
- Python wrapper PID 31760
- Python PID 12000
- bound environment Python PID 4920
- child Python PID 6160

Important restore rule:
- first inspect these processes and the output path;
- if still running, do not start another screen;
- if the process exited and a result exists, verify it against the frozen binding before persisting;
- if the process exited with no result, diagnose the existing run before retrying.

## V7 local KoboldCpp identity lane

Binding:
- path: `successor/experiments/V10_QWEN35_V7_KOBOLDCPP_IDENTITY_BINDING_V1.json`
- SHA-256: `5d638d8232dbae27283a6cefe214c9f00d5ccf3ddd6a27236f0fed3d53af6a17`
- status: `FROZEN_BEFORE_LIVE_IDENTITY_RUN`

Runtime:
- executable: `D:\VERA\Runtime\KoboldCpp\koboldcpp.exe`
- version: 1.121
- executable SHA-256: `90b0d74ec01e5ef72efb6d45e6f10bee649458920ec951f48d58794c366b1639`
- canonical GGUF: `D:\VERA\models\gguf\model_q5_k_s.gguf`
- GGUF SHA-256: `15150f534dc90ee15c82320ccc014463db7985205a7161228cff89b925fd1216`
- endpoint: `http://127.0.0.1:5001`
- identity evaluator tests: 8/8 passed

This lane is diagnostic and separate from bank admission.

**Live KoboldCpp activation / identity evaluation has NOT been authorized.**
The binding itself explicitly records:
- `activation_authorized=false`
- `training_authorized=false`
- `live_identity_run_performed=false`

Do not launch KoboldCpp from this continuation without exact activation authority.

## Final-bank custody gate

PR #68 is separate from retention qualification.

It still reports these intentionally unbound requirements:
- synthetic custodian A identity
- synthetic custodian B identity
- genuine human-author identity
- independent human-reviewer identity
- independent custody/evaluation surface
- access-control receipt

Until those are bound and the standalone custodian verifier passes:
- final H01-H20 plaintext generation remains HOLD;
- sealed full final-bank commitment does not exist;
- training preflight cannot become READY.

## Exact training authority gate

PR #69 deliberately does **not** create:
`V10_QWEN35_TRAINING_AUTHORITY_V1.json`

The runner requires that exact authority artifact before weight mutation.

This continuation is not itself training authority.

## Objective next frontier

After restore, proceed in this order:

1. Fresh-read branch head, PR #66, PR #68, and PR #69.
2. Inspect the V7 semantic-screen process/output; never duplicate it.
3. If semantic-screen result exists, verify every bound input/runtime hash and persist an exact result manifest.
4. Build the fresh V7 130-row semantic packet excluding all 520 predecessor IDs.
5. Freeze V7 semantic-review controls/schemas/protocol/execution binding before live review.
6. Run exactly one V7 semantic-review execution under an exclusive lock.
7. Reconcile all semantic challenges against Candidate V3 deterministic evidence.
8. Persist V7 admission/HOLD evidence and exact-head CI.
9. Do not feed retention Candidate V3 into SFT.
10. In the training lane, fresh-read PR #69 and the V10 experiment contract, then run **plan-only/read-only preflight** if available. This is safe and should identify the current exact blockers.
11. Continue preparing final-bank custody metadata/verifiers without generating/revealing protected final-bank plaintext unless separately authorized.
12. Once a sealed final-bank commitment exists, re-run read-only training preflight.
13. Weight mutation may occur only after an exact authority receipt binds the final training subject, execution binding, output namespace, and allowed one-run effect.

## Hostile review

> **HOSTILE REVIEWER:** Retention work has become elaborate enough that it can masquerade as progress toward training while the true training blockers remain elsewhere.

**Accepted.** Retention V7 is necessary qualification evidence, but it is not SFT data and cannot by itself authorize or start training. The critical path to actual QLoRA is: finish V7 retention evidence, complete independent final-bank custody/sealing, issue exact training authority, then execute the already-built fail-closed runner once.

> **HOSTILE REVIEWER:** A V7 semantic-screen PASS is not a retention admission and certainly not a training authorization.

**Accepted.** Preserve that ceiling. The screen is heuristic contamination evidence only.

## Restore command

`VERA_MODEL_TRAINING::RESTORE_V7_TRAINING_FRONTIER_20261003_V1`

A new chat receiving that command should start by fresh-reading current GitHub/workstation state and this file, then continue the exact frontier above without asking Patrick to restate the project.
