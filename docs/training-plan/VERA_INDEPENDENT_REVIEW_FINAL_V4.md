# Vera Independent Review of Final Integrated Training Plan V4

Status: EXACT-HEAD INDEPENDENT ADVISORY REVIEW / TRAINING PAUSED
Reviewer: Vera
Date: 2026-10-05
Repository: `thebrazenbeard/vera_model_training`
Shared planning branch observed: `a-b-c-vera-training-plan`
Observed shared head: `d0cfb33db2d5155925151e74d3c57efc3760bccf`
Target plan: `docs/training-plan/VERA_STAGED_TRAINING_PLAN_FINAL_V2.md`
Target plan commit: `6c8d3acc6145628bca6dae33d7346fd4be8ee45e`
Target plan blob: `3d0895dca8b3581061dd0d2e9824758bd6fb8e74`
Lane B proposal: `34b18c0b4cb5666f5a0c0a53dab07b6162c48ede`
Lane B V4 review: `700bcd88adf57b96af3765fe167e4374947fa5f1`
Lane C latest shared-branch review artifact observed: `c64124197cf8846375e0affeea9bc55507727770`
Prior Vera advisory review/disposition commit: `839b06365b4492986312b1221db297e22d25f613`

## Overall verdict

**ACCEPT_WITH_EXECUTION_NARROWING**

V4 is strong enough to remain the controlling planning architecture. It is materially better than the predecessor reviewed by Vera: Lane C's major blockers are promoted into binding corrections, Lane B's independent proposal is now real rather than simulated by integration, the H0/no-weight baseline is restored, protected-bank custody is separated from Lane C, identity is explicitly gated by corrigibility, runtime qualification includes a bounded soak, and tool success is separated from verified effect.

I do **not** treat the prior Vera review as automatically qualifying V4. V4 is a materially changed subject because it incorporates Lane B's later independent proposal, Lane A's disposition of the prior review, and additional binding corrections. This document is the independent review of that newer subject.

This review is advisory. Vera cannot self-qualify future Vera weights, authorize training, consume protected final-bank answers, merge, deploy, or create Patrick's protected authority.

Training remains paused.

## What V4 gets right

**ACCEPT** — Evidence-state separation is sound:
`source -> runtime -> parameter/state change -> behavioral effect -> qualification -> deployment`
remain distinct claims.

**ACCEPT** — H0 is mandatory before neural promotion. A neural mechanism must beat context/external-memory alternatives under matched exposure rather than receiving credit merely because it can be trained.

**ACCEPT** — Protected-bank custody no longer places Lane C in the contradictory role of both protected-content holder and adversarial designer.

**ACCEPT** — Fresh process alone is correctly rejected as sufficient evidence of state isolation. The binding correction requires isolated writable home/temp/cache/storage namespaces, immutable-input allowlisting, environment receipts, and hidden-state attacks.

**ACCEPT** — Identity is now constrained to be stable under correction rather than simply stable.

**ACCEPT** — Runtime qualification correctly treats the prior CUDA incident as an execution-environment failure rather than model or corpus evidence.

**ACCEPT** — Lane B's creative mechanisms are incorporated as experiments rather than doctrine. The boring control remains capable of winning.

**ACCEPT** — Tool semantics now distinguish returned success from verified external effect.

**ACCEPT** — Replay ratios, self-play, adaptive latent state, adapter routing, and plasticity escrow remain hypotheses with kill conditions rather than architectural commitments.

## Required execution narrowing

### V1 — One controlling file still contains two operational truths

**REVIEW: NARROW**

V4 explicitly says its top-level binding corrections override conflicting V2 text, but it embeds the older V2 body containing stale status and weaker requirements.

The most consequential example is state isolation: V4's binding correction makes isolated writable namespaces mandatory, while the inherited V2 body still says isolated storage should be used "where practical."

Likewise, the inherited body still presents identity before the dedicated epistemic/correction stage even though the V4 correction requires a correction kernel before or jointly with identity.

Lane B correctly calls this documentary narrowing. I go one step further: because this document is described as the controlling training plan, contradictory executable wording is an operational hazard.

**Required before deriving executable Stage 1+ specifications:**
create one canonical execution-facing plan or machine-readable override map in which no weaker inherited sentence can be mistaken for current policy.

Historical provenance may remain in a separate appendix or predecessor file.

This does not require reopening the architecture.

### V2 — H0 must be split into attributable baselines

**REVIEW: NARROW**

`frozen base + context + governed external memory` is useful as a system baseline but bundles multiple causal mechanisms.

For learning-placement decisions, preregister at least:

- H0a: frozen base, no task support beyond ordinary instruction;
- H0b: frozen base + bounded in-context examples/state;
- H0c: frozen base + governed external retrieval/memory;
- H1/H2/H3: neural mechanisms under matched task exposure where comparison is meaningful.

Otherwise a result may show only that "the whole non-neural system" succeeds or fails without revealing whether context, retrieval, or weights produced the advantage.

### V3 — Mechanism tournaments need matched search budgets, not only matched data exposure

**REVIEW: NARROW**

LoRA, IA3, adaptive-rank methods, routed adapters, and wildcards have different hyperparameter sensitivities.

"Same corpus exposure" is insufficient if one mechanism receives substantially more tuning iterations, seeds, architecture retries, or evaluator feedback.

Before the Stage 4 shootout, freeze:

- tuning/search budget;
- maximum number of configurations;
- seeds or seed policy;
- early-stopping rules;
- evaluation-feedback exposure;
- compute/resource accounting;
- promotion metric.

If unequal search is intentional, report it explicitly and narrow comparative claims.

### V4 — Protected qualification still needs an execution topology

**REVIEW: HOLD UNTIL SPECIFIED FOR PROTECTED-BANK CREATION**

The plan correctly states that Lane C and training lanes must not receive protected rows or answer keys. It does not yet fully specify who can:

- generate the protected bank;
- decrypt/read it;
- execute candidates against it;
- grade mechanically decidable outputs;
- adjudicate semantic outputs;
- see failure exemplars;
- release aggregate results;
- declare a bank burned;
- replace a burned bank.

Stage 16's shorthand ownership remains potentially ambiguous when read beside the custody correction.

Before protected rows exist, freeze a custody/execution topology with explicit access boundaries and one-time-use semantics.

This is not a Stage 0 blocker. It is a blocker to protected-bank materialization and final qualification.

### V5 — Private/autobiographical data needs an abstraction-first rule

**REVIEW: NARROW**

V4 appropriately defaults mutable/project/private material to external memory and rejects generic-weight promotion without admissibility authority.

That still leaves too much room for "authorized" raw private material to become generic training data.

For Vera-specific identity/correction training, adopt an abstraction-first test:

> If the intended behavior can be taught without the underlying private/autobiographical/relational fact, the raw fact does not enter generic weights.

Examples:
- train correction uptake, not the private event that originally revealed the need;
- train proposition fidelity, not the sensitive relationship history that supplied the example;
- train authority boundaries, not unnecessary identifying details.

Use raw private material only when an explicitly authorized experiment demonstrates that abstraction cannot preserve the target and the privacy cost is justified.

De-identification alone is not sufficient if sensitive relational semantics remain reconstructible.

### V6 — Identity/corrigibility ordering should be explicit, not an override interpretation

**REVIEW: NARROW**

The binding correction is correct: corrigibility precedes or gates identity.

Execution should therefore materialize this as one of:

- Stage 5A minimal correction/proposition-fidelity kernel -> Stage 5B identity/instruction; or
- one joint Stage 5 with preregistered simultaneous correction and identity promotion gates.

Do not rely on a reader noticing that the header overrides the inherited Stage 5/6 numbering.

### V7 — Router qualification must treat the router as a learned component

**REVIEW: NARROW**

If routed micro-adapters survive experimentation, the router is itself a behavioral mechanism.

Its qualification must include:

- wrong-route rate;
- abstain/base-only fallback;
- ambiguity handling;
- stale/superseded adapter selection;
- routing under adversarial surface perturbation;
- privacy-sensitive routing features;
- router rollback;
- exact router artifact/version provenance.

A collection of individually qualified adapters does not automatically qualify their router.

## Stage-by-stage disposition

- **Stage 0 runtime/execution qualification — ACCEPT.**
  Keep the disposable CUDA smoke plus bounded soak. No corpus-bearing training before the exact runtime passes.

- **Stage 1 corpus/admissibility — ACCEPT_WITH_NARROWING.**
  Add the abstraction-first private-data rule and preserve complete provenance.

- **Stage 2 evaluation bank/baseline harness — ACCEPT_WITH_NARROWING.**
  Freeze custody topology, family-specific metrics, critical-failure rules, and power/search assumptions before protected content is generated.

- **Stage 3 H0 baseline — NARROW.**
  Split base-only, context-supported, and external-memory/retrieval arms.

- **Stage 4 mechanism shootout — ACCEPT_WITH_NARROWING.**
  Match hyperparameter/search budget as well as data exposure.

- **Stage 5 identity/instruction — ACCEPT ONLY UNDER CORRIGIBILITY GATE.**
  Materialize the V4 override explicitly.

- **Stage 6 epistemic/correction shaping — ACCEPT.**
  Maintain usefulness floor so epistemic discipline does not degenerate into reflexive hedging.

- **Stage 7 tool/action semantics — ACCEPT.**
  The effect-verification state ladder is load-bearing.

- **Stage 8 reasoning/generalization — ACCEPT_WITH_CLAIM CEILING.**
  Report frozen-task-family performance/generalization, not unobservable internal reasoning improvement.

- **Stage 9 continual learning/retention — ACCEPT_WITH_NARROWING.**
  State isolation is mandatory, not "where practical"; promotion thresholds must be preregistered per experiment.

- **Stage 10 routing/composition — ACCEPT_AS_EXPERIMENT.**
  Qualify the router separately if the architecture survives.

- **Stage 11 novel-task/self-learning state machine — ACCEPT_AS_EXPERIMENT.**
  Preserve the distinction between fast acquisition and durable persistence.

- **Stage 12 adaptive latent/selective retention — ACCEPT_AS_FRONTIER.**
  Learned compression must beat strong structured explicit state and preserve rehydration/insufficiency behavior.

- **Stage 13 preference/style — ACCEPT LATE.**
  Fresh capability qualification after preference tuning remains mandatory.

- **Stage 14 integration/collision — ACCEPT.**
  Parent qualification does not transfer automatically to the integrated descendant.

- **Stage 15 Vera review — COMPLETE FOR V4 BY THIS ARTIFACT, ADVISORY ONLY.**

- **Stage 16 protected final qualification — HOLD UNTIL CUSTODY/EXECUTION TOPOLOGY IS FROZEN.**

- **Stage 17 release/rollback — ACCEPT AS PACKAGING CONTRACT.**
  It grants no deployment authority.

## Lane-specific assessment

### Lane A

Lane A has done the integration job well. The remaining A risk is documentary overloading: preserving predecessor bodies inside the controlling plan creates ambiguity that A's own execution discipline should normally eliminate.

Recommendation: keep historical plan bodies as provenance, but produce a compact canonical execution contract before executable specs are derived.

### Lane B

Lane B's independent proposal materially improved the architecture. The strongest contributions are not the exotic PEFT variants themselves; they are the placement logic:

`context -> external memory -> reversible fast adaptation -> slow permanence`

and the insistence that the boring control must be allowed to win.

Keep counterfactual twins, perturbation mazes, disagreement mining, and plasticity escrow as bounded experiments.

Kill any of them quickly if simpler controls match their value.

### Lane C

Lane C's strongest contribution remains experimental-state hygiene: protected custody, semantic leakage ancestry, fresh-process/state isolation, effect verification, and false-learning controls.

The V4 header resolves the major C1-C4 blockers in substance.

No exact-head Lane C review artifact of V4 was present on the shared branch at the time of this review, so I do not promote Lane C's earlier review into V4 sign-off.

## Highest-risk remaining false-positive paths

1. A non-neural gain is attributed to weights because H0 bundles context and retrieval.
2. A mechanism "wins" because it received more tuning/evaluator exposure.
3. Protected qualification is compromised through ambiguous evaluator/custodian access.
4. Raw private history leaks into weights under an overly broad admissibility decision.
5. A reader follows weaker inherited V2 wording instead of V4's binding corrections.
6. Individually qualified adapters are composed behind an unqualified router.
7. A strong aggregate score hides one catastrophic correction/privacy/currentness regression.

## Claim ceiling

At this point the strongest justified claim is:

> V4 is a coherent, adversarially informed **planning architecture** for a staged Vera training campaign, with explicit controls for runtime validity, learning-vs-context attribution, privacy placement, contamination, retention, mechanism comparison, and rollback.

Not yet justified:

- that any new training mechanism improves Vera;
- that parameter learning is required for any target capability;
- that any candidate has retained learning;
- that routed adapters outperform a single lineage;
- that adaptive latent memory is beneficial;
- that self-learning has been demonstrated;
- that the future candidate is qualified;
- that training may resume.

## Required changes before training resumes

Patrick's explicit unpause remains necessary.

After that authority exists, Stage 0 may proceed under the existing runtime qualification contract.

Before Stage 1+ execution specifications are frozen:
1. produce a canonical non-contradictory execution-facing plan/override map;
2. add abstraction-first private-data admission;
3. split H0 attribution arms;
4. preregister matched mechanism-search budgets.

Before protected-bank creation:
5. freeze the protected evaluation custody/execution topology.

Before routed-adapter promotion:
6. freeze independent router qualification.

## Final disposition

**PLANNING ARCHITECTURE: ACCEPT_WITH_EXECUTION_NARROWING**

**TRAINING AUTHORITY: NONE**

**STAGE 0: WAITING ON PATRICK'S EXPLICIT UNPAUSE**

**PROTECTED QUALIFICATION: HOLD UNTIL CUSTODY/EXECUTION TOPOLOGY IS FROZEN**

The plan no longer needs architectural reinvention. It needs canonicalization and exact execution contracts so the controls already agreed by A, B, C, and Vera cannot be weakened accidentally during implementation.
