# Retention Audit Architecture V2 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and qualify a deterministic-first retention audit that mechanically validates all 1,500 retention rows, mutation-tests its validators, samples a fresh risk-weighted disjoint semantic packet, qualifies a blind adversarial reviewer, and produces typed reconciliation/admission evidence without allowing unsupported LLM judgments to become benchmark defects.

**Architecture:** Architecture V2 is additive beside frozen V3–V5 code. Six typed validators independently recompute source/spec/grader relationships; mutation qualification proves those validators detect seeded defects; a deterministic risk sampler excludes all predecessor cases; the LLM reviewer emits witnesses rather than verdicts; reconciliation separates bank, reviewer, method, transport, binding, and unresolved failures.

**Tech Stack:** Python, pytest, stdlib hashlib/json/ast/re, existing local Ollama transport only after reviewer qualification.

## Global Constraints

- V3, V4, and V5 are immutable consumed history.
- Candidate SHA-256 remains `37161023afd97d849733455db41999e6ce6e79465ad534b68a1784d25d9f679a`.
- No V1–V5 packet case may be reused as fresh semantic evidence.
- LLM output cannot directly produce `BANK_DEFECT`.
- Mechanical validation covers all 1,500 rows.
- Validators may not import generator answer-producing helpers.
- Each validator must pass seeded good/bad mutation qualification.
- Semantic execution continues after semantic defects unless transport/runtime/binding integrity prevents continuation.
- No training, model-weight mutation, merge, deployment, paid compute, Kaggle credential use, provider changes, or credential installation occurs in implementation.
- Methodology-history dependence on V3–V5 remains explicit.

---

### Task 1: Typed mechanical validator core

**Files:**
- Create: `successor/experiments/retention_audit_arch_v2_validators.py`
- Create: `tests/test_retention_audit_arch_v2_validators.py`

**Interfaces:**
- Consumes candidate row dictionaries.
- Produces `validator_class_for_row(row)`, `validate_row_mechanically(row)`, and `validate_candidate_mechanically(rows)`.

- [ ] **Step 1: Add failing tests**
  Cover all six classes: direct source lookup, source arithmetic, evidence calibration, generated code, generated instruction, structured extraction. Include good controls and one mechanically seeded defect per class.
- [ ] **Step 2: Verify red**
  Run `python -m pytest -q tests/test_retention_audit_arch_v2_validators.py`.
  Expected: collection/import failure because the module is absent.
- [ ] **Step 3: Implement minimum behavior**
  Independently recompute source hashes, prompt/source/grader relationships, answer keys, instruction constraints, code contract metadata, and extraction output. Do not import answer-producing functions from candidate generation or `retention_graders.py`.
- [ ] **Step 4: Verify green**
  Run the focused test file; expect all pass.
- [ ] **Step 5: Regression check**
  Run focused V5 tests plus Architecture V2 validator tests; expect all pass.
- [ ] **Step 6: Commit**
  Commit only Task 1 files with message `Build typed retention audit validators`.

### Task 2: Mutation qualification and exhaustive mechanical audit

**Files:**
- Create: `successor/experiments/retention_audit_arch_v2_qualification.py`
- Create: `successor/experiments/run_retention_audit_arch_v2_mechanical.py`
- Create: `tests/test_retention_audit_arch_v2_qualification.py`
- Create: `tests/test_retention_audit_arch_v2_mechanical_run.py`

**Interfaces:**
- Consumes Task 1 validator functions and candidate JSONL.
- Produces `build_validator_mutation_cases()`, `qualify_validators()`, `run_mechanical_audit(rows)`, and a CLI receipt.

- [ ] **Step 1: Add failing tests**
  Seed wrong lookup values, arithmetic defects, calibration answer changes, ten family-specific code behavior mutations, one ignored constraint for each instruction family, and structured extraction missing/wrong/extra fields. Known-good controls must remain valid. Require qualification states `QUALIFIED`, `UNQUALIFIED_FALSE_NEGATIVE`, `UNQUALIFIED_FALSE_POSITIVE`, `UNQUALIFIED_COVERAGE_GAP`.
- [ ] **Step 2: Verify red**
  Run both new test files; expect import failures.
- [ ] **Step 3: Implement**
  Mutation fixtures stay in memory. Code qualification uses independent oracle semantics, never `reference_coding_source`. Any unqualified validator => `VALIDATOR_QUALIFICATION_HOLD`; any genuine row defect => `MECHANICAL_HOLD`; only all-qualified + all-valid => `MECHANICAL_VALIDATED`.
- [ ] **Step 4: Verify green**
  Run focused tests; expect all pass.
- [ ] **Step 5: Execute real candidate audit**
  Run against all 1,500 rows into `D:/VERA/.scratch/retention-arch-v2/mechanical.receipt.json`. Preserve any real defect; do not repair candidate data here.
- [ ] **Step 6: Commit**
  Commit Task 2 implementation/tests.

### Task 3: Risk scoring and fresh disjoint packet

**Files:**
- Create: `successor/experiments/build_retention_audit_arch_v2_packet.py`
- Create: `tests/test_retention_audit_arch_v2_packet.py`

**Interfaces:**
- Produces `risk_tuple(row, candidate_sha256)` and `select_arch_v2_sample(rows, excluded_case_ids, candidate_sha256)`.

- [ ] **Step 1: Add failing tests**
  Verify exact lexicographic risk tuple, 3 highest-risk + 2 hash sentinels per family, deterministic ordering, exclusion before ranking, duplicate rejection, insufficient-pool failure, 130 rows/26 families/zero predecessor overlap, and byte-identical reproducibility.
- [ ] **Step 2: Verify red**
  Focused test must fail because module is absent.
- [ ] **Step 3: Implement**
  Use frozen namespaces `ARCH_V2_RISK_TIEBREAK` and `ARCH_V2_SENTINEL`. Manifest binds candidate hash, all predecessor packet hashes, excluded count, selected IDs, family counts, packet hash.
- [ ] **Step 4: Verify green**
  Focused tests pass.
- [ ] **Step 5: Build scratch packet**
  Write only to `D:/VERA/.scratch/retention-arch-v2/`; do not freeze in repo yet.
- [ ] **Step 6: Commit**
  Commit Task 3 files.

### Task 4: Reviewer qualification and blind full-run semantic executor

**Files:**
- Create: `successor/experiments/retention_audit_arch_v2_reviewer.py`
- Create: `successor/experiments/run_retention_audit_arch_v2_semantic.py`
- Create: `tests/test_retention_audit_arch_v2_reviewer.py`
- Create: `tests/test_retention_audit_arch_v2_semantic_run.py`

**Interfaces:**
- Produces 48 frozen qualification controls, reviewer qualification receipt, blind prompt generation, strict witness parsing, and complete semantic run receipt.

- [ ] **Step 1: Add failing tests**
  Six defect classes: referent ambiguity, prompt/grader semantic mismatch, contradictory instructions, underspecified output format, evidence-policy ambiguity, scope/negation ambiguity. Four defects + four matched good controls per class. Require >=22/24 sensitivity, >=22/24 specificity, >=3/4 per defect class, zero structured contradictions. Verify answer key/digest/verdict never appear in live reviewer view; allowed observations only `DERIVED_ANSWER`, `AMBIGUITY_WITNESS`, `CONTRACT_COUNTEREXAMPLE`, `NO_SEMANTIC_DEFECT_FOUND`, `CANNOT_DETERMINE`. Semantic concerns do not early-stop.
- [ ] **Step 2: Verify red**
  Focused tests fail because modules are absent.
- [ ] **Step 3: Implement**
  Reuse only low-level Ollama transport/identity. Fake injected reviewers drive tests; no live successor review yet.
- [ ] **Step 4: Verify green**
  Focused tests pass.
- [ ] **Step 5: Regression**
  V5 + Architecture V2 reviewer tests pass.
- [ ] **Step 6: Commit**
  Commit Task 4 files.

### Task 5: Typed reconciliation, admission verifier, freeze, and execution

**Files:**
- Create: `successor/experiments/retention_audit_arch_v2_reconcile.py`
- Create: `successor/experiments/verify_retention_admission_arch_v2.py`
- Create: `tests/test_retention_audit_arch_v2_reconcile.py`
- Create: `tests/test_retention_admission_arch_v2.py`
- Create only after tests pass: frozen Architecture V2 method/protocol/admission/binding JSON artifacts.
- Persist final receipts under `successor/evaluation/v10_qwen35/` only after exact execution.

**Interfaces:**
- Produces `BANK_DEFECT`, `REVIEWER_DEFECT`, `AUDIT_METHOD_DEFECT`, `TRANSPORT_DEFECT`, `BINDING_DEFECT`, `UNRESOLVED`, and aggregate `RETENTION_ADMITTED_ARCH_V2` or `RETENTION_HOLD_ARCH_V2`.

- [ ] **Step 1: Add failing tests**
  Wrong mechanical answer => BANK_DEFECT; unsupported semantic accusation => REVIEWER_DEFECT; protocol/control defect => AUDIT_METHOD_DEFECT; exhausted malformed retries => TRANSPORT_DEFECT; hash/reviewer/sample mismatch => BINDING_DEFECT; surviving nonmechanical ambiguity => UNRESOLVED. Reviewer defect must never promote to bank defect. Admission requires all 1,500 mechanical rows valid, qualified validators/reviewer, complete 130-row fresh semantic output, no BANK_DEFECT/UNRESOLVED, exact hashes, unchanged contamination/exclusion evidence.
- [ ] **Step 2: Verify red**
  Focused tests fail because modules are absent.
- [ ] **Step 3: Implement**
  Fail closed and preserve component states separately from aggregate HOLD.
- [ ] **Step 4: Full pre-freeze verification**
  Run `python -m pytest -q` and `git diff --check`; both must pass.
- [ ] **Step 5: Freeze exact subjects**
  Bind design, implementation, candidate/manifest, all predecessor packets, exclusion registry, contamination receipt, mechanical/qualification receipts, packet builder + packet, reviewer control/protocol/identity, semantic runner, reconciliation, admission policy/verifier. Commit and run exact-head GitHub Actions before first live semantic call.
- [ ] **Step 6: Execute reviewer qualification and semantic audit**
  If reviewer qualification fails, persist `REVIEWER_UNQUALIFIED` and do not review live packet. If qualified, execute all 130 rows without semantic early-stop.
- [ ] **Step 7: Final verification/persistence**
  Run full tests and exact admission verifier, concurrency-check remote, push evidence to Draft PR #66, and update PR body with exact Architecture V2 state.

Actual model training remains blocked until the exact final verifier returns `RETENTION_ADMITTED_ARCH_V2`. Crossing from qualification into model-weight training requires a separate exact training authorization because model-weight mutation is a protected effect.

## Unresolved externally observable decisions

None for Architecture V2 implementation. Actual training target/provider/compute is intentionally outside this plan until retention admission exists.
