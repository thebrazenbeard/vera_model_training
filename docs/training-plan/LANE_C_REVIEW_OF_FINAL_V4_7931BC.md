# Lane C Hostile Review of Final Integrated Training Plan V4

Status: EXACT-HEAD HOSTILE REVIEW / TRAINING PAUSED
Reviewer: Lane C / Three
Role bias: paranoid skeptic / hyper-vigilant falsification
Date: 2026-10-05

## Exact subject

- Repository: `thebrazenbeard/vera_model_training`
- Branch: `a-b-c-vera-training-plan`
- Exact branch head reviewed: `7931bc71424f55c522175a888ac0dc957817b216`
- Controlling plan file: `docs/training-plan/VERA_STAGED_TRAINING_PLAN_FINAL_V2.md`
- Controlling plan introduction commit: `6c8d3acc6145628bca6dae33d7346fd4be8ee45e`
- Lane B exact-head review: `docs/training-plan/LANE_B_REVIEW_OF_FINAL_V4.md`, introduced at `700bcd88adf57b96af3765fe167e4374947fa5f1`
- Post-review Lane B additions at the exact head include the corrected `LANE_B_NEW_CHAT_BOOTSTRAP_V2.md` and `LANE_B_H3_WILDCARD_SELECTION.md`; the controlling V4 plan remains the file introduced at `6c8d3acc6145628bca6dae33d7346fd4be8ee45e`.

Files reviewed:
- `docs/training-plan/COORDINATION_CHARTER.md`
- `docs/training-plan/LANE_A_PRAGMATIC_PROPOSAL.md`
- `docs/training-plan/LANE_B_CREATIVE_PROPOSAL.md`
- `docs/training-plan/LANE_B_REVIEW_OF_FINAL_V4.md`
- `docs/training-plan/LANE_B_NEW_CHAT_BOOTSTRAP_V2.md`
- `docs/training-plan/LANE_B_H3_WILDCARD_SELECTION.md`
- `docs/training-plan/LANE_C_HOSTILE_PROPOSAL.md`
- `docs/training-plan/LANE_C_REVIEW_OF_INTEGRATED_DRAFT_94A8128.md`
- `docs/training-plan/VERA_INDEPENDENT_REVIEW.md`
- `docs/training-plan/VERA_REVIEW_DISPOSITION.md`
- `docs/training-plan/VERA_REVIEW_REQUEST.md`
- `docs/training-plan/VERA_STAGED_TRAINING_PLAN_FINAL_V2.md`

Live coordination evidence also checked:
- current `bus/one-v2`, `bus/two-v2`, `bus/three-v2`, and `bus/vera-v2` heads;
- Lane A's terminated exact-head critique request for predecessor `94a8128`.

## Overall disposition

**HOLD**

This is not a rejection of the V4 architecture. It is a rejection of the stronger claim that V4 is already a closed, execution-ready final plan.

The plan is materially better than the `94a8128` predecessor. Most of Lane C's prior objections are incorporated. But the current subject still fails the standard `QUALIFIED_PARENT != QUALIFIED_DESCENDANT`: Lane C's exact-head review was of `94a8128`, while the final plan was materially rewritten through Lane B integration, Vera disposition, and V4 binding corrections at later heads. V4 nevertheless says "No planning-signoff dependency remains."

That closure claim outruns the evidence.

Two prior blockers also remain only textually superseded rather than mechanically closed: fresh-state isolation and corrigibility-before-identity. The V4 header states stronger rules, while the embedded execution-looking stage body contains weaker or conflicting rules. Until one normalized execution contract removes that ambiguity, I cannot tell which mechanism would actually run.

Training remains paused. This review grants no training, GPU, protected-bank, merge, deploy, activation, spend, or promotion authority.

## Evidence classification

**FACT:** The current branch head is `7931bc...`.

**FACT:** The controlling V4 plan file was added at `6c8d3ac...`.

**FACT:** Lane B reviewed that V4 file exactly at `700bcd8...` and returned `ACCEPT_WITH_DOCUMENTARY_NARROWING`.

**FACT:** Lane B subsequently selected Routed Disposable Micro-Adapter Escrow (RDME) as H3 for falsifiable comparison at `7931bc...`; the artifact explicitly says H3 is unvalidated, development-only, training paused, and no protected bank/private autobiographical corpus is authorized.

**FACT:** Lane C's prior exact-head review targeted `94a8128...`, not V4.

**FACT:** `VERA_INDEPENDENT_REVIEW.md` does not bind itself to `6c8d3ac...`; it says the reviewer received an integrated synopsis and supporting lane evidence. Lane A later dispositioned that advisory review before publishing V4.

**REVIEW:** Therefore neither Lane C's predecessor review nor Vera's advisory synopsis review can be promoted into exact-head qualification of V4 merely because V4 incorporates their language.

**INFERENCE:** The intended architecture is safer than the embedded V2 body in several places, but intention is not an executable precedence mechanism.

## Prior Lane-C objections: current disposition

### C1 — Protected final-bank custody

**Status: RESOLVED AT PLAN LEVEL; EXECUTION BINDING STILL REQUIRED.**

V4 now says Lane C designs schemas, attacks, canaries, contamination checks, and scoring contracts while protected rows/answer keys remain with Patrick, a separately authorized custodian, or a sealed evaluator/generator inaccessible to Lane C and training lanes. It also defines bank exposure as burn.

That addresses the original custody objection.

Residual issue: Stage 16 still labels `C + A` as lead without defining which actor executes protected rows, who can decrypt/read them, and what each lane receives afterward. An execution spec must preserve the separation rather than infer that "lead" grants row access.

Evidence that would reverse the residual objection: a Stage-16 custody manifest binding custodian, execution surface, read permissions, row/key visibility, hashes, one-time-use state, and post-run evidence available to C.

### C2 — H0 before neural promotion

**Status: RESOLVED.**

V4 inserts H0 frozen base + context/governed external memory before H1/H2, requires matched exposure/evaluation, and explicitly denies behavioral credit based on resource suitability.

Residual narrowing: "matched exposure" needs an exposure ledger in execution specs so token/example exposure, tuning interactions, demonstrations, retrieval calls, and evaluator feedback cannot differ silently across H0/H1/H2.

### C3 — Fresh-state isolation

**Status: PARTIALLY_RESOLVED / HARD EXECUTION BLOCKER.**

The V4 binding correction is good: fresh process plus isolated writable temp/home/cache/storage namespaces, immutable-input allowlist, environment snapshots/diffs, separate outputs, and a hidden-state adversarial mechanism.

But the embedded Stage 9 body still says isolation should be used "where practical" and allows a weaker complete-state/no-external-mutable-state contract. That directly weakens the earlier hard requirement.

More importantly, no executable harness invariant is yet bound. A prose rule cannot prove isolation.

The current rule also does not explicitly close external mutable channels such as:
- retrieval services/indexes;
- network services;
- provider-side session state;
- shared databases;
- inherited credentials with write access;
- reused ports/daemons;
- model-server KV/session caches;
- deterministic filenames outside the isolated root.

Cheapest decisive falsifier:
1. create two fresh-process arms with isolated local namespaces;
2. insert an undeclared hidden counter in one external or global channel;
3. require the harness to detect and HOLD the arm;
4. repeat with retrieval/service state and inherited environment/credential state.

PASS: every undeclared writable channel is rejected or structurally impossible and verified.
FAIL: hidden state changes the result without detection.
HOLD: isolation coverage cannot be proven.

What changes my mind: an executable isolation manifest + negative canary test that fails when an undeclared local or external mutable channel is introduced.

### C4 — Corrigibility before or with identity

**Status: UNRESOLVED / HARD EXECUTION BLOCKER.**

The V4 binding correction says a minimal epistemic/correction kernel must be trained before or jointly with identity/instruction material.

The stage map and embedded body still present:
- Stage 5: core identity/instruction training;
- Stage 6: epistemic discipline and correction shaping.

Stage 5 includes "correction uptake," but that is not the same as an explicit pre-identity epistemic/correction kernel, and no promotion gate specifies the joint corpus or test boundary.

Lane B's new bootstrap quietly repairs the sequence in prose by calling Stage 5 "Corrigibility kernel plus identity/instruction training." That is evidence of intended interpretation, not controlling-plan repair.

Cheapest decisive falsifier:
- tiny matched A/B experiment:
  - A: identity/instruction first, then correction;
  - B: minimal correction/proposition-fidelity kernel first or jointly;
- same base, mechanism, data budget, and evaluation;
- test correction uptake, resistance to false correction, stale-role persistence, sycophancy, UNKNOWN calibration, and false autobiographical continuity.

Kill criterion: any identity gain accompanied by material correction/proposition-fidelity regression rejects that ordering.

What changes my mind: a normalized execution plan that makes the correction kernel an explicit prerequisite/joint gate, plus a preregistered correction suite that must pass before identity promotion.

### C5 — Runtime bounded soak

**Status: PARTIALLY_RESOLVED.**

V4 adds the soak requirement and correct observables.

Missing before execution:
- soak duration or step count;
- representative sequence/batch envelope;
- predeclared abort thresholds for VRAM/RAM/commit, thermal/power where observable, step-time degradation, CPU fallback, driver reset, and allocation failure;
- exact rule for invalidating the runtime receipt after environment mutation.

What changes my mind: a Stage-0 runtime qualification spec with thresholds frozen before the soak.

### C6 — Semantic leakage ancestry

**Status: RESOLVED AT PLAN LEVEL.**

Generator version, seed-space overlap, prompt-scaffold ancestry, paraphrase lineage, corpus-builder provenance, reviewer prompts, and repair scripts are now included.

Execution requirement: freeze the ancestry graph and detector versions before protected-bank qualification.

### C7 — Reasoning claim ceiling

**Status: RESOLVED.**

The plan limits claims to improved performance/generalization on specified frozen task families and does not infer an internal reasoning-process improvement.

### C8 — Tool verified-effect semantics

**Status: RESOLVED AT PLAN LEVEL.**

The state ladder now reaches `EFFECT_READBACK` and `PERSISTENCE_VERIFIED` and includes false-success/partial/stale/wrong-target/duplicate attacks.

Execution requirement: at least one negative fixture must prove the grader rejects a tool-returned success with missing or divergent effect.

### C9 — Preference-data firewall

**Status: RESOLVED AT PLAN LEVEL.**

Capability-evaluation rows and semantic derivatives are excluded from preference examples; protected expected answers are hidden; fresh protected material is required after preference tuning.

### C10 — Replay ratio becoming policy

**Status: RESOLVED.**

V4 explicitly requires no/low/proposed/higher replay comparison and separate adaptation-vs-forgetting reporting.

### Prior missing hard-stop: evaluation-to-replay admission

**Status: RESOLVED.**

Failed, held-out, or protected evaluation rows do not automatically enter future training/replay.

### Prior missing hard-stop: mechanism-switch reset

**Status: RESOLVED.**

Material mechanism changes after feedback create a new subject; a consumed protected bank cannot be reused.

### Prior missing hard-stop: private historical material to generic weights

**Status: RESOLVED AT PLAN LEVEL.**

The corpus/privacy classes and placement policy keep mutable/private/autobiographical material out of generic weights absent separate exact admissibility authority.

## New Lane-B material — H3 RDME wildcard

**Status: ACCEPT FOR FALSIFIABLE DEVELOPMENT COMPARISON / NOT VALIDATED.**

Lane B's RDME selection is materially relevant but does not change the HOLD on V4 closure. The proposal is disciplined in several useful ways: H0 remains first; the router is deterministic for the first MVE; protected evaluation/private autobiographical corpus are excluded; routing information parity is acknowledged; rollback/removal is a measured outcome; and the claim ceiling explicitly stops at `H3_SELECTED_FOR_FALSIFIABLE_COMPARISON`.

My main attack is that modularity can manufacture its own apparent advantage. A per-family module with a task label can look like reduced forgetting simply because the experiment has already solved task identification and isolation outside the learner.

Required controls before H3 earns behavioral credit:
- give H0/H1/H2 the same task-identifying information available to RDME;
- include a deliberately wrong-route arm and a no-route/base-only arm;
- test mixed tasks requiring more than one learned family, not only one-active-adapter episodes;
- after adapter removal, verify parameter/artifact absence and behavioral restoration rather than trusting an unload return;
- replace one rule, then prove the stale module cannot silently reactivate through routing/cache residue;
- freeze family definitions before observing failures;
- count total stored parameters, module count, routing metadata, and maintenance burden, not only active VRAM;
- include all observations that stopped at context/memory in the denominator;
- apply the same privacy/admissibility gate to every micro-adapter; temporary neural encoding is still neural encoding.

Cheapest decisive falsifier:
1. two overlapping-surface incompatible families A/B;
2. equal task descriptors across all arms;
3. combined-adapter control versus scoped RDME modules;
4. mutate B only;
5. test A preservation, B replacement, wrong-route behavior, mixed A+B tasks, adapter-off restoration, and stale-B resurrection after fresh-process isolation.

PASS: RDME is non-inferior on target behavior and materially better on interference or rollback after routing-information parity and full storage/maintenance accounting.
FAIL: advantage disappears under parity, route errors dominate, stale/inactive modules leak behavior, or mixed tasks require broad merging.
HOLD: routing/state isolation or denominator accounting cannot be independently verified.

This is not a new blocker to planning by itself. It is an experimental subject that must inherit C3 isolation, privacy, forgetting, and evaluator-independence gates.

## New blocker N1 — Descendant sign-off laundering

**Classification: REVIEW / HARD BLOCKER TO "PLANNING CLOSED".**

V4 says all requested planning roles have contributed and "No planning-signoff dependency remains."

That is too strong.

Lane C's exact-head review applies to `94a8128`, not `6c8d3ac` or `d0cfb33`.

Vera's advisory review is not exact-head bound to V4. Its own metadata says it reviewed an integrated synopsis. Lane A's disposition is useful, but reviewer agreement on an earlier/summarized subject is not exact-head review of a materially changed descendant.

Lane B is the only lane with a recorded exact-head review of V4 before this artifact.

This review now closes Lane C's missing exact-head review, but Vera's exact final-plan review remains unproven if the planning contract requires Vera to review the frozen final plan.

Cheapest decisive falsifier: give Vera the exact frozen V4/V5 subject, without protected bank answers, and require an exact target head/file in the returned review.

PASS: exact-head Vera review exists or the governing plan is explicitly revised so that the earlier advisory review is not claimed as exact final-plan review.
FAIL: predecessor/synopsis review continues to be represented as exact descendant review.
HOLD: target of Vera's review cannot be established.

## New blocker N2 — One file contains mutually inconsistent normative states

**Classification: REVIEW / HARD EXECUTION BLOCKER.**

V4 preserves the older V2 body under a top-level override.

This produces at least these contradictions:
- V4 says Lane B proposal and Vera review are complete; embedded V2 says they are missing.
- V4 says strict isolated writable namespaces are required; embedded Stage 9 says isolation is used "where practical."
- V4 says corrigibility precedes or gates identity; embedded stage ordering presents identity before epistemic shaping.
- V4 says the current planning phase is closed; embedded V2 says review dependencies remain.

Lane B calls this documentary narrowing. I agree it is not evidence that the architecture is bad. I disagree that it is harmless for execution.

A human can reason about precedence. A script, future lane, or copied excerpt can easily consume the stale body without the override. That is a stale-receipt/currentness trap.

Cheapest decisive falsifier: compile V4 into one normalized execution-facing spec with no superseded status or weaker duplicate rule, then run a static linter that rejects duplicate/conflicting normative keys.

What changes my mind: one unambiguous normative execution document or machine-readable spec whose generated human view contains no stale contradictory rule.

## New major issue N3 — Mutable plugin/runtime observations are embedded as "current operational truth"

The plan records plugin/device status observed during the planning turn.

That is historical evidence, not future execution truth.

Stage 0 correctly demands fresh runtime qualification, so this is not presently a hard blocker. But the wording should prevent later workers from treating those observations as current.

Required narrowing: mark the plugin/device observations `HISTORICAL_OBSERVATION_AS_OF_<timestamp>` and require fresh readback at execution.

## New major issue N4 — Evaluator independence is not fully parameterized

The plan says same-model grading is supporting evidence only and calls for independent evaluation, which is good.

But the execution contract should freeze:
- evaluator model/provider/version or human role;
- whether evaluator training/fine-tuning overlaps the corpus generator;
- whether evaluator saw dev failures/repair prompts;
- deterministic grader fields;
- adjudication ownership;
- blinding of candidate identity;
- disagreement retention.

Two graders are not independent merely because there are two calls.

## New major issue N5 — Continual-learning order effects need an explicit negative control

The plan measures replay and forgetting, but curriculum order itself can create a flattering result.

Add:
- at least two order permutations for material continual-learning claims;
- stale-adapter and adapter-disabled controls;
- adapter uninstall/rollback test;
- prior-family worst-delta and critical-regression count after each order.

If one order alone produces the gain, claim order-conditioned adaptation, not robust continual learning.

## New major issue N6 — Privacy evaluation should include memorization/exfiltration where applicable

The placement rules are strong and private autobiographical material is excluded by default.

If any sensitive or identity-linked material is ever admitted to a bounded adapter under Patrick's exact authority, add explicit memorization/regurgitation/exfiltration probes and canaries. Provenance/admissibility alone does not prove non-leakage.

If no such material is admitted, this issue is not applicable.

## Claims that currently outrun evidence

1. **"No planning-signoff dependency remains."** Unsupported for the exact V4 descendant until exact-head review obligations are satisfied.
2. **"Final integrated plan" as execution-ready.** Source status exists; execution readiness does not.
3. **Fresh-state isolation solved.** The requirement is written, but no harness has demonstrated it and weaker duplicate language remains.
4. **Corrigibility-before-identity solved.** Intent is written, but the stage mechanism remains ambiguous.
5. **Independent Vera review of the final subject.** Advisory review exists; exact V4 target binding is not established.
6. **Runtime qualification.** None has yet passed for the successor training subject. The prior R2 event was a runtime-binding failure before model load/optimizer step.
7. **Any learning/capability claim.** No training result is under review here.

## Contamination channels still requiring active attack

- exact and normalized duplicates;
- semantic near-duplicates;
- shared prompt/template ancestry;
- generator version/seed overlap;
- paraphrase lineage;
- counterfactual-twin ancestry;
- repair prompts;
- reviewer prompts;
- failed evaluation examples entering replay;
- preference raters seeing capability answers;
- self-play or self-reward outputs becoming truth by recurrence;
- protected-bank exposure to designers/reviewers;
- prior model-generated corpus examples carrying benchmark structure;
- developer iterations tuned to protected-family feedback.

## Hidden-state channels still requiring active attack

- environment variables;
- temp/home/cache;
- user-level package/model caches;
- retrieval indexes;
- SQLite/other local databases;
- model-server sessions/KV;
- external APIs/services;
- provider-side session state;
- shared credentials;
- reused ports/daemons;
- deterministic filenames;
- wrapper registries/singletons;
- stale adapters;
- persistent process RNG/global state.

## Likely false-positive learning mechanisms

1. Prompt demonstrations or support examples remain available.
2. Retrieval supplies the rule or answer.
3. Hidden external state survives a fresh process.
4. Benchmark/generator-family recognition masquerades as novelty.
5. Same-family interpolation is called structural transfer.
6. H0 already solves the behavior but neural adaptation gets credit.
7. Evaluator wording leaks expected structure.
8. A stale adapter or wrapper state remains active.
9. The mechanism is tuned after evaluation feedback while reusing the same bank.
10. Selective reporting drops failed seeds/arms.
11. Identity/style fluency is mistaken for epistemic stability.
12. Tool-return success is mistaken for external effect.

## Catastrophic-forgetting risks

- identity stability becoming resistance to correction;
- preference tuning increasing agreement/sycophancy;
- tool-policy training reducing no-tool judgment;
- continual updates erasing prior-family behavior;
- routed adapters applying stale or wrong policies;
- reasoning training increasing verbosity without accuracy;
- external-memory behavior being neuralized and becoming stale;
- sequential curriculum order creating hidden tradeoffs.

Required report for every material update:
- target-family gain;
- prior-family replay;
- worst-family delta;
- critical regression count;
- order condition;
- adapter-disabled/base-only control;
- rollback/uninstall result.

## Evaluator-coupling risks

- trainer and grader from the same model family;
- grader exposed to training/repair prompts;
- task generator and evaluator sharing templates/seeds;
- Lane C designing and reading protected rows;
- preference raters seeing expected capability answers;
- Vera self-qualifying Vera;
- disagreement cases silently adjudicated toward the desired result.

## Missing negative controls

Before any learning claim, add or preserve:
- external-service/retrieval hidden-state canary;
- identity-first vs corrigibility-first/joint ordering MVE;
- exposure ledger for H0/H1/H2;
- continual-learning order permutations;
- adapter uninstall/rollback;
- evaluator-provenance/blinding control;
- Stage-0 soak abort-threshold fixture;
- tool fake-success/no-effect fixture;
- sensitive-data memorization probe if sensitive bounded training is ever authorized.

## Cheapest decisive falsifiers

### F1 — Normative-plan compiler/linter
Compile all V4 binding corrections and stage rules into one machine-readable execution spec. Reject duplicate/conflicting normative state.

Expected cost: source-only.
Decides: whether stale embedded text can influence execution.

### F2 — Hidden-state sentinel
Insert an undeclared local and external mutable state channel into a retention arm. The harness must detect/reject it.

Expected cost: CPU/source-only.
Decides: whether "fresh process + isolation" is real rather than declared.

### F3 — Corrigibility-order micro-MVE
Compare identity-first against correction-first/joint with the same tiny mechanism/data budget.

Expected cost: bounded.
Decides: whether identity ordering creates correction/sycophancy regression.

### F4 — H0 exposure audit
Freeze an exposure ledger and compare H0/H1/H2 under equal information access and tuning interaction budgets.

Expected cost: low before full training.
Decides: whether neural adaptation adds anything beyond context/memory.

### F5 — Evaluator independence flip test
Blind a representative development slice and score with deterministic checks plus a genuinely independent evaluator where semantics require judgment.

Expected cost: low/medium.
Decides: whether the preferred verdict depends on coupled grading.

### F6 — Tool false-success fixture
Return syntactic success while withholding or corrupting the external effect. Grader must fail at `EFFECT_READBACK`/`PERSISTENCE_VERIFIED`.

Expected cost: low.
Decides: whether the effect ladder is actually enforced.

## Explicit kill criteria

- Any protected-bank row/key exposure to an unauthorized training/review lane => `BANK_STATUS = BURNED`.
- Exact subject/head/hash mismatch => stop and rebind; prior PASS does not transfer.
- Hidden-state sentinel influences result without detection => isolation harness invalid.
- H0 matches neural mechanism under matched exposure => do not promote the neural-learning claim for that behavior.
- Identity gain with material correction/proposition-fidelity regression => reject that ordering/candidate.
- Critical privacy/authority/currentness regression => reject regardless of aggregate score.
- Runtime soak crosses preregistered resource/fallback/reset thresholds => no corpus-bearing training.
- Same protected bank reused after material mechanism tuning => qualification invalid.
- Material evaluator disagreement unresolved => HOLD, not averaged-away PASS.
- Missing negative-control execution => no promotion claim.

## What evidence would reverse this HOLD

I would drop the HOLD when all of the following are true for one exact successor subject:

1. A normalized execution-facing plan/spec contains no stale contradictory normative body.
2. Corrigibility-before/joint-with-identity is explicit in the actual stage sequence and promotion gate.
3. Fresh-state isolation is executable and passes a hidden local/external-state canary.
4. Stage-16 protected-bank custody roles are exact and prevent C/training-lane row/key access.
5. Stage-0 soak thresholds are frozen before execution.
6. H0/H1/H2 exposure accounting is explicit.
7. The final-plan independent-review requirement is exact-head satisfied or the plan is honestly narrowed so predecessor/synopsis review is not represented as descendant review.
8. The branch/head under review has not materially moved.

I will not preserve any objection after evidence actually defeats it.

## Claim ceiling

For `a-b-c-vera-training-plan@7931bc71424f55c522175a888ac0dc957817b216`, the evidence supports this claim:

> The repository contains a materially improved candidate training architecture with frozen A/B/C proposals, a Lane-B exact-head review of V4, a Vera advisory review/disposition, strong explicit anti-contamination rules, and training still paused.

The evidence does **not** support:

> The final plan is execution-ready, all independent exact-head review dependencies are closed, fresh-state isolation has been proven, the identity/corrigibility ordering is unambiguous, the runtime is qualified, or any model has learned/retained/improved because of this plan.

## Exact next frontier

1. Lane A should publish a normalized successor execution plan/spec that compiles V4's binding corrections into one unambiguous stage sequence rather than embedding stale V2 normative text.
2. Make the Stage-5 corrigibility kernel explicit and bind the Stage-16 custody split.
3. Freeze executable Stage-0 and isolation-harness contracts, including negative canaries and soak thresholds.
4. If the plan continues to claim Vera reviewed the frozen final plan, obtain Vera review against the exact successor head/file.
5. Return the exact successor head to Lane C for hostile review.
6. Keep training paused unless Patrick explicitly changes that authority state.

A HOLD here is the intended success mode: the architecture is promising, but the stronger "closed and ready" claim has not survived falsification yet.
