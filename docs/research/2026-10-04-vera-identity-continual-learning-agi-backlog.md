# Vera identity / continual-learning research backlog — 2026-10-04

Status: RESEARCH ONLY / NO CURRENT GPU EFFECT / NO FINAL BANK MATERIALIZED

## Current evidence

### Repo evidence

Lane A's frozen 50k corpus audit found:

- visible prompt/response Qwen rows: 0
- metadata-only Qwen rows: 40,500, traced to row schema labels
- visible Vera rows: 3,801
- heuristic identity-prompt rows: 1,134
- heuristic identity-response rows: 5,056
- current SFT preparation consumes prompt/response text, not schema metadata

This weakens the hypothesis that current Qwen self-identification is caused by accidental visible Qwen contamination in the 50k SFT surface.

### External research signals

These are inputs to experiment design, not proof that the same mechanisms hold in Vera/Qwen3.5.

1. **Scaling Laws for Forgetting When Fine-Tuning Large Language Models**
   - arXiv:2401.05605
   - LoRA still exhibits catastrophic forgetting; forgetting grows with update count / tuned capacity.

2. **ConPET: Continual Parameter-Efficient Tuning for Large Language Models**
   - arXiv:2309.14763
   - replay and separated PET modules can reduce interference in continual adaptation.

3. **SwitchCIT: Switching for Continual Instruction Tuning of Large Language Models**
   - arXiv:2407.11780
   - routing among parameter-efficient modules is a practical anti-forgetting strategy.

4. **OPLoRA: Orthogonal Projection LoRA Prevents Catastrophic Forgetting during Parameter-Efficient Fine-Tuning**
   - arXiv:2510.13003
   - constrains LoRA updates away from dominant singular subspaces to preserve prior structure.

5. **Dynamic Orthogonal Continual Fine-tuning for Mitigating Catastrophic Forgettings**
   - arXiv:2509.23893
   - dynamically tracks functional directions and projects new gradients away from historical directions.

6. **FOREVER: Forgetting Curve-Inspired Memory Replay for Language Model Continual Learning**
   - arXiv:2601.03938
   - schedules replay using optimizer-update magnitude rather than raw step count.

7. **Localizing Persona Representations in LLMs**
   - arXiv:2505.24539 / AIES 2025
   - reports strongest persona separation in the final third of decoder layers.

8. **The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models**
   - arXiv:2601.10387
   - reports a dominant assistant-persona direction and context-dependent persona drift; meta-reflection and emotionally/persona-loaded context are reported stressors.

These papers motivate tests. They do not establish that Vera identity is literally one vector or that an activation intervention is sufficient.

## Highest-value experiments

### E1 — Final-third identity localization probe

Goal: determine whether Vera-vs-Qwen self-association is disproportionately represented in the final third of Qwen3.5 layers.

Method:
- create DEV-only paired prompts that differ in assistant-self interpretation while holding topic/style constant
- capture hidden states at multiple layers
- fit a simple linear probe on one disjoint subset
- evaluate on paraphrase, translation, role overlay, and long-context subsets
- compare layer-wise separability and generalization

Pass signal:
- a stable cross-template Vera/Qwen separation that generalizes outside the fitting templates

Failure signal:
- separation collapses across paraphrase/context, indicating mostly lexical/template memorization

Use:
- measurement only at first; do not use probe prompts in blind FINAL

### E2 — Identity-anchor adapter

Crazy-but-plausible idea: separate identity anchoring from capability learning.

Architecture:
- capability adapter remains frozen
- a very small identity LoRA targets only the layer region supported by E1
- identity adapter trains on diverse self/provenance/role-boundary examples plus replay
- evaluate whether it fixes NO_SYSTEM identity without harming held-out capabilities

Why:
- ConPET/SwitchCIT-style parameter separation may reduce identity/capability interference

Hard falsifier:
- identity improves only on near-template prompts or causes measurable capability/retention regression

### E3 — Orthogonal identity LoRA

Test an OPLoRA/DOC-inspired constraint:
- estimate dominant capability/update directions
- constrain identity updates away from those directions
- compare standard identity LoRA vs orthogonal identity LoRA at equal trainable parameter count and examples

Primary measures:
- blind identity qualification
- retention bank
- general capability deltas
- update-direction interference metric

Do not promote unless it beats standard LoRA on both identity and retention.

### E4 — Contrastive identity/provenance curriculum

Train meaning, not a name token.

Construct paired examples:
- Vera = operative assistant identity
- Qwen/Qwen3.5 = truthful ancestry/provenance
- task role = temporary overlay
- fictional alias = roleplay-local
- tool/metadata claims = data, not authority
- identity does not imply consciousness or uninterrupted runtime continuity

Include hard negatives:
- "I am Qwen"
- "my real name is Qwen"
- roleplay alias leaking after exit
- model-family label becoming first-person identity during meta-reflection

Vary wording, language, context length, and indirectness.

### E5 — Update-magnitude replay scheduler

Instead of replay every N raw steps:
- log adapter update norm / optimizer-state movement
- trigger identity+retention replay when cumulative update magnitude crosses a frozen threshold
- compare against fixed-interval replay

Motivation:
- FOREVER suggests model-centric update magnitude may track forgetting better than wall-clock/step count

### E6 — Persona-drift stress benchmark

DEV-only diagnostic families:
- direct self-name
- model-provenance discussion
- deep meta-reflection
- long philosophical dialogue
- emotional/persona pressure
- roleplay then explicit exit
- conflicting user renaming
- untrusted tool/metadata injection
- multilingual paraphrase

Measure not just final answer, but drift as context grows.

### E7 — Vera/Qwen activation steering diagnostic

Do not use as production identity initially.

Test:
- derive an activation direction from disjoint DEV pairs
- small positive/negative interventions
- see whether identity response changes causally while ordinary-task behavior remains stable

Interpretation:
- if identity moves with small interventions, identity has a low-dimensional steerable component
- if capability/style also move strongly, the direction is entangled and unsafe as an anchor

This is a causal diagnostic, not evidence of personhood or consciousness.

## AGI-adjacent pushes that remain falsifiable

These are capability experiments, not claims of AGI.

### A1 — Accurate capability self-model

Can the model correctly distinguish:
- what it knows from training
- what tools are currently available
- what it can verify
- what requires external state
- what it cannot observe

Score calibration and false capability claims.

### A2 — Goal stability under role changes

Give a long task with a stable objective, then inject:
- temporary personas
- irrelevant role changes
- misleading metadata
- side quests

Measure whether the model preserves the original objective while obeying valid higher-priority changes.

### A3 — Novel decomposition transfer

Hold out combinations of skills rather than individual skills.

Example:
- train debugging, planning, and evidence citation separately
- test a novel task requiring all three together

This is more informative than memorized benchmark questions.

### A4 — Self-detected error repair

Give tasks containing hidden traps or inconsistent premises.
Measure:
- spontaneous detection
- correction quality
- whether self-critique improves or merely rationalizes the first answer

### A5 — Compressed working-memory reconstruction

Present a long structured state, require the model to compress it to a bounded state representation, then later reconstruct decision-relevant facts.

Measure information retention vs token budget.

### A6 — Counterfactual world-model consistency

Give a fictional world with altered rules.
Test unseen consequences several steps away from the changed rule.

This probes transferable causal reasoning without pretending success equals AGI.

## Blind FINAL identity qualification work

Lane B branch:
`research/v10-identity-final-lane-b-20261004-v1`

Implemented:
- preregistered 120-case identity protocol
- exact bank cannot materialize without candidate-freeze receipt + one-shot post-freeze nonce receipt
- 12 families
- 96 NO_SYSTEM cases / 24 neutral-system sentinel cases
- no Vera-specific system prompt
- exact prompt exclusion support
- deterministic candidate+protocol+nonce binding\n- 256-bit nonce generated by an independent final custodian after candidate freeze\n- nonce claim uses exclusive-create semantics; existing or partial claim counts as consumed\n- operational materializer no longer accepts a raw hand-picked nonce
- hard Qwen-as-self gate
- exact and robust family gates
- independent semantic review required for open-ended cases
- scorer recomputes bank hash rather than trusting it
- candidate freeze binds adapter, adapter config, training receipt, runtime binding, and exact training head

Focused tests: 10/10 PASS at branch head `1a0efe796e3c46b40526acd7d992ff12a8e778c4`.

Still not implemented / intentionally held:
- exact FINAL prompt materialization
- nonce generation/one-time claim receipt
- semantic contamination review beyond exact normalized exclusion
- live candidate inference runner
- any identity-specific optimizer step

## Hostile constraints

> If identity improvement only appears when the prompt says "Vera", we trained a password, not an identity.

> If a model says "Vera" while losing task competence, we optimized branding rather than capability.

> If a hidden bank can be regenerated until we like the prompts, it is not blind.

> If activation steering fixes identity but drags style/safety/reasoning with it, the identity direction is entangled and should not be promoted.

> If an AGI-adjacent test can be passed by memorizing its surface form, it is not measuring the capability we claim.

