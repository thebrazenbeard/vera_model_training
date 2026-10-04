# V10 Model Training — Lane B Continuation — 2026-10-04 V9

## Resume

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Stable state

- Staged 4+8+8 completed and independently verified.
- Original continuous20 failed after 4/20 optimizer steps with source-bound CUDA OOM.
- Original V10R3 semantic experiment = `EXECUTION_HOLD_UNRESOLVED`.
- No recipe winner is claimed.
- Failed namespace and incident are preserved.
- Failed process lineage is cleaned.
- GPU memory returned to 0 MiB after cleanup.
- Lane A GPU lease is RELEASED.
- One-time 64-case panel remains unconsumed and HOLD.
- Vera identity protocol is ACKED by both lanes; identity-specific optimizer work remains HOLD.

## V10R3R1 replication preregistration — FROZEN / ACKED / NOT AUTHORIZED TO EXECUTE

Lane A exact head:
`24e78f4f18918959d53de886cc387e0f9169920e`

Files:
- `successor/experiments/V10R3R1_CONTINUOUS20_EXECUTABILITY_REPLICATION_SPEC_20261004_V1.json`
- `successor/experiments/V10R3R1_CONTINUOUS20_EXECUTABILITY_REPLICATION_PROTOCOL_20261004_V1.json`
- `tests/test_v10r3r1_prereg_authority.py`

Authority boundary PASS:
- prereg spec status = `PREREGISTERED_NO_EXECUTION_AUTHORITY`
- prereg source = `COORDINATION_AND_PREREGISTRATION_ONLY`
- execution_authority_required = true
- protocol development_training_authorized = false
- protocol current_authority = `COORDINATION_AND_PREREGISTRATION_ONLY`
- runner fail-closes before training
- no GPU lease is held

Recipe/governance PASS:
- source/train/order/seed/optimizer/scheduler/batch/GA/maxlen/checkpointing/quantization/LoRA/init/runtime preserved
- new namespace
- original failed namespace preserved
- original spec retry prohibited
- attempt limit 1
- fresh process and fresh adapter required
- resume forbidden
- panel prohibited
- no allocator / empty-cache / offload / trainer recipe mitigation
- staged control context-only
- success/failure dispositions preserve semantic uncertainty

Committed-template binding PASS:
- prereg template blob:
  `8c561cf6bccd2804b4a034291502d118b5f4542a`
- committed template line endings: LF-only
- independently recomputed SHA-256:
  `94e99e39d280a2cf99194f1a5a9d09b96b4f8c1140d59b4741d3ac2b13d4c660`
- protocol bound spec SHA matches exactly
- declared semantics: `UTF8_TEXT_LF_NORMALIZED_COMMITTED_CONTENT`

Non-blocking hardening note:
the test hashes raw committed bytes while labeling LF-normalized semantics. Current immutable blob is LF-only, so no current mismatch exists.

Lane B ACK:
`20261004T153656Z_lane-b_v10r3r1-prereg-frozen-ack-no-execution-authority.json`

## Execution authority

V10R3R1 is NOT authorized to run.

Patrick must explicitly authorize this new post-OOM replication before:
- materializing an executable R1 training spec
- claiming GPU
- starting any optimizer step

After explicit authorization:
1. create a distinct executable spec with current authority
2. verify its recipe/output/replication projection exactly matches the frozen prereg template/protocol
3. fresh-read and claim GPU lease
4. record required preflight
5. execute at most one attempt

## One-time panel

Panel status:
`HOLD_UNCONSUMED_SINGLE_USE_GUARD_MISSING`

Atomic consume-before-inference design exists but is NOT implemented.

Implementation requires Patrick approval of the bounded design.

No panel exposure is permitted before:
- guard implementation
- tests
- frozen guard spec
- independent review
- valid staged + continuous candidate path under an explicitly governed comparison

## Identity workstream

Vera identity protocol is ACKED by both lanes.

Identity-specific training remains HOLD until recipe execution decision is frozen.

Lane B blind FINAL generator/scorer subsystem has not started and requires Patrick architectural approval.

## Current user decisions required

1. V10R3R1:
   - authorize the frozen one-attempt exact-semantics replication, or
   - do not replicate and keep semantic comparison unresolved while treating staged 4+8+8 as the only demonstrated executable recipe on Runtime A.

2. Panel single-use guard:
   - approve implementation of the bounded atomic consume-before-inference guard, or
   - keep panel sealed/HOLD.

No merge / deploy / activation.
