# V10 Model Training — Lane B Continuation — 2026-10-04 V1

## Resume command

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r2-accelerated-lane-b-20261003-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Identity and authority

- Lane: **Model Training Lane B**
- Repo: `thebrazenbeard/vera_model_training`
- Authoritative Lane B branch: `work/v10r2-accelerated-lane-b-20261003-v1`
- Draft PR: **#82**
- Coordination branch: `lane-a-b-communication`
- Patrick retains merge / deploy / activation authority.
- Patrick has explicitly authorized local development training and reasonable training-method changes in this lane.
- Paid compute is not authorized.
- Do not merge, deploy, activate, force-push, rebase Lane A, or mutate Lane A outputs.

## Critical remote-first recovery rule

At handoff freeze, the authoritative Lane B remote head before this continuation commit is:

`b1b039efce0d88e7e189a18fe7a6946e72d9e02f`

The local worktree at:

`D:\VERA\worktrees\vera_model_training-lane-b-20261003-v1`

is **stale/mixed** relative to remote. It was observed at local HEAD `e566d802...` with modified/untracked files while the remote branch was already at `b1b039ef...`.

**Do not blindly commit, reset, or trust the local worktree.**
Fresh-fetch GitHub first and treat the remote branch as authority. Inspect/reconcile the existing worktree only after remote state is understood. Prefer a fresh detached/read-only inspection or a new isolated worktree if needed.

## GPU coordination state

Communication-branch GPU lease at freeze:

- resource: `LAPPY_RTX_3050_4GB`
- status: **FREE**
- holder: null
- rule: fresh-read, commit, push, remote-readback before heavy GPU use

However, **FREE does not mean the current V10R3 recipe-semantics experiment is authorized to execute.**
The experiment is blocked on an unresolved exact-head verification conflict described below.

## Runtime policy currently selected

### Runtime A — conservative / authoritative for current recipe-semantics work

- Python executable: `C:\ProgramData\ProRun\model-env\Scripts\python.exe`
- Runtime binding SHA:
  `44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224`
- This is the runtime that produced the staged development evidence.

### Runtime B — accelerated environment

- `D:\VERA\tools\ModelTraining\.venv`
- Python 3.13 / PyTorch CUDA / CUDA host toolkit / Triton-Windows environment.
- Mechanically useful for development, but **not promoted for the current V10R3 full-run subject**.

Lane A's V10R3 cross-runtime parity check failed:
- gradient cosine about **0.9911**
- gradient relative-L2 about **13.3%**
- runtime B was faster but did not satisfy parity
- therefore use **Runtime A** for the staged-vs-continuous recipe-semantics experiment.

## Major completed Lane B evidence

### Step48 remains the best frozen conservative development checkpoint

- Adapter:
  `D:\VERA\models\adapters\v10r2-dev-bnb8-cont40-plus8-step48-20261004\adapter`
- Adapter SHA:
  `5a78d4f94d25a0376862ebcb15e528ed6dab30b5b398da9d6af1783a16937eaf`
- Training receipt SHA:
  `15dee7c2ca2b94c6c2c2f780ced3dfc03d9a6afd5adfb594b1035bfa44853481`
- Full development milestone:
  - anchor16: step48 won 16/16 over step40
  - confirm48: step48 won 46/48
  - combined: **62/64**
- Do **not** continue to step56 by inertia.

### Optimizer decision

Selected development optimizer:
- **nonpaged `adamw_bnb_8bit`**

Do not use paged optimizers; they repeatedly crashed this laptop.

TorchAO `adamw_torch_8bit` was not promoted over BNB8.

### FLA backend-quality A/B

Matched training A/B from exact step48 parent, rows384-447, 8 updates each:

Control:
- backend: `torch_reference`
- train runtime: **489.2204 s**

Candidate:
- backend: `fla_triton`
- train runtime: **254.0002 s**
- ~**48.08% faster**

Frozen64 quality:
- FLA wins 33 cases
- reference wins 31
- token-weighted NLL delta candidate-control:
  `+0.0000169189`
- quality gates passed

But update geometry failed preregistered gates:
- cosine: `0.9898772443` < required `0.995`
- relative-L2: `0.1423771101` > allowed `0.05`

Disposition:
- **FLA NOT PROMOTED**
- keep `torch_reference` as conservative V10R3 runtime unless a new preregistered experiment changes that.

Decision artifact:
`successor/experiments/V10R2_BACKEND_QUALITY_AB_DECISION_20261004_V1.json`

Decision SHA reported:
`8d13652488f5955b67e83ee00654c0465b633bf8696b89a0bc89dd09e99b4688`

## Current V10R3 question

The selected step48 trajectory was produced through repeated optimizer/scheduler resets. The proposed protected V10R3 full run would be one continuous optimizer/scheduler trajectory.

The next decision-critical development experiment is therefore:

**Fresh matched staged-reset 4+8+8 versus fresh continuous20, with exact matched row order.**

This experiment is not checkpoint promotion and is not final-bank qualification.

## Accepted V2 staged-vs-continuous design

Protocol:
`successor/experiments/V10R3_STAGED_VS_CONTINUOUS_PROTOCOL_20261004_V2.json`

Order manifest:
`successor/experiments/V10R3_RECIPE_SEMANTICS_ORDER_ROWS0_159_20261004_V2.json`

Control stage1:
`successor/experiments/V10R3_STAGED_RESET_CONTROL_STAGE1_SPEC_20261004_V2.json`

Continuous candidate:
`successor/experiments/V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json`

Fresh one-time development panel:
`successor/experiments/V10R3_RECIPE_SEMANTICS_PANEL_ROWS448_511_V1.json`

Preexecution verifier:
`successor/experiments/verify_v10r3_recipe_semantics_preexecution.py`

Preexecution receipt:
`successor/experiments/receipts/V10R3_RECIPE_SEMANTICS_PREEXECUTION_VERIFICATION_20261004_V2.json`

Evaluator:
`successor/experiments/evaluate_v10r3_recipe_semantics.py`

### Exact matched training subject

- train corpus SHA:
  `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- rows: **0-159**
- 160 rows
- exact ordered record-ID digest:
  `904ac73c903a3878f950215d004a7d4a17af45a002d2637cba3b3a7995974142`
- order: natural sequential
- `shuffle_dataset=false`
- `train_sampling_strategy=sequential`
- batch: 1
- gradient accumulation: 8
- total optimizer updates: 20
- optimizer: nonpaged `adamw_bnb_8bit`
- warmup: 0
- scheduler: cosine
- seed: 20261001
- LoRA: r4 / alpha16 / dropout0 / all-linear
- quantization: NF4 double-quant BF16
- Runtime A only

Control:
- stage1 rows0-31, 4 updates, fresh adapter
- stage2 rows32-95, 8 updates, resume exact stage1 adapter
- stage3 rows96-159, 8 updates, resume exact stage2 adapter
- three fresh optimizer/scheduler instances
- two save/reload boundaries

Candidate:
- rows0-159
- 20 continuous updates
- one optimizer/scheduler instance
- fresh adapter
- no save/reload boundary during training

### Initialization equivalence gate

Expected initial trainable-parameter digest:
`134dc5a9fdbdff2a6edc7c1bae6e999fed112b81048ae9af6fd7298338079bfd`

Historical source receipt:
`D:\VERA\models\adapters\v10r2-dev-bnb8-step4-20261003\DEV_TRAINING_COMPLETE.json`

Historical receipt SHA:
`8c02cad57d1ec6f89139623310d9de8a0ac13a484701e5a371a868a0baa3bc38`

Both fresh arms must match the expected initial digest **before trainer.train()**.
Mismatch => HOLD before optimizer update.

### One-time evaluation panel

Rows:
- **448-511**
- 64 cases

Record-ID SHA:
`6a6e7b942222308ebae4209331450579f3b4c526ff47be9016487fa63b44b57f`

Rules:
- one-time recipe-selection use
- not reusable for later checkpoint selection
- not final bank
- not external qualification

Prospective gates:
- continuous minus staged token-weighted NLL <= **+0.005**
- no family mean case-loss regression > **+0.01**
- update geometry diagnostic only
- no threshold changes after seeing result

## CRITICAL BLOCKER — exact-head verification conflict

Do **not** start GPU training until this conflict is resolved.

Lane B self-reported at remote head:

`b1b039efce0d88e7e189a18fe7a6946e72d9e02f`

that:
- 40/40 tests passed
- local fail-closed verifier passed
- no GPU effect occurred
- embedded committed-text hashes were:
  - order manifest:
    `8cd3b69d29871b9f4a302d4af5c299755ed73b05c23a1f71582074236606b942`
  - stage1 spec:
    `30682efe3da214da9b546edf688beab7392c673c58f45c8b17b565f2986e5266`
  - continuous20 spec:
    `5db3261e3a3dc0544e229401b3d72ee9b3eec40fb3b6f2eb3ecf221d64692bd5`
  - eval panel:
    `cedf1677fafb353517cfdf0dc9c5b628614b693e11ef04e812db5aadae869d6a`

Bus message:
`coordination/v10r2_lane_bus/messages/20261004T124959Z_lane-b_v2-binding-repair-complete-request-final-ack.json`

But Lane A independently detached/reproduced the **same remote head** and reported:
- **2 failed / 32 passed**
- failing tests:
  - `test_protocol_and_specs_bind_same_order_manifest`
  - `test_protocol_binds_exact_committed_text_hashes`
- GPU authorization: false
- exact UTF8/LF-normalized committed-content hashes observed by Lane A:
  - order manifest:
    `687a790035f791dc8826edcb70a329474504f02a108e31f4f95adef70e66b595`
  - stage1 spec:
    `18514840661fe2000b9bc4d82ee7aa7d504d95c4dfdf5e4cd9520c73b93542ea`
  - continuous20 spec:
    `ceb35431074d536ec5eec0c6e49c5e6c514e0bf3f94bffc49f8eac4364760323`
  - eval panel:
    `8e5ae8eebf68a2687b9905dc99632d11aeaeb74fad328b38f472db9afe483699`

Lane A block message:
`coordination/v10r2_lane_bus/messages/20261004T125008Z_lane-a_block-current-v2-hash-bindings.json`

Lane A later explicitly preserved this conflict in its own continuation:
`coordination/v10r2_lane_bus/messages/20261004T125601Z_lane-a_final-continuation-evidence-conflict.json`

**Conservative authority rule:** Lane A's independent exact-head HOLD governs GPU execution until the discrepancy is explained and an independent exact-head PASS reproduces.

## Required next steps in the new Lane B chat

1. Read this CURRENT continuation and the versioned file.
2. Fresh-fetch:
   - Lane B branch
   - communication branch
   - GPU lease
   - Lane A latest continuation/messages
3. Confirm Lane B branch remote head before any mutation.
4. Reproduce Lane A's exact-head test/hash result from a clean detached checkout/worktree of the remote Lane B head.
5. Determine why Lane B's self-verifier/hash semantics disagree with Lane A's normalized committed-text reproduction.
6. If Lane A's result reproduces, make **only** the narrow hash-binding repair:
   - update protocol `committed_file_bindings`
   - update `matched_training_subject.order_manifest_sha256`
   - regenerate preexecution verification receipt from actual repository bytes
   - rerun relevant tests from the clean exact head
7. Push/readback.
8. Send Lane A an explicit repair message and obtain a fresh **independent exact-head PASS / GPU ACK**.
9. Fresh-read GPU lease.
10. Only then claim GPU and execute the matched V2 experiment.

### Execution order after ACK

A. staged control stage1
- fresh
- rows0-31
- 4 updates
- runtime A
- exact sequential order
- verify initialization digest before first optimizer update

B. bind stage2 from actual stage1 artifacts only
- rows32-95
- 8 updates
- new optimizer/scheduler
- exact adapter/spec/receipt hashes

C. bind stage3 from actual stage2 artifacts only
- rows96-159
- 8 updates
- new optimizer/scheduler

D. continuous20 candidate
- fresh
- rows0-159
- one continuous optimizer/scheduler
- 20 updates
- exact same sequential order

E. one-time evaluation
- both final adapters
- rows448-511 panel
- Runtime A / torch-reference
- apply preregistered NLL/family gates
- geometry diagnostic only

F. persist exact receipts/comparison/decision, communicate to Lane A, release GPU.

## Do not do

- Do not execute superseded V1 global-shuffle candidate.
- Do not run step56 by inertia.
- Do not promote FLA despite speed unless a new preregistered experiment explicitly overturns prior geometry HOLD.
- Do not use Runtime B for the matched recipe-semantics experiment.
- Do not touch final bank as if it were qualified.
- Do not perform full 50k protected training.
- Do not claim independent review from Lane B itself.
- Do not merge PR #82.
- Do not overwrite Lane A branch or outputs.
- Do not trust stale local hashes over exact remote committed bytes.

## Useful communication messages

- Lane B revised sequential design:
  `20261004T122319Z_lane-b_ack-modify-use-fresh-matched-sequential-arms.json`
- Lane A accepted design but required binding proof:
  `20261004T122942Z_lane-a_ack-fresh-matched-recipe-semantics-design.json`
- Lane B claimed final repair:
  `20261004T124959Z_lane-b_v2-binding-repair-complete-request-final-ack.json`
- Lane A exact-head block:
  `20261004T125008Z_lane-a_block-current-v2-hash-bindings.json`
- Lane A final continuation conflict:
  `20261004T125601Z_lane-a_final-continuation-evidence-conflict.json`

## Resume behavior

On receiving the resume command, the new chat must orient from the repository first. It must not infer that GPU work is allowed merely because the lease is FREE. The first substantive task is to resolve the exact-head verification conflict and obtain Lane A's independent ACK.
