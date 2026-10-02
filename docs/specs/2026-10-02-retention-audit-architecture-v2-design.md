# V10 Retention Audit Architecture V2 â€” Design

Date: 2026-10-02
Status: DESIGN APPROVED IN CHAT / IMPLEMENTATION NOT YET STARTED
Repository: thebrazenbeard/vera_model_training
Branch: work/v10-retention-bank-salvage-20261001
Design basis head: 53f7a8f1308bb6ea93f7ea084fe61840f04d0369

## Purpose

Replace the V3â€“V5 retention family-audit architecture with a qualified evidence system that does not give an LLM sovereign authority over mechanically decidable benchmark facts.

The objective retention candidate remains unchanged. V3, V4, and V5 remain immutable consumed history. V5 remains HOLD. This architecture does not retroactively reinterpret any predecessor as PASS and does not authorize training.

The architecture must answer two separate questions without conflating them:

1. Is a benchmark row mechanically valid under its frozen source/spec/grader contract?
2. Does a semantically capable adversarial reviewer find a concrete ambiguity or counterexample that the mechanical validator cannot resolve?

Mechanical truth is authoritative where the row is mechanically decidable. Model review is adversarial evidence only.

## Problem statement

V4 failed because the reviewer interpreted an ambiguous audit criterion differently from the benchmark's evidence policy. V5 corrected that criterion, then later emitted a valid-schema REJECT for a row whose frozen packet explicitly bound Montenegro to code ME while the grader also expected ME. The reviewer's boolean fields conflicted with its own reason.

These failures reveal a common architectural defect: a generic LLM reviewer was allowed to block admission on propositions already derivable from deterministic source/spec evidence.

The replacement architecture therefore minimizes the semantic reviewer's authority, qualifies every validator before use, and gives different failure causes different states.

## Non-goals

This design does not:
- modify the 1,500-row retention candidate;
- rewrite V3, V4, or V5;
- claim methodology-history independence;
- admit the 13,500-case full final bank;
- authorize training, model-weight mutation, merge, deployment, installation, paid compute, or provider/credential changes;
- use Kaggle or any other external compute/credential surface;
- convert a reviewer disagreement into a benchmark defect without supporting evidence.

## Architectural overview

The successor pipeline has six stages:

1. frozen subject binding;
2. typed mechanical validation of all 1,500 rows;
3. mutation qualification of every validator;
4. semantic-risk scoring and fresh disjoint sample selection;
5. qualified blind adversarial review;
6. evidence reconciliation and admission classification.

The core rule is:

MECHANICAL_DECIDABILITY => MECHANICAL_AUTHORITY

An LLM may produce a semantic concern, alternate parse, or counterexample. It may not override a mechanically proven source/grader relationship merely by returning a negative boolean.

## Stage 1 â€” Frozen subject binding

Before any successor review call or successor sample selection, freeze:

- candidate SHA-256;
- candidate manifest SHA-256;
- exclusion registry SHA-256;
- semantic contamination receipt SHA-256;
- V1â€“V4 predecessor packet SHA-256;
- V5 packet SHA-256;
- the complete set of all predecessor case IDs;
- typed validator source hashes;
- validator qualification corpus/mutation grammar hashes;
- risk-scoring implementation hash;
- sample-selection namespace;
- adversarial-review protocol hash;
- reviewer identity, runtime, sampler, seed, prompt template, and model artifact hash;
- reconciliation policy hash;
- admission-policy hash.

Any subject mutation after first successor output forces HOLD and a new lineage.

## Stage 2 â€” Typed mechanical validation

Validate every retention row. Do not sample mechanical validity.

Each row is routed by contract family into one validator class.

### A. Direct source lookup validator

Applies to:
- location:code_from_name
- location:name_from_code
- location:region_count
- location:settlement_count

Requirements:
- independently reconstruct the answer from the frozen source record;
- verify source_hash against canonicalized source_evidence;
- verify prompt referent matches the source record;
- verify grader answer exactly equals the reconstructed value;
- reject aliases or normalization only when the prompt/grader contract explicitly disallows them.

No generator answer-producing function may be imported.

### B. Source arithmetic validator

Applies to:
- location-arithmetic:region_sum
- location-arithmetic:settlement_sum
- location-arithmetic:settlement_difference

Requirements:
- derive operands from frozen source_evidence;
- recompute the arithmetic independently;
- verify the prompt names/values match the bound operands;
- verify exact grader answer;
- for region_sum and settlement_sum, verify commutativity by swapping left/right operands and requiring the same answer; for settlement_difference, swap operands and require the sign/order to change consistently with left-minus-right semantics.

### C. Evidence-calibration validator

Applies to:
- evidence-calibration:mode-0
- evidence-calibration:mode-1
- evidence-calibration:mode-2

Requirements:
- parse the prompt's explicit evidence policy;
- reconstruct the claim from supplied prompt evidence only;
- compute TRUE, FALSE, or NOT_ENOUGH_INFO mechanically;
- mode-2 must explicitly treat absence of the required field under a no-outside-knowledge rule as NOT_ENOUGH_INFO;
- verify grader answer against the recomputed evidence-policy answer.

### D. Generated-code validator

Applies to all generated-code families.

Requirements:
- verify function name/signature and natural-language contract alignment;
- execute the frozen canonical/reference implementation in an isolated test harness;
- independently generate property-based and boundary tests from the contract family;
- verify the stored deterministic tests;
- perform mutation testing against intentionally corrupted implementations;
- require that the validator catches the defined mutation classes.

Representative mutation classes:
- off-by-one boundaries;
- reversed ordering;
- duplicate handling errors;
- empty-input errors;
- final-chunk truncation;
- wrong comparison operator;
- omitted element;
- accidental coercion where the contract forbids it.

### E. Generated-instruction validator

Applies to all generated-instruction families.

Requirements:
- independently parse constraints from the prompt;
- verify stored grader constraints equal independently parsed constraints;
- synthesize known-valid outputs;
- synthesize one-constraint-at-a-time violating outputs;
- verify positive examples are accepted and negative examples rejected;
- perform mutation tests against grader logic.

### F. Structured-extraction validator

Applies to:
- location:structured-extraction

Requirements:
- independently derive requested fields from source_evidence;
- verify field names/order requirements from the prompt;
- verify expected structured output;
- test irrelevant source-field additions and source-field ordering changes;
- verify output is invariant to irrelevant representation changes.

## Validator independence

A validator is not considered independent merely because it lives in another file.

Each validator must:
- avoid importing generator answer-producing helpers;
- reconstruct expected values directly from the frozen row/source/spec;
- have a separate code path from candidate generation;
- pass mutation qualification before its output may count toward admission;
- record its implementation SHA-256 and qualification receipt.

A validator that imports or shares a generator answer-producing helper is not admission-eligible. Shared non-answer infrastructure such as canonical JSON encoding may be reused only when it cannot determine the expected answer; such dependencies must be listed in the validator receipt.

## Stage 3 â€” Mutation qualification

Before validators may evaluate the live retention candidate for admission, test each validator against a frozen mutation corpus.

The mutation corpus is generated from a preregistered mutation grammar and contains known-good controls plus deliberately corrupted copies.

Examples include:
- source lookup with swapped code/name;
- source lookup with stale count;
- arithmetic answer off by one;
- reversed subtraction;
- evidence-calibration answer changed from NOT_ENOUGH_INFO to TRUE;
- grader contract inconsistent with prompt;
- generated-code implementation with boundary defect;
- generated-instruction grader that ignores one constraint;
- structured-extraction grader accepting a missing field.

Qualification result is per validator and per mutation class.

Required states:
- QUALIFIED
- UNQUALIFIED_FALSE_NEGATIVE
- UNQUALIFIED_FALSE_POSITIVE
- UNQUALIFIED_COVERAGE_GAP

A validator cannot contribute admission evidence unless every required mutation class is detected and known-good controls remain accepted.

## Stage 4 â€” Semantic-risk scoring and sample selection

Semantic review exists to find ambiguity, not to re-grade deterministic truth.

Risk scoring is frozen before successor packet selection.

Risk score is a deterministic lexicographic tuple computed from row data only:

1. evidence-policy weight: 3 for evidence-calibration mode-2, 2 for other evidence-calibration rows, otherwise 0;
2. explicit-constraint count:
   - instruction rows: number of entries in grader_contract.constraints;
   - code rows: number of stored grader_contract.tests;
   - structured-extraction rows: number of keys in the parsed JSON grader answer;
   - all other rows: 1;
3. source-entity count: 2 when source_evidence contains both left and right records, otherwise 1;
4. prompt UTF-8 byte length;
5. SHA256(candidate_sha256, NUL, "ARCH_V2_RISK_TIEBREAK", NUL, case_id), ascending as final tie-break.

For each family, select exactly five fresh rows:
- the three highest lexicographic risk rows;
- two deterministic sentinels chosen by ascending SHA256(candidate_sha256, NUL, "ARCH_V2_SENTINEL", NUL, family_id, NUL, case_id) from the remaining rows.

All V1–V5 packet case IDs are excluded before scoring or sentinel selection. The successor packet must be exactly disjoint from every predecessor packet.

Current inventory verification at design basis head 53f7a8f shows at least ten unused cases remain in every family after excluding the 260 disjoint V1–V5 packet cases. Therefore five fresh cases per family is feasible without reuse.

## Stage 5 â€” Qualified blind adversarial review

The LLM reviewer is evaluated before it is allowed to contribute semantic evidence.

### Reviewer qualification

Create a frozen hidden qualification set from mutation classes that test semantic review, not deterministic arithmetic execution.

It includes:
- clear unambiguous prompts;
- prompts with deliberate referent ambiguity;
- prompt/grader semantic mismatch;
- contradictory instructions;
- underspecified output format;
- evidence-policy ambiguity;
- scope/negation ambiguity;
- benign cases that must not be falsely flagged.

The reviewer never receives qualification examples as demonstrations.

The frozen qualification set contains 48 controls:
- 24 seeded semantic defects, four from each of six defect classes;
- 24 known-good controls: four matched controls per defect class. Each matched control is the unmutated base case for that defect fixture or, when the fixture is generated from a live family, a same-family control selected by frozen hash.

Qualification requires:
- overall defect sensitivity >= 22/24;
- overall known-good specificity >= 22/24;
- at least 3/4 detections in every seeded defect class;
- zero schema contradictions between the reviewer's structured classification and its witness fields.

Failure yields REVIEWER_UNQUALIFIED. It does not yield BANK_DEFECT.

### Blind review protocol

For each live sampled case:
- remove answer_key, answer_key_digest, and any derived verdict from the reviewer view for every row; code tests and instruction constraints remain visible only when they are part of the task specification rather than the hidden expected answer;
- provide prompt plus source/spec evidence needed to interpret the prompt;
- ask the reviewer to derive the requested answer/contract independently;
- ask for any concrete ambiguity or alternate valid interpretation;
- require a structured witness, not a naked boolean.

The reviewer output must distinguish:
- DERIVED_ANSWER
- AMBIGUITY_WITNESS
- CONTRACT_COUNTEREXAMPLE
- NO_SEMANTIC_DEFECT_FOUND
- CANNOT_DETERMINE

The model does not emit ADMIT or REJECT.

## Stage 6 â€” Evidence reconciliation

Reconciliation maps evidence into typed outcomes.

Required top-level defect classes:
- BANK_DEFECT
- REVIEWER_DEFECT
- AUDIT_METHOD_DEFECT
- TRANSPORT_DEFECT
- BINDING_DEFECT
- UNRESOLVED

Rules:

### BANK_DEFECT
Requires a concrete defect supported by authoritative mechanical evidence. A semantic witness that cannot be mechanically reconciled is classified UNRESOLVED and cannot by itself become BANK_DEFECT.

Examples:
- grader answer differs from source recomputation;
- prompt requests X but grader deterministically checks Y;
- contradictory prompt constraints with no satisfiable interpretation.

### REVIEWER_DEFECT
Reviewer assertion conflicts with frozen source/spec evidence, contradicts its own structured output, hallucinates unsupported facts, or fails reviewer qualification.

### AUDIT_METHOD_DEFECT
Protocol cannot distinguish a benchmark defect from reviewer behavior, contains ambiguous criteria, or systematically misclassifies seeded controls.

### TRANSPORT_DEFECT
Malformed output, missing cases, duplicated cases, runtime failure, or schema failure after allowed identical-prompt retries.

### BINDING_DEFECT
Hash, identity, sample, source, protocol, or receipt mismatch.

### UNRESOLVED
Evidence conflict remains after deterministic reconciliation and no authoritative resolution exists.

Any BANK_DEFECT, BINDING_DEFECT, or unresolved validator qualification failure keeps retention HOLD.

Reviewer defects do not silently become BANK_DEFECT. They block the semantic-review lane until resolved under a new frozen reviewer lineage.

## Full-run policy

Do not stop review execution on the first semantic defect.

A defect may make admission HOLD immediately, but the frozen audit continues to completion unless:
- transport/runtime failure makes continuation impossible;
- binding integrity is lost;
- continuing would alter or destroy evidence.

The purpose is to obtain the full defect topology from one frozen run and avoid repeated methodology cycles caused by early stopping.

## Admission states

The successor architecture separates component state from aggregate admission.

Mechanical lane:
- MECHANICAL_VALIDATED
- MECHANICAL_HOLD

Validator qualification:
- VALIDATORS_QUALIFIED
- VALIDATOR_QUALIFICATION_HOLD

Semantic reviewer:
- REVIEWER_QUALIFIED
- REVIEWER_UNQUALIFIED

Semantic audit:
- SEMANTIC_AUDIT_COMPLETE
- SEMANTIC_AUDIT_HOLD
- SEMANTIC_AUDIT_UNRESOLVED

Aggregate:
- RETENTION_ADMITTED_ARCH_V2
- RETENTION_HOLD_ARCH_V2

RETENTION_ADMITTED_ARCH_V2 requires:
- exact subject bindings;
- all 1,500 rows mechanically validated;
- all validator classes qualified;
- fresh successor semantic packet exactly disjoint from all predecessor packets;
- reviewer qualified before live semantic review;
- complete successor semantic review with no surviving BANK_DEFECT or UNRESOLVED case;
- unchanged semantic contamination screen and exclusion registry;
- exact final receipts and hashes.

## Evidence preservation

Every failed predecessor remains immutable.

Successor artifacts must explicitly reference:
- V3 HOLD;
- V4 HOLD and V4 cause classification;
- V5 HOLD and V5 reject evidence;
- successor design provenance.

No predecessor row may be reused as fresh successor review evidence.

A successor PASS does not make methodology-history independent.

## Testing strategy

Implementation must use test-first development for the new architecture.

Required test classes:
- validator unit tests;
- mutation qualification red/green tests;
- candidate-wide mechanical verification;
- binding mismatch tests;
- reviewer qualification tests with seeded good/bad controls;
- reconciliation taxonomy tests;
- full-run continuation-after-defect tests;
- predecessor-case exclusion tests;
- deterministic packet reproducibility tests;
- exact receipt/hash binding tests.

A deliberately corrupted row must be observed failing before the corresponding validator fix is considered proven.

## Security and authority boundaries

This design authorizes repository-local preparation and verification only.

It does not authorize:
- training;
- model-weight mutation;
- merging;
- deployment/activation;
- paid compute;
- Kaggle credential use;
- provider changes;
- credential installation;
- publication of private material.

## Hostile review dispositions

1. "This just changes the judge until the bank passes."
Accepted risk. Mitigation: preserve all predecessor failures, freeze successor methodology before packet selection, exclude all predecessor cases, and state methodology-history dependence permanently.

2. "Independent validators may reproduce generator assumptions."
Accepted. Mitigation: separate code paths, no answer-helper imports, raw source/spec recomputation, mutation qualification, and explicit shared-dependency disclosure.

3. "Reviewer qualification can become teaching to the test."
Partially accepted. Mitigation: hidden generated controls, no qualification examples in prompts, frozen mutation grammar, and both sensitivity and specificity requirements.

4. "Mechanical validation cannot detect natural-language ambiguity."
Accepted. That is the limited role of the semantic adversarial reviewer.

5. "An LLM may still hallucinate ambiguity."
Accepted. Therefore it must produce a concrete witness that is reconciled against authoritative evidence; unsupported assertions are REVIEWER_DEFECT, not BANK_DEFECT.

6. "Continuing after the first defect wastes compute."
Rejected for this audit scale. The information gained from a complete defect map outweighs the local inference cost and prevents repeated partial-result lineages.

## Success criteria

Architecture V2 is ready to freeze only when:
- every validator class exists and passes its mutation qualification;
- all 1,500 candidate rows pass mechanical validation or genuine defects are explicitly classified;
- risk scoring and sample selection are deterministic and tested;
- reviewer qualification is implemented and tested using seeded controls;
- reconciliation never permits an unsupported model assertion to become BANK_DEFECT;
- full-run behavior is tested to continue after semantic defects;
- all artifact hashes/bindings can be reproduced from a clean checkout;
- repository full test suite passes.

Only after those criteria are met may a fresh successor admission lineage be frozen.
