docs/plans/2026-10-03-retention-candidate-v3-architecture-v7-identity.md
Task 1: complete
Task 2: complete
Task 3: complete
Task 4: in_progress

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

V7 semantic-screen:
- status: PASS
- failures: 0
- max cosine: 0.6243317723274231
- frozen threshold: 0.9
- binding SHA-256: 033affb5d2fb6f4e76fba03617ccee322001b2ef8ff65beb9c549148b579c018
- result SHA-256: 4af52b8cf84e3d7662ec5ff5866a25225b0d91c518b245e0fb8c95e3cb9948fd
- all bound source/runtime hashes verified

V7 semantic packet:
- rows: 130
- families: 26 x 5
- excluded predecessor case IDs: 520
- overlap: 0
- packet SHA-256: 4de3ae3f5757f76417f8561f4c415b4be1daedf3ca4c42cd202b2cb92e1cd20f
- all 130 sampled rows are MECHANICAL_VALID

V7 local identity lane:
- KoboldCpp executable: D:\VERA\Runtime\KoboldCpp\koboldcpp.exe
- Version: 1.121
- Executable SHA-256: 90b0d74ec01e5ef72efb6d45e6f10bee649458920ec951f48d58794c366b1639
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
