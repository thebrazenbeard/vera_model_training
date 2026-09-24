# Vera Qwen3.5 Behavior V2 Full Training Runtime Receipt

Date: 2026-09-24
HF job: `6ab59c3852d0dbd7f1d8cd4c`
Trainer commit: `7047d24b5f71bb73a429b4d860b2b54782881d38`
Output identity: `Vera-Qwen3.5-4B-Behavior-V1`

Runtime result:
- terminal status: COMPLETED
- SFT rows: 736
- preference rows: 616
- SFT SHA-256: `0f0db383c170260f484a39172e03b39247c5416d272155eb5fd4a9d85e3f63a6`
- preference SHA-256: `aca9bedb00eabefde53f012eeea42f604420c03e42036aa9128f2dd3cb7dc3ef`
- SFT training loss: 1.388859194257985
- ORPO training loss: 1.5670089969387302
- LoRA: r=4, alpha=16, target_modules=all-linear
- targeted modules: 248
- linear-attention targets: 120
- MLP targets: 96
- full-attention targets: 32
- saved adapter dtype: bfloat16
- adapter archive bytes: 12854260
- adapter archive SHA-256: `5dddfdbfccbe63ad12a84e329c324e50e5162fdde3a0d332b554a207ddc8c2a4`
- durable custody: 17 raw tar.gz parts; reconstruct and verify SHA-256 before use

This establishes a trained adapter candidate only. Behavioral qualification, merged-model equivalence, GGUF conversion correctness, runtime installation, and deployment effect remain separate states.

Claim ceiling:
`FULL_TRAINING_COMPLETE / ADAPTER_SPLIT_ARTIFACT_FROZEN / BEHAVIORAL_QUALIFICATION_PENDING`
