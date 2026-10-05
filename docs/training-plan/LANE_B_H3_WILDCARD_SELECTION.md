# Lane B H3 Wildcard Selection

Status: LANE B BOUNDED FOLLOW-UP / PLANNING ONLY / TRAINING PAUSED
Date: 2026-10-05
Lane: B
Parent planning branch: a-b-c-vera-training-plan
Parent exact head: 1e0bb1d4a5ddd0b225773f23229447956b7d8959
Main head observed: 0e1546bd8a5e0f2fbf46ca3e901e0d2cf0de11c9
Coordination head observed before INTENT: 37d350b86c23e15e416baeb18779fc95cc5a4584
GPU lease observed: HELD by LANE_A for V10R3R2_DURABLE_CONTINUOUS20_EXECUTION. This work is source-only and does not use or alter that lease.

## Decision

HYPOTHESIS: H3 should not be another PEFT recipe. Lane B selects Routed Disposable Micro-Adapter Escrow (RDME).

RDME is a two-speed learning topology:
1. frozen base / qualified slow core;
2. context first;
3. governed external memory second;
4. only recurring stable unresolved deficits may enter a capability-scoped disposable micro-adapter;
5. fast adapters remain quarantined, reversible, attributable, and expirable;
6. no automatic slow-core promotion exists.

The adapter substrate is not the H3 claim. If H1 selective LoRA wins the boring mechanism comparison, RDME may use tiny LoRA modules. If H2 IA3 wins, RDME may use IA3-like modules. H3 tests where learning lives, when weight change is allowed, and whether scoped reversible fragments beat one continually rewritten adapter.

SOURCE: LANE_B_CREATIVE_PROPOSAL.md already favors two-speed plasticity, plasticity escrow, modular behavioral organoids, and routed micro-adapters.
SOURCE: VERA_STAGED_TRAINING_PLAN_FINAL_V2.md leaves H3 open and permits protected slow core + disposable fast adapters and routed micro-adapters.
FACT: This artifact selects a research hypothesis only. It authorizes no training, protected evaluation, merge, deployment, paid compute, or promotion.

## Assumption attacked

RDME attacks:
- ONE_MODEL == ONE_MONOLITHIC_MUTABLE_STATE
- DURABLE_BEHAVIOR == IMMEDIATE_WEIGHT_PROMOTION
- CONTINUAL_LEARNING == CONTINUAL_REWRITE_OF_ONE_ADAPTER
- FORGETTING == ALWAYS_BAD

The core proposition is that adaptation and consolidation do not have to be the same event.

## Mechanism

OBSERVE
-> TRY_CONTEXT
-> TRY_EXTERNAL_MEMORY
-> CONFIRM_RECURRING_STABLE_DEFICIT
-> CREATE_FAST_ESCROW_ADAPTER
-> SUPPORT_REMOVAL
-> UNSEEN_TRANSFER
-> REGRESSION / INTERFERENCE TEST
-> EXPIRE | RETAIN_QUARANTINED | PROPOSE_SLOW_PROMOTION

For the first MVE, routing is deterministic and externally specified. Do not train the router yet. A learned router would confound the first question.

## Minimum viable experiment

EXPERIMENT DESIGN ONLY. Training remains paused.

Use development-only synthetic task families. No protected bank. No private autobiographical corpus.

Create three families with different latent rules, deliberately similar surface forms, one later-changing rule, one recurring family, and one one-off family.

Compare under matched exposure:
- H0: frozen model + context/external memory.
- H1: one selective LoRA/QLoRA adapter across all families.
- H2: one IA3-style adapter across all families.
- H3/RDME: context/memory first, then one disposable micro-adapter per recurring unresolved family; deterministic router; one active adapter at inference.

Match total examples, total optimization-step budget, evaluation settings, open-test families, replay exposure, support-removal protocol, and task-identifying information available to each arm.

Report target gain, unseen-instance transfer, unseen-family transfer, prior-family regression, mutable-rule replacement, false-route rate, adapter-off restoration, stored parameters, active parameters, peak RAM/VRAM, wall time, and number of observations that never needed weight change.

A system that achieves equal behavior with fewer promoted weight updates wins even if headline accuracy ties.

## Cheapest falsifier

EXPERIMENT DESIGN ONLY UNTIL PATRICK UNPAUSES TRAINING.

Use the smallest local surrogate capable of cross-task interference. Two families are enough:
- A and B use overlapping surface tokens but incompatible rules.
- train one combined-adapter control;
- train two scoped disposable modules with deterministic routing;
- change B and retrain only B.

Kill RDME if modular escrow does not reduce interference, improve rollback, or preserve A while B changes.

If routing reveals task information unavailable to controls, the result is invalid.

## Expected result if correct

HYPOTHESIS:
- many episodes stop at context/external memory and never trigger weights;
- scoped modules reduce cross-family forgetting;
- replacing/removing one module affects only its intended family;
- support removal reveals exactly which behavior is adapter-carried;
- inactive modules can remain off-device;
- provenance and rollback are cleaner than one merged adapter lineage.

The architecture-changing result would be discovering that a large fraction of planned training should never touch permanent weights.

## Expected result if wrong

- H1/H2 matches or beats RDME on retention and transfer;
- routing errors erase modularity benefit;
- mixed tasks require broad adapter merging;
- storage/maintenance cost dominates;
- apparent gains vanish after routing-information controls.

Then keep the simpler single-lineage adapter and kill RDME.

## Triage

WILDNESS: 5/5
UPSIDE: 5/5
TEST_COST: 2/5 kill test; 3/5 model-scale MVE
FALSIFIABILITY: 5/5
REGRESSION_RISK: 2/5 while quarantined
CONTAMINATION_RISK: 2/5 with synthetic development families
REVERSIBILITY: 5/5

INFERENCE: 4 GB VRAM makes RDME more interesting because only one tiny adapter needs to be active at inference and the topology can be killed on a surrogate before full-model GPU time.

No paid compute is justified for the first falsifier.

## Easiest ways this could fool us

1. Router label leakage. Give every arm the same task descriptor and score routing separately.
2. Denominator laundering. Report solved and non-promoted cases; refusing to learn is not a capability win.
3. Hidden routing state. Fresh process and isolated writable state remain mandatory.
4. Storage accounting tricks. Report total disk/RAM footprint and adapter count, not only active VRAM.
5. Family definitions tuned after failures. Freeze families before evaluation.
6. Single-family scoring hides composition failure. Include mixed-task probes.

## Forgetting and privacy

RDME is intended to reduce interference, but stale routing can resurrect obsolete modules. Attack corrected rules, overlapping claims, gradual concept drift, genuinely new tasks, and mixed tasks.

Do not silently merge adapters to hide conflict.

FACT: Mutable facts, personal records, episodic history, current repo state, and source-sensitive claims remain external-memory material by default.

A temporary adapter is still neural encoding. RDME is not a privacy loophole.

HYPOTHESIS: useful continual learning may require selective forgetting. Fast modules should expire when the behavior was one-off, the rule changed, recurrence vanished, external memory now suffices, a better module supersedes it, replay shows regression, or provenance becomes invalid.

## What I would delete if RDME succeeds

Do not delete evaluation, custody, hostile review, or receipts. Delete unnecessary weight-training assumptions:

1. one capability -> one permanent training stage as the default model;
2. direct slow-core updates for first-contact novel tasks;
3. neural storage of mutable tool schemas, project state, current facts, episodic history, or user-specific records;
4. continual learning as repeatedly reopening one adapter;
5. automatic consolidation after fast adaptation;
6. broad replay for unrelated capabilities if scoped modules prevent the same interference more cheaply;
7. later training stages that H0/RDME converts into evaluation + routing + memory-placement stages.

If H0 alone matches RDME, delete RDME too.

## Handoff

Lane A execution packet after explicit unpause:
- subject: H3_RDME_MVE_V1
- same Stage-4 development exposure contract as H0/H1/H2
- deterministic frozen router
- tiny substrate selected from H1/H2 feasibility without changing the H3 claim
- Stage-0-qualified runtime only
- protected evaluation prohibited
- local-only first; no paid compute
- pass: non-inferior target performance plus materially lower interference or materially better rollback/reversibility
- fail: no retention/interference advantage after fair routing controls
- abort: privacy breach, protected-bank exposure, hidden mutable state, unbound source/runtime, or resource escape
- artifacts: exact spec, metrics, route decisions, module hashes, adapter-on/off tests, resource receipt

Lane C should attack router leakage, cross-arm state, family-definition tuning, private-memory laundering, inactive adapter residue, composition failure, and denominator manipulation.

Vera should review the operational proposition, not metaphors: capability-scoped reversible neural modules may reduce interference and unnecessary permanent weight updates versus one continually rewritten adapter.

## Hostile self-review

> HOSTILE REVIEWER: This is multiple LoRAs plus an if-statement dressed up as a theory of learning.

PARTIALLY ACCEPTED. The first MVE should be that boring. If deterministic routing plus scoped adapters fails, a learned router or adapter ecology is unjustified. The novelty is the promotion topology and expiry policy.

> HOSTILE REVIEWER: H3 cheats because task isolation itself prevents interference.

ACCEPTED AS THE POINT, NOT AS A FREE WIN. Controls get the same task identity, mixed-task composition must work, and total storage/maintenance cost must be counted. If fair controls remove the advantage, kill H3.

> HOSTILE REVIEWER: H0 may already solve everything.

ACCEPTED. H0 is the first gate. If context + governed external memory solves the behavior with acceptable latency and fidelity, do not train H3.

## Abandon conditions

Abandon RDME on any surviving result:
- no measurable interference/forgetting reduction versus single-adapter control;
- route error dominates task error;
- mixed tasks require broad merging;
- module removal does not cleanly demonstrate rollback;
- per-module privacy/admissibility cannot be enforced;
- operational burden exceeds benefit;
- H0 already solves the capability;
- simpler H1/H2 achieves the same result with equal or better reversibility.

## Claim ceiling

FACT: H3 is selected as Lane B's preferred wildcard hypothesis.
UNKNOWN: RDME has not been experimentally validated.
UNKNOWN: No training is authorized or executed by this artifact.
CLAIM CEILING: H3_SELECTED_FOR_FALSIFIABLE_COMPARISON; not H3_VALIDATED, not TRAINING_RESUMED, not MODEL_IMPROVED, not VERA_QUALIFIED.
