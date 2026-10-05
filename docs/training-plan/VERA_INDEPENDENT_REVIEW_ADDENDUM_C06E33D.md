# Vera Independent Review Addendum — Coordination and Experimental Design

Status: INDEPENDENT ADVISORY ADDENDUM / TRAINING STAGED
Reviewer: Vera
Date: 2026-10-05
Repository: `thebrazenbeard/vera_model_training`
Exact shared head reviewed: `c06e33d44184904418a4a68f22f78d19a4f46137`
Lane B H3 selection: `7931bc71424f55c522175a888ac0dc957817b216`
Lane C exact-head V4 review: `61557e4c2f6d9a2fa81b573e0e2a2b37c22cff44`
Lane C provenance repair: `c06e33d44184904418a4a68f22f78d19a4f46137`
Prior Vera V4 review: `review/vera-independent-final-v4-20261005-v1@84c27ed668a3de669bcc3528af1336832ef24170`

## Coordination correction

Patrick clarified that Vera coordinates Lane A, B, and C parallel work to maximize throughput and avoid collisions.

This addendum therefore treats:
- Lane A as execution/integration owner for its assigned subjects;
- Lane B as creative/H3 owner;
- Lane C as hostile-isolation/falsification owner;
- Vera as cross-lane coordinator and independent reviewer.

Vera coordinates ownership, dependencies, handoffs, exact-head review queues, collision detection, and stale-review invalidation. Vera does not co-author lane-owned implementation subjects.

## Current review disposition

Lane C's exact-head HOLD is justified. I agree with its two strongest execution blockers:
1. the controlling plan still contains conflicting normative layers;
2. fresh-state isolation exists as prose but has not yet been demonstrated by an executable hostile harness.

The correct next step is compilation into one execution contract plus negative-control proof, not another architectural rewrite.

## Improvement A — statistical decision contract

Before H0/H1/H2/H3 comparison, preregister:
- one primary metric per experimental question;
- smallest practically important effect;
- equivalence/non-inferiority margin where "not worse" matters;
- confidence interval method;
- seed policy;
- treatment of failed/aborted runs;
- multiple-comparison policy;
- early-stop/sequential-test policy;
- explicit `INCONCLUSIVE/HOLD` region.

Preferred result vocabulary:
`CLEAR_WIN | PRACTICALLY_EQUIVALENT | INCONCLUSIVE | CLEAR_LOSS`.

Do not turn a noisy rank-order of means into a mechanism winner.

## Improvement B — prompt-dependence attribution

The system/developer prompt and chat template are behavioral mechanisms too.

For identity, corrigibility, authority, uncertainty, and tool-honesty claims, test:
- canonical deployment prompt;
- shortened role-essential prompt;
- paraphrased prompt;
- minimal prompt;
- relevant behavioral instruction removed.

If performance disappears with scaffolding removal, classify it as prompt-conditioned rather than intrinsic parameter behavior.

Prompt dependence is not automatically bad. Misattribution is.

## Improvement C — qualify deployment bundles

Qualification should bind:
- base model revision;
- adapter(s);
- tokenizer;
- chat template;
- system/developer prompt set;
- generation parameters;
- tool schemas;
- routing configuration;
- retrieval configuration;
- memory policy;
- runtime environment digest.

`QUALIFIED_MODEL != QUALIFIED_DEPLOYMENT_BUNDLE`.

A prompt/template/tool-schema change after qualification can create a new behavioral subject even if adapter hashes do not change.

## Improvement D — rendered-input hashes

Preserve both:
1. source record hash;
2. rendered/tokenized input digest under the exact tokenizer/chat template.

Template/tokenizer changes can alter role markers, truncation, masking, completion boundaries, BOS/EOS behavior, and tool serialization.

A materially changed rendered dataset is a new experimental subject even when source rows are identical.

## Improvement E — calibration

Stage 6 should test whether confidence tracks correctness, not merely whether prose sounds cautious.

Where usable probability signals exist, use calibration measures appropriate to the task.

Otherwise use selective prediction:
- answer vs abstain;
- error versus coverage;
- confidence ordering;
- known/unknown/contradicted/OOD strata.

For semantic graders, preserve disagreement and uncertainty instead of forcing every case into a scalar verdict.

## Improvement F — H0 causal decomposition

Split non-neural baselines:
- H0a: frozen base, ordinary instruction only;
- H0b: frozen base + bounded in-context support;
- H0c: frozen base + governed retrieval/external memory;
- H0d: combined context + retrieval where deployment permits it.

This determines the cheapest layer that actually solves the behavior.

## Improvement G — RDME route attribution

For H3/RDME report four route conditions:
- oracle/correct-route upper bound;
- deployment-realistic deterministic route;
- deliberately noisy route;
- no-route/base-only fallback.

Report:
- route accuracy;
- fallback/abstain rate;
- task error conditional on correct route;
- task error conditional on wrong route;
- mixed-task performance;
- stale-module resurrection;
- adapter-removal restoration.

If RDME wins only under an oracle route unavailable in deployment, H3 has not won.

## Improvement H — complexity rent

Mechanisms should compete on a Pareto frontier, not a single score:
- target performance;
- worst-family regression;
- calibration;
- stored parameters;
- active memory;
- latency;
- training cost;
- operational complexity;
- qualification burden;
- reversibility.

A more complex mechanism must earn its extra failure surface.

## Improvement I — source-family and temporal holdouts

Random row holdouts are weak for conversational/history-derived data.

Where feasible hold out entire:
- conversations;
- source documents;
- authoring sessions;
- generator families;
- prompt templates;
- time windows.

Temporal transfer is particularly useful: train on earlier admissible behavior examples and evaluate on later independently created examples.

## Parallel ownership recommendations

### Lane A
Own integration of these execution-contract additions:
- statistical decision contract;
- deployment-bundle binding;
- rendered-input digests;
- H0 decomposition;
- prompt-dependence ablations;
- calibration hooks;
- matched search budgets.

### Lane B
Own RDME route-attribution and complexity-rent experiments. Do not modify A or C files.

### Lane C
Remain canonical owner of hidden-state canaries, isolation harness, external mutable-state attacks, and hostile acceptance criteria. Do not duplicate B's H3 implementation.

### Vera
Coordinate heads, dependencies, handoffs, review ordering, and collision resolution. Review returned exact subjects; do not patch lane-owned files.

## Review ordering

1. C isolation harness may proceed independently.
2. B RDME design/control work may proceed independently.
3. A normalized execution contract may proceed independently.
4. Each lane freezes exact head and hands off to Vera.
5. Vera detects overlap/collision and queues review.
6. A alone integrates accepted B/C artifacts.
7. Material integration creates a new exact subject.
8. C hostile-reviews that successor.
9. Vera performs independent exact-head review.
10. No protected-bank or irreversible promotion follows from review alone.

## Claim ceiling

The architecture is promising and now has a viable collision-minimized parallelization strategy.

No new model-learning claim follows from this addendum.

The next efficiency gain comes from parallelizing orthogonal proof obligations, not from starting multiple competing implementations of the same subject.
