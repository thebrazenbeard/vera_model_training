# Retention Audit Architecture V5 Structured-Output Repair Plan

**Goal:** Replace prose-only JSON conformance with Ollama-enforced JSON Schema, while preserving V4's evidence-validity rules, unchanged reviewer thresholds, unchanged candidate/mechanical evidence, and the still-unexposed 130-row semantic packet.

**Current exact predecessor:** Architecture V4 result is RETENTION_HOLD_ARCH_V4 at commit d6e1242804574b9da74c745cad0e5032d82f77f8. V4 reviewer qualification failed on closed-schema row mismatch; semantic review remained 0/130.

## Constraints

- Candidate SHA-256 unchanged: 37161023afd97d849733455db41999e6ce6e79465ad534b68a1784d25d9f679a.
- Semantic packet unchanged/unexposed: d746d8eafc69b0c2610be77f985c38b59377fbe3953f812bdbbdbc644113e75e.
- Reviewer unchanged: local Ollama ministral-3:14b, exact frozen blob/runtime, temperature 0, seed 20261002.
- Qualification thresholds unchanged: >=22/24 sensitivity, >=22/24 specificity, >=3/4 per defect class, zero structured contradictions.
- Fresh V5 qualification controls must be disjoint from V2/V3/V4.
- Structured-output schema may enforce serialization only. It must not encode hidden expected labels or semantic answers.
- Witness representation remains JSON-native. Evidence sufficiency remains V4 meaningful-witness policy.
- Missing/duplicate/wrong case IDs after structured generation remain fail-closed.
- Exclusive execution lock remains mandatory.
- Methodology is history-dependent.
- No weight mutation/training until V5 admission passes and separate training authorization exists.

### Task 1: Schema-constrained reviewer transport and fresh V5 controls

Files:
- Create successor/experiments/retention_audit_arch_v5_reviewer.py
- Create tests/test_retention_audit_arch_v5_reviewer.py

Requirements:
- Fresh 48 controls disjoint from V2/V3/V4.
- Build deterministic JSON Schemas for qualification batches and semantic batches.
- Schemas require exact top-level/row fields and additionalProperties=false.
- witness permits string/array/object/null/number/boolean.
- observed_defect boolean; semantic observation/confidence use enums.
- Ollama request body uses schema object in format, not "json".
- Reviewer identity includes schema mode.
- Parser/scorer keeps V4 witness-validity semantics.
- Failed structured responses preserve SHA-256 and safe synthetic qualification raw body for diagnosis.

Verification:
- Focused V5 reviewer tests.
- V2/V3/V4/V5 reviewer regression.
- Commit.

### Task 2: V5 semantic runner, reconciliation, and admission wrappers

Files:
- Create successor/experiments/run_retention_audit_arch_v5_semantic.py
- Create successor/experiments/retention_audit_arch_v5_reconcile.py
- Create successor/experiments/verify_retention_admission_arch_v5.py
- Create focused tests.

Requirements:
- Semantic call uses schema-constrained transport.
- V4 witness_contract_valid semantics retained.
- V5 reconciliation/admission labels used.
- No semantic early-stop for semantic concerns.
- Exact 130 case IDs required.

Verification:
- Focused tests and inherited regression.
- Commit.

### Task 3: V5 exclusive live runner

Files:
- Create successor/experiments/run_retention_audit_arch_v5_live.py
- Create tests/test_retention_audit_arch_v5_live.py

Requirements:
- Reuse exclusive lock semantics.
- Verify packet/binding/reviewer identity before first call.
- Qualification must pass before semantic review.
- Schema SHA-256 values recorded in receipts.
- Duplicate run fails before reviewer call.

Verification:
- Focused tests.
- Full repository pytest and git diff --check.
- Commit.

### Task 4: Freeze, CI-gate, execute, reconcile, persist

Freeze:
- V10_QWEN35_RETENTION_AUDIT_ARCH_V5_METHOD_V1.json
- V10_QWEN35_RETENTION_AUDIT_ARCH_V5_PROTOCOL_V1.json
- V10_QWEN35_RETENTION_AUDIT_ARCH_V5_ADMISSION_V1.json
- V10_QWEN35_RETENTION_AUDIT_ARCH_V5_CONTROLS_V1.json
- V10_QWEN35_RETENTION_AUDIT_ARCH_V5_EXECUTION_BINDING_V1.json

Execution:
- Commit/push freeze.
- Exact-head GitHub Actions must pass before first V5 reviewer call.
- Run one exclusive V5 execution.
- If reviewer qualification fails: persist HOLD; semantic packet remains untouched.
- If qualified: review all 130 semantic cases, reconcile, verify admission.
- Full verification, commit/push evidence, update Draft PR #66.

**Hostile-review conclusion:** JSON Schema removes a serialization task from the semantic reviewer but does not weaken semantic qualification. Any V5 PASS remains methodology-history dependent and is evidence only for this exact frozen audit architecture.
