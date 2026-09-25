# Qwen3.5 Objective-Fidelity V2 Training Continuation — 2026-09-25

> **Superseded status — 2026-09-25:** Behavioral qualification is no longer pending. The exact V2 adapter failed the historical 40-row control relative to base and is not behaviorally qualified. That 40-row set has also been consumed as a V3 development control. Continue from `state/continuation/QWEN35_BEHAVIOR_V3_DEV_CONTROL_20260925.md`.

Restore:
`QWEN35::RESTORE_AND_RUN::OBJECTIVE_FIDELITY_V2_COMPLETE_20260925`

## Final trained subject

Output identity:
`Vera-Qwen3.5-4B-Behavior-V1`

Final corpus:
- SFT rows: 760
- SFT SHA-256: `b0988e78987f91e15a665c6cb4163219e28111c7e5cd7882c1989882228553c0`
- preference rows: 648
- preference SHA-256: `2157be2ecb419bc41c4631f4422d1439c9bd00d9ed93d0dbe8f4bd41362c9555`

The final corpus includes:
- chat-derived behavior training;
- repo-derived engineering behavior from BT2, DriftGuard, Project Achilles, vera_model_training, Roots, and SQL Connectome;
- objective/referent/proxy fidelity;
- general rehearsal;
- frozen gold behavior pairs.

Reward-hacking material is not a positive teacher. It is admitted only as adversarial/red-team evidence and possible reviewed rejected material.

## Full training

Exact custody-source HF job:
`6ab5cd3e52d0dbd7f1d8db36`

Trainer commit:
`b0b4564c9a6ce04b988e417be0a4724c20e42a18`

Runtime:
- terminal status: COMPLETED
- base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- all-linear QLoRA
- r=4
- alpha=16
- 248 target modules
- SFT loss: 1.3865353534096165
- ORPO loss: 1.5743041921544958

## Final adapter custody

Git custody commit:
`202d84099ecbfee5981e84e390808de4cc9d8d47`

Adapter archive:
- bytes: 12,854,865
- SHA-256: `1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69`
- 18 raw Git parts
- independent CPU reconstruction PASS
- required files present:
  - `adapter/adapter_config.json`
  - `adapter/adapter_model.safetensors`

Manifest:
`successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-objective-v2-adapter-manifest.json`

Training receipt:
`successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-objective-v2-training-receipt.json`

Runtime/custody receipt:
`successor/qwen35/qualification/FULL_TRAINING_RUNTIME_RECEIPT_OBJECTIVE_V2.md`

## Verification

Exact branch contract at commit:
`e6ba3fd8a2ec272123e7834d2939ab3e44b1390e`

Result:
`10 passed in 0.08s`

## Superseded artifact

The earlier 736-SFT / 616-preference adapter with SHA-256
`5dddfdbfccbe63ad12a84e329c324e50e5162fdde3a0d332b554a207ddc8c2a4`
is a valid earlier candidate but is superseded as final V2 by the 760/648 objective-fidelity subject.

HF job `6ab655a852d0dbd7f1d8f67d` also completed the final 760/648 subject, but its 65,536-character artifact log chunks are truncated by retrieval. Do not use that job for artifact custody. Use `6ab5cd3e52d0dbd7f1d8db36`.

## Remaining gate

Behavioral qualification remains pending.

Planned evaluation:
- frozen 40-row V1 control holdout;
- new 100-row behavior holdout;
- retention checks;
- objective/proxy-gaming red-team holdout.

Do not claim behavioral qualification, merged-model equivalence, GGUF conversion correctness, installation, activation, or deployment effect yet.

No further GPU jobs were launched after final artifact custody because the previously authorized HF compute ceiling of $6 has already been reached/exceeded conservatively by executed GPU work.

## Claim ceiling

`FINAL_V2_CORPUS_FROZEN / FULL_TRAINING_COMPLETE / FINAL_ADAPTER_CUSTODY_VERIFIED / CONTRACT_10_OF_10_PASS / BEHAVIORAL_QUALIFICATION_PENDING / NOT_DEPLOYED`
