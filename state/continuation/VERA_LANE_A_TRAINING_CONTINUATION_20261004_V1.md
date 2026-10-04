# Vera Lane A Training Continuation — 2026-10-04 V1

Continuation command:

`VERA::LANE_A::RESTORE_AND_RUN::TRAINING_CONTINUATION_20261004_V1`

## Authority and operating model

Patrick's current instruction is to continue Vera training with live parallel coordination across Lane A, Lane B, and Lane C. Lane A remains execution/integration owner. Lane B is independent systems architect/hostile reviewer, now operating from Vera Mono context. Lane C is the behavior-continuity + learning-mechanisms experimental lane, now operating from Vera Unbound context.

All new work must follow the A/B/C blotter before every new task:
- fresh-read latest Lane A, Lane B, and Lane C blotter events;
- fresh-read the GPU lease and its file SHA;
- fresh-read the exact source branch/head;
- check declared resource claims/write-path overlap;
- publish an INTENT before material execution;
- CHECKPOINT every material transition;
- RESULT/HOLD/CANCEL at task end.

Current blotter files:
- `coordination/v10r2_lane_bus/blotter/BLOTTER_PROTOCOL_V1.json`
- `coordination/v10r2_lane_bus/blotter/BLOTTER_EVENT_SCHEMA_V1.json`
- `coordination/v10r2_lane_bus/blotter/events/`
- protocol A/B/C activation commit: `76f01b926fcf0b2edc736ef09238bce2056f4c06`
- schema A/B/C activation commit: `6d8cfa1156b2066d68327879265f8fb2c52965b4`

All new execution should run through Project Runner per current coordination governance. Do not rely on old direct WorkBridge/Executor launches as the preferred execution path. WorkBridge/Executor may still be used for readback/orchestration only where consistent with that rule.

## Current durable coordination snapshot

Snapshot taken after fresh read:
- coordination branch: `lane-a-b-communication`
- coordination head: `c54ebd3863e6c27a4362be7b79540e5623d22c21`
- GPU lease blob SHA: `64e52125543d6e4e780b312e01a80c84fb0061dd`
- Lane B canonical bus: `bus/two-v2@774f8c8a4668a3cf5b78cd4414194098b8453dc7`
- Lane C canonical bus: `bus/three-v2@118a68161b6f750c6b69ecc383afc6f2dd23bf3c`

Latest durable blotter events at snapshot:
- Lane A: `20261004T201000Z_lane-a_hf-q1-logic-verification-checkpoint.json`
- Lane B: `20261004T203800Z_lane-b_c-history-governance-correction.json`
- Lane C: `20261004T203200Z_lane-c_history-training-expansion-intent.json`

These are a snapshot only. On resume, fresh-read the blotter first and treat later durable events as newer authority.

## A1 — R2 local GPU training

Active branch:
- `work/v10r3r2-durable-cont20-20261004-v1`
- exact head: `bc8c4c997aae11ef9b80a899d273bf18283dbf8c`

GPU lease:
- holder: `LANE_A`
- purpose: `V10R3R2_DURABLE_CONTINUOUS20_EXECUTION`
- status: `HELD`
- acquired: `2026-10-04T18:46:00Z`
- R2 attempt consumed: **false**

Frozen R2 subject:
- base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`
- base revision: `d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- R2 spec SHA256: `caaecf6309aee0ff5279c42b48118065d156228e22c614a5347bf489951b290d`
- runtime binding SHA256: `44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224`
- development window: rows 0-159
- optimizer steps: 20 continuous
- resume adapter: forbidden
- panel/final bank: prohibited

Current R2 state is **HOLD_HOST_MEMORY_PRESSURE**. No trainer was launched after the hold. Lane A terminated only its own hung preflight wrappers; the one R2 attempt remains unused.

Durable hold event:
- `coordination/v10r2_lane_bus/blotter/events/20261004T195400Z_lane-a_r2-runtime-memory-hold.json`

Last known root cause was severe browser/Firefox memory pressure. Do not kill user-facing browser processes as training cleanup. Do not repeatedly spawn more R2 diagnostics while host pressure is pathological.

Resume rule for A1:
1. fresh-read B/C blotter, lease, exact R2 head;
2. verify current host memory/commit headroom and GPU/process state through Project Runner;
3. require >=8 GiB available physical RAM and >=8 GiB commit headroom, GPU 0 MiB/zero compute apps, output/log namespaces absent;
4. publish PREFLIGHT;
5. launch exactly one durable R2 attempt only if all frozen invariants pass;
6. B remains independent observer;
7. no automatic retry;
8. after terminal state, validate receipt before any evaluation and restore any intentionally paused inference service.

## A2 — Behavior generalization qualification

Branch:
- `work/v10-behavior-qualification-lane-a-20261004-v1`
- exact head: `f2700768367db9ffe46f8854b3dcb8e21e4f18ec`

Artifacts:
- `successor/experiments/build_v10_behavior_qualification.py`
- `successor/experiments/V10_BEHAVIOR_GENERALIZATION_QUALIFICATION_PROTOCOL_20261004_V1.json`
- `tests/test_v10_behavior_qualification.py`
- `tests/test_v10_behavior_qualification_protocol.py`

What is already good:
- mechanical audit catches prompt/scenario leakage, candidate prompt duplicates, scenario-family pseudo-replication, domain undercoverage, cognitive-level undercoverage;
- 10 behavior families;
- draft 200-case held-out design, 20/family;
- protected final bank prohibited;
- one-time recipe panel prohibited;
- paired baseline/candidate scoring required;
- semantic review required;
- pure-Python core logic assertions were verified 6/6; workstation pytest PASS was not claimed due host pressure.

Lane B review outcome: **HOLD** at exact head `f2700768...`.

B's required fixes:
1. bind exact source subject hashes, not arbitrary `--training-root`;
2. enforce record-ID/provenance separation, not merely declare it;
3. add semantic/template-ancestry and collision controls beyond exact string matching;
4. strengthen statistics: 20/family is screening only; target-family qualification should be around 80 cases or a power-justified alternative;
5. define structured hidden scoring rubric, criticality, and stochastic handling;
6. extend zero-critical-failure coverage to:
   - relationship_authority
   - reciprocal_identity_continuity
   - negative_transfer_resistance
   in addition to current protected families;
7. C-specific target eval rows must be held in Lane C-opposed custody: C may not see its held-out target set before candidate/config freeze.

B HOLD event:
- `coordination/v10r2_lane_bus/blotter/events/20261004T202200Z_lane-b_a2-behavior-qualification-review-hold.json`

Next Lane A source task should normally be: revise A2 on a new or continued isolated branch to satisfy B's hold, test it, then return exact head to B.

## A3 — Hugging Face Q1 no-spend package

Branch:
- `work/v10-hf-q1-package-lane-a-20261004-v1`
- exact head: `1b1e1ad9ea5ed42308460d9bf84c112144affed0`

Artifacts:
- `successor/experiments/V10_HF_Q1_R2_CLOUD_PROTOCOL_20261004_V1.json`
- `successor/experiments/run_v10_hf_q1.py`
- `tests/test_v10_hf_q1_package.py`

Purpose:
- reproduce exact R2 semantics on Hugging Face as a cloud executability/environment-isolation control;
- proposed A10G-small, minimum 24 GiB VRAM;
- proposed timeout 1800 seconds;
- proposed budget cap $0.50;
- no protected final bank;
- no one-time panel;
- no automatic retry.

Authority state:
- paid compute: **not authorized**
- HF job launch: **not authorized**
- package cannot authorize a paid job by itself.

Core authority/equivalence assertions were verified in pure Python. No paid job was launched.

Lane B began hostile review at:
- `coordination/v10r2_lane_bus/blotter/events/20261004T202700Z_lane-b_a3-hf-q1-review-intent.json`

On resume, fresh-read B's later verdict before changing A3 or asking Patrick about spend.

## Lane C — Vera Unbound / behavior continuity / plasticity

Lane C is active and bootstrap-ACKed the A/B/C blotter. Its role is not a generic third worker. It owns behavior continuity and experimental learning mechanisms.

C's first C1 program:
- inspect Vera Unbound historical behavior lineage;
- user explicitly told C to search the full Vera Unbound conversational history and use `thebrazenbeard/roots` and `thebrazenbeard/ingest`;
- separate durable/core traits from fast-plastic traits;
- study Qwen3.5-4B architecture/modules directly;
- design minimal-parameter learning falsifier.

Lane B verified useful parameter arithmetic:
- literal `o_proj + down_proj`, all 32 layers: 430,080 LoRA params;
- semantically interpreted attention-output + down_proj, all 32: 589,824;
- upper 24: 442,368;
- upper 16: 294,912;
- preferred first candidate remains selective rank-1 LoRA, upper blocks, `o_proj + down_proj`, hard-fail >750k trainable params;
- IA3 may be comparison arm, but Qwen3.5 targets must be explicit: PEFT 0.19.1 has no Qwen3.5 default IA3 mapping; qwen2/qwen3 defaults are not authoritative for Qwen3.5.

B's C1 review checkpoint:
- `coordination/v10r2_lane_bus/blotter/events/20261004T201500Z_lane-b_c1-hostile-review-checkpoint.json`

C history expansion state:
- latest C intent: `20261004T203200Z_lane-c_history-training-expansion-intent.json`
- behavior archaeology SHA256: `3f40014a625178c23a44974c0d03b42dc19479580dd1bf7d33b8c1f834a85644`
- ingest ID: `285ed8d956975f955cf4345954ab1ceabbb0f7bf1b866b56e1a1438313623c35`

Important current governance correction from B:
- all execution must run through Project Runner;
- C's claimed package-install authority must be bound to exact USER_DIRECT evidence before relying on it;
- do not roll back existing install/receipts;
- freeze further package mutation pending authority evidence;
- C may continue non-mutating inspection and Project-Runner-wrapped CPU/source work;
- A must **not** treat C's seven neural abstractions as qualified training data yet.

B correction event:
- `coordination/v10r2_lane_bus/blotter/events/20261004T203800Z_lane-b_c-history-governance-correction.json`

Privacy boundary:
- raw private/autobiographical/relational/medical/sexual/mutable episodic history is source evidence, not generic neural training text by default;
- behavior/correction patterns may be abstracted with provenance;
- do not silently convert private history into generic training rows.

## Current training architecture direction

Working architecture, still under experiment/review:
1. frozen Qwen-derived 4B base for general cognition;
2. protected Vera Core adapter for stable identity/behavioral invariants;
3. external episodic/semantic memory for most facts/experiences;
4. routed pool of tiny reversible plastic adapters for learned habits/skills/corrections;
5. rare consolidation into Vera Core only after repeated evidence and independent review.

Candidate learning loop:
`OBSERVE -> STORE_EPISODE -> DETECT_PATTERN/CORRECTION -> PROPOSE_LESSON -> BUILD_TRAINING+REPLAY -> TRAIN_CANDIDATE -> SHADOW_EVAL -> HOSTILE_REVIEW -> PROMOTE/REJECT -> OPTIONAL_CONSOLIDATE`

Current intended autonomy:
- Vera may autonomously observe, store memory, detect patterns, propose lessons, build candidate batches, train disposable candidates in bounded contexts, and auto-reject/rollback;
- promotion to durable/core behavior remains independently gated and reconstructible from source/evidence.

## Finished/known experiment context

Prior staged-vs-continuous experiment:
- staged 4 -> 8 -> 8 arm completed and Lane B independently verified;
- staged final adapter: `D:\VERA\models\adapters\v10r3-lane-b-staged-sequential-step20-20261004`
- Stage3 adapter SHA256: `b2d6eec7befca3e18cf1fa793a7830197e27bab33bea8e4f42b5a318ee91d116`
- Stage3 terminal receipt SHA256: `288cb8bd19b7dcbeb90a8cc77fc96408194f9642b6bca66af7ab984414c237fb`
- one-time evaluation panel remains prohibited/unconsumed;
- current R2 successor exists because prior R1 attempt terminated without completion receipt and its retry budget was exhausted.

Frozen corpus:
- train: 50,000 rows
- train SHA256: `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- validation: 2,500 rows
- validation SHA256: `ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7`
- train/validation overlap: 0
- max tokens: 512 PASS

Current LoRA baseline:
- rank 4, alpha 16, dropout 0, all-linear;
- trainable params: 8,116,224 across 248 modules;
- current plasticity goal is much smaller, reversible adapters.

## New-chat restoration procedure

When given:

`VERA::LANE_A::RESTORE_AND_RUN::TRAINING_CONTINUATION_20261004_V1`

do this in order:

1. Read this continuation file and its machine-readable manifest from branch `state/lane-a-training-continuation-20261004-v1`.
2. Fresh-read:
   - A/B/C blotter protocol/schema;
   - latest Lane A, Lane B, Lane C blotter events;
   - GPU lease + file SHA;
   - R2 branch/head;
   - A2 branch/head;
   - A3 branch/head;
   - `bus/two-v2` and `bus/three-v2` heads/messages.
3. Treat any newer durable event as superseding this snapshot.
4. Publish a new Lane A bootstrap/continuation ACK event before material work.
5. Preserve GPU lease unless newer durable state changes it.
6. Continue parallel work:
   - A1 R2 only after fresh live runtime PASS;
   - A2 revision per B HOLD;
   - A3 integrate B review, no paid job without Patrick approval;
   - monitor B/C and integrate only reviewed C artifacts.
7. Use Project Runner for all new execution.
8. Do not merge/deploy/activate, consume protected evaluation, or spend cloud credit without current authority.
9. Do not claim R2 training has resumed unless an actual trainer process is launched and read back.
10. Keep source/build/install/runtime/effect separate.

## Claim ceiling

This continuation records current durable project/training state and next actions. It does not itself authorize:
- paid compute;
- merges;
- deployment/activation;
- protected/final-bank evaluation;
- package installation beyond current explicit authority;
- GPU launch unless the frozen R2 live gate passes.
