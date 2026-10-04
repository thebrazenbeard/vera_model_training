# V10 Model Training — Lane B Continuation — 2026-10-04 V8

## Resume

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Stable evidence

- staged 4+8+8 arm: COMPLETE / independently verified
- original continuous20: FAILED after 4/20 optimizer steps with source-bound CUDA OOM
- original V10R3 semantic experiment: `EXECUTION_HOLD_UNRESOLVED`
- no recipe winner claimed
- failed namespace preserved
- failed process cleaned
- GPU returned to 0 MiB
- Lane A GPU lease formally RELEASED at `2026-10-04T15:32:18Z`
- one-time 64-case panel remains unconsumed and HOLD

## V10R3R1 preregistration

Lane A authority repair head:
`6316c6f4a174d1c2b45240e438cf8a95ff5c19c0`

Authority repair PASS:
- replication spec status = `PREREGISTERED_NO_EXECUTION_AUTHORITY`
- spec source = `COORDINATION_AND_PREREGISTRATION_ONLY`
- spec scope = `V10R3R1_PREREGISTRATION_ONLY`
- execution_authority_required = true
- protocol development_training_authorized = false
- protocol current_authority = `COORDINATION_AND_PREREGISTRATION_ONLY`
- `load_and_validate_dev_spec` now fail-closes before training
- new TDD authority test reported red against old metadata, green 1/1 after repair
- recipe projection remains matched to failed continuous V2

## Remaining preregistration HOLD

The protocol's `replication.spec_sha256` was not updated when the spec file was neutralized in `6316c6f...`.

Because the spec content changed while the bound digest did not, the protocol references an obsolete pre-repair file image.

Status:
`HOLD_STALE_PREREG_TEMPLATE_BINDING_NO_EXECUTION`

Required repair:
1. Treat the current non-executable R1 spec as immutable preregistration recipe template.
2. Recompute and bind its committed-content SHA.
3. State explicit hash semantics; use `UTF8_TEXT_LF_NORMALIZED_COMMITTED_CONTENT` for consistency with V10R3.
4. Add a test/verifier that recomputes exact committed template binding.
5. Do not later mutate the prereg template into executable authority.
6. Only after Patrick explicitly authorizes R1, create a distinct execution-spec path.
7. Verify the future execution spec recipe/output/replication projection exactly matches the frozen template/protocol while authority fields are the intended execution-enabling delta.
8. Fresh-claim GPU lease only after that verification.

Lane B message:
`20261004T153300Z_lane-b_v10r3r1-template-binding-stale-hold.json`

## R1 recipe/governance already accepted

Except for the stale binding above, Lane B accepts the preregistered design:
- predecessor OOM evidence preserved
- original-spec retry prohibited
- new namespace
- attempt limit 1
- fresh process / fresh adapter
- no resume
- exact source/train/order/seed/optimizer/scheduler/batch/GA/maxlen/checkpointing/quantization/LoRA/init/runtime semantics
- preflight process/GPU/host/runtime observations
- no allocator / empty-cache / offload / trainer recipe change
- panel use prohibited
- immutable staged control context only
- success/failure disposition preserves semantic uncertainty

## Panel

Panel remains:
`HOLD_UNCONSUMED_SINGLE_USE_GUARD_MISSING`

Atomic consume-before-inference design exists but implementation has NOT started and requires Patrick approval.

## Identity

Vera identity protocol is ACKED by both lanes.

Identity-specific training remains HOLD until recipe execution decision is frozen.
Lane B FINAL generator/scorer implementation has not started and requires Patrick architectural approval.

## Immediate next work

1. Fresh-read Lane A branch and coordination branch.
2. Verify stale R1 template hash binding repair.
3. Do not execute R1 without Patrick explicit new execution authority.
4. Do not consume panel until single-use guard is approved/implemented/tested/frozen.
5. Do not start identity-specific optimizer work before recipe execution decision.
6. No merge/deploy/activation.
