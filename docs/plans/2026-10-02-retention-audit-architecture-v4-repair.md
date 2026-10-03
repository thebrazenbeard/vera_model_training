# Retention Audit Architecture V4 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair V3's witness-representation failure without weakening reviewer qualification, make semantic witness handling representation-tolerant but evidence-strict, prevent concurrent duplicate execution, and refreeze before any V4 live reviewer call.

**Architecture:** V4 keeps the exact 1,500-row candidate, mechanical receipts, contamination/exclusion evidence, reviewer model/sampler, and still-unexposed 130-row semantic packet. It introduces fresh V4 qualification controls, JSON-native witness parsing with separate evidence-validity scoring, V4 semantic parsing/reconciliation, and an exclusive execution lock. V2/V3 remain consumed historical evidence and are never rewritten.

**Tech Stack:** Python 3.14, pytest, local Ollama HTTP API, Git/GitHub Actions.

## Global Constraints

- Candidate SHA-256 remains `37161023afd97d849733455db41999e6ce6e79465ad534b68a1784d25d9f679a`.
- Semantic packet SHA-256 remains `d746d8eafc69b0c2610be77f985c38b59377fbe3953f812bdbbdbc644113e75e`; V2 and V3 each reviewed 0/130 semantic rows.
- Reviewer remains local Ollama `ministral-3:14b`, blob `bfb40fc6bb9c3b2ed529b480e04f824c005ea8f86733d4ebbf0c204de484891e`, runtime `ollama version is 0.34.2`, temperature 0, seed 20261002, JSON format, non-streaming.
- V4 qualification controls must be fresh and case-ID-disjoint from V2 and V3.
- Qualification thresholds do not change: >=22/24 sensitivity, >=22/24 specificity, >=3/4 detection per defect class, zero structured contradictions.
- A claimed defect requires meaningful witness content. Representation may be JSON string, array, or object; null, empty/whitespace, `NONE`, numbers, booleans, empty arrays, and empty objects are scoreable contradictions, not transport failures.
- A no-defect response still requires the exact `NONE` sentinel. Any other witness representation is a scoreable contradiction.
- Retries are only for malformed JSON or unscorable closed-schema failures such as missing/extra case IDs, missing required fields, invalid boolean type, or invalid confidence enum. Witness representation alone never consumes a retry.
- Semantic reviewer output never directly determines bank admission. Invalid semantic witness content is reviewer defect evidence, not bank defect and not transport failure.
- Only one V4 live execution may hold the execution lock. A second invocation must fail before reviewer qualification.
- V4 remains methodology-history dependent because it is designed after observing V2 and V3 failures.
- Training/model-weight mutation remains unauthorized until exact V4 retention admission returns PASS and separate training authority exists.

---

### Task 1: JSON-native qualification witnesses with fresh V4 controls

**Files:**
- Create: `successor/experiments/retention_audit_arch_v4_reviewer.py`
- Create: `tests/test_retention_audit_arch_v4_reviewer.py`

**Interfaces:**
- Consumes: low-level `ollama_text` transport from Architecture V2 only.
- Produces: `build_reviewer_qualification_controls_v4()`, `qualification_batch_prompt_v4()`, `parse_qualification_batch_response_v4()`, `meaningful_witness_v4()`, `qualify_reviewer_v4()`, `run_batched_reviewer_qualification_v4()`.

- [ ] **Step 1: Add the focused failing tests**
  - 48 controls; six defect classes; 4 defect + 4 good controls per class; IDs disjoint from V2 and V3.
  - Parser accepts witness values that are strings, arrays, objects, null, numbers, and booleans without transport failure.
  - `meaningful_witness_v4` returns true only for nonempty semantic strings/arrays/objects and false for null, `NONE`, empty structures, numbers, and booleans.
  - Defect + nonempty object/list witness is scoreable and not contradictory.
  - Defect + empty/scalar witness is a structured contradiction.
  - No-defect + exact `NONE` is valid; any other witness is a contradiction.
  - Batched qualification never retries a scoreable witness contradiction.

- [ ] **Step 2: Verify the relevant failure**
  Run: `python -m pytest -q tests/test_retention_audit_arch_v4_reviewer.py`
  Expected: import/module failure or missing public V4 interfaces.

- [ ] **Step 3: Implement the minimum behavior**
  - Generate fresh `arch-v4-reviewer-...` controls with new prompt content/tokens.
  - Keep closed row keys and exact case IDs.
  - Preserve the raw JSON witness value in receipts and add a canonical `witness_text` representation for inspection.
  - Score evidence validity separately from JSON type.

- [ ] **Step 4: Verify the focused pass**
  Run the same focused pytest command; expected all V4 reviewer tests pass.

- [ ] **Step 5: Run affected integration checks**
  Run V2/V3/V4 reviewer tests together; expected all pass.

- [ ] **Step 6: Commit**
  Commit only V4 reviewer implementation/tests.

### Task 2: Representation-tolerant semantic audit and typed reconciliation

**Files:**
- Create: `successor/experiments/run_retention_audit_arch_v4_semantic.py`
- Create: `successor/experiments/retention_audit_arch_v4_reconcile.py`
- Create: `successor/experiments/verify_retention_admission_arch_v4.py`
- Create: `tests/test_retention_audit_arch_v4_semantic.py`
- Create: `tests/test_retention_audit_arch_v4_reconcile.py`
- Create: `tests/test_retention_admission_arch_v4.py`

**Interfaces:**
- Produces `parse_witness_response_v4()`, `run_semantic_audit_v4()`, `reconcile_audit_v4()`, and `verify_admission_v4()`.

- [ ] **Step 1: Add focused failing tests**
  - Semantic ambiguity/counterexample with nonempty object/list witness parses and is reviewable.
  - Required-witness observation with null/empty/scalar witness is preserved with `witness_contract_valid=false`; no retry is consumed.
  - Malformed JSON, wrong case set, or invalid observation/confidence remains transport/schema failure and may retry.
  - Reconciliation maps invalid semantic witness contract to `REVIEWER_DEFECT`, never `BANK_DEFECT`.
  - Admission requires exact 1,500 mechanical validity, qualified V4 reviewer, exact 130 semantic IDs, complete semantic audit, zero blocking defect classes, exact bindings.

- [ ] **Step 2: Verify red**
  Run focused V4 semantic/reconciliation/admission tests; expected missing interfaces.

- [ ] **Step 3: Implement minimum behavior**
  - Reuse V2 blind review prompt generation.
  - Preserve raw JSON witness plus canonical text and validity flag.
  - Keep semantic concerns non-early-stop.
  - Produce V4 status labels `RETENTION_ADMITTED_ARCH_V4` / `RETENTION_HOLD_ARCH_V4`.

- [ ] **Step 4: Verify focused green**
  All focused V4 tests pass.

- [ ] **Step 5: Regression**
  Run V2/V3/V4 reconciliation and admission tests together.

- [ ] **Step 6: Commit**
  Commit only Task 2 files.

### Task 3: Exclusive V4 live execution orchestration

**Files:**
- Create: `successor/experiments/run_retention_audit_arch_v4_live.py`
- Create: `tests/test_retention_audit_arch_v4_live.py`

**Interfaces:**
- Produces `exclusive_execution_lock(path)` and `run_live_review_v4(...)`.

- [ ] **Step 1: Add failing tests**
  - First lock acquisition succeeds; concurrent second acquisition fails before reviewer call.
  - Lock is released in `finally` after success or exception.
  - Runner verifies packet hash/case IDs and exact reviewer identity before qualification.
  - Reviewer qualification must complete and pass before any semantic call.
  - Qualification transport failures persist raw-response SHA-256 and parse error; scoreable witness contradictions do not retry.
  - Semantic execution uses 5-case batches and processes all 130 rows unless a transport/runtime/binding failure occurs.

- [ ] **Step 2: Verify red**
  Focused live tests fail for missing module/interfaces.

- [ ] **Step 3: Implement minimum behavior**
  - Atomic create-exclusive lock file containing PID and binding identity.
  - Fail closed on existing lock; do not auto-delete stale locks.
  - Canonical LF JSON output.
  - Preserve qualification and semantic receipts.

- [ ] **Step 4: Verify focused green**
  V4 live tests pass.

- [ ] **Step 5: Full pre-freeze verification**
  Run `python -m pytest -q` and `git diff --check`; expected full green.

- [ ] **Step 6: Commit**
  Commit Task 3 files.

### Task 4: Freeze V4, exact-head gate, execute, reconcile, persist

**Files:**
- Create: `successor/experiments/V10_QWEN35_RETENTION_AUDIT_ARCH_V4_METHOD_V1.json`
- Create: `successor/experiments/V10_QWEN35_RETENTION_AUDIT_ARCH_V4_PROTOCOL_V1.json`
- Create: `successor/experiments/V10_QWEN35_RETENTION_AUDIT_ARCH_V4_ADMISSION_V1.json`
- Create: `successor/experiments/V10_QWEN35_RETENTION_AUDIT_ARCH_V4_EXECUTION_BINDING_V1.json`
- Persist after exact execution: `successor/evaluation/v10_qwen35/retention_arch_v4.*`

**Interfaces:**
- Frozen binding covers V2/V3 historical result manifests, V3 execution incident, candidate/mechanical evidence, exact semantic packet, V4 code/tests, reviewer identity, witness policy, execution lock contract, reconciliation, and admission verifier.

- [ ] **Step 1: Freeze exact subjects before first V4 live call**
  Record methodology history dependence, unchanged bank/packet/model/sampler, fresh qualification controls, JSON-native witness policy, and zero prior semantic packet exposure.

- [ ] **Step 2: Verify frozen bytes**
  Execution binding verifier must hash-match every bound artifact and live reviewer identity must equal frozen identity.

- [ ] **Step 3: Commit/push freeze and run exact-head GitHub Actions**
  No V4 reviewer call before exact-head CI success.

- [ ] **Step 4: Execute V4 qualification under exclusive lock**
  If unqualified, persist HOLD and do not review semantic packet. If qualified, execute all 130 semantic rows.

- [ ] **Step 5: Reconcile and verify admission**
  Run V4 reconciliation/admission verifier against current exact receipts.

- [ ] **Step 6: Full verification and persistence**
  Run full pytest, `git diff --check`, concurrency-check remote, commit/push V4 evidence, and update Draft PR #66 with exact state.

## Unresolved externally observable decisions

None. V4 keeps all existing admission thresholds, model identity, candidate/packet bytes, and training boundary unchanged; the only new externally observable execution behavior is fail-closed exclusive locking for duplicate V4 runs.
