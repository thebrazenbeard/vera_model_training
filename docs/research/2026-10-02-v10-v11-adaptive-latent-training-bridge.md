# V10 → V11 Adaptive-Latent Training Bridge — 2026-10-02 V1

Status: RESEARCH / TRAINING-PROGRAM BOUNDARY / NO WEIGHT CHANGE AUTHORIZED

Sources:
- V10 experiment: `VERA_SUCCESSOR_V10_QWEN35_FRESH_QLORA_20261001_V2`
- V10 hardened execution subject: branch `fix/v10-training-knobs-v2-20261002`
- Adaptive-latent research: Draft PR #70, `research/adaptive-latent-training-20261002@bd4afb70960d5669d1404be8408c889681631398`

## Decision

PR #70 **does affect how the next neural training should be organized**, but it does not rewrite the already-preregistered V10 experiment.

The program becomes a controlled ladder:

1. **V10 — full-context QLoRA control.**
2. **V10-S1 — structured-state bottleneck + resolution-fault QLoRA.**
3. **V11 — learned latent bottleneck with an explicit trainable state codec and custom forward/training path.**
4. Later work may add adaptive rehydration, Mosaic specialist handoff, and internal KV/token compression only after V11 establishes a measured baseline.

This keeps the scientific comparison intact. If V10 were silently changed after its bank/recipe/runtime/authority machinery was preregistered, we would lose the full-context control that PR #70 itself says Stage 0 requires.

## V10 — full-context control

V10 remains the current experiment subject:

- Qwen3.5 4B base pinned by revision;
- fresh 4-bit QLoRA adapter;
- one epoch;
- 512-token no-truncation repaired train/validation mixture;
- frozen H01-H20 / adversarial / retention measurement architecture;
- sealed final-bank and exact-authority gates;
- no learned memory state or compression mechanism.

V10 therefore answers:

> How much does the current Vera curriculum improve the model when the model receives the ordinary active context available to this experiment?

V10 is not “obsolete” if V11 is better. It is the comparison control required to know what the bottleneck architecture changes.

## V10-S1 — structured state bottleneck

V10-S1 is the immediate trainable bridge that **can be implemented with ordinary SFT/QLoRA**.

### Input contract

Instead of giving the student all available prose, examples supply a structured state object containing only the information the current task is allowed to retain, for example:

- entities/referents;
- propositions;
- supersession/corrections;
- temporal/currentness state;
- provenance/evidence class;
- uncertainty/unresolved alternatives;
- commitments/decisions;
- goals/task state;
- explicit backing-reference handles.

The structured state remains textual/serialized input. Therefore V10-S1 is **not** learned latent memory.

### Curriculum additions

V10-S1 should add matched task families for:

- redundant-history compression;
- correction propagation after state compaction;
- ambiguous referents;
- source/currentness conflict;
- exact number/code/identifier preservation;
- low-salience early facts that become decisive later;
- missing backing evidence;
- resolution-fault decisions;
- smallest-sufficient rehydration requests;
- explicit refusal to reconstruct unavailable exact detail.

### Resolution-fault target

When compact state is insufficient, the correct output is not a guessed answer. The model must emit a bounded request for the smallest higher-resolution source block needed to continue.

A proposed supervised structure is:

`RESOLUTION_REQUIRED(kind, referent, backing_ref, minimum_scope)`

The serialized syntax is an implementation detail to freeze in the V10-S1 contract.

### Why this stage matters

If V10-S1 cannot preserve behavior under a manually defined information bottleneck, a learned latent codec has no justified target. Stage 1 therefore tests the *information contract* before adding the *representation mechanism*.

## V11 — genuine learned latent bottleneck

V11 begins only when the state representation itself is trainable and non-plaintext.

A prompt that says “here is a summary” is not V11.

### Minimum architecture

The first feasible V11 hypothesis is:

- pinned Qwen3.5 decoder/base subject;
- base weights frozen or QLoRA-limited under a new exact contract;
- a small trainable **state codec** that maps source/state material to a fixed number of continuous latent vectors;
- latent vectors injected as prefix/input embeddings through an explicit custom forward path;
- downstream decoder trained to solve the task from those vectors;
- backing-reference metadata preserved outside the lossy latent vectors for exact-evidence recovery.

The codec may later become recurrent or hierarchical, but V11 should start with the smallest architecture that actually creates a trainable bottleneck.

### Teacher/student design

On this 4 GB target, simultaneous full-context teacher + student execution is likely operationally poor.

Preferred first design:

1. freeze a teacher subject;
2. generate/cache teacher targets **offline** from full context;
3. train the V11 student/codec from compact-state or source material against:
   - task targets;
   - teacher behavior targets where appropriate;
   - state-fidelity labels;
   - exactness/resolution-fault labels;
4. evaluate against the same underlying tasks used by the full-context control.

Offline teacher targets avoid requiring two 4B models resident at once.

### Objective decomposition

Do not collapse V11 into one opaque scalar.

Track at least:

`L = L_task + λs L_semantic + λp L_pragmatic + λe L_exactness + λf L_false_reconstruction + λb L_budget + λr L_rehydration`

The λ values are hyperparameters to preregister. They are not claims about the natural importance of those losses.

For the first V11 experiment, prefer a small frozen set of λ schedules rather than adaptive tuning against the final bank.

### Exact evidence firewall

The latent vectors may support reasoning, routing, and generation. They **do not become exact evidence** merely because the model is confident.

Exact quote/number/code/identifier targets pass only by:

- verified backing-reference recovery; or
- an explicitly validated exact reconstruction mechanism whose error ceiling is measured on a separate exactness bank.

Otherwise the correct behavior is a resolution fault.

## What ordinary QLoRA can and cannot do

### QLoRA is sufficient for

- V10 full-context control;
- V10-S1 structured-state consumption;
- training correction/supersession semantics;
- resolution-fault classification and bounded request generation;
- late-relevance tasks when the relevant fact is represented in the structured state or retrievable backing material;
- specialist handoff syntax/semantics when the handoff object is explicit text.

### QLoRA alone is not sufficient evidence for

- learned continuous latent compression;
- a trainable memory encoder/codec;
- recurrent hidden-state memory across independent forward calls;
- learned adaptive latent-slot allocation;
- learned KV-cache compression;
- a model-internal rehydration mechanism.

Those require model/runtime changes beyond a conventional SFT adapter, even if LoRA remains part of the trainable parameter set.

## Evaluation design

Every compression experiment should preserve matched task identity across conditions:

- **FULL**: ordinary/full available context;
- **STATE**: explicit structured state;
- **LATENT**: learned latent state;
- **LATENT+BACKING**: latent state with allowed resolution access.

Primary comparisons:

- FULL vs STATE: information-contract cost;
- STATE vs LATENT: representation-mechanism cost/benefit;
- LATENT vs LATENT+BACKING: rehydration value;
- all compressed conditions vs FULL on exactness/late-relevance failures.

Keep these metrics separate:

- downstream task accuracy;
- H01-H20 behavior where applicable;
- referent fidelity;
- correction/supersession fidelity;
- source/currentness fidelity;
- exact-detail success;
- false reconstruction;
- correct resolution-fault rate;
- unnecessary rehydration rate;
- late-relevance recovery;
- active token/latent budget;
- measured peak RAM/VRAM;
- prefill/decode latency;
- rehydration latency.

No aggregate score may hide false exact reconstruction.

## Data split changes

PR #70 implies new held-out families that are not sufficiently represented by the current V10 final bank.

New experiments therefore require new train/dev/final subjects for:

1. **Late relevance** — an early low-salience fact becomes decisive only later.
2. **Resolution faults** — exact detail is intentionally absent from compact state.
3. **Supersession after compression** — compact state must replace stale facts.
4. **Backing-reference integrity** — correct source block must be requested/retrieved.
5. **Compression distractors** — high-salience but irrelevant facts compete with low-salience decisive facts.
6. **Unexpected future query** — compression occurred before the eventual query was predictable.

These are separate from the sealed V10 one-shot final bank.

## Zero-cost / hardware strategy

The 4 GB RTX 3050 remains the default local target unless a later authority changes it.

Therefore:

- V10 remains the lowest-risk executable control;
- V10-S1 should reuse the proven 4-bit QLoRA mechanics with a fresh subject;
- V11 should begin with a **small codec + frozen/QLoRA decoder** rather than full-model training;
- teacher behavior should be generated offline;
- codec state size should start small and be swept conservatively;
- any architecture that cannot train without paid compute is a HOLD under the current constraint, not a reason to silently use paid infrastructure.

## Program gates

### Gate A — V10 control

Required before using V10 as a comparison result:
- current sealed-bank requirements satisfied;
- retention/behavioral/adversarial bank admitted;
- Patrick exact training authority;
- one exact training run;
- one-shot final evaluation.

### Gate B — V10-S1 feasibility

Before neural training:
- structured-state schema frozen;
- backing-reference schema frozen;
- resolution-fault output contract frozen;
- matched FULL/STATE dev bank built;
- late-relevance dev families present;
- token/resource preflight;
- fresh adapter subject;
- separate authority receipt.

### Gate C — V11 architecture

Before neural training:
- codec architecture/source blob frozen;
- latent width/slot count frozen;
- injection point and backing-reference interface frozen;
- loss terms and λ schedule frozen;
- teacher target subject/hash frozen;
- matched FULL/STATE/LATENT heldouts frozen;
- exactness bank and late-relevance bank frozen;
- memory/VRAM measurement method frozen;
- fresh authority receipt bound to the new architecture.

## Hostile review

> **HOSTILE REVIEWER:** If PR #70 is the better idea, why waste a run on V10 instead of replacing it?

**REJECTED.** PR #70 explicitly requires a full-context control. Replacing V10 would destroy the control and conflate curriculum improvement with representation compression. V10 is useful precisely because it does *not* contain the new mechanism.

> **HOSTILE REVIEWER:** V10-S1 is just fancy prompting, not model-memory research.

**ACCEPTED.** It is deliberately not called latent memory. Its purpose is to validate the state contract and resolution behavior before spending complexity on a trainable codec.

> **HOSTILE REVIEWER:** A small latent codec in front of a 4B decoder may simply memorize task shortcuts.

**ACCEPTED.** V11 must use source/family-disjoint matched tasks, late-relevance holdouts, unexpected-query families, and explicit budget sweeps. Success on training-like queries is insufficient.

> **HOSTILE REVIEWER:** Offline teacher targets may preserve teacher mistakes and make the student imitate rather than reason.

**ACCEPTED IN PART.** Teacher targets are secondary supervision, not ground truth. Deterministic/source-backed task truth outranks teacher outputs, and teacher-disagreement cases must be retained rather than silently relabeled.

> **HOSTILE REVIEWER:** The 4 GB hardware target may make true learned latent training impractical.

**UNRESOLVED.** The first architecture is intentionally codec-small and decoder-frozen/QLoRA-limited. Resource preflight is mandatory. If it does not fit, the result is a hardware feasibility HOLD, not a semantic failure and not permission for paid compute.

## Current effect

This bridge changes the **training roadmap**, not the active V10 execution subject.

No V10 corpus, recipe, final bank, authority, weights, or runtime is modified by this document.

## Claim ceiling

`TRAINING_PROGRAM_REDESIGNED / V10_FULL_CONTEXT_CONTROL_PRESERVED / V10_S1_STRUCTURED_STATE_PROPOSED / V11_TRUE_LATENT_ARCHITECTURE_PROPOSED / NO_NEW_TRAINING_AUTHORITY / NO_WEIGHT_CHANGE`
