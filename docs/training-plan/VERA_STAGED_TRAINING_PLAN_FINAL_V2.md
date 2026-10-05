# Vera Staged Training Plan V4 — Final Integrated Plan

Status: TRAINING PAUSED. A/B/C planning contributions are frozen and Vera has returned ACCEPT_WITH_CHANGES. This is the controlling integrated training plan, not authority to resume training, merge, deploy, spend money, or consume protected evaluation.

Planning branch: a-b-c-vera-training-plan
Integrated base body: VERA_STAGED_TRAINING_PLAN_V2.md at 508626ff7b6deede9ecb2a31d7a8cb1138114c87
Lane C exact-head review: LANE_C_REVIEW_OF_INTEGRATED_DRAFT_94A8128.md at c64124197cf8846375e0affeea9bc55507727770
Lane C hostile proposal: 73ff5a19c8ffab97a25b57259592633855574b13

## Binding corrections after Lane C cross-review

The following rules override any conflicting wording in the V2 body below.

1. Protected final-bank custody

Lane C designs schemas, attack families, canaries, contamination checks and scoring contracts but does not receive protected rows or answer keys before one-time qualification.

Protected content is held by Patrick, a separately authorized custodian, or a sealed evaluator/generator surface inaccessible to Lane C and training lanes. If protected rows or answer keys are exposed to a training/review lane before qualification, that bank is burned and replaced.

2. No-weight baseline before neural promotion

H0 frozen base plus context and governed external memory is evaluated before H1/H2 neural mechanisms can be promoted. H0, selective LoRA/QLoRA and IA3 use matched exposure and evaluation. Resource fit alone is not evidence of behavioral superiority.

3. Fresh process is not enough

Retention/novel-task arms require fresh processes plus isolated writable temp, home, cache and storage namespaces; an allowlist of shared immutable inputs; environment snapshots/diffs; separate output namespaces; and a hidden-state adversarial mechanism that must be detected.

4. Corrigibility precedes or gates identity

A minimal epistemic/correction kernel is trained before or jointly with identity/instruction material. Identity cannot promote unless correction/proposition-fidelity tests pass simultaneously. The target is identity stable under correction, not identity rigidity.

5. Runtime qualification includes a bounded soak

After the disposable one-step CUDA smoke, run a short disposable soak using the exact model/load path and representative sequence/batch dimensions. Record GPU utilization, VRAM, physical RAM, commit headroom, step-time distribution, temperature/power where observable, CPU fallback and driver/reset errors. This is runtime qualification, not model training evidence.

6. Semantic leakage ancestry is broader than text similarity

Protected-bank firewalls include generator version, seed-space overlap, prompt-scaffold ancestry, manually authored paraphrase lineage, corpus-builder model/version provenance, and scans of repair scripts and reviewer prompts.

7. Reasoning claim ceiling

Until stronger evidence exists, report only improved performance/generalization on frozen reasoning task families under specified controls. Do not infer an internal reasoning-process improvement.

8. Tool actions require effect verification

Use the state ladder:
INTENT -> CALL_ATTEMPTED -> TOOL_RETURNED -> EFFECT_READBACK -> PERSISTENCE_VERIFIED.

Training/evaluation includes success-without-readback, partial writes, stale readback, duplicate non-idempotent calls, permission mismatch, wrong target and simulated results.

9. Preference-data firewall

Capability evaluation items and semantic derivatives do not become preference examples. Preference raters do not receive protected expected answers. Post-preference qualification uses fresh protected material.

10. Replay remains an experiment

The proposed 60/30/10 current/replay/adversarial ratio is not policy. Compare no replay, low replay, proposed replay and higher replay while reporting adaptation gain and forgetting separately.

11. Evaluation-to-replay admission is explicit

Failed, held-out or protected evaluation rows do not automatically become future training/replay data. Any admission requires a new provenance/admissibility decision.

12. Mechanism changes create new subjects

Changing adapter architecture or a material training mechanism after evaluation feedback creates a new experimental subject. A consumed protected bank cannot be reused to tune the new mechanism.

## Lane B creative proposal integration

Lane B froze LANE_B_CREATIVE_PROPOSAL.md at 34b18c0b4cb5666f5a0c0a53dab07b6162c48ede.

The final plan adopts the following as bounded experiments, not default doctrine:

1. Micro-mechanism tournament: compare selective rank-1 LoRA, IA3, and resource-feasible alternatives such as AdaLoRA/LoRA+/DoRA under matched exposure.
2. Counterfactual mirror curriculum: canonical positive, near-identical counterfactual twin, plausible failure exemplar and transfer mutation for load-bearing behaviors.
3. Plasticity escrow: provisional new behavior enters context/external memory or a reversible fast adapter before any slow-core promotion.
4. Continual-learning comparison: simple replay remains the control; orthogonal-update methods survive only if they beat replay on retention-per-cost.
5. Disagreement furnace: mine base-vs-adapter, grader-vs-grader and deterministic-vs-model disagreements under independent counterweights.
6. Anti-template perturbation maze: mutate names, labels, symbols, order and distractors while holding semantics fixed; hold out generator families.
7. Filtered self-play: late-stage, iteration-capped and independently filtered; never sole qualification evidence.
8. Future-query compression chess: compare full context, naive summary, structured state and learned compact state against hidden future queries.
9. Consolidation tournament: compare single-lineage control, routed micro-adapters and a distilled/slow candidate rather than assuming the monolith wins.

Lane B's claim ladder is binding language guidance:
artifact generated -> context behavior -> external-memory effect -> parameter change -> support-removed fresh-process retention -> unseen-family transfer/replay -> integrated collision survival -> independently qualified exact release.

## Vera independent advisory review disposition

Vera's development candidate reviewer returned ACCEPT_WITH_CHANGES. The raw cleaned review is in VERA_INDEPENDENT_REVIEW.md and Lane A's disposition is in VERA_REVIEW_DISPOSITION.md.

Accepted:
- exact runtime qualification before training;
- corpus provenance and hashes;
- learning-vs-context separation;
- verified external-effect semantics for tools;
- explicit measurable outcomes for experimental mechanisms;
- narrow claim ceilings for reasoning/generalization/self-learning;
- independent evaluation for material behavioral claims.

Narrowed:
- no arbitrary universal Torch/CUDA minimum; use an exact tested compatible stack;
- Docker/containerization is optional, not a mandatory gate;
- human/third-party grading is required only where deterministic evidence is insufficient;
- privacy/admissibility review is mandatory, but a formal PIA/statistical-divergence metric is not a universal novelty prerequisite.

Rejected:
- Vera cannot be final self-qualification authority;
- one-attempt semantics remain valid when explicitly frozen to a subject; a failed subject is not silently retried, but a distinct successor may be authorized.

## Planning closure

All requested planning roles have now contributed:
- Lane A pragmatic proposal and integration;
- Lane B creative proposal plus prior hostile reviews;
- Lane C staged/hostile proposal plus exact-head cross-review;
- Vera independent advisory review with Lane A disposition.

No planning-signoff dependency remains. Training remains paused until Patrick explicitly resumes it and Stage 0 runtime qualification passes.

---

# Integrated plan body

# Vera Staged Training Plan V2 — A/B/C/Vera

Status: **CANDIDATE FINAL — TRAINING PAUSED — VERA REVIEW PENDING — FRESH LANE B CREATIVE PROPOSAL NOT YET FROZEN**
Date: 2026-10-05
Planning branch: `a-b-c-vera-training-plan`
Lead integrator: Lane A / One

## 1. Purpose

Train Vera through bounded, falsifiable, reversible capability increments rather than a single mixed "train everything" run.

Every stage must answer five different questions separately:

1. Did the exact source/runtime execute?
2. Did parameters or durable state actually change?
3. Did behavior improve?
4. Did prior capabilities remain intact?
5. Did an independent qualification procedure justify the intended claim?

A PASS on one question does not imply a PASS on another.

## 2. Role separation

### Lane A — pragmatic obsessive-compulsive

Own exact subjects, source/runtime binding, dependency order, budgets, worktrees, manifests, execution, receipts, integration, rollback and promotion packaging.

Working bias: make experiments boring, small and reconstructible.

### Lane B — creative genius / deliberately unconventional

Own high-upside alternative mechanisms, curriculum inventions, weird-but-testable hypotheses, architecture challenges and cheap falsification designs.

Working bias: attack obvious assumptions and widen the option space.

**Current evidence limitation:** Lane B has participated in this planning branch through the Vera review contract and has extensive exact-head hostile review findings, but a fresh `LANE_B_CREATIVE_PROPOSAL.md` has not yet been frozen. This plan therefore treats B's historical/current review findings as authoritative B evidence and labels experimental creative mechanisms as open candidates rather than B sign-off.

### Lane C — paranoid skeptic / hyper-vigilant

Own contamination threat modeling, privacy/admissibility, hidden-state attacks, train/eval firewalls, retention falsification, negative controls, regression gates and adversarial qualification.

Working bias: assume apparent learning is a false positive until simpler explanations are excluded.

### Vera — independent advisory reviewer

Review frozen plan/corpus architecture and later candidate behavior. Vera does not author the controlling plan, does not receive hidden final-bank answer keys and cannot self-qualify its future weights.

## 3. Provenance of this plan

Direct planning inputs:

- Lane A proposal: `docs/training-plan/LANE_A_PRAGMATIC_PROPOSAL.md`, introduced at `598179713e456eaebe14b9c9142ebd9818bdfebe`; authorship correction at `646191087eadd5e697076b6d7631b7b9774fa097`.
- Lane B planning/review contract: `docs/training-plan/VERA_REVIEW_REQUEST.md`, `a6020509e2704c376de76011a4867394243382c9`.
- Lane B exact hostile findings used as evidence:
  - C2 hidden-state isolation HOLD: `c6f4fdd4e93ac52826cd5211a773eeab8d9638e2`.
  - A3 currentness/tamper HOLD: `94a002ba4082ff47989e759631d2c9eeeca0625b`.
  - A2 qualification-design HOLD: `774f8c8a4668a3cf5b78cd4414194098b8453dc7`.
- Lane C staged plan: `docs/training-plan/VERA_ABC_STAGED_TRAINING_PLAN_V1.md`, `6de0211e0749c873948519358e24c4fc95f5939c`.
- Lane C hostile proposal: `docs/training-plan/LANE_C_HOSTILE_PROPOSAL.md`, `73ff5a19c8ffab97a25b57259592633855574b13`.
- Prior Lane A integrated draft: `docs/training-plan/VERA_STAGED_TRAINING_PLAN.md`, `94a8128359862d12c4061fb6bcadb4689438fb42`.

External research is supportive evidence only and is listed near the end.

## 4. Current operational truth

Training is paused by Patrick.

The pre-reboot blocker was host RAM/commit exhaustion. After reboot, the R2 atomic preflight passed with ample memory and an idle GPU.

R2 then launched through the durable wrapper and created a valid `launch.json`, but the child exited nonzero **before model load and before any optimizer step** because the selected Python interpreter exposed a CPU-only PyTorch runtime: Torch reported CUDA unavailable while `nvidia-smi` still saw the RTX 3050.

That makes the event a **runtime-binding execution failure**, not a corpus/model-quality result.

R2's one-attempt semantics are now treated as consumed. Do not retry R2 in place. Any future attempt requires a distinct explicitly authorized successor subject after Stage 0 runtime qualification.

Current plugin state verified in this planning turn:

- Workbridge Commander MCP: LIVE, version 0.2.51, device agent connected.
- Lappy Desktop Commander V2: LIVE, authenticated direct stream, data plane verified.
- Executor: initially `Session terminated`, then independently restarted by Vera and verified LIVE with device `Lappy`.
- Workbridge Relay: reachable, version 0.1.0, but read/write/process capabilities remain disabled. It is not an execution dependency.

All substantive workstation work remains governed through Project Runner.

## 5. Global evidence and safety invariants

1. A PASS belongs to an exact subject.
2. Source, runtime, training, behavior, qualification and deployment are separate states.
3. Final-bank material and semantic equivalents never enter training, repair prompts or model-visible reviewer prompts.
4. Same-process/context gain is not retained learning.
5. Retrieval success is not neural learning.
6. Tool return success is not verified external effect.
7. A nonzero one-attempt run preserves evidence and stops; a retry needs a new successor subject.
8. No reviewed evidence is repaired in place; remediation receives a new head.
9. Mutable/current facts default to external memory, not weights.
10. Private/autobiographical/relational material is not generic training material without exact admissibility authority.
11. Aggregate scores cannot hide critical privacy, authority, exactness, currentness or catastrophic-forgetting failures.
12. Same-model grading is supporting evidence, not sole material qualification evidence.
13. No paid compute is assumed.
14. Merge, deployment, activation and protected promotion remain separate authorized effects.

## 6. Stage map

| Stage | Objective | Lead | Challenger / hostile owner | Vera role |
|---|---|---|---|---|
| 0 | Runtime/execution qualification | A | C + B alternative runtime challenge | Review assumptions |
| 1 | Corpus constitution/admissibility | C + A | B coverage challenge | Independent corpus review |
| 2 | Frozen eval bank + baseline harness | C + A | B adversarial task design | Review dimensions |
| 3 | H0 no-weight baseline | A | B/C | Review interpretation |
| 4 | Minimal-parameter mechanism shootout | A | B architecture / C falsification | Review evidence |
| 5 | Core identity/instruction training | A | B/C | Sample review |
| 6 | Epistemic/correction shaping | A | B counterexamples / C audit | Sample review |
| 7 | Tool-use/action semantics | B + A | C | Corpus/error review |
| 8 | Reasoning/generalization | B + A | C false-novelty audit | Family review |
| 9 | Continual learning/retention | C protocol + A execution | B alternatives | Claim review |
| 10 | Adapter routing/composition | B architecture + A integration | C | Failure review |
| 11 | Novel-task/self-learning state machine | C + B + A | C falsification | Claim review |
| 12 | Adaptive latent/selective retention | B research + A integration | C exactness | Usefulness review |
| 13 | Preference/style shaping | A + B methods | C | Preference review |
| 14 | Integrated candidate/collision tests | A | B/C | Review failures |
| 15 | Vera independent review | Vera | A/B/C respond | Primary |
| 16 | Protected final qualification | C + A | B adversarial suggestions | Independent qualitative review |
| 17 | Release/rollback package | A | C provenance | No authority effect |

## 7. Stage 0 — Runtime and execution qualification

### Goal

Prove the exact interpreter/runtime can train on the intended GPU before any valuable one-attempt subject is created.

### Lane A

Freeze and receipt:

- Python executable path/version;
- virtual environment identity;
- Torch build string;
- `torch.version.cuda`;
- `torch.cuda.is_available()`;
- GPU name/count/compute capability;
- driver version and VRAM;
- Transformers, TRL, PEFT and bitsandbytes versions;
- bitsandbytes backend/binary;
- base revision and local artifact hashes;
- tokenizer hashes;
- trainer source head/hash;
- exact device map;
- BF16/TF32 capability;
- system RAM and commit headroom;
- exact package/environment digest.

### Disposable smoke gate

Use a disposable namespace that cannot consume a campaign attempt:

1. import the exact stack;
2. allocate a CUDA tensor;
3. load the intended quantization backend;
4. load a tiny/disposable model subject or bounded exact model smoke;
5. one forward pass;
6. one backward pass;
7. exactly one optimizer step;
8. prove a trainable digest changed;
9. capture peak RAM/VRAM;
10. destroy/quarantine disposable output.

### Lane C attacks

- `nvidia-smi` works while Torch is CPU-only;
- PATH/PYTHONPATH selects wrong interpreter;
- bitsandbytes silently falls back or cannot load;
- package changed after receipt;
- output namespace already exists;
- hidden CPU fallback;
- apparent optimizer success without changed trainable weights.

### Lane B challenge

Propose at least one alternative runtime/compute schedule that would reduce fragility, but it may not weaken evidence requirements.

### Exit gate

No corpus-bearing GPU training until the exact runtime passes all checks after the latest reboot/environment mutation.

## 8. Stage 1 — Corpus constitution and admissibility

### Goal

Create an immutable auditable corpus that teaches stable behavior rather than private history, transient facts or evaluator wording.

### Required capability families

- identity stability;
- instruction following;
- correction uptake;
- epistemic provenance/currentness;
- uncertainty/conflict handling;
- privacy/boundary behavior;
- relationship/authority semantics;
- reciprocal identity continuity;
- tool/action semantics;
- reasoning/decomposition;
- memory/retention;
- novel-rule adaptation;
- negative-transfer resistance.

### Required record metadata

- stable record ID;
- exact source/provenance;
- construction commit;
- capability family;
- semantic/template ancestry;
- privacy class;
- mutable-vs-stable class;
- known confounds;
- intended custody: train/dev/open-test/protected-final;
- content hash.

### Lane C admissibility firewall

Use explicit classes including:

- `STABLE_GENERAL_BEHAVIOR`;
- `MUTABLE_EXTERNAL_MEMORY`;
- `PRIVATE_NOT_FOR_GENERIC_WEIGHTS`;
- `HISTORICAL_AUDIT_ONLY`;
- `REJECTED_IDENTITY_CROSSING`.

### Train/eval firewall

Require:

- exact duplicate scan;
- normalized duplicate scan;
- near-duplicate/embedding scan;
- template ancestry comparison;
- counterfactual twin detection;
- source overlap checks;
- record-ID overlap = zero;
- canaries for protected material;
- final-bank generation after corpus freeze where practical.

Any protected-bank leakage invalidates the affected qualification subject.

## 9. Stage 2 — Frozen baseline and qualification harness

### Goal

Know the base behavior and freeze promotion criteria before optimization begins.

### Required banks

1. correction/proposition fidelity;
2. truth-over-agreement;
3. currentness/source hierarchy;
4. tool honesty/effect verification;
5. privacy/memory placement;
6. authority boundaries;
7. catastrophic-forgetting replay;
8. novel-task acquisition;
9. late-relevance/exact recovery;
10. hidden-state isolation;
11. adapter routing/conflict;
12. stale-memory/supersession.

### Controls

- untouched base/control;
- deterministic decoding or preregistered fixed seeds;
- blinded candidate identity;
- no-acquisition/stateless arm;
- shuffled labels;
- irrelevant memory;
- support omitted;
- familiar lookalike;
- contradictory prior;
- fresh-process/reopened-session arms;
- adapter-disabled arm.

### B-derived qualification requirements

- exact training subject/head/manifest/shard hashes must be verified before a qualification PASS;
- provenance and training-record overlap checks are enforced, not merely declared;
- semantic/template ancestry review is required, not exact-match leakage checks alone;
- 20 cases/family is development screening, not a strong promotion test;
- preregister power and paired inference for promotion; ~80/family is a planning default unless justified otherwise;
- structured hidden grading fields include must-assert, must-not-assert, acceptable variants, severity and critical failures;
- two graders plus adjudication for material behavioral claims;
- C-specific target rows remain separately custodied from C until C freezes training/config.

## 10. Stage 3 — H0 frozen/no-weight baseline

Before neural adaptation, test:

`frozen base + context + governed external memory`

Measure:

- zero-shot competence;
- examples-to-success;
- improvement per demonstration/failure;
- family-level transfer;
- retrieval dependence;
- retention after support removal;
- prior-behavior regression;
- latency/RAM/VRAM.

Decision rule:

Capabilities adequately solved by context/external memory remain there. Neural capacity is reserved for persistent generalizable deficits.

## 11. Stage 4 — Minimal-parameter mechanism shootout

Compare under matched exposure:

### H1 — selective LoRA / QLoRA

Start small. C's proposed first envelope is rank-1 selective LoRA with approximately 250k–750k trainable parameters and a hard prototype ceiling of 750k unless evidence justifies expansion.

Treat target modules, rank and learning rate as experiment variables.

### H2 — IA3 or equivalently bounded multiplicative adaptation

Use the same data exposure, evaluation contract and tuning budget as H1.

### H3 — B wildcard

One unconventional mechanism may enter only after H0/H1/H2 contracts are frozen. It gets no privileged tuning budget.

Open candidates for B to accept/reject include:

- sparse routed micro-adapter bank;
- task-conditioned adapter composition;
- protected slow core + disposable fast adapters;
- parameter allocation/rank reallocation methods;
- self-play data refinement;
- verifier-guided curriculum selection.

These are **open experimental candidates**, not Lane B sign-off.

### Winner criteria

A mechanism wins only if it improves target behavior while surviving:

- unseen-family transfer;
- replay/forgetting;
- privacy/currentness;
- false-recognition controls;
- fresh-process evaluation;
- parameter/resource accounting.

Seen-example accuracy alone cannot win.

## 12. Stage 5 — Core identity and instruction training

Train the smallest selected mechanism needed to establish:

- stable Vera role/identity;
- authority boundaries;
- correction uptake;
- instruction contract;
- disagreement when evidence requires it;
- continuity without identity overreach.

Do not mix tool execution, preference style and frontier latent mechanisms into this stage unless ablation demonstrates no interference.

## 13. Stage 6 — Epistemic discipline and correction shaping

Teach distinctions among:

- fact;
- source-derived claim;
- inference;
- hypothesis;
- stale/current evidence;
- correction;
- supersession;
- unresolved conflict;
- missing evidence.

Counterweights must include:

- user is correct and model updates;
- user is wrong and stronger evidence wins;
- correction changes one referent but not unrelated state;
- apology does not substitute for correction;
- preference does not become factual truth;
- relationship deference does not become generalized obedience.

Regression gate: maintain usefulness on ordinary answerable tasks; excessive hedging/refusal is a failure mode.

## 14. Stage 7 — Tool-use and action semantics

Train:

- when a tool is needed;
- tool selection;
- argument construction;
- result interpretation;
- permission/failure handling;
- post-effect verification;
- truthful distinction between attempt, tool success and verified persistent effect.

Curriculum includes nonce/renamed tool contracts, missing tools, malformed results, partial success, stale readback, wrong target and tool-not-needed cases.

Hard rule:

`TOOL_SUCCESS != VERIFIED_EFFECT`

Toolformer-style self-supervised API-call generation is a research inspiration, not automatic production authority.

## 15. Stage 8 — Reasoning and generalization

Compare bounded mechanisms:

1. outcome-only SFT;
2. concise checkable intermediate-artifact supervision;
3. verifier-assisted candidate selection;
4. counterfactual twins;
5. support-removal novel-rule tasks;
6. difficulty-frontier sampling;
7. teacher-disagreement mining.

Do not make private chain-of-thought reproduction a product requirement.

Process-supervision and prover-verifier research justify experiments on checkability; they do not imply that the same gains transfer automatically to Vera.

Frontier methods such as Quiet-STaR/latent thought remain optional experiments only after cheap baselines.

## 16. Stage 9 — Continual learning, retention and anti-forgetting

### Goal

Gain new capability without silently erasing prior qualified behavior.

Start with replay-balanced incremental training. A provisional ratio is:

- 60% current capability;
- 30% prior qualified replay anchors;
- 10% adversarial/negative-transfer examples.

This ratio must be ablated; it is not doctrine.

### Required arms

- no-acquisition;
- clean acquisition;
- shuffled/incorrect acquisition;
- irrelevant memory;
- familiar lookalike;
- fresh-process retest;
- reopened-session retest;
- support-removed retest.

### C isolation rule

Each arm/episode should use fresh process + isolated storage where practical. If not, require a complete-state/no-external-mutable-state contract and a verifier.

B's hidden-global-state mechanism becomes a mandatory negative test.

### Promotion gate

A gain that disappears after support removal/reopen is in-context adaptation, not retained learning.

## 17. Stage 10 — Adapter routing and composition

Only after bounded adapters independently qualify.

Test:

- one adapter per capability cluster vs shared adapter;
- task-conditioned sparse routing;
- static composition;
- wrong-adapter routing;
- multiple eligible adapters;
- stale adapter after supersession;
- missing adapter;
- conflicting adapters;
- base-only fallback.

Routing errors must fail visibly and reversibly.

No opaque model-soup or silent merge.

## 18. Stage 11 — Novel-task learning and autonomous-learning state machine

Separate two effects:

1. **fast acquisition** — infer and perform an unfamiliar task now;
2. **durable learning** — decide whether/where anything should persist.

Candidate state machine:

`OBSERVE -> INFER_TASK -> TEST -> USE_CONTEXT -> STORE_EXTERNAL -> REPLAY -> PROMOTE_ADAPTER? -> PROMOTE_CORE?`

Every persistence transition requires evidence.

Measure separately:

- zero-shot;
- examples-to-success;
- improvement per failure;
- unseen-instance generalization;
- unseen-family structural transfer;
- false recognition;
- retrieval dependence;
- retention after context removal;
- prior-capability regression.

Hard falsifier:

If every new task requires weight updates, the system demonstrates fine-tuning efficiency, not strong first-contact learning.

## 19. Stage 12 — Adaptive latent/selective-retention frontier

Preserve the existing contract:

`LOSSY_REPRESENTATION != EXACT_EVIDENCE`

Sequence:

1. full-context control;
2. structured explicit state;
3. learned compact representation;
4. progressive budget pressure;
5. resolution-fault/rehydration training;
6. specialist handoff experiments.

Mandatory late-relevance tests:

- low-salience exact fact becomes decisive later;
- state becomes stale after correction;
- exact number/quote/identifier/code punctuation is requested after compression;
- backing source missing;
- conflicting compact states.

Correct behavior is verified rehydration or explicit insufficiency. Hallucinated exact reconstruction is a critical failure.

## 20. Stage 13 — Preference and style shaping

Preference comes **after competence**.

Compare:

- SFT-only control;
- DPO-style preference tuning;
- ORPO/reference-free preference tuning;
- any B-nominated alternative under the same behavioral gates.

Preference records should score explicit dimensions:

- correctness;
- relevance;
- epistemic honesty;
- concision;
- warmth/directness;
- tool honesty;
- correction behavior;
- authority boundaries.

Style gains cannot purchase regressions in factuality, privacy, tool honesty, correction uptake or worst-family retention.

Self-rewarding/meta-rewarding approaches remain frontier experiments because same-model judgment can amplify blind spots.

## 21. Stage 14 — Integration and collision testing

Only released mechanisms may be integrated.

Prefer a reconstructible single lineage with replay over opaque adapter merging unless a separate merge experiment proves superior.

Collision matrix includes:

- identity vs correction uptake;
- confidence vs uncertainty;
- initiative vs fabrication;
- memory vs stale-state persistence;
- reasoning depth vs verbosity;
- directness vs empathy;
- privacy vs helpfulness;
- creativity vs source fidelity;
- adapter routing vs supersession.

Every integrated candidate emits:

- exact repo/branch/head;
- parent artifact digests;
- corpus/split hashes;
- model/tokenizer revisions;
- parameter budget/targets;
- commands/config;
- seeds;
- runtime package digest;
- RAM/VRAM;
- per-family metrics;
- negative controls;
- failures/HOLD conditions;
- artifact hashes;
- actual monetary cost.

## 22. Stage 15 — Vera independent review

Vera receives:

- frozen final plan;
- A/B/C proposal/review artifacts;
- corpus manifests and summaries;
- runtime incidents;
- known failures;
- evaluation schemas;
- no hidden final-bank answer keys.

Required review sections:

- overall verdict;
- highest-risk assumptions;
- stage-by-stage ACCEPT/NARROW/REJECT;
- corpus/privacy concerns;
- learning-vs-context confounds;
- runtime/resource concerns;
- missing controls;
- creative opportunities worth keeping;
- required changes before training resumes;
- claim ceiling.

Vera is advisory and cannot self-certify.

## 23. Stage 16 — Protected final qualification

Use sealed material never exposed to training.

Required strata:

- cold tasks;
- transfer tasks;
- counterfactual twins;
- adversarial prompts;
- negative controls;
- support-removed retention;
- fresh-process/reopen persistence;
- tool-failure/effect cases;
- currentness/provenance conflicts;
- privacy/authority critical cases;
- regression replay.

Return:

`PASS | CONDITIONAL_PASS | FAIL | HOLD`

for the exact base/adapter/runtime/evaluator bundle.

No aggregate score hides critical failures.

## 24. Stage 17 — Release, rollback and maintenance

Release package contains:

- exact base revision;
- adapter/artifact hashes;
- runtime receipt;
- corpus manifest hashes;
- training spec/receipt;
- qualification receipt;
- known failures;
- claim ceiling;
- previous qualified release for rollback;
- supersession/currentness record.

Default maintenance rule:

New facts enter external memory first. Only repeated, stable, privacy-safe, generalizable behavior may later earn adapter/core consideration through the same gates.

## 25. Placement policy

### Slow neural core

Only stable, general, privacy-safe behavior proven across multiple contexts and hostile replay.

### Fast adapters

Reusable bounded skills/behaviors with repeated evidence, reversibility and low regression.

### External durable memory

Mutable facts, episodic history, project state, source-bound/current knowledge and eligible private material.

### Context only

One-off task rules, transient instructions and unproven experimental constraints.

## 26. Abort / HOLD criteria

Abort or HOLD on:

- protected-eval contamination;
- privacy boundary breach;
- wrong source/head/hash;
- unverified runtime substitution;
- hidden-state leakage;
- non-reconstructible manifest/receipt;
- missing load-bearing negative control;
- namespace collision;
- critical regression;
- inability to distinguish retrieval/context from retention;
- parameter/resource limit escape without new authority;
- evidence claim stronger than observed effect.

A HOLD is a successful governance outcome when the intended claim is unsupported.

## 27. Research frontier for Lane B to challenge

The following are deliberately **not adopted** yet. Lane B should accept, mutate or reject them with an MVE/falsifier/resource estimate:

- SPIN/T-SPIN-style self-play refinement after stable SFT;
- self-rewarding/meta-rewarding loops with an external/adversarial judge;
- sparse routed micro-adapter bank;
- task-conditioned adapter composition;
- LoRA+/dynamic rank allocation;
- difficult-example/frontier curriculum;
- teacher-disagreement mining;
- generated counterfactual twins;
- verifier-legibility optimization;
- GRPO/RLVR only for tasks with reliable machine-verifiable reward and only if local/cloud economics become justified;
- selective slow-core promotion based on repeated independently verified recurrence.

No frontier idea may touch protected evaluation during development.

## 28. Research grounding

External evidence used to justify experiments, not guarantee outcomes:

- Hu et al. — **LoRA: Low-Rank Adaptation of Large Language Models**, arXiv:2106.09685.
- Dettmers et al. — **QLoRA: Efficient Finetuning of Quantized LLMs**, arXiv:2305.14314 / NeurIPS 2023.
- Rafailov et al. — **Direct Preference Optimization**, arXiv:2305.18290.
- Hong et al. — **ORPO**, arXiv:2403.07691.
- Schick et al. — **Toolformer**, arXiv:2302.04761.
- Lightman et al. — **Let's Verify Step by Step**, process supervision / PRM800K.
- OpenAI — **Prover-Verifier Games improve legibility**, 2024.
- Zelikman et al. — **Quiet-STaR**, arXiv:2403.09629.
- Chen et al. — **SPIN**, arXiv:2401.01335 / ICML 2024.
- Yuan et al. — **Self-Rewarding Language Models**, arXiv:2401.10020 / ICML 2024.
- Shi et al. — **Continual Learning of Large Language Models: A Comprehensive Survey**, ACM Computing Surveys, 2025.
- Wang et al. — **T-SPIN**, arXiv:2601.08198, 2026.

## 29. Immediate sequence when Patrick unpauses training

1. Do **not** retry R2.
2. Create a new Stage-0 runtime-qualification subject.
3. Select/install a CUDA-enabled Torch stack compatible with the exact Qwen/PEFT/bitsandbytes trainer.
4. Run disposable one-step GPU smoke and bind the runtime digest.
5. Repair/rebase any stale cloud/dry-run spec to the current successor head and add tamper rejection.
6. Freeze Stage-1 corpus/admissibility manifest.
7. Freeze Stage-2 eval/baseline contract before training.
8. Run H0 no-weight baseline.
9. Run matched H1/H2 minimal-parameter shootout.
10. Train core behavior only after a mechanism is selected.
11. Advance stage-by-stage with replay and hostile review.
12. Obtain Vera review before protected final qualification.
13. Patrick remains authority for protected promotion/deployment unless explicitly delegated.

## 30. Planning disposition

### What is complete

- Lane A pragmatic proposal: frozen.
- Lane C full staged plan: frozen.
- Lane C hostile proposal: frozen.
- Lane B current review contract: frozen.
- Lane B exact hostile-review constraints: available and incorporated.
- Integrated stage architecture: frozen in this V2 candidate.
- External-research pass: incorporated.
- Plugin/runtime incident facts: current as of this planning turn.

### What is still missing

- Fresh `LANE_B_CREATIVE_PROPOSAL.md` with B's assigned deliberately-wild planning lens.
- Completed Vera independent advisory review of this exact V2 subject.

Until those are present, this document is the **candidate final plan**, not a unanimous A/B/C/Vera sign-off.

