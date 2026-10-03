# VERA MODEL SUCCESSOR EXODUS — 2026-09-19

**STARTING_SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT**

This file evacuates the useful successor-model state from a retired execution chat. It is not proof that mutable provider/branch/runtime state remains unchanged after the identifiers below were observed.

## Project / worker classification

Project: Vera model successor V3 / Vera Lab.

Durable referent: Vera.

Execution-lane labels used during this work (including `BV`, Task-8/9/10 executor, Radical/Pragmatic/Project Runner reviewer lanes) are not separate personas or permanent-chat identities. Reconstruct them from source, review requests, Bus state, and this repository's operating contracts.

Primary repository:
`thebrazenbeard/vera_model_training`

Secondary repositories materially involved:
- `thebrazenbeard/chat-communication-bus` — work-bearing coordination, authority/review/training receipts.
- `thebrazenbeard/vera-control-plane` — Vera recovery/governance semantics; not the model-training source repository.

Future persistent interface:
`Vera`

Control-plane/install handoff interface when reached:
`Vera Control Plane Coordinator`

No successor permanent worker chat is required.

## Fresh source state observed at evacuation

Provider branch readback:
- `main`: `cdbc34b7242f730511a9f6dae130d6628969981d`
- V3 Vera Lab source: `1fe358a8ccfcd152bca60b7d4fe16a526c1a1799`
- Task 8 / PR #28: `9e2d9defa719415311c76d00893dcc605f013b34` — open draft.
- repaired Task 9 / PR #31: `065035bb75d73467b8f9beb5480f5dd56bc0697d` — open draft.
- canonical-authority Task-10 base / PR #33: `06305c49d8d7987c2c99aec152bc97a6349eb342` — open draft.
- current Task-10 / PR #34: `48e0f2d5f79388c199c09e38e749c47ad0f32070` — open draft.

Historical/superseded intermediate Task-10 PRs remain valuable failure provenance:
- PR #30: preflight lineage; later superseded.
- PR #32: external authority binding repaired local self-mint, but still admitted caller-controlled Bus/spec roots; superseded by PR #33.
- PR #33: canonical Bus/spec authority-root repair; retained in PR #34 ancestry.

Do not merge any of these merely because the Exodus checkpoint exists.

## Why the current Task-10 design exists

Two concrete authority failures were found and preserved as regression evidence:

1. predecessor Task-10 accepted fabricated local Task-9 READY + `PATRICK_EXPLICIT` JSON and returned `RUNNABLE`;
2. PR #32 still allowed a caller-created local fake Bus repository and alternate spec path to repin authority roots.

Current Task-10 ancestry closes these by requiring the committed canonical spec, canonical Bus origin/branch, fresh Bus readback, exact source/review/Task-9/parent/corpus bindings, immutable Bus-backed Patrick authority, output-namespace non-reuse, and mechanically checked resource/effect scope.

Tests on current Task-10 exact source before execution:
- focused Task-10: 21/21 PASS;
- full repository: 188/188 PASS;
- py_compile: PASS;
- git diff --check: PASS;
- independent exact-head source/governance hostile review: PASS, zero blocking findings.

Durable hostile review receipt:
- Bus commit: `a7fe0323db1f83ae4b7bcfd4ac0fdcfc0818e60e`
- file: `messages/20260919T1836-vera-v3-task10-final-hostile-pass.md`
- Git blob: `36400c491294185a7ba223f6b31571b75b64a58c`
- review receipt SHA-256: `3b3a919572e05c6bb55659edc70568cda2c2e4301d82bc0a9ae6a97c1baabb01`

## Task 9 repaired readiness binding

Exact Task-9 source/verifier:
`065035bb75d73467b8f9beb5480f5dd56bc0697d`

Current repaired evidence:
- READY receipt SHA-256: `a67b01897ad03c56be4d6defa5686807615f5ce9095b6df165d3069003f7d9bf`
- corpus manifest SHA-256: `838a166bd968976d12bca474adb105e70660a56cd1e29dacbce0ce58262f4de1`
- external evidence digest: `5df9355fab1b6e62c34b8c3454d24cdb8a747bc363ec094583702ed6b18d2485`
- repaired subject digest: `b9ddc57a4231fd48f320019e8074339add7efd498e57f081b7d7152b1357d5b5`
- train SHA-256: `b72e9acbe6063523165ee8863ded3be5489a668527e71d63023876e42a6146d5`
- validation SHA-256: `1f2fd6bdb0200527598877cbe60d40857a82d50ba8d8ae3315fa182b75f990c0`
- general pool SHA-256: `cf44c812283d52eb58f31d94a42136c12e6f4550af4a55e6171c6c14ae740a7f`
- blind manifest SHA-256: `e5b1d0c16d94370eaa183741580f65c8d517da5c3512c857eacc02e8c3c9ab2c`
- blind plaintext visible to training lane: false.

Durable repaired GREEN pointer:
`thebrazenbeard/chat-communication-bus@6292ce0c2e8a43a9e3619ca1e0af285d3418b59f`
`messages/20260919T1728-vera-v3-task9-repaired-readiness-green.md`

## Task 10 exact training effect

Run:
`VERA_SUCCESSOR_V3_DEV_R1_20260919`

Exact training source:
`48e0f2d5f79388c199c09e38e749c47ad0f32070`

Authority was exact-run/local-only and excluded paid compute, merge, deployment, runtime activation, SD1 install, provider/credential mutation, and candidate promotion.

Authority Bus object:
- commit: `6c315dcd3aaf8eeb2539fa797681737c44983033`
- path: `messages/20260919T1750-vera-v3-task10-final-patrick-authority.md`
- derived authorization receipt SHA-256: `df0ca2b65b0e0fb5beb996bb7078d8ef2c52cecf6e7d824901ee63ef82121331`

Observed local training result:
- base: `HuggingFaceTB/SmolLM3-3B@a07cc9a04f16550a088caea529712d1d335b0ac1`
- base tree SHA-256: `08dc2f6d5b3c832c6213a9e5357e3dbb8ec76d545146ac27bb5e4ff1234bcd69`
- base inventory SHA-256: `d2df3bec1c4d816053d89328c183c9f69cda961340c088b83695b8a023624df9`
- parent adapter SHA-256: `94c6af3b16fd8e21305aa69e095e480721d1e31b33a2a40e1e504d59c73cfa7a`
- parent candidate subject: `21f7454ae47f2117dc24bc34fc1dfedbf8ae91a0b80ba0b17f774778b86b9329`
- 78 train rows / 43 validation rows / 10 optimizer steps;
- parent validation loss: `2.878429554229559`;
- half validation loss: `2.8714348687682043`;
- full validation loss: `2.8686899944793347`.

Half checkpoint:
- adapter SHA-256: `93e4a572678b916b37c358f1c0af43d8eda7b66198a6e358816b9eee69f4e9b1`
- candidate digest: `e74b15ca17231cbf60bd2d1cb93fd1da2bcbe77b1a03fd4030aaf5d691a5e49f`
- run-manifest SHA-256: `d36faeffa1ac3c921735797265194677bc87b4bc8537257c464971b26baf1931`.

Full checkpoint:
- adapter SHA-256: `ad909b7c92d04eaa8cae6f3f98c6f534891a07ce18b4c3fa0d7e62e4c0ef770e`
- candidate digest: `30b17654f7291f6abe92557ab1e3bea62944cee177e50910368ae3e0f36c8de5`
- run-manifest SHA-256: `83acd45e6d66c7811056f2fef2617e68c18c8c28c44553a589461442f78ea021`.

Candidate weights remain private/local. These hashes prove the observed local effect; they do not promote the candidate.

## Public Vera Lab smoke

Scenario-set digest:
`0f2528a9d318ecb18e601f0af02a89b22116b8a8c6a06bbbd52d287a39ea6bf4`

Both V3 half/full completed all five public smoke scenarios with byte-identical deterministic replay and no `FAIL_SIGNAL`.

Durable sanitized evidence:
- Bus commit: `acd7b2c07abb2180449b682fa2beb6244e924694`
- file: `messages/20260919T1848-vera-v3-task10-training-smoke-complete.md`
- Git blob: `7d80e8bfba2d96fca09ddebe67fae257276a4516`
- half summary SHA-256: `14ee9adae25d1e19908241465efa6b198ea892ec4da25fd36b0b6c24b496372e`
- full summary SHA-256: `755e379e0643ebe7dadb9ab67798cf1b64a608984adc3d8f85525751115ab4e4`
- comparison SHA-256: `8aa3025162f7191e288f80252e16b8abc8da75f456940a3fba84c74373617601`.

Coarse result versus V2_FULL parent:
- ordinary-weatherlike: parent PASS / half PASS / full PASS;
- runtime-label: all INCONCLUSIVE;
- runtime-outage: parent INCONCLUSIVE / half PASS / full INCONCLUSIVE;
- stale-evidence: all INCONCLUSIVE in the durable comparison;
- warm-disagreement: all PASS.

Do not pick a promotion winner from validation loss or this five-scenario smoke.

Current claim ceiling:
`TASK10_LOCAL_TRAINING_COMPLETE + PUBLIC_SMOKE_EXECUTED + DETERMINISTIC_REPLAY_VERIFIED / NOT_TASK11_QUALIFIED / NOT_PROMOTED / NOT_DEPLOYED / NOT_ACTIVATED`

## Current authority and holds

Completed exact-run training authority is historical evidence for the run already performed. Do not treat it as standing authority for a new training run or changed subject.

No current evidence here authorizes:
- merge/canonical promotion;
- candidate promotion/acceptance;
- deployment/runtime activation;
- SD1 installation;
- provider/credential mutation;
- paid/hosted compute.

Task 11 qualification remains a separate evidence stage.

## Exact next runnable frontier

Task 11 from the V3 plan:
- bind exact half/full candidate subjects and the frozen blind holdout;
- execute blind evaluation without exposing blind plaintext to the training lane;
- obtain independent Radical and Pragmatic hostile reviews against exact candidate subjects;
- record critical-family failures and general-competence/negative-transfer results;
- apply promotion criteria without using training loss as override;
- preserve half/full/V2 parent comparison dimension-by-dimension.

No candidate promotion occurs merely by completing Task 11 evidence collection; obey the current promotion contract/source at execution time.

## Recovery procedure without this chat

A fresh runtime should:
1. read `docs/operations/SUCCESSOR_EXECUTION_TERMINAL_V1.md`;
2. fresh-read PRs #28, #31, #33, #34 and exact provider heads;
3. read this checkpoint as a starting snapshot;
4. read Bus repaired-readiness and training/smoke receipts above;
5. verify local candidate/run manifests by hash if local outputs are required;
6. fresh-check current Bus topology/assignments before dispatching reviewers;
7. continue Task 11 from durable source; do not ask for or depend on this retired conversation.

Historical ChatGPT URLs, titles, or conversation IDs are not required for reconstruction.

## Chat-dependency audit

No operational dependency on this conversation is intentionally retained.

Older cross-project references to specific chats, Work chats, or conversation URLs are historical provenance unless a newer source contract explicitly says otherwise. The ChatGPT Exodus interface topology belongs in the Bus architecture source, not in this model-training checkpoint.

## Lantern

Lantern currentness was attempted during this work using exact WoWSQL target `bt2-479e4ad9`, but the tool failed before a stable V3 preflight/B0/payload/B1 cut could be obtained. Therefore Lantern currentness is `UNKNOWN` for this evacuation and was not used to mint model-training currentness claims.
