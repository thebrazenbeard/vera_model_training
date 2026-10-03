# Retention Candidate V2 / Architecture V6 Repair Plan

**Goal:** Replace the V1 retention candidate's weak coding graders with a new 1,500-row candidate whose entire 250-row coding lane has explicit family semantics, stronger deterministic edge coverage, and per-row mutation adequacy before any new semantic admission audit.

**Predecessor evidence:** Architecture V5 is final HOLD at commit 89b3216f8efc34be0880b9e196006e44bd8e1781. Reviewer qualification passed 24/24 sensitivity, 24/24 specificity, zero contradictions; semantic audit completed 130/130. Frozen V5 reconciliation produced 5 REVIEWER_DEFECT and 16 UNRESOLVED. Independent mutation analysis then showed 44/250 coding graders accepted a known wrong implementation: 8 rotate_left, 13 chunk_list, 23 unique_preserve. Instruction lane mutation analysis found 0/250 gaps.

## Constraints

- Preserve retention_candidate_v1 and all V2-V5 evidence unchanged.
- Create retention_candidate_v2; never rewrite V1.
- Non-coding rows must remain byte-equivalent to V1 rows for the same case IDs.
- Regenerate all 250 coding rows under a new coding contract revision and generator identity.
- Keep the same 10 coding families and same 250 selected coding case IDs unless strengthened preflight proves a collision/problem.
- Strengthen prompts only where semantics are genuinely underspecified:
  - rotate_left: explicitly normalize k modulo len(values) for non-empty lists.
  - chunk_list: explicitly require positive chunk size n.
- Every coding row's reference implementation must pass every stored test.
- Every coding row must kill all frozen plausible mutants for its family.
- Mutation adequacy must be tested per row, not merely once per family.
- Re-run 1,500-row mechanical validation on candidate V2.
- V5 semantic packet is consumed and may not be reused as fresh evidence.
- New semantic packet must be disjoint from all predecessor semantic/audit packet case IDs.
- Training/model-weight mutation remains blocked until successor admission passes and exact training authority is established.

### Task 1: Candidate V2 coding contracts and mutation suite

Files:
- Create successor/experiments/build_v10_qwen35_retention_candidate_v2.py
- Create successor/experiments/retention_code_mutants_v2.py
- Create tests/test_v10_qwen35_retention_candidate_v2.py

Requirements:
- New coding revision V10_RETENTION_OBJECTIVE_CONTRACTS_20261002_V2.
- Fresh coding generation actor ID.
- Family-wide deterministic test matrices for all ten coding families.
- Multiple plausible mutants per family.
- rotate_left tests include k=0, in-range, k==len, k>len, and empty.
- chunk_list tests include n=1, exact division, remainder, empty, and positive-n contract.
- preserve prompt/grader/source-hash binding under the new coding source record.
- candidate V2 manifest records parent candidate SHA and mutation adequacy policy.

Verification:
- TDD focused tests.
- Every generated coding reference passes all row tests.
- Every frozen mutant is killed by every row in its family.
- No coding case-ID drift.
- Commit.

### Task 2: Build candidate V2 and re-run mechanical validation

Files:
- Generate successor/evaluation/v10_qwen35/retention_candidate_v2.jsonl
- Generate successor/evaluation/v10_qwen35/retention_candidate_v2.manifest.json
- Generate successor/evaluation/v10_qwen35/retention_arch_v6.validator_qualification.json
- Generate successor/evaluation/v10_qwen35/retention_arch_v6.mechanical.receipt.json
- Create tests for candidate-level invariants as needed.

Requirements:
- Exactly 1,500 rows and same category allocation.
- Non-coding rows equal V1.
- Coding rows use V2 revision.
- 1,500/1,500 MECHANICAL_VALID.
- Validator mutation qualification passes.
- Persist a code mutation adequacy receipt proving 250/250 references pass and zero frozen mutants survive.

Verification:
- Full focused tests and diff check.
- Commit.

### Task 3: Fresh contamination/semantic packet and Architecture V6 freeze

Files:
- Create fresh semantic/contamination screen for candidate V2 using existing repo-supported path.
- Create successor/evaluation/v10_qwen35/retention_arch_v6.semantic.packet.jsonl
- Create packet manifest.
- Create V6 method/protocol/admission/execution binding.
- Reuse V5 JSON-Schema reviewer transport only after rebinding candidate/packet/schema hashes.

Requirements:
- Fresh packet: 26 families x 5 rows = 130.
- Exclude every unique case ID consumed by V1-V5 predecessor packets/semantic audits.
- Freeze before first V6 reviewer call.
- Exact-head CI must pass before live review.
- Exclusive execution lock mandatory.

### Task 4: Execute V6 semantic audit, reconcile, admit or repair

Requirements:
- Reviewer must requalify on fresh controls or a frozen successor control set.
- Review all 130 fresh rows if qualified.
- Reviewer false positives do not gain sovereign veto: only mechanically/adjudicatively supported bank defects, unresolved findings, binding, transport, or audit-method defects block admission.
- Any semantic challenge against coding rows is checked against strengthened per-row mutation/property contracts.
- Persist exact V6 result before any training action.
- No weight mutation unless V6 admits and protected training effect is explicitly authorized.

**Claim ceiling:** Candidate V2/V6 is methodology-history dependent because it is designed after V5 findings. Passing V6 would establish only the frozen successor retention admission, not independent external review.
