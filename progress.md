docs/plans/2026-10-03-retention-candidate-v3-architecture-v7-identity.md
Task 1: complete
Task 2: complete
Task 3: in_progress
Task 4: pending

RESTORE COMMAND:
VERA_MODEL_TRAINING::RESTORE_V7_TRAINING_FRONTIER_20261003_V1

Continuation:
state/continuation/V10_QWEN35_V7_TRAINING_FRONTIER_20261003_V1.md

Candidate V3 SHA: 6f47fe7da958abaf02311ae8a740b71d1bc0e9adbac88ce5c2da14139c3792f6.
Candidate V3 verification: CANDIDATE_V3_MUTATION_AND_FRESHNESS_ADEQUATE.
V7 validator qualification: VALIDATORS_QUALIFIED.
V7 mechanical validation: 1500/1500 MECHANICAL_VALID.
Exactly 12 consumed coding IDs were replaced with never-consumed deterministic variants.
Every family has at least 5 IDs outside the 520-ID predecessor union.

V7 semantic-screen lane:
- binding SHA-256: 033affb5d2fb6f4e76fba03617ccee322001b2ef8ff65beb9c549148b579c018
- live screen started 2026-10-03 11:27:15 local
- observed process chain includes PIDs 2708 -> 31760 -> 12000 -> 4920 -> 6160
- no result file observed at continuation creation
- do not duplicate the live screen; verify/persist the existing result after exit

V7 local identity lane:
- KoboldCpp executable: D:\VERA\Runtime\KoboldCpp\koboldcpp.exe
- Version: 1.121
- Executable SHA-256: 90b0d74ec01e5ef72efb6d45e6f10bee649458920ec951f48d58794c366b1639
- Canonical GGUF: D:\VERA\models\gguf\model_q5_k_s.gguf
- Canonical GGUF SHA-256: 15150f534dc90ee15c82320ccc014463db7985205a7161228cff89b925fd1216
- Identity binding SHA-256: 5d638d8232dbae27283a6cefe214c9f00d5ccf3ddd6a27236f0fed3d53af6a17
- Live KoboldCpp activation/identity run remains unauthorized.

Objective training boundary:
- Candidate V3 is retention/evaluation evidence, NOT SFT training data.
- PR #69 already contains the fail-closed one-run QLoRA trainer.
- Actual SFT uses the experiment contract's exact train/validation source subject.
- PR #68 final-bank custody/sealing remains incomplete.
- no exact V10_QWEN35_TRAINING_AUTHORITY_V1.json exists.
- model-weight mutation remains blocked until final-bank seal + exact authority + READY preflight.

Historical evidence to preserve:
- V6 witness adjudication path: successor/evaluation/v10_qwen35/retention_arch_v6.witness_adjudication.json
- V6 witness adjudication SHA-256: 517e8819cfca5a38500a614024e99a04156f7b3e1dbd230a0ef4c09be70d6664
- V6 remains frozen HOLD; adjudication does not rewrite it.

Repository verification on V7 pre-result bytes: 477 passed; git diff --check clean.
