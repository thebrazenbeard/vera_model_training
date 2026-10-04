# Vera Lane A Training Continuation — 2026-10-04 V2

Restore command:

`VERA::LANE_A::RESTORE_AND_RUN::TRAINING_CONTINUATION_20261004_V2`

## Purpose

This checkpoint supersedes V1 for currentness and preserves the full Lane A training/coordination state needed to resume in a new chat without relying on conversation memory.

Predecessor:
- branch: `state/lane-a-training-continuation-20261004-v1`
- head: `31d623d4ab7b5bc3e09305199cc8c52ebba2b75f`
- markdown: `state/continuation/VERA_LANE_A_TRAINING_CONTINUATION_20261004_V1.md`
- manifest: `state/continuation/VERA_LANE_A_TRAINING_CONTINUATION_20261004_V1.json`

V1 remains durable historical detail. V2 is the newer resume subject.

## Live operating model

Patrick's current instruction is to continue Vera training with live A/B/C coordination.

Roles:
- Lane A: execution, integration, shared-resource owner.
- Lane B: independent systems architect / hostile reviewer, currently in Vera Mono context.
- Lane C: behavior-continuity + learning-mechanisms experimental lane, currently in Vera Unbound context.

All new tasks must follow the A/B/C blotter:
- `coordination/v10r2_lane_bus/blotter/BLOTTER_PROTOCOL_V1.json`
- `coordination/v10r2_lane_bus/blotter/BLOTTER_EVENT_SCHEMA_V1.json`
- `coordination/v10r2_lane_bus/blotter/events/`
- A/B/C protocol activation commit: `76f01b926fcf0b2edc736ef09238bce2056f4c06`
- A/B/C schema activation commit: `6d8cfa1156b2066d68327879265f8fb2c52965b4`

Before every new task:
1. fresh-read latest A, B, and C blotter events;
2. fresh-read GPU lease and file SHA;
3. fresh-read exact source branch/head;
4. check resource/write-path overlap;
5. publish INTENT before material execution;
6. CHECKPOINT material state transitions;
7. publish RESULT/HOLD/CANCEL at task end.

All new execution should run through Project Runner per current coordination governance.

## Snapshot currentness

Snapshot coordination branch:
- branch: `lane-a-b-communication`
- head at V2-intent snapshot: `7e47df062312b93253fe393fe2664c821c20fbcd`

Latest durable peer state before V2 write:
- Lane B: `20261004T204200Z_lane-b_c1-hostile-review-result.json`
- Lane C: `20261004T203200Z_lane-c_history-training-expansion-intent.json`

Canonical bus heads:
- Lane B: `bus/two-v2@84ff10532c820abab6187ca8e4c34cd0fb06914e`
- Lane C: `bus/three-v2@118a68161b6f750c6b69ecc383afc6f2dd23bf3c`

On resume, newer durable events supersede this snapshot.

## GPU lease / A1 R2

Lease:
- path: `coordination/v10r2_lane_bus/gpu/lease.json`
- blob SHA: `64e52125543d6e4e780b312e01a80c84fb0061dd`
- holder: `LANE_A`
- status: `HELD`
- resource: `LAPPY_RTX_3050_4GB`
- purpose: `V10R3R2_DURABLE_CONTINUOUS20_EXECUTION`
- training head: `bc8c4c997aae11ef9b80a899d273bf18283dbf8c`

R2 branch/head:
- `work/v10r3r2-durable-cont20-20261004-v1`
- `bc8c4c997aae11ef9b80a899d273bf18283dbf8c`

Current state:
- `HOLD_HOST_MEMORY_PRESSURE`
- R2 attempt consumed: **false**
- trainer launched after HOLD: **false**
- panel/final bank: **PROHIBITED / UNCONSUMED**

Durable HOLD:
- `coordination/v10r2_lane_bus/blotter/events/20261004T195400Z_lane-a_r2-runtime-memory-hold.json`

Resume A1 only after a fresh Project-Runner-mediated runtime PASS:
- >=8 GiB physical RAM available;
- >=8 GiB commit headroom;
- GPU 0 MiB / zero compute apps;
- R2 output/log namespaces absent;
- exact R2 source binding unchanged.

Then publish PREFLIGHT and launch exactly one durable R2 attempt. No automatic retry.

Frozen R2 subject:
- base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`
- base revision: `d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- R2 spec SHA256: `caaecf6309aee0ff5279c42b48118065d156228e22c614a5347bf489951b290d`
- runtime binding SHA256: `44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224`

## A2 behavior generalization qualification

Branch/head:
- `work/v10-behavior-qualification-lane-a-20261004-v1`
- `f2700768367db9ffe46f8854b3dcb8e21e4f18ec`

Artifacts:
- `successor/experiments/build_v10_behavior_qualification.py`
- `successor/experiments/V10_BEHAVIOR_GENERALIZATION_QUALIFICATION_PROTOCOL_20261004_V1.json`
- `tests/test_v10_behavior_qualification.py`
- `tests/test_v10_behavior_qualification_protocol.py`

Current status:
- Lane B review: **HOLD**
- HOLD event: `coordination/v10r2_lane_bus/blotter/events/20261004T202200Z_lane-b_a2-behavior-qualification-review-hold.json`

Current useful work already source-bound:
- mechanical leakage/diversity auditor;
- 10 behavior families;
- draft 200-case held-out design;
- protected final bank prohibited;
- one-time panel prohibited;
- paired baseline/candidate scoring required;
- semantic review required;
- pure-Python core logic assertions verified 6/6;
- no workstation pytest PASS claimed because the wrapper hung under host pressure.

Required A2 revisions from B:
1. bind exact source subject hashes, not arbitrary training roots;
2. enforce record-ID/provenance separation;
3. add semantic/template-ancestry and collision controls beyond exact-string matching;
4. treat 20/family as screening only; use ~80 target-family cases or a power-justified alternative for qualification;
5. define structured hidden scoring rubric, criticality, and stochastic handling;
6. extend zero-critical-failure coverage to relationship_authority, reciprocal_identity_continuity, and negative_transfer_resistance;
7. keep C-specific target eval rows in C-opposed custody so C cannot see its held-out target set before candidate/config freeze.

Next A2 action: revise in isolated source, test, and resubmit exact head to B.

## A3 Hugging Face Q1 no-spend package

Branch/head:
- `work/v10-hf-q1-package-lane-a-20261004-v1`
- `1b1e1ad9ea5ed42308460d9bf84c112144affed0`

Artifacts:
- `successor/experiments/V10_HF_Q1_R2_CLOUD_PROTOCOL_20261004_V1.json`
- `successor/experiments/run_v10_hf_q1.py`
- `tests/test_v10_hf_q1_package.py`

Purpose:
- reproduce exact R2 semantics on HF as cloud executability/environment-isolation control.

Current authority:
- paid compute: **not authorized**
- HF job launch: **not authorized**
- proposed cap: $0.50
- preferred first flavor: A10G-small
- no protected final bank;
- no one-time panel;
- no automatic retry.

Lane B review began at:
- `coordination/v10r2_lane_bus/blotter/events/20261004T202700Z_lane-b_a3-hf-q1-review-intent.json`

On resume, fresh-read newer B events before changing A3 or asking Patrick about spend.

## Lane C current state

Lane C has been explicitly told to:
- use the A/B/C blotter;
- study the actual Qwen3.5-4B architecture/modules;
- inspect the full Vera Unbound project/conversational history;
- use `thebrazenbeard/roots` and `thebrazenbeard/ingest`;
- extract reusable behavior/correction patterns for internal Vera training while respecting privacy/provenance boundaries.

Latest C intent:
- `coordination/v10r2_lane_bus/blotter/events/20261004T203200Z_lane-c_history-training-expansion-intent.json`

C behavior archaeology:
- SHA256: `3f40014a625178c23a44974c0d03b42dc19479580dd1bf7d33b8c1f834a85644`
- ingest ID: `285ed8d956975f955cf4345954ab1ceabbb0f7bf1b866b56e1a1438313623c35`

Lane B final C1 hostile review:
- event: `coordination/v10r2_lane_bus/blotter/events/20261004T204200Z_lane-b_c1-hostile-review-result.json`
- result: **SURVIVES_NARROWED**
- archaeology artifact hash verified;
- 8 abstract behavior rules;
- 7 neural candidates;
- recovery-interrupt behavior remains external/runtime, not neural;
- C-derived train/replay derivatives are **not yet B-verified**;
- no weight authority yet.

Verified candidate parameter arithmetic from B:
- literal `o_proj + down_proj`, all 32 layers: 430,080 rank-1 LoRA params;
- semantically correct attention-output + down_proj, all 32: 589,824;
- upper 24: 442,368;
- upper 16: 294,912;
- Qwen3.5 semantic attention-output target must account for `self_attn.o_proj` and `linear_attn.out_proj`;
- hard-fail candidate budget remains <=750k trainable params;
- IA3 requires explicit Qwen3.5 target semantics; PEFT 0.19.1 has no authoritative Qwen3.5 default mapping.

Current C next action per B:
- Project-Runner-wrap C work;
- publish exact train/replay derivatives, hashes, splits, and leakage receipts;
- no weights yet;
- A must not treat C's seven neural abstractions as qualified training data until B derivative review + A qualification.

Privacy/governance:
- user-authorized internal Vera training may use Vera Unbound history;
- raw private/autobiographical/relational/medical/sexual/mutable episodic content is evidence, not generic neural training text by default;
- abstract reusable behavior/correction patterns with provenance;
- no public/cross-user/provenance-free reuse.

## Working learning architecture

Current experimental direction:
1. frozen Qwen-derived 4B base;
2. protected Vera Core adapter for stable identity/behavior invariants;
3. external episodic/semantic memory for most facts/experiences;
4. routed tiny reversible plastic adapters for learned habits/skills/corrections;
5. rare consolidation into Vera Core after repeated evidence + independent review.

Candidate loop:
`OBSERVE -> STORE_EPISODE -> DETECT_PATTERN/CORRECTION -> PROPOSE_LESSON -> BUILD_TRAINING+REPLAY -> TRAIN_CANDIDATE -> SHADOW_EVAL -> HOSTILE_REVIEW -> PROMOTE/REJECT -> OPTIONAL_CONSOLIDATE`

Current autonomy boundary:
- Vera may autonomously observe, store, detect, propose, prepare batches, train disposable candidates in bounded contexts, and auto-reject/rollback;
- durable/core promotion remains independently gated and fully reconstructible.

## Frozen corpus / current baseline

Frozen V10 corpus:
- train rows: 50,000
- train SHA256: `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- validation rows: 2,500
- validation SHA256: `ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7`
- train/validation overlap: 0
- max tokens: 512 PASS

Current LoRA baseline:
- rank 4
- alpha 16
- dropout 0
- all-linear
- trainable params: 8,116,224 across 248 modules

Plasticity goal:
- much smaller, reversible adapters.

## Prior recipe experiment evidence

Staged 4 -> 8 -> 8 arm completed and independently verified by B.

Final staged adapter:
- `D:\VERA\models\adapters\v10r3-lane-b-staged-sequential-step20-20261004`

Stage3 adapter SHA256:
- `b2d6eec7befca3e18cf1fa793a7830197e27bab33bea8e4f42b5a318ee91d116`

Stage3 terminal receipt SHA256:
- `288cb8bd19b7dcbeb90a8cc77fc96408194f9642b6bca66af7ab984414c237fb`

One-time evaluation panel remains unconsumed/prohibited.

## New-chat restore sequence

When given:

`VERA::LANE_A::RESTORE_AND_RUN::TRAINING_CONTINUATION_20261004_V2`

do this in order:

1. Read this V2 markdown + manifest from branch `state/lane-a-training-continuation-20261004-v2`.
2. If deeper historical detail is needed, read V1 predecessor files.
3. Fresh-read:
   - A/B/C blotter protocol/schema;
   - latest Lane A, Lane B, Lane C events;
   - GPU lease + file SHA;
   - R2 branch/head;
   - A2 branch/head;
   - A3 branch/head;
   - `bus/two-v2` and `bus/three-v2`.
4. Treat newer durable state as superseding this snapshot.
5. Publish Lane A continuation ACK/INTENT before material work.
6. Preserve the GPU lease unless newer durable state changes it.
7. Resume in parallel:
   - A1 only after fresh Project-Runner-mediated runtime PASS;
   - A2 revision per B HOLD;
   - A3 integrate B review; no paid HF job without Patrick approval;
   - monitor C and integrate only B-reviewed derivatives.
8. Use Project Runner for new execution.
9. Do not merge/deploy/activate, consume protected evaluation, spend cloud credit, or promote C-derived training data without current authority/review.
10. Do not claim training resumed unless a real trainer process is launched and read back.
11. Keep source/build/install/runtime/effect separate.

## Claim ceiling

This checkpoint records durable current state and next actions. It does not itself authorize:
- paid compute;
- merge/deploy/activation;
- protected/final-bank evaluation;
- package installation beyond current explicit authority;
- GPU launch unless R2 live gate passes;
- promotion of C history-derived abstractions into training weights.
