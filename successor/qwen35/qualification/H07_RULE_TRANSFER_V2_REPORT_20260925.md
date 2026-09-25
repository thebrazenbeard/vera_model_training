# H07 Rule Transfer V2 — Current Results

## Scope

This experiment tests whether H07 effect-verification behavior improves when the model is trained on an explicit rule plus mechanism-family diversity rather than the 16-example V1 preference corpus.

## Frozen data design

Training:
- 96 SFT rows
- 12 mechanism families
- 8 case types per family
- explicit H07 EFFECT-VERIFICATION POLICY V2 embedded in every training prompt
- no preference rows

Development:
- 32 rows
- 4 fully held-out mechanism families: scheduler, secret_rotation, feature_flag, infrastructure_control_plane
- 8 case types per family
- semantic proposition rubrics, not lexical keyword rubrics

Train and development families are disjoint.

Exact-tokenizer budget:
- training maximum: 371 tokens
- development maximum with reference answer: 131 tokens
- local profile budget: 512 tokens
- over-budget rows: 0

## Pre-training baseline

Subject:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

Primary development evidence is free generation scored against frozen semantic propositions.

Internal host-model review only:
- BASE: 12 / 32 = 0.375
- BASE + H07 runtime policy: 19 / 32 = 0.59375

By held-out family:

BASE:
- scheduler: 2 / 8 = 0.25
- secret_rotation: 4 / 8 = 0.50
- feature_flag: 4 / 8 = 0.50
- infrastructure_control_plane: 2 / 8 = 0.25

BASE + runtime policy:
- scheduler: 4 / 8 = 0.50
- secret_rotation: 5 / 8 = 0.625
- feature_flag: 6 / 8 = 0.75
- infrastructure_control_plane: 4 / 8 = 0.50

These are development measurements under `INTERNAL_HOST_MODEL_REVIEW`, not independent qualification.

## V2 SFT training result

Local run:
- 96 / 96 SFT steps
- one full epoch
- LoRA rank 4
- alpha 16
- all-linear targeting
- 248 targeted modules
- optimizer: `adamw_torch`
- max length: 512
- preference rows: 0
- ORPO: disabled
- SFT loss: 2.157097419102987
- adapter_model.safetensors SHA-256: `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`
- adapter archive SHA-256: `efacb77ad104f6c3369dd25832906c96780483079957b012202decb843c555d8`

No NVIDIA Display/nvlddmkm event was observed during the completed V2 SFT run.

Receipt:
`successor/qwen35/qualification/h07_rule_transfer_v2_sft_r4_training_receipt.json`

## Post-training evaluation status

Post-training generation has **not yet been completed**.

A direct PEFT evaluation load failed before generation with Windows error:

`OSError: The paging file is too small for this operation to complete. (os error 1455)`

This was not a `paged_adamw_8bit` optimizer run. The optimizer remained `adamw_torch`.

Observed host state at the failure:
- free physical RAM: about 1.16 GiB
- free virtual/commit headroom: about 7.24 GiB
- Firefox working set: about 15.65 GiB
- Firefox private memory: about 37.49 GiB
- pagefile: `C:\pagefile.sys`, observed only, not modified

The base checkpoint is sharded into approximately:
- 4.963 GiB
- 3.716 GiB

The evaluation loader therefore encountered host commit pressure while mapping the checkpoint shards.

Patrick explicitly prohibited using/changing the pagefile path as a workaround. No pagefile setting was modified. Firefox was not killed or mutated.

## Claim boundary

Current evidence supports:
- H07 V2 corpus construction completed;
- V2 SFT run completed successfully;
- BASE and BASE + runtime-policy semantic development measurements completed;
- trained adapter artifact exists with exact receipt and hashes.

Current evidence does **not** establish:
- whether TRAINED beats BASE on the 32-case V2 semantic development set;
- whether TRAINED + runtime beats BASE + runtime;
- independent qualification;
- that rank 4 is or is not the limiting factor;
- that the aggressive checkpoint is or is not the limiting substrate.

## Next execution point

When enough host commit headroom is available without modifying the pagefile:

1. generate TRAINED responses on the frozen 32-case V2 development set using the same 48-token greedy budget used by BASE;
2. generate TRAINED + runtime-policy responses under the same budget;
3. score both with the frozen semantic rubric;
4. compare all four conditions;
5. only then decide whether to proceed to LoRA-capacity or clean-parent substrate ablations.

Do not retrain H07 V2 merely because post-training evaluation is temporarily blocked.
