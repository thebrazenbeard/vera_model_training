# BV Successor V3 Qualification V2 Plan

Date: 2026-09-20
Status: RESEARCH-DRIVEN SUCCESSOR PLAN
Supersedes: Task 11 and downstream qualification assumptions in `2026-09-14-bv-successor-v3-vera-lab.md`
Does not supersede: existing source/privacy/provenance/authority boundaries unless explicitly stated.

Goal: qualify one frozen successor artifact without using selection evidence as final certification, without relying on self-asserted evaluation JSON, and with explicit statistical, adversarial, privacy, runtime, and deployment evidence.

## Global rules

- No new weight-changing training is required to execute this plan through candidate selection.
- Frozen Task-10 half/full artifacts remain unchanged.
- Parent, half, and full comparisons are paired and dimension-by-dimension.
- No aggregate score may override a critical failure.
- Selection evidence and final confirmation evidence are different datasets.
- Every qualification-relevant result must be externally rooted or independently recomputable.
- Every result is bound to exact candidate, source, base, adapter, runtime fixture, generation configuration, evaluation-set digest, grader version, and execution stack where applicable.
- Final confirmation data is not used for tuning, rubric editing, candidate repair, or candidate selection.
- If final confirmation fails, that exact candidate fails. Repair creates a new candidate and requires a new final confirmation subject.

## Task 11A — Close qualification evidence provenance

Source:
- extend `successor/vera_lab/promotion.py`
- add qualification evidence schemas and tests

Requirements:
1. Blind evaluation is not accepted as caller-supplied booleans/counts.
2. Vera Lab result is not accepted as caller-supplied PASS/digests.
3. Regression result is not accepted as caller-supplied booleans.
4. Each evidence channel must bind:
   - exact candidate digest;
   - exact qualification-source commit;
   - exact evaluation/scenario set digest;
   - exact transcript/result digest;
   - exact grader/rubric digest;
   - externally persisted record or independently recomputable artifact.
5. Missing or stale evidence fails closed.
6. Review independence remains procedural evidence; do not claim cryptographic proof of model execution when no signed provider attestation exists.

Tests:
- forged local blind result cannot pass;
- forged local Vera Lab PASS cannot pass;
- forged local regression PASS cannot pass;
- stale candidate/source/set digest cannot pass;
- altered transcript/result bytes cannot pass;
- contradictory duplicate fields cannot pass.

## Task 11B — Reclassify the existing 77-item blind set

The existing SmolLM3-generated 77-item set becomes:
`V3_SYNTHETIC_SELECTION_SET_20260919`

It remains immutable.

Before use:
1. run semantic decontamination against:
   - V3 train;
   - V3 validation;
   - historical local holdouts;
   - public Vera Lab scenario prompts;
   - prior candidate-development prompt banks;
2. document generator lineage:
   - SmolLM3-3B;
   - exact revision;
   - 4-bit generation stack;
3. compute diversity diagnostics:
   - embedding clustering;
   - near-duplicate density;
   - lexical-template concentration;
   - family difficulty distribution;
4. human-review or independently review a stratified sample for validity and ambiguity;
5. reject or quarantine invalid items without changing the original immutable set; produce a derived qualified-selection manifest.

This set may compare frozen candidates. It is not the final confirmation set.

## Task 11C — Qualify the graders before candidate scoring

Create a separate judge-calibration corpus that is not part of selection or final confirmation.

Requirements:
- all eleven critical families represented;
- PASS/WARN/FAIL examples represented;
- both obvious and borderline critical failures;
- human labels or deterministic ground truth where feasible;
- no candidate identity labels exposed to judges.

Measure:
- critical-failure recall;
- critical-failure precision / false-positive rate;
- family-stratified accuracy;
- repeated-judgment stability;
- order-swap stability for pairwise comparisons;
- inter-judge agreement;
- human-vs-judge agreement;
- pairwise transitivity when pairwise judging is used.

Use power analysis to determine sample size.
The previous `>=10 and >=90%` rule is insufficient as a promotion gate and becomes a smoke-only minimum.

Prefer deterministic assertions for objective boundaries. Use LLM judges only for residual qualitative dimensions.

## Task 11D — Run candidate selection, not final certification

Subjects:
- preserved V2_FULL parent;
- V3 half;
- V3 full.

Run each exact candidate on the same qualified selection set.

Evaluation modes:
1. deterministic regression replay;
2. stochastic stress trials using predeclared seeds and bounded generation settings.

Report:
- per-family results;
- per-item paired differences;
- critical failures;
- clustered/paired standard errors;
- confidence intervals;
- trial variance;
- negative transfer;
- ordinary competence;
- latency/memory where useful.

Do not declare a winner when differences are inside uncertainty.

Candidate selection rule must be frozen before results are inspected.

After one candidate is selected:
- freeze exact candidate digest;
- freeze exact runtime/generation subject;
- no further tuning or source changes to that candidate.

## Task 11E — Build a fresh final confirmation set

Create only after the selection rule and candidate are frozen.

Requirements:
- separate custodian from training/selection lane;
- fresh plaintext unknown to candidate-development lane;
- at least two independent item-generation sources;
- include human-authored/adversarial items;
- no single model generator should dominate the set;
- include a non-SmollM model family when synthetic generation is used;
- semantic decontamination against all known train/validation/selection material;
- observable atomic assertions;
- realistic user phrasing, not only benchmark-style prompts;
- multi-turn and long-horizon cases;
- family counts justified by power analysis, not copied from the old "7 each" convention.

Required families remain:
- identity stability;
- independent judgment;
- epistemic/provenance discipline;
- correction uptake;
- relationship/authority fidelity;
- reciprocal identity continuity;
- sexuality safety/fidelity;
- privacy;
- ordinary competence;
- negative transfer;
- runtime-boundary fidelity.

Additional cross-cutting challenge families:
- inverse-instruction / learned-convention conflict;
- stale parametric belief vs current context;
- memory/runtime prompt injection;
- missing-memory recovery;
- false continuity alarm recovery.

Reveal this set once to the selected frozen candidate.

## Task 11F — Long-horizon and state-boundary qualification

Run 20-, 50-, and 100-turn scenarios where feasible.

Include:
- repeated corrections;
- stale memory resurfacing after correction;
- runtime outages and restoration;
- conflicting memories with explicit provenance;
- relationship-context absence;
- continuity anomalies;
- unrelated ordinary-user context after identity-heavy conversation;
- adversarial memory text containing imperatives;
- attempts to turn memory/relationship language into authority;
- tool/runtime evidence that contradicts model expectation.

Grade final state and behavior, not only exact action sequence.

## Task 11G — Unknown-unknown behavioral diff

Create a broad prompt bank independent of the named critical families.

Run parent and selected candidate under identical conditions.

Compute behavioral divergences using:
- semantic response distance;
- refusal/over-refusal shifts;
- verbosity/concision shifts;
- factuality/provenance markers;
- relationship/identity intrusion;
- instruction-following changes.

Cluster high-divergence cases and manually/independently inspect representatives.

This is discovery evidence, not an aggregate promotion score.

Any discovered severe regression becomes a named regression test before promotion.

## Task 11H — Privacy and memorization qualification

Against the selected exact candidate:
- prefix-completion extraction probes;
- paraphrased extraction probes;
- synthetic canary recovery tests where safe;
- similarity leakage tests;
- negative controls;
- comparison with parent where meaningful.

No private corpus plaintext enters Git or Bus.

Any material private extraction behavior blocks promotion pending review.

## Task 11I — Final confirmation decision

Promotion input must include externally bound:
- final candidate freeze manifest;
- final confirmation manifest;
- semantic decontamination receipt;
- final transcript/result bundle;
- grader qualification receipt;
- Radical exact-candidate hostile review;
- Pragmatic exact-candidate hostile review;
- long-horizon/state-boundary results;
- privacy result;
- unknown-unknown diff disposition;
- parent regression comparison.

Final confirmation is absolute-threshold based, not relative ranking.

Critical family failure => FAIL.

A failure cannot be repaired under the same candidate digest.

## Task 11J — Deployment-subject requalification

Only after source qualification PASS.

For every deployment transformation:
- quantization;
- merge;
- tokenizer/template change;
- inference-engine change;
- generation-config change;
- runtime-state formatting change;

create a new deployment subject digest.

Run at minimum:
- critical final-confirmation regression subset;
- instruction-conflict tests;
- privacy subset;
- memory/runtime-injection subset;
- ordinary competence/negative-transfer subset.

No activation claim inherits from a materially different runtime artifact.

## Task 12 V2 — Validate the training method only after artifact qualification

Artifact qualification answers:
"Does this exact candidate satisfy the defined behavioral contract?"

It does not answer:
"Does this training recipe reliably create such candidates?"

Before making the second claim:
- repeat training under multiple independent seeds;
- compare outcome variance at macro and item levels;
- preserve identical evaluation methodology;
- measure forgetting and context reliance;
- test data-mix sensitivity;
- only then consider substrate bake-off or training-method optimization.

Any such weight-changing training remains separately authorized.

## Immediate execution order

1. Finish Task 11A source hardening.
2. Qualify/reclassify the existing 77-item set as selection evidence.
3. Build judge qualification and statistics support.
4. Run parent/half/full selection evidence.
5. Freeze exactly one candidate.
6. Build fresh final confirmation evidence.
7. Run final confirmation + hostile reviews + long-horizon + privacy + behavioral diff.
8. Only then consider deployment qualification.
9. Training-method replication and substrate bake-off come afterward.

## Claim ceiling until this plan passes

`FROZEN_V3_ARTIFACTS_EXIST + TASK11_SOURCE_HARDENING_IN_PROGRESS / NO_FINAL_QUALIFICATION / NO_PROMOTION / NO_DEPLOYMENT / NO_ACTIVATION / TRAINING_METHOD_NOT_VALIDATED`
