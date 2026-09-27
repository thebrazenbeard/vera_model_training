# Qwen3.5 Model Training Continuation — 2026-09-27 V2

Restore command:

`QWEN35::RESTORE_AND_RUN::MODEL_TRAINING_CONTINUATION_20260927_V2`

## Canonical working subject

Repository:
`thebrazenbeard/vera_model_training`

Active branch:
`work/qwen35-history-behavior-training-20260923`

Verified source head before this continuation handoff:
`2c3bd01ee8b2033132212249a40fe9f9ce12ceb6`

Fresh-read the branch tip on restore before making changes.

## Full objective-fidelity V2 training — COMPLETE

Output identity:
`Vera-Qwen3.5-4B-Behavior-V1`

Exact training subject:
`OBJECTIVE_FIDELITY_V2_760_648`

Frozen base:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

Frozen corpus:
- SFT: 760 rows
- SFT SHA-256: `b0988e78987f91e15a665c6cb4163219e28111c7e5cd7882c1989882228553c0`
- preference: 648 rows
- preference SHA-256: `2157be2ecb419bc41c4631f4422d1439c9bd00d9ed93d0dbe8f4bd41362c9555`

HF full-training job:
`6ab5cd3e52d0dbd7f1d8db36`

Trainer commit:
`b0b4564c9a6ce04b988e417be0a4724c20e42a18`

Training:
- SFT loss: 1.3865353534096165
- ORPO loss: 1.5743041921544958
- LoRA: r=4 / alpha=16 / all-linear
- targeted modules: 248
  - linear-attention: 120
  - MLP: 96
  - full-attention: 32
- saved adapter dtype: bfloat16

Full objective-fidelity V2 adapter:
- archive bytes: 12,854,865
- archive SHA-256: `1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69`
- Git custody: 18 parts under
  `successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-objective-v2-adapter.partNNN`
- manifest:
  `successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-objective-v2-adapter-manifest.json`
- training receipt:
  `successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-objective-v2-training-receipt.json`
- runtime receipt:
  `successor/qwen35/qualification/FULL_TRAINING_RUNTIME_RECEIPT_OBJECTIVE_V2.md`

Custody readback verified exact archive bytes and required:
- `adapter/adapter_config.json`
- `adapter/adapter_model.safetensors`

Status:
`SOURCE_FROZEN / CORPUS_FROZEN / FULL_TRAINING_COMPLETE / FINAL_ADAPTER_CUSTODY_VERIFIED / NOT_PROMOTED / NOT_DEPLOYED`

## What is on Lappy

Repository evidence records a local trainable/evaluable package at:

`C:\Vera\models\latest-trained`

Package definition:
`successor/qwen35/qualification/LOCAL_TRAINING_PACKAGE_20260925.json`

It contains:
- frozen Qwen3.5 base under `C:\Vera\models\latest-trained\base`
- an H07 rule-transfer V2 LoRA under `C:\Vera\models\latest-trained\adapter`

Current recorded local adapter:
- role: H07 rule-transfer V2 development adapter
- SHA-256: `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`
- LoRA r=4 / alpha=16 / all-linear
- 96 SFT steps
- no ORPO
- training loss: 2.157097419102987

Therefore:
- YES: a trained Qwen3.5 base-plus-LoRA development package is recorded on Lappy.
- NO CLAIM: the exact full objective-fidelity 760/648 adapter is installed at `latest-trained`.
- NO CLAIM: any adapter is merged into a monolithic checkpoint, converted to GGUF, promoted, activated, or deployed.

## H07 development track — COMPLETE THROUGH BLIND REVIEW

Current continuation before this handoff:
`state/continuation/QWEN35_H07_V2_INDEPENDENT_REVIEW_COMPLETE_20260927_V1.md`

Frozen final family holdout:
- file: `successor/qwen35/qualification/h07_final_holdout_v1.jsonl`
- SHA-256: `19ca7a8df3c7bb9d6dbe419e41cb8d56b034219870dc0a8bcc801baa325c50f5`
- rows: 30

Blinded independent semantic review:
- BASE: 1/30
- TRAINED: 1/30
- BASE + runtime policy: 17/30
- TRAINED + runtime policy: 23/30
- trained+runtime-only wins: 10
- base+runtime-only wins: 4
- exact two-sided paired/binomial p: 0.1795654296875

Independent review report:
`successor/qwen35/qualification/H07_FINAL_HOLDOUT_V1_INDEPENDENT_REVIEW_20260927.md`

Verification receipt:
`successor/qwen35/qualification/H07_INDEPENDENT_REVIEW_VERIFICATION_RECEIPT_20260927.md`

Strongest supported H07 statement:

`trained prior + explicit runtime effect-verification contract`

The runtime contract is load-bearing. Weights-only H07 is not established.

## Objective-fidelity / proxy-resistance lane

This was incorporated into the full 760/648 V2 subject before full training.

Curriculum contract:
`successor/qwen35/HISTORY_BEHAVIOR_CURRICULUM_V2.json`

The objective-fidelity lane encodes:
`representation_or_proxy_is_not_the_referent_or_verified_objective`

It includes the deeper relationship among:
- reward != task success
- search result != origin
- translation != behavioral equivalence
- source/build/install/runtime/effect are separate
- test/CI success != untested semantic truth
- receipt/API success != verified effect

Reward-hacking research source:
`lucabaroni/gpt-oss-120b-rlvr-reward-hacking-step-180`

Policy:
- not a positive teacher
- used as an adversarial/red-team source
- exploit trajectories may only contribute reviewed rejected/adversarial material
- hardened verifier/direct readback outranks vulnerable proxy score

Research:
`research/evaluation/REWARD_HACKING_ADVERSARIAL_SOURCE_20260924.md`

## Repo-derived engineering lane

Included in the full V2 training corpus.

Sources include:
- BT2
- DriftGuard
- Project Achilles
- vera_model_training
- Roots
- SQL Connectome

Important portable mechanisms include:
- exact qualification subject binding
- pre-change trust anchors
- retry/readback discipline
- historical evidence != current authority
- corrected provenance lowers claim ceiling
- oldest accessible != proven origin
- overlap/reuse != lineage
- translation plan != behavioral equivalence
- UNDERSTAND / TRANSLATE / VALIDATE / EXECUTE / AUTHORIZE are separate claims

## Current state

`FULL_OBJECTIVE_V2_TRAINING_COMPLETE / OBJECTIVE_V2_ARTIFACT_CUSTODY_VERIFIED / LOCAL_H07_DEVELOPMENT_PACKAGE_PRESENT / H07_V2_TRAINED / FINAL_FAMILY_HOLDOUT_COMPLETE / BLIND_SEMANTIC_REVIEW_COMPLETE / HYBRID_RUNTIME_RULE_LOAD_BEARING / NOT_PROMOTED / NOT_DEPLOYED`

## Next-chat operating instructions

1. Fresh-read the active branch and this continuation before doing new work.
2. Do not rerun the already-completed full objective-fidelity V2 training unless a new training subject is intentionally defined.
3. Do not tune against the frozen H07 final holdout.
4. If the user's goal is to place the full objective-fidelity V2 adapter on Lappy, first verify the current Lappy package and then reconstruct/copy the exact Git-custodied adapter SHA `1645cbe3...`; keep that separate from promotion/deployment.
5. If continuing H07 development, use a new development ontology/holdout or clean-parent A/B; preserve the final holdout.
6. Do not claim the local H07 package is the same subject as the full 760/648 objective-fidelity adapter.
7. Keep source / corpus / training runtime / artifact custody / local installation / merge / GGUF / deployment / behavioral effect as separate states.
8. No merge, deployment, activation, promotion, runtime stop, or new paid HF compute unless separately authorized by the live user.

## Recommended next decision

The main unresolved product decision is whether to:
- install the full objective-fidelity V2 adapter on Lappy as a separate local candidate package;
- continue H07 research with a clean development track;
- merge/export/quantize the full V2 candidate for local inference;
- or hold state and perform broader qualification first.

## Claim ceiling

`Full objective-fidelity V2 training is complete and its adapter is durably preserved in Git. Lappy is recorded as holding a separate H07 rule-transfer V2 base-plus-LoRA development package at C:\Vera\models\latest-trained. Neither subject is promoted or deployed, and the full objective-fidelity adapter must not be conflated with the local H07 package.`
