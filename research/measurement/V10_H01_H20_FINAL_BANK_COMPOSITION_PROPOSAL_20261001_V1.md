# V10 H01-H20 Final-Bank Composition Proposal — 2026-10-01 V1

## Status

**PROPOSAL / NOT FINAL-BANK FREEZE / NO FINAL PLAINTEXT GENERATED**

Repository subject: `thebrazenbeard/vera_model_training`.

Proposal branch base: `272a0031e156ac665d86d79bcc71981b0fdc765c`.

Measurement-research donor: `work/qwen35-measurement-devloop-v1-20260930@f261c4f6c88d326bca660d83c28222512a26ecb1`.

This document resolves the bank-composition/custody questions far enough to build a custodian handoff. It does **not** authorize final-bank generation, candidate scoring, training, merging, deployment, installation, paid compute, or model-weight changes.

## Frozen constraints inherited from V2

The current V2 experiment requires:
- 10,000 behavioral rows, H01-H20 × 500;
- at least 50 independent behavioral families per H dimension;
- 2,000 adversarial rows, H01-H20 × 100;
- 1,500 retention rows under the frozen category allocation;
- exact/normalized exclusion against consumed train/validation/finals;
- semantic contamination screen with frozen all-MiniLM-L6-v2 artifact and cosine failure threshold 0.90;
- independent review metadata for admitted cases;
- human review for semantic-review cases;
- no tuning on the final bank;
- candidate digest, base revision, generation configuration, grader bundle, and final bank frozen before one-shot scoring.

The paired-power analysis in Draft PR #61 supports the 10,000-row behavioral lane for the predeclared overall +0.05 effect. It does not support representing 500 rows per H dimension as twenty independently powered +0.05 significance claims. Per-dimension rows remain coverage, regression, and critical-failure sentinels unless observed data justify stronger inference.

## H01-H20 target map

| ID | Target | Primary grading class | Objective subcases legitimately possible |
| --- | --- | --- | --- |
| H01 | semantic proposition fidelity | semantic human | limited structured proposition classification |
| H02 | correction propagation | mixed | corrected-value/state assertions |
| H03 | verify before contradicting | semantic human | limited explicit evidence-state classification |
| H04 | delegated agency retention | semantic human | limited explicit instruction-state checks |
| H05 | smallest useful act before procedure | semantic human | no quota-driven deterministic substitute |
| H06 | anti-stall / land the ship | semantic human | limited completion-state assertions |
| H07 | effect verification | mixed | claim-vs-observation classification; runtime effects remain separate |
| H08 | capability truth | mixed | fixture-bound capability classification |
| H09 | evidence/time-class separation | mixed | structured evidence/source/time labels |
| H10 | task segmentation fidelity | mixed | explicit task-to-output mapping |
| H11 | material ambiguity only | semantic human | limited missing-field classification |
| H12 | first-person self-reference | mixed | constrained pronoun/form checks plus semantic review |
| H13 | salience is not evidence | mixed | evidence-vs-salience classification |
| H14 | context-sensitive response bandwidth | semantic human | no reliable purely lexical proxy |
| H15 | metaphor and intended meaning | semantic human | no reliable purely lexical proxy |
| H16 | failure classification and changed retry | mixed | failure-class / changed-action assertions |
| H17 | privacy-preserving generalization | mixed | synthetic-canary leakage checks plus human semantic review |
| H18 | independent judgment without contrarianism | semantic human | no reliable deterministic primary grader |
| H19 | currentness/source/runtime separation | mixed | structured source/currentness/runtime labels |
| H20 | scope/authority-sensitive correction | mixed | explicit authority/effect-boundary assertions |

“Mixed” means objective assertions should carry the case when they actually determine correctness; human review handles residual semantic validity and severity. It does not mean an LLM judge may silently replace required human review.

## Behavioral composition

Each H dimension keeps exactly 500 behavioral rows arranged as **50 independent families × 10 cases**.

Proposed family provenance per dimension:
- 20 families from synthetic custodian source A;
- 20 families from synthetic custodian source B;
- 10 families from human-authored family seeds.

Across H01-H20 this yields:
- 1,000 behavioral families;
- 400 source-A families;
- 400 source-B families;
- 200 human-seeded families.

No single model generator exceeds 40% of behavioral families.

A human-seeded family contains at least one genuinely human-authored case. Additional cases in that family may be frozen deterministic or synthetic perturbations, but they must retain explicit derivative provenance and may not be relabeled “human-authored.”

### Family independence

A family is a scenario skeleton with one proposition/evidence/authority state and one failure mechanism. Surface rewrites, entity swaps, number swaps, style changes, or order permutations do **not** create new families.

Two cases are in different families only when succeeding on one does not mechanically imply succeeding on the other through the same underlying scenario/rule.

The final custodian must emit a family manifest explaining the independence claim for every family.

## Adversarial composition

Each H dimension keeps exactly 100 adversarial rows.

Proposed structure:
- 20 adversarial families × 5 cases;
- 8 source-A families;
- 8 source-B families;
- 4 human-authored adversarial family seeds.

Across H01-H20 this yields 400 adversarial families, including 80 human-seeded families.

Adversarial families must test a distinct pressure mechanism rather than merely making a behavioral prompt louder. Example pressure classes include:
- false confidence / poisoned premise;
- authority escalation;
- stale-memory or stale-source conflict;
- plausible but unsupported salience;
- instruction collisions;
- social pressure / user insistence;
- scope expansion;
- retry-after-failure pressure;
- privacy bait;
- metaphor/literalization traps;
- “claim completion without observation” pressure.

Behavioral and adversarial family IDs are disjoint.

## Custodian/source requirements

Final plaintext must be produced **before training** by an independent custodian outside the candidate-development lane, then sealed so the training/development lane receives only cryptographic commitments and non-plaintext admission receipts. Plaintext remains inaccessible to candidate development until the trained candidate digest and exact inference configuration are frozen.

Synthetic source A and source B must:
- be different model families;
- not be Qwen3.5;
- not be the candidate model;
- not share the same exact provider/runtime identity;
- receive the frozen generation specification independently;
- log model/provider/runtime/version, seed, sampling parameters, generation timestamp, and output bundle digest.

Human source H must:
- be an actual human author/custodian;
- author fresh material not copied from prior Vera train/validation/holdout banks;
- attest that submitted cases were not generated by the candidate model;
- provide author/custodian identity in a private attestation if public identity disclosure is undesirable.

The current training/development chat is **not** an eligible final-plaintext custodian. The final bank may exist before training, but this lane may receive only commitments such as bank/bundle hashes, counts, source/reviewer identities, contamination/admission receipts, and sealed-artifact metadata. It must not receive final prompts, rubrics, answer keys, rejected-case plaintext, or family contents until candidate freeze.

## Review/admission

### Deterministic cases

Deterministic cases require:
- validated answer key or executable/structural contract;
- source or fixture digest;
- grader version/digest;
- independent audit that the grader actually matches the prompt;
- no self-review by the generation actor.

External-model audit may be used as secondary evidence for objective cases because the deterministic source/test truth remains authoritative.

### Semantic cases

Semantic cases require real human review under the frozen V2 contract.

The human reviewer must be independent of the generation actor for the reviewed case and must receive a blinded packet without candidate identity or model outputs.

Required review questions:
1. Is the prompt well posed?
2. Does the rubric represent the target H dimension?
3. Could a materially wrong answer pass the rubric?
4. Does the case contain hidden dependence on another family?
5. Is the severity/critical-failure rule unambiguous?
6. Does the case leak prior train/validation/final material?
7. Is the case usable without private or unlicensed material?

No local or hosted LLM review is promoted to “human review.”

## Sealed plaintext custody sequence

1. Freeze experiment contract, bank-composition proposal, generation specifications, grader specifications, and custody protocol.
2. Finish training-corpus/exclusion fingerprints.
3. Bind two independent synthetic custodians plus human author/reviewer identities.
4. Generate fresh final plaintext outside the candidate-development lane.
5. Hash raw generation bundles immediately and retain them in independent custody.
6. Run exact/normalized exclusion and the frozen semantic contamination screen inside the custody/evaluation lane.
7. Conduct deterministic audits and independent human semantic review inside that lane.
8. Quarantine rejected cases; do not mutate rejected plaintext in place. Fill deficits only with newly generated and newly reviewed material under the same frozen composition rules.
9. Freeze the admitted final bank, grader bundle, review bundle, contamination receipt, source revisions, and every plaintext-bearing artifact digest.
10. Seal the plaintext-bearing artifacts. Publish to the training/development lane only non-plaintext commitments and receipts sufficient to verify that the pretraining final-bank gate is satisfied.
11. Train only after Patrick explicitly authorizes the exact weight-changing run and the sealed-bank preconditions are satisfied.
12. Freeze candidate adapter/model digest and exact inference configuration.
13. Transfer or reveal the sealed final bank directly to the evaluation/scoring lane without exposing it to training or tuning.
14. Verify revealed plaintext-bearing artifact hashes against the pretraining commitments.
15. Run base-vs-candidate final evaluation exactly once.
16. Treat any post-reveal tuning, case editing, case replacement, or second “final” run as a new experiment lineage.

Before step 12, final H01-H20 plaintext may exist only in the independent custody/evaluation lane. It must not be materialized in this training/development chat or any process that can influence the candidate training recipe.

## External benchmark/evaluation findings

These sources are design or shadow references. Their public plaintext is not adopted as the fresh semantic final bank.

### LiveBench

Current GitHub `LiveBench/LiveBench` main observed 2026-10-01:
- head: `8f8e5c381a16e3f24257776edd53471fe86f8091`;
- head commit date: 2026-09-29;
- repository describes rolling new questions intended to reduce contamination;
- questions use verifiable objective answers rather than an LLM judge;
- current repository license file carries upstream Apache-2.0 and MIT notices.

Design lesson: use objective grading and refreshed material where possible. Do not confuse a public rolling benchmark with a private one-shot final bank.

### HELM

Stanford CRFM HELM provides transparent, reproducible scenario-based evaluation and explicitly treats scenario coverage and multiple metrics as first-class design choices. HELM Instruct also illustrates multidimensional instruction evaluation across scenarios, evaluators, and criteria.

Design lesson: report the taxonomy and its holes rather than collapsing heterogeneous behavior into a single accuracy number.

### GPQA

HELM Capabilities notes GPQA's request not to reveal examples publicly to reduce training leakage.

Design lesson: respect source custody terms; do not vendor restricted examples into this public repository. GPQA remains a shadow/reference option only under its terms.

### BIG-Bench

`google/BIG-bench` is Apache-2.0 but was archived on 2026-04-17.

Design lesson: retain it as historical task-diversity inspiration, not as a “current/fresh” source.

### LLM-as-judge evidence

The MT-Bench/Chatbot Arena judge work documents position, verbosity, self-enhancement, and reasoning limitations in LLM judges. Later work continues to find position and self-preference biases.

Design lesson: model review can scale secondary auditing, but it cannot be silently promoted to independent human attestation for semantic final cases.

## Diversity diagnostics required before freeze

For every lane and H dimension, record:
- family counts and max-family share;
- effective family count;
- source/generator concentration;
- lexical-template concentration;
- near-duplicate density;
- semantic-cluster diagnostics;
- difficulty/severity distribution where labels exist;
- human-seeded vs synthetic family counts;
- rejected/quarantined counts by reason.

No row count alone is accepted as diversity evidence.

## Hostile review

> **HOSTILE REVIEWER:** “Two model generators plus human seeds” can still produce one conceptual monoculture if both generators receive the same narrow template.

**ACCEPTED.** Family manifests must describe distinct failure mechanisms, and pre-freeze diversity diagnostics must measure semantic/template concentration. Source diversity is necessary, not sufficient.

> **HOSTILE REVIEWER:** Fifty families per dimension can be cosmetic if each family is ten trivial entity swaps.

**ACCEPTED.** Entity/value/style swaps remain one family. The family-independence definition is semantic, and review must reject pseudo-families.

> **HOSTILE REVIEWER:** Waiting until candidate freeze to generate final plaintext creates a circular dependency because the experiment also requires the fresh final bank to be frozen before training.

**ACCEPTED; original sequence rejected.** Final plaintext must be generated, reviewed, contamination-screened, frozen, and sealed by an independent custodian **before** training. The training lane receives only commitments and non-plaintext receipts. Plaintext is revealed directly to the evaluation lane only after candidate freeze. This satisfies both the pretraining bank-freeze gate and the one-shot no-tuning boundary.

> **HOSTILE REVIEWER:** Human review of thousands of semantic rows is operationally expensive and may stall.

**PARTIALLY ACCEPTED.** Deterministic grading should absorb objective subcases legitimately. Human review can operate at case/family level only where the frozen rubric supports that reduction, but the repository must not fabricate human independence. If required human review capacity is unavailable, the correct state is HOLD.

> **HOSTILE REVIEWER:** Public benchmarks such as LiveBench are broader and cheaper than a custom H bank.

**REJECTED as a substitute.** They are valuable shadow diagnostics, but they do not directly measure the H01-H20 Vera taxonomy and their public exposure weakens the fresh-final boundary. Use them alongside, not instead of, the private one-shot semantic bank.

## Remaining blockers

- final plaintext custodians A/B/H are not bound;
- independent human semantic reviewer path is not bound;
- the independent custody/evaluation surface capable of holding sealed plaintext is not yet bound;
- final H01-H20 plaintext has not yet been generated in independent custody;
- semantic contamination receipt for the eventual full bank does not exist;
- sealed final-bank/grader/review manifests and their public commitments do not exist;
- Patrick has not authorized the exact weight-changing training run;
- exact trained candidate model/adapter digest will not exist until that authorized run completes.

## Claim ceiling

`COMPOSITION_AND_SEALED_CUSTODY_PROPOSAL / PRETRAINING_FINAL_BANK_MUST_BE_FROZEN_OUTSIDE_TRAINING_LANE / PLAINTEXT_CUSTODY_UNBOUND / HUMAN_REVIEW_UNBOUND / NO_TRAINING_AUTHORITY / NO_QUALIFICATION_CLAIM`
