# Vera Qwen3.5 Objective-Fidelity V2 Full Training Runtime Receipt

Date: 2026-09-25
Output identity: `Vera-Qwen3.5-4B-Behavior-V1`
Final training subject: `OBJECTIVE_FIDELITY_V2_760_648`

## Exact runtime subject

- HF job: `6ab5cd3e52d0dbd7f1d8db36`
- trainer commit: `b0b4564c9a6ce04b988e417be0a4724c20e42a18`
- terminal status: COMPLETED
- base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- SFT rows: 760
- SFT SHA-256: `b0988e78987f91e15a665c6cb4163219e28111c7e5cd7882c1989882228553c0`
- preference rows: 648
- preference SHA-256: `2157be2ecb419bc41c4631f4422d1439c9bd00d9ed93d0dbe8f4bd41362c9555`
- SFT loss: 1.3865353534096165
- ORPO loss: 1.5743041921544958
- LoRA: r=4, alpha=16, all-linear
- targeted modules: 248
  - linear-attention: 120
  - MLP: 96
  - full-attention: 32
- saved adapter dtype: bfloat16

## Durable artifact custody

- archive bytes: 12,854,865
- archive SHA-256: `1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69`
- source transport: 1,429 HF log chunks at 12,000 base64 characters per full chunk
- Git custody: 18 raw binary parts under
  `successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-objective-v2-adapter.partNNN`
- custody commit: `202d84099ecbfee5981e84e390808de4cc9d8d47`

Independent CPU reconstruction from the Git parts read back:
- bytes: 12,854,865
- SHA-256: `1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69`
- required files present:
  - `adapter/adapter_config.json`
  - `adapter/adapter_model.safetensors`

## Supersession

The earlier 736-SFT / 616-preference adapter
`5dddfdbfccbe63ad12a84e329c324e50e5162fdde3a0d332b554a207ddc8c2a4`
remains valid as an earlier trained artifact but is **superseded as the final V2 candidate** by the 760/648 objective-fidelity subject above.

The later HF job `6ab655a852d0dbd7f1d8f67d` also completed the 760/648 training subject, but its 65,536-character artifact log chunks are truncated by HF log retrieval and therefore are not used for custody. The earlier exact-subject job `6ab5cd3e52d0dbd7f1d8db36` used proven-safe 12,000-character chunks and is the artifact-custody source.

## Qualification boundary

This establishes:
`SOURCE_FROZEN / CORPUS_FROZEN / FULL_TRAINING_COMPLETE / FINAL_ADAPTER_CUSTODY_VERIFIED`

It does **not** establish:
`BEHAVIORAL_QUALIFICATION / MERGED_MODEL_EQUIVALENCE / GGUF_CONVERSION / INSTALLATION / DEPLOYMENT_EFFECT`

Behavioral GPU qualification remains pending because the authorized HF compute ceiling has been reached/exceeded conservatively by already-executed GPU work; no additional GPU job is launched from this receipt.
