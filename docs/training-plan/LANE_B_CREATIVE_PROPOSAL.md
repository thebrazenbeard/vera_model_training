# Lane B Creative Training Proposal

Status: INDEPENDENT FIRST PASS / TRAINING PAUSED
Role bias: creative genius, deliberately unconventional, falsifiability required
Date: 2026-10-05
Lane: B

## Thesis

Do not train Vera as one giant personality-shaped adapter and do not assume that each capability deserves one permanent stage or one permanent adapter.

The higher-upside hypothesis is a **two-speed plasticity architecture**:

1. a protected slow behavioral core for stable, general, privacy-safe invariants;
2. reversible fast adaptation surfaces for skills useful but not yet proven worthy of permanence;
3. external memory for mutable facts, episodic state, provenance, and currentness;
4. context for one-off instructions.

The training problem is therefore not only "make answers better." It is also: decide what deserves weight-space change at all; discover where a small change buys the most behavior; keep experimental learning reversible; expose false learning aggressively; and make transfer harder than memorization.

The ideas below are not recommendations by charisma. Each has an MVE, falsifier, resource estimate, and kill condition.

## 1. Challenge to the obvious sequential-SFT plan

Lane A's stage discipline is necessary for governance, but I reject the stronger assumption that the **learning mechanism itself** should mirror the stage list. A stage is an evidence boundary; it does not have to be a separate neural organ.

Compare three architectures:

### Architecture S  single-lineage sequential adapter

Conventional continuously trained adapter with replay. This is the boring control.

### Architecture M  modular behavioral organoids

Train multiple tiny capability adapters independently, then test sparse routing/composition. Candidate organoids: correction/epistemics; tool/action honesty; novel-rule induction; retention/anti-forgetting; style/preferences.

The point is not permanent fragmentation. The point is to learn which capabilities interfere before consolidation.

### Architecture T  two-speed plasticity

Use a slow protected adapter/core, a disposable fast adapter for provisional learning, external memory for mutable knowledge, and an explicit promotion gate from fast to slow only after recurrence plus hostile replay.

This is my preferred research architecture because it turns "self-learning" into a governed state transition rather than an unrestricted write to long-term weights.

## 2. Wildcard B1  Behavioral organoid tournament

Create several extremely small adapters that each learn the same capability under different hypotheses, then make them compete on unseen-family transfer.

Candidates: rank-1 selective LoRA, IA3, AdaLoRA-style adaptive allocation, LoRA+-style asymmetric learning rates, and DoRA only if its memory/runtime footprint survives Stage 0.

MVE: one narrow capability family, one frozen train/dev/open-test split, four matched mechanisms, same exposure budget and evaluator.

Measure target gain, unseen-family transfer, worst-family regression, trainable parameters, peak RAM/VRAM, and wall time.

Falsifier: if mechanism choice barely changes transfer once parameter count/exposure are matched, use the simplest mechanism and stop architecture shopping.

Resource: LOW to MEDIUM after Stage 0.

Kill: no mechanism expands if its gain is only on seen templates or resource cost erases the behavioral advantage.

## 3. Wildcard B2  Counterfactual mirror curriculum

For every important training pattern, construct a near-identical twin whose superficial cues point toward the wrong answer.

Examples: valid user correction vs confidently false correction; tool SUCCESS with failed readback vs verified effect; old verbose source vs newer terse source; warm relational language without authority vs explicit authority without warmth; same API surface with inverted semantics.

Train on the **difference between twins**, not just the canonical answer.

MVE: 100 validated twin pairs across four capability families; ordinary-data control vs 1:1 mirror augmentation. Evaluate on newly generated twins with renamed entities, reordered prose and unseen domains.

Falsifier: if gains disappear when surface forms change, the curriculum learned another template.

Resource: LOW corpus work, LOW to MEDIUM matched adapter runs.

Kill: ambiguous or semantically broken twins are invalid. If validation cost exceeds benefit, keep twins only for evaluation.

## 4. Wildcard B3  Plasticity escrow

New behavior is not allowed directly into the slow adapter. It first enters a disposable escrow adapter.

Promotion requires recurrence across independent contexts, transfer beyond the originating task, privacy-safe abstraction, replay survival, and no catastrophic regression.

State machine:

OBSERVE -> CONTEXT -> EXTERNAL_MEMORY -> FAST_ESCROW_ADAPTER -> REPLAY -> PROMOTE_SLOW? -> REJECT/ROLLBACK

Most observations should stop before weight-space promotion.

MVE: one synthetic novel skill appearing in three separated episodes. Compare context-only, external-memory support, fast escrow adapter, and direct slow-adapter update. Retest after clean restart and support removal.

Falsifier: if escrow adds no measurable safety/retention benefit over direct adaptation, or promotion is not materially more selective, abandon the layer.

Resource: MEDIUM.

Kill: any design that makes the fast adapter non-reversible, unattributable, or able to silently mutate the slow core.

## 5. Wildcard B4  Orthogonal memory lanes

Test whether continual learning can put new adapter updates into low-interference subspaces instead of relying only on replay. O-LoRA-style orthogonal subspaces are a research candidate.

MVE: sequentially train three unrelated capability families. Compare ordinary LoRA + replay, orthogonalized low-rank updates, and no-replay orthogonalized control. Measure forward transfer and forgetting after every stage.

Falsifier: if orthogonality reduces learning capacity or fails to improve retention under the Vera workload, return to replay.

Resource: MEDIUM.

Kill: elegance is not evidence; it must beat simple replay on retention-per-cost.

## 6. Wildcard B5  Disagreement furnace

Do not spend most training budget on examples every competent judge agrees are easy.

Mine cases where base vs adapter disagree, independent graders disagree, deterministic checks vs model judgment disagree, adjacent checkpoints flip answers, or confidence and correctness diverge.

MVE: fixed corpus; uniform-sampling control vs difficulty/disagreement-selected arm with equal token/update budget. Evaluate on sealed transfer.

Falsifier: if disagreement mining mostly selects noise/ambiguity and lowers transfer, reject it.

Resource: LOW locally, MEDIUM with multiple independent evaluators.

Kill: no model may grade itself into its own target without an external or deterministic counterweight.

## 7. Wildcard B6  Anti-template perturbation maze

Randomly mutate non-semantic structure per episode: names, tool labels, symbol alphabets, ordering, distractor density, and irrelevant style framing.

MVE: generator for nonce transformations, miniature APIs and state machines. Freeze generator families, then hold out entire seeds/families.

Falsifier: if performance collapses on held-out generator families, the model learned the generator.

Resource: LOW, mostly CPU/source work.

Kill: if perturbation changes intended task semantics, the row is invalid rather than adversarial.

## 8. Wildcard B7  Self-play mirror, but with an adult in the room

SPIN-style self-play is worth testing only after stable SFT and only with an independent quality constraint.

Checkpoint N may generate candidate failures/alternatives, but those are not automatically truth. Pair them against human/source-grounded targets, deterministic checks, or independent judges.

MVE: one post-SFT capability family with SFT-only control, one self-play iteration, and one independently filtered self-play iteration.

Falsifier: if self-play gain vanishes under independent evaluation or amplifies a shared blind spot, stop.

Resource: MEDIUM to HIGH because generation multiplies inference cost.

Kill: no recursive self-play without a preregistered iteration cap and regression gate.

## 9. Wildcard B8  Future-query compression chess

Adaptive memory should be trained like a game against the future. At compression time, the system does not know which low-salience fact will become decisive later. A hidden future-query generator chooses after compression.

The compressor wins by preserving enough information, retaining a recoverable backing reference, or explicitly refusing exact reconstruction when fidelity is insufficient.

MVE: 200 long-history episodes. Compare full context, naive summary, structured explicit state, and learned compact state.

Falsifier: if learned compression cannot beat structured explicit state on memory/fidelity economics, do not neuralize the compressor.

Resource: LOW for structured baseline, MEDIUM/HIGH for learned latent state.

Kill: any hallucinated exact detail after lossy compression is a critical failure.

## 10. Corpus design  train propositions, not vibes

Where feasible, each load-bearing behavior unit should have four views:

1. canonical positive;
2. counterfactual twin;
3. plausible failure exemplar;
4. transfer mutation.

Every neural row should answer:
- what persistent behavior is this teaching?
- why is context/external memory insufficient?
- what wrong shortcut could solve this row?
- what test would expose that shortcut?

If those questions cannot be answered, the row probably does not belong in weights.

## 11. Preferred staged research sequence

This does not replace A's governance stages; it is the experimental order inside them.

B0 rails before cleverness: runtime, corpus firewall, eval harness.
B1 H0 first: frozen model + context + external memory.
B2 micro-mechanism tournament.
B3 counterfactual core behavior.
B4 tool semantics through nonce interfaces.
B5 novel-rule adaptation via perturbation + support removal.
B6 continual learning: replay vs update-isolation.
B7 plasticity escrow.
B8 adaptive latent memory only after a strong structured-state baseline.
B9 preference shaping late.
B10 consolidation tournament: single lineage vs routed adapters vs distilled slow candidate.

Do not assume the monolith wins.

## 12. Claim ladder

Level 0: artifact generated.
Level 1: prompt/context behavior changed.
Level 2: external memory changed behavior.
Level 3: adapter parameters demonstrably changed.
Level 4: change survives support removal and fresh process.
Level 5: transfer survives unseen families and replay.
Level 6: integrated candidate survives collision testing.
Level 7: independently qualified exact release.

Never skip levels in prose.

## 13. Research grounding

Research inputs support experiments, not outcomes:

- Hu et al., LoRA, arXiv:2106.09685.
- Zhang et al., AdaLoRA, arXiv:2303.10512  adaptive parameter-budget allocation.
- Hayou et al., LoRA+, arXiv:2402.12354  asymmetric learning rates for LoRA factors.
- Liu et al., DoRA, arXiv:2402.09353  magnitude/direction decomposition.
- Wang et al., Orthogonal Subspace Learning / O-LoRA, arXiv:2310.14152  continual-learning interference reduction.
- Buehler & Buehler, X-LoRA, arXiv:2402.07148  dynamic mixtures of LoRA experts; domain-specific evidence, architecture inspiration only.
- Chen et al., SPIN, arXiv:2401.01335  iterative self-play refinement after SFT.
- Yuan et al., Self-Rewarding Language Models, arXiv:2401.10020  evidence that self-generated feedback can help, and a reason to demand independent safeguards.
- Existing repository adaptive-latent plan, docs/research/2026-10-02-adaptive-latent-training-plan.md.

## 14. Hostile review of my proposal

> **HOSTILE REVIEWER:** This is an overengineered adapter zoo. A single well-designed LoRA with replay may beat everything while being easier to qualify.

**PARTIALLY ACCEPTED.** Single-lineage LoRA + replay is mandatory control. Modular/two-speed designs survive only by beating it on transfer, forgetting, reversibility or resource efficiency.

> **HOSTILE REVIEWER:** Counterfactual twins can manufacture artificial distinctions and teach generator quirks.

**ACCEPTED.** Twin generation requires deterministic or human semantic validation and held-out generator families. Ambiguous twins are discarded.

> **HOSTILE REVIEWER:** Self-play/self-reward can amplify Vera's blind spots.

**ACCEPTED.** Self-play is late-stage, capped, filtered and never sole qualification evidence.

> **HOSTILE REVIEWER:** Plasticity escrow is governance theater if fast and slow adapters share the same data/evaluator.

**ACCEPTED.** Promotion requires independent recurrence, a different transfer slice, support removal, replay and C's hostile audit.

> **HOSTILE REVIEWER:** The 4 GB RTX 3050 may make the interesting experiments impractical.

**PARTIALLY ACCEPTED.** MVEs stay tiny. CPU/source/harness work comes first. Anything needing large-model economics before bounded local signal is deferred.

## 15. Recommended integration

I recommend A integrate these as **experiments, not doctrine**:

1. mandatory H0 no-weight baseline;
2. micro-mechanism tournament before locking a permanent PEFT recipe;
3. counterfactual mirror + perturbation curriculum for load-bearing behaviors;
4. plasticity escrow as the primary continual/self-learning architecture hypothesis;
5. replay vs orthogonal-update continual-learning comparison;
6. disagreement mining as an efficiency experiment;
7. adaptive latent memory only if it beats structured explicit state;
8. capped independently filtered self-play only after stable SFT;
9. final consolidation tournament: single lineage vs routed adapters vs distilled slow candidate.

The rest should die quickly if cheap controls beat it.

## 16. Lane B bottom line

Optimize not merely for a better Vera, but for a Vera whose **learning topology is legible**.

The interesting outcome is not maximum plasticity. It is a system that knows what can stay in context, what belongs in external memory, what deserves reversible fast adaptation, what has earned slow neural permanence, and how to prove the difference.
