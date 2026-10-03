docs/plans/2026-10-03-retention-candidate-v3-architecture-v7-identity.md
Task 1: complete
Task 2: complete
Task 3: complete
Task 4: in_progress

RESTORE COMMAND:
VERA_MODEL_TRAINING::RESTORE_V7_LIVE_AND_TRAINING_FRONTIER_20261003_V2

Continuation:
state/continuation/V10_QWEN35_V7_LIVE_AND_TRAINING_FRONTIER_20261003_V2.md

Training critical path:
docs/plans/2026-10-03-v10-qwen35-training-critical-path.md

Candidate V3:
- SHA-256: 6f47fe7da958abaf02311ae8a740b71d1bc0e9adbac88ce5c2da14139c3792f6
- verification: CANDIDATE_V3_MUTATION_AND_FRESHNESS_ADEQUATE
- 1500 rows; 250 coding rows
- 12 consumed coding rows replaced with never-consumed deterministic variants
- zero reference failures / zero mutant survivors / zero fresh deficits

V7 pre-review evidence:
- validator qualification: VALIDATORS_QUALIFIED
- mechanical validation: 1500/1500 MECHANICAL_VALID
- semantic screen: PASS; 0 failures; max cosine 0.6243317723274231 at frozen 0.9 threshold
- fresh semantic packet: 130 rows; 26 families x5; excludes all 520 predecessor IDs; zero overlap
- packet SHA-256: 4de3ae3f5757f76417f8561f4c415b4be1daedf3ca4c42cd202b2cb92e1cd20f

V7 semantic-audit implementation:
- fresh reviewer controls disjoint from V6
- reviewer false positives nonblocking only after deterministic contradiction
- BANK_DEFECT / UNRESOLVED / AUDIT_METHOD_DEFECT / TRANSPORT_DEFECT / BINDING_DEFECT remain blocking
- live runner requires exact packet binding and excluded_case_count=520
- full repository verification on exact frozen bytes: 488 passed
- freeze binding verification: 38/38 artifacts
- qualification schemas: 12/12 regenerate exactly
- semantic schemas: 26/26 regenerate exactly
- reviewer identity exact-match
- frozen head: 2c83b1f171891f2da1ed19680767db9d1ea78308
- V7 execution binding SHA-256: 069d6f87fe09d292114dc6852c23ec07ecfdbdc13aca8c5c602e865ecf76033d
- live execution began 2026-10-03 12:04 local under D:\VERA\.scratch\retention-arch-v7.execution.lock; do not duplicate

Objective training boundary:
- Candidate V3 is retention/evaluation evidence, NOT SFT training data.
- actual SFT subject is the 50,000-train / 2,500-validation corpus bound by V10_QWEN35_EXPERIMENT_CONTRACT_V2.
- PR #69 contains the fail-closed single-run QLoRA trainer.
- PR #68 final-bank custody/sealing remains incomplete.
- exact V10_QWEN35_TRAINING_AUTHORITY_V1.json does not exist.
- model-weight mutation remains blocked pending exact authority.

Current critical path:
V7 retention result -> final-bank custody -> full 13,500 bank freeze/screen/admission -> sealed commitment -> exact training authority -> read-only READY preflight -> one QLoRA run -> diagnostics -> final one-shot evaluation.
