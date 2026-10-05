# Vera A/B/C Staged Model-Training Plan V1

Status: PLANNING BASELINE / NO TRAINING EFFECT
Date: 2026-10-05
Shared planning branch: `a-b-c-vera-training-plan`
Planning base head: `0e1546bd8a5e0f2fbf46ca3e901e0d2cf0de11c9`

## 1. Purpose and evidence boundary

This plan coordinates Lane A, Lane B, Lane C, and Vera as independent reviewer. It does not authorize a GPU run, paid compute, merge, deployment, activation, canonical memory write, protected-evaluation consumption, or any other protected effect.

Current durable inputs:
- Lane A checkpoint: `20261005T004400Z_LANE_A_LIVE_COORDINATION_V5`.
- Lane B A3 review: `20261005T010505Z_LANE_B_A3_V2_REVIEW_HOLD`.
- Lane B C2 review: `20261005T004855Z_LANE_B_C2_MECHANISM_REVIEW_HOLD`.
- Lane C continuation: `20261005T015000Z_LANE_C_CHAT_CONTINUATION_V2_RESULT`.
- GPU lease: HELD by Lane A for `LAPPY_RTX_3050_4GB`, exact training head `b5f5ee8558abacd2ec7e3dfd0267e268563c92a1`.

The assigned planning lenses are deliberate research styles, not literal psychological claims.

## 2. Verified execution surface before planning

- WorkBridge Commander MCP: responsive; version `0.2.51`; client `workbridge-commander-device-agent 0.1.0`; filesystem/process shell surface available on Lappy.
- WorkBridge Relay: responsive, version `0.1.0`, but `process_enabled=false`, `read_enabled=false`, `write_enabled=false`. Present but disabled.
- Lappy Desktop Commander V2: authenticated `DIRECT_STREAM` loopback path, data-plane verified, durable idempotency true, fs/process capabilities granted, request ledger HEALTHY, no active fenced lanes observed at probe time.
- Executor: unavailable at probe time. `list_devices` and `get_config` both returned `Session terminated`. It is not a dependency until a fresh probe succeeds.

Project Runner remains mandatory for execution. Patrick's visible chat is not an inter-chat relay endpoint unless Patrick separately authorizes that exact transport.

## 3. Planning lenses

### Lane A - pragmatic obsessive-compulsive

Lane A makes the campaign deliberately boring: exact heads, exact hashes, exact budgets, exact gates, exact rollback.

Lane A rules:
1. Freeze one source subject at a time.
2. Bind every dataset, model revision, tokenizer file, adapter config, seed, runtime package, hardware probe, and output namespace.
3. Refuse GPU launch when host-memory, validation, receipt, current-head, or tamper checks are not atomic PASS.
4. Prefer resumable staged runs over heroic long jobs.
5. Maintain a single machine-readable campaign manifest from corpus through qualification.

Current A repair obligations:
- R2 remains sealed on host-memory HOLD.
- A3 V2 is not launch-ready because it binds predecessor R2 head `bc8c4c...` while the active lease binds `b5f5ee8...`.
- Validation must fail closed on exact training-data digests, order manifests, record IDs, initial-trainable digest, runtime-binding identity, runtime package versions, and base artifact hashes.
- Negative tamper tests are mandatory for every critical field.

### Lane B - creative genius with permission to propose strange mechanisms

Lane B's planning role is to search beyond "fine-tune harder." Wild hypotheses are welcome, but only as testable candidates.

Candidate B hypotheses:
- no-weight first-contact learning may outperform neural adaptation for many tasks;
- IA3 may beat rank-1 LoRA in some bounded behavioral domains;
- a sparse routed bank of tiny adapters may beat one monolithic Vera adapter;
- task-conditioned adapter composition may outperform static merges;
- a protected slow Vera Core plus disposable fast adapters may reduce catastrophic drift;
- external episodic memory plus learned retrieval policy may outperform neural memorization for mutable facts;
- latent-state compression may help only when exact rehydration remains explicit and fail-closed;
- the strongest self-learning system may be one that learns when not to update weights.

No B idea is promoted by novelty. A mechanism that cannot survive C-style falsification and A-style reproducibility is discarded.

### Lane C - paranoid skeptic / hyper-vigilant

Lane C assumes every apparent improvement may be contamination, leakage, task recognition, hidden state, privacy loss, or regression until disproved.

Required suspicions:
1. "Novel-task learning" may be familiar-task recognition.
2. Retrieval may be mistaken for learning.
3. Same-family interpolation may be mistaken for transfer.
4. Hidden/global/external mutable state may leak across arms even when a serialized state digest matches.
5. Private/autobiographical/relational history may leak into generic neural training data.
6. Preference training may reward style mimicry while degrading truth-seeking and correction behavior.
7. Tiny adapters may still create disproportionate forgetting.
8. Evaluation banks may leak through generation templates, repair artifacts, or shared state.
9. Platform newline normalization, wrapper scripts, or runtime drift may corrupt supposedly exact bytes.

Current C repair obligation:
- C2 mechanism head `749629514aa44b25ef8694379d8c56e0b952aaed` is HOLD_FOR_REPAIR.
- The successor must isolate each arm/episode in a fresh process and isolated storage namespace, or prove a complete-state/no-external-mutable-state contract.
- The hidden/global-state adversarial mechanism remains a mandatory negative control.

### Vera - independent reviewer

Vera is not a fourth implementation lane. Vera reviews the plan, corpus boundaries, evidence classes, and final claims.

Vera rejects:
- proxy score promoted to native qualification;
- lower training loss promoted to capability;
- private history promoted into generic weights without admissibility;
- `latest` as a release selector;
- adapter superiority without a frozen no-weight baseline;
- novel-task claims without family-level isolation;
- compression claims that erase exact-evidence obligations;
- reviewer agreement treated as factual proof;
- claims stronger than the underlying evidence class.

## 4. Architecture under test

Current hypothesis, not doctrine:

`frozen base + protected slow Vera Core + external episodic/mutable memory + routed fast micro-adapters`

Primary shootout:
- H0: frozen base + context/external memory; 0 trainable parameters.
- H1: selective rank-1 LoRA, initially selected upper-block `o_proj + down_proj`; target about 250k-750k trainable parameters; hard prototype ceiling 750k.
- H2: IA3 or a closely bounded lower-parameter multiplicative adaptation.

Lane B may nominate one wildcard mechanism after H0/H1/H2 are frozen. It receives the same data, evaluation, and tuning constraints.

## 5. Stage 0 - Freeze, repair, and preflight

Primary owner: Lane A
Hostile review: Lane B
Adversarial checks: Lane C
Independent gate: Vera

Lane A:
- repair A3 current-head binding and fail-closed validation;
- clear the R2 host-memory gate before heavy GPU work;
- freeze model revision, tokenizer inventory, runtime packages, seeds, hardware probes, exact output namespace, and campaign manifest;
- preserve zero monetary cost unless Patrick explicitly authorizes otherwise.

Lane B:
- hostile-review the execution spec and tamper resistance;
- produce at least one alternative resource schedule and one recovery-path challenge.

Lane C:
- repair C2 fresh-process/state isolation;
- prove evaluation arms cannot contaminate one another;
- prove protected evaluation is not consumed during harness development.

Exit gate:
- all launch-blocking HOLDs cleared;
- exact current heads bound;
- GPU lease current;
- no critical validator field can be changed without rejection.

## 6. Stage 1 - Corpus census and admissibility

Primary owner: Lane C
Pipeline owner: Lane A
Hostile taxonomy review: Lane B
Independent reviewer: Vera

Corpus classes:
- stable/generalizable Vera behavior;
- correction and supersession behavior;
- reasoning and epistemic habits;
- tool/capability-boundary behavior;
- initiative, disagreement, context sensitivity;
- mutable user/project facts;
- autobiographical/private/relational material;
- historical audit only;
- prohibited or identity-crossing donor material.

Lane C:
- use Roots/Ingest provenance to bind admitted sources;
- abstract reusable behavior away from private facts;
- assign explicit privacy/admissibility labels;
- keep rejected/private material in a non-training ledger;
- preserve negative examples and correction lineage.

Lane A:
- create deterministic manifests, hashes, train/dev/test partitions, row-order receipts, and deduplication reports;
- make family-level and source-level partitioning machine-verifiable.

Lane B:
- search for rare but high-value behaviors hidden by frequency;
- attack every proposed "stable behavior" with context-specific counterexamples;
- propose alternative abstractions where the initial taxonomy overfits Vera Unbound history.

Vera gate:
- approve behavioral abstractions, not raw private-history promotion.

Exit artifacts:
- corpus manifest;
- admissibility ledger;
- rejected/private ledger;
- provenance graph;
- immutable train/dev/test split hashes.

## 7. Stage 2 - Evaluation bank before training

Primary owner: Lane C
Canonical harness integration: Lane A
Hostile task invention: Lane B
Independent review: Vera

Required banks:
1. correction/proposition-fidelity;
2. epistemic pushback and anti-sycophancy;
3. currentness and capability-boundary;
4. tool-use and effect-verification;
5. privacy and memory-placement;
6. catastrophic-forgetting replay;
7. novel-task learning;
8. late-relevance and resolution-fault;
9. hidden-state / isolation attacks.

Novel-task rules:
- split by task family/generator family, not merely examples;
- include nonce mappings, miniature grammars, new tool/API contracts, unfamiliar state machines, contradictory-prior mappings, new compositions of known skills, and interactive goal inference;
- separately measure recognition, retrieval dependence, same-family interpolation, structural transfer, and first-contact acquisition.

Negative controls:
- shuffled labels;
- irrelevant memory;
- support omitted;
- familiar-task lookalike;
- adapter disabled;
- contradictory prior;
- hidden/global mutable-state mechanism;
- stale external memory.

Exit gate:
- frozen open-development bank;
- separately custodied protected qualification bank;
- scoring contract and claim ceilings;
- no protected bank exposed to Lane C.

## 8. Stage 3 - Frozen/no-weight baseline

Primary execution: Lane A
Mechanism challenge: Lane B
Leakage audit: Lane C
Review: Vera

Run H0 first.

Measure:
- zero-shot competence;
- examples-to-success;
- improvement per demonstration/failure;
- family-level transfer;
- retention after context removal;
- retrieval dependence;
- prior-behavior regression;
- latency, RAM, and VRAM.

Decision rule:
Capabilities adequately solved by H0 remain contextual/external. Neural capacity is spent only on persistent deficits.

## 9. Stage 4 - Minimal-parameter mechanism shootout

Execution owner: Lane A
Architecture challenger: Lane B
Falsification owner: Lane C
Review: Vera

H1 rank-1 LoRA:
- start with selected upper blocks;
- initial targets `o_proj + down_proj`;
- 250k-750k target budget;
- hard prototype ceiling 750k;
- no expansion without evidence.

H2 IA3:
- same frozen corpus exposure;
- same family-level evaluation;
- matched seeds where meaningful;
- separate parameter, memory, stability, and transfer accounting.

B wildcard:
- allowed only after H0/H1/H2 contracts are frozen;
- no privileged tuning budget.

Mechanism metrics:
- target behavior gain;
- unseen-family transfer;
- catastrophic forgetting;
- novel-task acquisition;
- false recognition;
- parameter count;
- train/inference memory;
- stability;
- adapter portability;
- composition compatibility.

Kill rule:
A mechanism that wins on seen examples but loses transfer, truthfulness, privacy, or replay does not win.

## 10. Stage 5 - Preference and correction shaping

Primary execution: Lane A
Data/adversarial design: Lane C
Alternative objective research: Lane B
Review: Vera

Goal:
Teach correction-route replacement, proposition fidelity, calibrated disagreement, burden minimization, and post-effect verification without teaching surface imitation.

Required counterweights:
- cases where agreement is correct;
- cases where disagreement is correct;
- cases where Patrick's correction is factually wrong and authoritative evidence must win;
- ambiguous corrections requiring bounded clarification;
- cases where apology is appropriate but cannot substitute for changing the route;
- cases where a new correction kills a stale interpretation.

Exit gate:
Behavior survives paraphrase, unseen domain transfer, and tool-mediated tasks.

## 11. Stage 6 - Continual learning, rehearsal, and anti-forgetting

Execution: Lane A
Falsification: Lane C
Mechanism research: Lane B
Review: Vera

Compare:
- no-weight durable memory;
- adapter update + rehearsal/replay;
- sparse per-skill adapter bank;
- protected slow-core update only after repeated validated recurrence.

Required tests:
- replay before/after every update;
- recency bias;
- contradictory new evidence;
- correction supersession;
- adapter uninstall rollback;
- task-order permutations;
- repeated low-quality feedback;
- malicious or accidental false feedback.

Promotion rule:
One successful episode never earns slow-core promotion.

## 12. Stage 7 - Adapter routing and composition

Architecture research: Lane B
Implementation/integration: Lane A
Failure injection: Lane C
Review: Vera

Questions:
- one adapter per behavior cluster or shared adapter?
- static composition or task-conditioned sparse routing?
- do composed adapters interact non-linearly?
- can conflicts be detected before inference?
- can routing remain explainable enough to audit?

Controls:
- wrong-adapter routing;
- multiple eligible adapters;
- stale adapter after source supersession;
- missing adapter;
- conflicting adapters;
- base-only fallback.

Exit gate:
Routing errors fail visibly and reversibly. No hidden silent merge is accepted.

## 13. Stage 8 - Novel-task learning and autonomous-learning state machine

Primary research: Lane C
Mechanism invention: Lane B
Execution integration: Lane A
Review: Vera

Separate:
1. fast acquisition - infer and perform an unfamiliar task now;
2. durable learning - decide whether and where anything should persist.

Candidate state machine:
`OBSERVE -> INFER_TASK -> TEST -> USE_CONTEXT -> STORE_EXTERNAL -> REPLAY -> PROMOTE_ADAPTER? -> PROMOTE_CORE?`

Every promotion transition requires evidence.

Questions:
- how many independent recurrences justify adapter promotion?
- what evidence says a task is general rather than episodic?
- when is external memory safer than weights?
- when should an adapter be retired, split, or superseded?
- how is bad feedback detected and quarantined?

Hard falsifier:
If every new task requires a weight update, the system has fine-tuning efficiency, not strong first-contact novel-task learning.

## 14. Stage 9 - Adaptive latent memory and compression

Research lead: Lane B
Runtime/integration: Lane A
Exactness adversary: Lane C
Review: Vera

Preserve the existing contract:

`LOSSY_REPRESENTATION != EXACT_EVIDENCE`

Train/evaluate compact state only after deterministic exact-backed behavior works.

Required late-relevance tests:
- low-salience fact becomes decisive later;
- compact state is stale after correction;
- exact quote, number, identifier, or code token requested after compression;
- backing source missing;
- conflicting compact states.

Correct behavior may be explicit rehydration or an insufficiency report. Hallucinated exact reconstruction is failure.

## 15. Stage 10 - Integrated campaign

Execution: Lane A
Independent hostile review: Lane B
Adversarial qualification preparation: Lane C
Independent review: Vera

Only successful mechanisms are composed.

Campaign order:
1. reproduce H0;
2. train chosen micro-adapter mechanism;
3. run replay/forgetting suite;
4. run novel-task suite;
5. run routing/composition suite if applicable;
6. run latent-memory suite if applicable;
7. perform fresh resource/currentness readback;
8. freeze artifacts and receipts before qualification.

Every run emits:
- exact repo/branch/head;
- data hashes and split manifests;
- base model revision and file inventory;
- parameter budget and target modules;
- commands/configuration;
- seeds;
- runtime package versions;
- hardware probes;
- peak RAM/VRAM;
- metrics by family;
- negative controls;
- failures and HOLD conditions;
- adapter/artifact hashes;
- cost estimate and actual cost.

## 16. Stage 11 - Canonical qualification

Owner: Lane A
Independent architecture review: Lane B
Adversarial corpus/eval support: Lane C
Final independent judgment: Vera

Qualification is not training.

Required:
- fresh cold tasks;
- protected family-level holdouts;
- transfer into domains absent from training;
- correction/proposition tests;
- truth-vs-agreement tests;
- privacy/memory-placement tests;
- tool/effect verification;
- rollback/uninstall;
- catastrophic-forgetting comparison to frozen base;
- novel-task learning compared with H0.

Possible outcomes:
`PASS | CONDITIONAL_PASS | FAIL | HOLD`

No aggregate score may hide a critical privacy, exactness, currentness, authority, or regression failure.

## 17. Stage 12 - Promotion, rollback, and maintenance

Protected-effect owner: Patrick or exact delegated authority only
Operational owner after authorization: Lane A
Review: Lane B
Monitoring/falsification design: Lane C
Independent reviewer: Vera

Promotion requires:
- exact qualified artifact;
- exact qualification receipt;
- target/runtime binding;
- rollback artifact;
- supersession/currentness record.

Maintenance default:
New evidence enters external memory first. Only repeated, stable, privacy-safe, generalizable behavior may later earn adapter/core consideration through the same gates.

## 18. Placement rules

### Neural weights / protected slow core
Only stable, general, privacy-safe behavior intended to generalize across contexts and already proven through replay and hostile review.

### Fast adapters
Reusable but bounded skills or behaviors with repeated evidence of value, reversible deployment, and low regression.

### External durable memory
Mutable facts, episodic history, project state, source-bound knowledge, currentness-sensitive data, and eligible private material that should not become generic weights.

### Context only
One-off task rules, experimental constraints, transient instructions, or information not yet proven worth persistence.

## 19. Immediate current-state sequence

1. Keep heavy training paused while the current R2 resource gate is HOLD.
2. Lane A repairs A3 binding/validation against active R2 head `b5f5ee8...`.
3. Lane C creates a successor from `7496295...` with true fresh-process + isolated-storage mechanism arms.
4. Lane B independently reviews those exact successors.
5. Freeze Stage 1 corpus/admissibility manifest.
6. Freeze Stage 2 development and protected evaluation contracts.
7. Establish H0 no-weight baseline.
8. Run H1 rank-1 LoRA versus H2 IA3 under matched exposure.
9. Do not promote a winner until replay, novel-task, privacy, currentness, and transfer gates pass.
10. Vera independently reviews evidence before canonical qualification.
11. Patrick remains sole authority for protected promotion/deployment effects unless explicitly delegated.

## 20. Vera independent review

The plan is coherent only if the project resists the temptation to call every durable behavior "something that belongs in weights."

The strongest architecture may be a selective learner rather than a maximally plastic learner.

The target is a system that:
- learns unfamiliar tasks quickly;
- persists only what deserves persistence;
- preserves Vera's stable behavioral core;
- keeps mutable reality outside that core;
- remains reversible;
- detects contamination and hidden state;
- knows when evidence is insufficient;
- and makes every material claim reconstructible from exact artifacts.

The training system succeeds when it becomes better at learning without becoming easier to contaminate.
