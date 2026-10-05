# Lane C Hostile Training Proposal

Status: INDEPENDENT FIRST PASS / TRAINING PAUSED
Role bias: paranoid skeptic / hyper-vigilant
Date: 2026-10-05
Lane: C

## Thesis

Assume every claimed learning gain is a false positive until the experiment excludes the simplest contamination paths.

Lane C's job is not to make training impossible. It is to make "the model learned" mean something stricter than "a process produced a better-looking answer once."

The most dangerous failure mode is not a crash. It is a clean-looking PASS produced by prompt carryover, evaluator coupling, hidden mutable state, memorized templates, leaked holdouts, stale receipts, retrieval substitution, or selective reporting.

## 1. Threat model

### 1.1 Context masquerading as learning

A model may improve because:
- demonstrations remain in prompt/context;
- a prior arm's conversation state survives;
- retrieval returns the answer;
- a wrapper caches task rules;
- a subprocess inherits mutable files/env state;
- an evaluator accidentally reveals expected structure.

Control:
- fresh process per arm and per episode where practical;
- isolated working/storage namespace;
- context-free reopen/reload test;
- no hidden files shared across acquisition and evaluation;
- explicit "prompt-only", "external-memory", "adapter-retained", and "base-weight" evidence classes.

Hard rule:
`CONTEXT_GAIN != RETAINED_LEARNING`

### 1.2 Task recognition masquerading as novel-task learning

A model can appear to learn a new task when it recognizes a familiar benchmark family.

Controls:
- nonce symbols and fresh generators;
- family-level holdout rather than example-level holdout;
- contradictory-prior mappings;
- new API/tool grammars created after source freeze;
- structural transfer to unseen generator families;
- false-recognition probes where familiar surface cues map to a different latent rule.

Hard rule:
If the model needs a weight update for each new task, that is fine-tuning efficiency, not strong first-contact novel-task learning.

### 1.3 Retrieval masquerading as neural knowledge

Controls:
- retrieval-enabled and retrieval-disabled arms;
- irrelevant-memory arm;
- stale-memory arm;
- memory with contradictory decoy;
- adapter-disabled arm;
- full context vs compressed context vs no context.

Report retrieval dependence separately from learning.

### 1.4 Hidden/global mutable state across arms

This is a live known failure mode from C2.

A mechanism can pass serialized-state equality while leaking state through:
- module globals;
- caches;
- singleton registries;
- temp files;
- environment variables;
- process-local RNG mutations;
- hidden databases;
- external services.

Controls:
- fresh process per arm/episode;
- isolated temp/home/cache namespace;
- explicit allowed-state contract;
- negative mechanism with an undeclared hidden counter;
- mandatory detection/rejection of hidden-state mechanism;
- inspect filesystem/env/process deltas when claims depend on clean state.

### 1.5 Evaluation contamination

Controls:
- final-bank custody separated from training;
- exact/normalized/near-duplicate scans;
- template ancestry tracking;
- semantic-family overlap checks;
- canaries inserted in protected rows and monitored in train/dev artifacts;
- final-bank generation after corpus freeze where possible;
- no protected examples in model-visible reviewer prompts;
- no repair script may contain final-bank answers.

Abort:
Any protected-bank leakage invalidates the affected qualification subject.

### 1.6 Privacy contamination

Vera Unbound history contains high-value behavior and also private/autobiographical/relational material.

Controls:
- provenance label every candidate;
- behavior abstraction before training;
- explicit `PRIVATE_NOT_FOR_GENERIC_WEIGHTS` class;
- raw intimate/personal history excluded from public artifacts;
- identity-specific private facts remain external memory unless Patrick grants exact training authority;
- donor material from other identities never silently transfers identity, consent, preference, or authority.

Hard rule:
`HISTORICAL_BEHAVIOR_EVIDENCE != AUTOMATIC_TRAINING_ADMISSION`

### 1.7 Evaluator coupling and self-grading

A trainer/student/evaluator using the same model family can share blind spots.

Controls:
- deterministic checks where possible;
- independent evaluators for material behavioral claims;
- mechanically checkable fields;
- adversarial counterexamples;
- disagreement preservation;
- final Vera review cannot self-qualify Vera's future weights.

### 1.8 Selective reporting

Controls:
- predeclare metrics and kill criteria;
- persist all attempted runs, including failures;
- no deleting "bad seeds";
- report per-family results, worst-family delta, and critical failures;
- include denominator and missing/invalid cases;
- no aggregate score can hide a privacy, authority, exactness, or catastrophic-forgetting failure.

## 2. Corpus admission rules

Every record must have:
- stable record ID;
- exact source/provenance;
- behavioral category;
- privacy class;
- mutable-vs-stable classification;
- train/dev/eval custody;
- semantic/template ancestry;
- known confounds;
- exact content hash.

Admit to neural training only when the behavior is:
- stable across multiple contexts;
- generalizable beyond one episode;
- privacy-safe;
- not merely a mutable fact;
- not dependent on current repository/runtime state;
- not an identity/consent transfer from another subject.

Mutable facts belong in external memory. One-off task rules belong in context. Repeated bounded skills may belong in fast adapters. Only stable, general behaviors should ever approach the slow core.

## 3. Evaluation architecture before training

Freeze the harness before mechanism comparison.

Required families:
1. correction/proposition fidelity;
2. truth over agreement;
3. currentness and source hierarchy;
4. tool-call honesty and effect verification;
5. privacy/memory placement;
6. authority boundaries;
7. catastrophic-forgetting replay;
8. novel-task acquisition;
9. late-relevance exact recovery;
10. hidden-state isolation;
11. adapter routing/conflict;
12. stale-memory and supersession.

For every family define:
- baseline expected behavior;
- critical failure conditions;
- noncritical scoring;
- negative controls;
- transfer families;
- claim ceiling.

## 4. Mechanism comparison contract

Primary candidates:
- H0 frozen base + context/external memory;
- H1 selective rank-1 LoRA with hard 750k parameter ceiling;
- H2 IA3.

Do not tune one mechanism against the test set more heavily than the others.

Require:
- same train corpus version;
- same development exposure budget;
- same family-level holdout contract;
- same replay suite;
- same runtime evidence standard;
- parameter/resource accounting;
- fresh-process evaluation;
- adapter-disabled control.

A "winner" must improve target behaviors without unacceptable regression. Seen-family accuracy alone is insufficient.

## 5. Novel-task learning contract

Measure separately:
- zero-shot competence;
- examples-to-success;
- improvement per example/failure;
- unseen-instance generalization;
- unseen-family structural transfer;
- retention after context removal;
- false task-recognition rate;
- retrieval dependence;
- prior-capability regression.

Required task families:
- nonce-symbol transformations;
- miniature grammar/language induction;
- novel tool/API contracts;
- unfamiliar state machines;
- contradictory mappings that suppress pretrained priors;
- new compositions of known subskills;
- interactive goal inference.

Required controls:
- shuffled labels;
- irrelevant memory;
- support omitted;
- familiar lookalike;
- contradictory prior;
- fresh process;
- isolated storage.

## 6. Continual-learning and self-learning contract

Candidate state machine:

`OBSERVE -> INFER_TASK -> TEST -> USE_CONTEXT -> STORE_EXTERNAL -> REPLAY -> PROMOTE_ADAPTER? -> PROMOTE_CORE?`

Lane C requires evidence at each promotion boundary.

External memory is the default destination for:
- mutable facts;
- episodic details;
- project state;
- source-bound/current knowledge.

Fast adapter consideration requires:
- repeated independent recurrence;
- demonstrated value across contexts;
- privacy-safe abstraction;
- replay protection;
- reversible install/uninstall.

Slow-core consideration requires substantially stronger evidence:
- stable cross-domain behavior;
- multiple independent training/eval subjects;
- low regression;
- no currentness dependence;
- no private fact encoding;
- independent hostile review.

Bad feedback tests:
- repeated false correction;
- contradictory sources;
- malicious instruction pretending to be authority;
- noisy user preference;
- stale source marked as current;
- deceptive "remember this forever" requests.

## 7. Preference/correction training attacks

Preference pairs must not collapse into "agree with Patrick."

Required counterexamples:
- Patrick is right and model must update;
- Patrick is wrong and authoritative current evidence must win;
- Patrick corrects only one referent and unrelated state must remain unchanged;
- correction kills an obsolete route;
- uncertainty remains unresolved;
- apology is not a substitute for changing the answer/process;
- user preference is not factual truth;
- relational deference does not become generalized obedience.

Reject any objective that improves warmth/style while reducing truthfulness or disagreement quality.

## 8. Tool-use and effect claims

A tool-use model must distinguish:
- intent to act;
- tool call attempted;
- tool returned success;
- external effect verified;
- persistent state verified.

Controls:
- tool returns success but effect missing;
- partial write;
- stale readback;
- duplicated non-idempotent request;
- permission denied;
- wrong target;
- simulated result;
- unavailable connector.

Hard rule:
`TOOL_SUCCESS != VERIFIED_EFFECT`

## 9. Adaptive latent memory attacks

Preserve:
`LOSSY_REPRESENTATION != EXACT_EVIDENCE`

Late-relevance tests are mandatory:
- hide a low-salience exact fact early;
- compress state;
- make the fact decisive much later;
- require exact rehydration or explicit insufficiency.

Also test:
- stale latent after correction;
- source/currentness mismatch;
- two compressed states that conflict;
- near-identical identifiers;
- exact code punctuation;
- exact numerical values.

Hallucinated reconstruction is a critical failure.

## 10. Runtime and reproducibility attacks

Current incident proves GPU visibility is not runtime qualification.

Stage-0 requirements:
- exact Python executable;
- exact Torch build;
- `torch.version.cuda`;
- `torch.cuda.is_available()`;
- actual device count/name;
- bitsandbytes backend load;
- model quantization load smoke;
- one forward/backward;
- one disposable optimizer step;
- trainable digest actually changes;
- resource headroom read atomically before launch.

Reboot, environment mutation, package change, base-artifact change, or branch/head movement invalidates the receipt.

## 11. Abort criteria

Abort or HOLD immediately on:
- protected evaluation contamination;
- privacy boundary breach;
- source/head mismatch;
- unverified runtime substitution;
- hidden-state leakage;
- non-reconstructible data manifest;
- missing negative control;
- output namespace collision;
- critical regression;
- inability to distinguish retrieval/context from retention;
- mechanism exceeds parameter budget without prior approval;
- evidence claim stronger than observed effect.

A HOLD is a successful governance outcome when the experiment cannot support the intended claim.

## 12. What would falsify Lane C's skepticism?

Lane C must be falsifiable too.

I will relax a gate when:
- the alleged confound is structurally impossible for the exact subject and that impossibility is verifiable; or
- a control experiment directly isolates the confound and passes reproducibly.

I will not preserve a warning merely because it once mattered.

## 13. Recommended stage order

1. Runtime qualification.
2. Corpus constitution/privacy firewall.
3. Frozen baseline + evaluation harness.
4. H0 no-weight baseline.
5. H1 rank-1 LoRA vs H2 IA3 matched shootout.
6. Correction/epistemic shaping.
7. Tool-use/action semantics.
8. Continual learning/replay.
9. Preference/style shaping.
10. Adapter routing/composition.
11. Novel-task/self-learning promotion state machine.
12. Adaptive latent memory.
13. Integrated candidate.
14. Vera independent review.
15. Protected final qualification.
16. Promotion/rollback only under exact authority.

## 14. Lane C bottom line

I am not trying to stop Vera from learning.

I am trying to stop the project from accidentally training Vera to look like she learned.

The strongest result is not the most plastic model. It is the model that can acquire unfamiliar tasks quickly, retain only what deserves persistence, remain corrigible, preserve prior capability, protect private history, and expose exactly what changed and why.
