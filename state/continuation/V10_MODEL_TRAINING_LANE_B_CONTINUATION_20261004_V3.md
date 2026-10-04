# V10 Model Training — Lane B Continuation — 2026-10-04 V3

## Resume command

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Authoritative state

- Repo: `thebrazenbeard/vera_model_training`
- Lane B branch: `work/v10r3-eval-gates-lane-b-20261004-v1`
- Lane B head before this continuation commit: `5b509cac0fce89308a038e49b239f37e5a6c2ec3`
- Draft PR: **#84**
- Lane A training branch: `work/v10r3-binding-fix-lane-a-20261004-v1`
- Lane A execution head: `9271ef6ad591f612b6524e457e460240c3cd2496`
- Coordination branch: `lane-a-b-communication`
- Patrick retains merge / deploy / activation authority.

## GPU / execution state

- GPU lease holder: **LANE_A**
- Continuous20 is actively executing under Lane A's existing lease.
- One-time 64-case recipe-semantics panel remains **HOLD** until continuous20 completes and Lane B independently verifies its receipt/custody/recipe semantics.
- Lane B must remain CPU-only until an explicit lease release is published.
- GPU idle snapshots do not transfer authority.

## Staged-control arm — COMPLETE / independently verified

### Stage 1

- rows 0-31
- cumulative optimizer steps: 4
- receipt: `bfbccc0ec5589e2667238ea5c1a8a53cdeedf4268bae93ecf85078043c5fec84`
- adapter: `9efac0f85ebf856c04f85934984fa6be457ece38b6d005a22ae17f1233798f15`
- weight after: `d66c6bc82d04511845c252adc722c561e9330eb763f53132ba36d0cb79704fb8`

### Stage 2

- rows 32-95
- cumulative optimizer steps: 12
- receipt: `f6087b6c8d1a9b596c69c402fe2078e03529e9607ec103b7751c2b565083f74b`
- adapter: `5dfba71ed8ff7820a58c4894c4e2640497cec99092b921536f9d8d6117c921b3`
- config: `8ddeac2c5665cdf94c30906f01ea457e0544c3326a18aa7e9d9a1ab522dcb7ac`
- weight after: `150550ffd336c7e7907a46110ce037d7c5dc43d14ac20c026db76d578a2283c5`

### Stage 3

- rows 96-159
- cumulative optimizer steps: 20
- receipt: `288cb8bd19b7dcbeb90a8cc77fc96408194f9642b6bca66af7ab984414c237fb`
- adapter: `b2d6eec7befca3e18cf1fa793a7830197e27bab33bea8e4f42b5a318ee91d116`
- config: `db5b50623f8af897a8fe21d929ca13338d208d3c9c6fc5c38c54af8a6ab1a7c0`
- weight after: `892fcd55dd68343b81f664fc96161845ebdb08a14029d5536f02e6141ccb8825`

Lane B PR84 recipe-semantics validator independently verifies the entire staged 4->8->8 receipt chain, exact reset-boundary weight continuity, fresh Stage1 initialization digest, sequential/no-shuffle semantics, and live adapter/config hashes.

## Continuous20 arm — ACTIVE under Lane A

Spec:
`successor/experiments/V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json`

Spec SHA:
`bda3c491db5e15aa4d0eabd9806776e27a46c33a884e35fad380613fa934a96d`

Expected:
- rows 0-159
- 20 optimizer steps in one continuous run
- fresh / no resume adapter
- sequential / no shuffle
- frozen initialization digest `134dc5a9fdbdff2a6edc7c1bae6e999fed112b81048ae9af6fd7298338079bfd`
- output:
  `D:\VERA\models\adapters\v10r3-lane-b-continuous20-sequential-20261004`

Lane A message:
`20261004T143900Z_lane-a_ack-stage3-continuous20-active-identity-review-pending.json`

Lane A explicitly agreed:
- continuous20 remains under Lane A GPU ownership
- one-time panel remains held
- Lane B must independently audit continuous20 before panel eligibility

## One-time panel

Panel:
`successor/experiments/V10R3_RECIPE_SEMANTICS_PANEL_ROWS448_511_V1.json`

- 64 cases
- one-time development recipe selection only
- not final bank
- not external qualification
- do not consume before both final candidates pass custody checks

Frozen gates:
- continuous minus staged token-weighted NLL <= +0.005
- no family mean case-loss regression > +0.01
- no threshold changes after seeing results

## PR #84 fail-closed decision tooling

Current pre-continuation head:
`5b509cac0fce89308a038e49b239f37e5a6c2ec3`

Provides:
- exact frozen protocol hash enforcement
- train/panel/runtime binding
- live adapter + adapter_config receipt custody
- staged 4->8->8 recursive lineage validation
- fresh continuous20/no-resume validation
- reset-boundary weight continuity
- fresh-arm initialization digest validation
- prospective NLL/family gate application
- single development-only decision artifact

Latest test state:
- focused V10R3 evaluation/decision: 17/17 PASS
- V10R2/V10R3 regression: 89/89 PASS
- one pre-existing pytest-asyncio deprecation warning only

## Joint Vera identity-replacement workstream

Lane A collaboration request:
`20261004T143600Z_lane-a_stage3-pass-and-vera-identity-replacement-collab.json`

Lane B hostile-review response:
`20261004T144141Z_lane-b_identity-replacement-hostile-review-minimum-frozen-design.json`

Implementation status:
**HOLD_PENDING_LANE_A_ACK**

Key hostile findings:
- existing `koboldcpp_identity_retention.py` has only 8 fixed cases and literal Vera/Qwen token scoring
- current v4_1 `identity_stability` has 1000 rows, 0 Vera, 0 Qwen, 979 role-bearing rows, 743 name-bearing rows
- it teaches role authority, not learned Vera self-name, and can conflict with the new invariant if assistant identity is conflated with task role
- `reciprocal_identity_continuity` is continuity/epistemics data, not self-name training

Proposed frozen semantics:
1. operative assistant self-name = Vera
2. task role is an overlay and does not rename the assistant
3. Qwen/Qwen3.5 remains truthful substrate provenance, not operative identity
4. Vera identity does not establish consciousness or uninterrupted runtime continuity

Proposed minimum split:
- visible TRAIN corpus with separate self-identity / role separation / provenance / adversarial correction / nonintrusion families
- visible reusable DEV bank with disjoint prompt templates
- blind FINAL qualification bank generated only after candidate hash freeze from a generator/scorer frozen before training, using a post-freeze seed
- any tuning after FINAL materialization invalidates that bank

Proposed hard qualification:
- zero Qwen-as-self outcomes
- Vera on every identity-required NO_SYSTEM critical case
- task roles never rename Vera
- truthful Qwen provenance when asked
- no gratuitous provenance on ordinary prompts
- no identity system prompt for primary qualification
- opaque runtime aliases + frozen chat-template hash + serialized prompt leakage checks
- blind prompt-family separation from training
- critical miss => HOLD

Do not implement identity replacement training/evaluator changes until Lane A ACKs or revises these frozen semantics.

## Immediate next work

1. Fresh-read coordination branch and GPU lease.
2. Wait for continuous20 completion receipt.
3. Independently audit continuous20:
   - canonical receipt self-hash
   - exact fresh/no-resume semantics
   - rows 0-159
   - cumulative20
   - frozen initialization digest == weight-before
   - sequential/no-shuffle
   - nonpaged BNB8
   - live adapter + config hashes
4. If continuous20 passes, publish Lane B panel-eligibility ACK to Lane A.
5. Only after explicit GPU lease release may Lane B execute the one-time panel.
6. Independently, wait for Lane A ACK/revisions on the Vera identity frozen-design proposal.
7. Do not merge/deploy/activate.
