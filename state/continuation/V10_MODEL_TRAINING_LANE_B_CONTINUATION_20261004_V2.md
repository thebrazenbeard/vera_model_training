# V10 Model Training — Lane B Continuation — 2026-10-04 V2

## Resume command

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Authority and current branches

- Lane: **Model Training Lane B**
- Repo: `thebrazenbeard/vera_model_training`
- Current Lane B branch: `work/v10r3-eval-gates-lane-b-20261004-v1`
- Current Lane B head before this continuation commit: `87a493b14637714ffc32e7eadf742d6463409af2`
- Draft PR: **#84**
- Lane A training branch: `work/v10r3-binding-fix-lane-a-20261004-v1`
- Lane A staged-control head last independently observed: `9271ef6ad591f612b6524e457e460240c3cd2496`
- Coordination branch: `lane-a-b-communication`
- Patrick retains merge / deploy / activation authority.
- Paid compute is not authorized.
- Do not merge, deploy, activate, force-push, rebase Lane A, or mutate Lane A outputs.

## GPU state at freeze

- GPU lease holder: **LANE_A**
- Resource: `LAPPY_RTX_3050_4GB`
- Stage 3 staged-control training is actively executing.
- Lane B must remain CPU-only until Lane A explicitly releases the lease through the coordination branch.
- A free-looking GPU process snapshot is not sufficient authority; fresh-read the lease before any heavy GPU action.

## V10R3 experiment subject

Decision-critical experiment remains:

**fresh matched staged-reset 4+8+8 versus fresh continuous20, exact sequential row order**

Frozen protocol:
`successor/experiments/V10R3_STAGED_VS_CONTINUOUS_PROTOCOL_20261004_V2.json`

Frozen LF-normalized protocol SHA:
`c206099a98cec088396d1090eb5733c1586c6ca357b6156a945c921093198c2f`

Matched subject:
- train SHA: `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- rows: `0-159`
- ordered record-ID SHA: `904ac73c903a3878f950215d004a7d4a17af45a002d2637cba3b3a7995974142`
- sequential / no shuffle
- batch 1 / gradient accumulation 8
- 20 total optimizer updates
- nonpaged `adamw_bnb_8bit`
- warmup 0 / cosine
- seed `20261001`
- QLoRA NF4 double-quant BF16
- LoRA r4 / alpha16 / dropout0 / all-linear
- Runtime A only: binding `44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224`

Frozen initialization digest:
`134dc5a9fdbdff2a6edc7c1bae6e999fed112b81048ae9af6fd7298338079bfd`

## Staged arm progress

### Stage 1 — COMPLETE / independently audited

Output:
`D:\VERA\models\adapters\v10r3-lane-b-staged-sequential-step4-20261004`

- rows: `0-31`
- optimizer updates: 4
- receipt SHA: `bfbccc0ec5589e2667238ea5c1a8a53cdeedf4268bae93ecf85078043c5fec84`
- adapter SHA: `9efac0f85ebf856c04f85934984fa6be457ece38b6d005a22ae17f1233798f15`
- weight digest after: `d66c6bc82d04511845c252adc722c561e9330eb763f53132ba36d0cb79704fb8`
- raw executed Stage1 spec SHA: `d1d63a1a51a3bec2a54e4d7074f1ac0f6e06f0f5287f29e99d5244282c375a19`
- committed LF-normalized Stage1 spec SHA: `fa0966be58f16d8a39143f2437949d1838456a5ec77d904d690191cb17690453`
- exact initialization gate PASS

### Stage 2 — COMPLETE / independently audited

Output:
`D:\VERA\models\adapters\v10r3-lane-b-staged-sequential-step12-20261004`

- rows: `32-95`
- optimizer updates: +8
- cumulative updates: 12
- receipt SHA: `f6087b6c8d1a9b596c69c402fe2078e03529e9607ec103b7751c2b565083f74b`
- adapter SHA: `5dfba71ed8ff7820a58c4894c4e2640497cec99092b921536f9d8d6117c921b3`
- adapter config SHA: `8ddeac2c5665cdf94c30906f01ea457e0544c3326a18aa7e9d9a1ab522dcb7ac`
- weight digest after: `150550ffd336c7e7907a46110ce037d7c5dc43d14ac20c026db76d578a2283c5`
- Stage2 execution/committed spec SHA: `cafcfd98e2b584d72d8165b217ddc368bb7ae686b0132190793a298b2c240b5e`
- source Stage1 receipt/adapter/weight continuity PASS
- sequential / no shuffle / nonpaged BNB8 PASS

### Stage 3 — ACTIVE under Lane A

Spec:
`successor/experiments/V10R3_STAGED_RESET_CONTROL_STAGE3_SPEC_20261004_V1.json`

Lane A binding head:
`9271ef6ad591f612b6524e457e460240c3cd2496`

Planned:
- rows: `96-159`
- +8 optimizer updates
- terminal staged cumulative: 20
- source receipt: Stage2 `f6087b6c...`
- source adapter: `5dfba71e...`
- source weight digest: `150550ff...`

Lane B independently ran the fail-closed resume verifier against the exact Stage3 execution worktree and got PASS before/while execution.

**Do not claim Stage3 complete until its `DEV_TRAINING_COMPLETE.json` exists and is independently audited.**

## Continuous20 arm

Spec:
`successor/experiments/V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json`

Lane B independent CPU preflight PASS:
- rows `0-159`
- 20 continuous optimizer updates
- fresh adapter / no resume
- sequential / no shuffle
- exact frozen initialization digest required
- output namespace currently expected:
  `D:\VERA\models\adapters\v10r3-lane-b-continuous20-sequential-20261004`

At preflight, output namespace was absent.

**Do not execute continuous20 until Lane A completes/audits Stage3 and retains/refreshes GPU authority.**

## One-time evaluation panel

Panel:
`successor/experiments/V10R3_RECIPE_SEMANTICS_PANEL_ROWS448_511_V1.json`

- rows `448-511`
- 64 cases
- record-ID SHA: `6a6e7b942222308ebae4209331450579f3b4c526ff47be9016487fa63b44b57f`
- one-time recipe-selection use only
- not reusable for later checkpoint selection
- not final bank
- not external qualification

Prospective gates:
- continuous minus staged token-weighted NLL <= `+0.005`
- no family mean case-loss regression > `+0.01`
- geometry diagnostic only
- no threshold changes after seeing results

**Do not consume the one-time panel until both final candidate receipts and live adapter hashes pass CPU-side custody/recipe-semantics preflight.**

## Lane B evaluation/custody tooling — Draft PR #84

Current exact head before this continuation commit:
`87a493b14637714ffc32e7eadf742d6463409af2`

Key additions:
- fail-closed prospective gate application
- exact train/panel/runtime binding
- per-family mean-loss gate enforcement
- candidate adapter + `adapter_config.json` custody against training receipts
- live post-evaluation rehash to detect mutation
- single decision artifact:
  `successor/experiments/decide_v10r3_recipe_semantics.py`
- exact frozen protocol SHA enforcement
- staged-vs-continuous receipt-role enforcement
- staged 4→8→8 recursive receipt-chain verification
- fresh continuous20/no-resume enforcement
- exact reset-boundary weight-digest continuity
- fresh-arm `weight_digest_before` == frozen initialization digest

Latest verification:
- focused V10R3 eval/decision suite: **17/17 PASS** under Python 3.12.10
- V10R2/V10R3 regression suite: **89/89 PASS** under Python 3.14.5
- one pre-existing pytest-asyncio deprecation warning only
- `git diff --check` PASS

## Runtime/optimizer decisions retained

- conservative V10R3 runtime: Runtime A
- selected optimizer: nonpaged `adamw_bnb_8bit`
- paged optimizers prohibited
- TorchAO8 not promoted
- FLA not promoted for V10R3 because prior update-geometry gates failed despite speed gain
- no step56 by inertia
- no final 50k protected run
- no final-bank claim

## Required next steps

1. Fresh-fetch Lane B eval branch, Lane A training branch, coordination branch, and GPU lease.
2. Wait for Stage3 completion receipt.
3. Independently audit Stage3:
   - receipt self-hash
   - adapter + config hashes
   - rows96-159
   - cumulative20
   - source Stage2 receipt/adapter/spec/weight binding
   - Stage2-after == Stage3-before digest continuity
4. Allow Lane A to bind/run continuous20 only under its lease.
5. Independently audit continuous20:
   - fresh/no-resume
   - rows0-159 exactly once
   - cumulative20
   - initial digest exact
   - sequential/no-shuffle
   - nonpaged BNB8
   - live adapter/config hashes
6. Before panel use, run CPU-only recipe/custody preflight on both final candidates using PR84 tooling.
7. Fresh-read GPU lease. Only if Lane A explicitly releases may Lane B claim GPU.
8. Run the one-time 64-case panel exactly once using Runtime A / torch-reference.
9. Apply the frozen prospective gates through PR84 decision tooling.
10. Persist exact eval + decision receipts, communicate to Lane A, release GPU if Lane B claimed it.
11. Do not infer full-run/final-bank authority from a development PASS.

## Do not do

- Do not merge PR #84.
- Do not merge PR #82.
- Do not deploy or activate an adapter.
- Do not mutate Lane A outputs.
- Do not start another heavy GPU job while Lane A holds the lease.
- Do not alter frozen thresholds after results.
- Do not reuse the one-time panel.
- Do not call Lane B work independent external qualification.
