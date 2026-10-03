docs/plans/2026-10-03-retention-candidate-v3-architecture-v7-identity.md
Task 1: complete
Task 2: complete
Task 3: complete
Task 4: in_progress

RESTORE COMMAND:
VERA_MODEL_TRAINING::RESTORE_V7_TRAINING_FRONTIER_20261003_V1

Continuation:
state/continuation/V10_QWEN35_V7_TRAINING_FRONTIER_20261003_V1.md

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
- V6 evidence hierarchy/authority separation retained
- reviewer false positives remain nonblocking only after deterministic contradiction
- BANK_DEFECT / UNRESOLVED / AUDIT_METHOD_DEFECT / TRANSPORT_DEFECT / BINDING_DEFECT remain blocking
- live runner requires exact packet binding and excluded_case_count=520
- V6->V7 focused regression: 26/26 passed
- full repository verification: 488 passed
- git diff --check pending at commit checkpoint

V7 local identity lane:
- binding SHA-256: 5d638d8232dbae27283a6cefe214c9f00d5ccf3ddd6a27236f0fed3d53af6a17
- live KoboldCpp activation/identity run remains unauthorized

Objective training boundary:
- Candidate V3 is retention/evaluation evidence, NOT SFT training data.
- PR #69 contains the fail-closed single-run QLoRA trainer.
- actual SFT uses the experiment contract's exact train/validation subject.
- PR #68 final-bank custody/sealing remains incomplete.
- exact V10_QWEN35_TRAINING_AUTHORITY_V1.json does not exist.
- model-weight mutation remains blocked.
