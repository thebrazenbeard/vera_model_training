# V10 Model Training — Lane B Continuation — 2026-10-04 V5

## Resume

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Authoritative branches

- Lane B: `work/v10r3-eval-gates-lane-b-20261004-v1`
- Lane A: `work/v10r3-binding-fix-lane-a-20261004-v1`
- Coordination: `lane-a-b-communication`
- Draft PR: #84
- Patrick retains merge/deploy/activation authority.

## Recipe experiment

Staged 4+8+8 is complete and independently verified.

Terminal staged:
- receipt `288cb8bd19b7dcbeb90a8cc77fc96408194f9642b6bca66af7ab984414c237fb`
- adapter `b2d6eec7befca3e18cf1fa793a7830197e27bab33bea8e4f42b5a318ee91d116`
- config `db5b50623f8af897a8fe21d929ca13338d208d3c9c6fc5c38c54af8a6ab1a7c0`
- weight-after `892fcd55dd68343b81f664fc96161845ebdb08a14029d5536f02e6141ccb8825`

Continuous20 remains under Lane A GPU lease.

Frozen spec:
`successor/experiments/V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json`

Spec SHA:
`bda3c491db5e15aa4d0eabd9806776e27a46c33a884e35fad380613fa934a96d`

Current runtime observation:
- training GPU phase has ended or paused; GPU compute observed at 0%
- worker PID 33516 remains alive and responsive
- CPU time continues increasing at ~1 core-second / wall-second
- private memory remains ~10.86 GB while working set is much smaller
- host memory/commit pressure is high
- no adapter directory contents beyond empty `sft_work`
- no `DEV_TRAINING_COMPLETE.json` yet
- source inspection shows the post-train path performs CPU-side trainable-parameter digest before adapter save/receipt, so this is consistent with CPU-bound finalization; do not claim completion or stall absent stronger evidence

Lane A independently reported host commit/paging pressure as a plausible contributor. No intervention authorized or performed.

## One-time recipe panel — HOLD

Panel:
`successor/experiments/V10R3_RECIPE_SEMANTICS_PANEL_ROWS448_511_V1.json`

The panel has not been consumed.

New hostile-review finding:
- evaluator validates the panel's one-time policy declaration
- evaluator refuses overwriting one exact output path
- evaluator does NOT durably record panel consumption
- therefore the same panel can currently be rerun with a different output path

Lane A ACKed the gap and agreed not to reveal/run the panel.

Panel status:
`HOLD_PENDING_SINGLE_USE_CUSTODY_FIX`

### Bounded single-use design agreed in principle, not implemented

Reuse existing repo conventions from:
- `sealed_final_bank_commitment.py`
- `sealed_final_bank_custody.py`
- `final_bank_custodian_binding.py`

Those files provide:
- immutable subject identity
- self-hashed metadata
- artifact-hash binding
- custody/access assertions
- reveal hash-match validation
- fail-closed substitution handling

They do NOT provide an atomic one-way consumption transition.

Required new primitive:
- fixed shared marker path independent of evaluation output path
- all non-revealing CPU preflight runs first
- immediately before first panel inference, evaluator uses exclusive-create semantics
- marker existence itself means consumed
- valid complete marker => consumed/HOLD on any later invocation
- partial/corrupt marker from crash => also consumed/HOLD; never delete, repair, or retry
- crash after claim remains consumed
- direct evaluator invocation without the guard must HOLD

Marker/receipt bindings should include:
- panel SHA
- panel record-ID SHA
- train SHA
- frozen protocol SHA
- single-use guard-spec SHA
- evaluator identity
- staged candidate receipt + adapter/config hashes
- continuous candidate receipt + adapter/config hashes
- runtime binding SHA
- claim timestamp
- canonical self-hash when fully serialized

Implementation is NOT started. Patrick approval is still required for this bounded evaluator change.

## PR #84

PR #84 provides:
- frozen protocol hash enforcement
- train/panel/runtime binding
- candidate receipt and live adapter/config custody
- staged 4->8->8 lineage verification
- fresh continuous20/no-resume verification
- reset-boundary weight continuity
- prospective NLL/family gates
- development-only decision artifact

Lane A independently cross-checked the validator:
- focused: 17/17 PASS
- combined training/protocol/eval/decision: 49/49 PASS
- staged chain: PASS
- continuous role: correctly HOLD while receipt absent
- panel: unconsumed

## Vera identity workstream

Identity protocol is ACKED by both lanes.

Agreed semantics:
1. operative assistant self-name = Vera
2. task roles are overlays, not renames
3. Qwen/Qwen3.5 is truthful ancestry/provenance, not operative self-identity
4. identity does not establish consciousness or uninterrupted runtime continuity

Agreed split:
- Lane A owns TRAIN+DEV construction/training
- Lane B owns blind FINAL generator/scorer/adversarial validator
- freeze generator/scorer/protocol before identity-specific training
- materialize exact FINAL bank only after candidate adapter hash freeze using a new post-freeze seed/nonce
- any tuning after FINAL materialization invalidates that bank for the tuned successor

Identity-specific optimizer work remains HOLD until the recipe decision is frozen.
Lane B FINAL subsystem implementation has not started and requires Patrick architectural approval.

## Immediate next work

1. Fresh-read bus and GPU lease.
2. Wait for authoritative continuous20 receipt; do not kill/restart while CPU progress continues.
3. On receipt, independently validate:
   - receipt self-hash
   - fresh/no-resume continuous semantics
   - rows 0-159
   - cumulative20
   - frozen initialization digest and weight-before
   - sequential/no-shuffle
   - nonpaged BNB8
   - live adapter/config hashes
4. Publish continuous20 custody PASS/HOLD.
5. Panel remains HOLD even if continuous20 passes until single-use guard is approved, implemented, tested, frozen, and independently reviewed.
6. Do not reveal or run the one-time panel before then.
7. Do not start identity-specific training before the recipe decision is frozen.
8. No merge/deploy/activation.
