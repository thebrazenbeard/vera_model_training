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


## Four-way semantic development result

All four conditions use the same frozen 32-row family-held-out development set and the same greedy generation budget:
- `max_new_tokens=48`
- `do_sample=false`

Internal semantic review result:

| Condition | Passes | Accuracy |
| --- | ---: | ---: |
| BASE | 12 / 32 | 0.375 |
| TRAINED | 13 / 32 | 0.40625 |
| BASE + runtime policy | 19 / 32 | 0.59375 |
| TRAINED + runtime policy | 24 / 32 | 0.75 |

By held-out family:

| Condition | Scheduler | Secret rotation | Feature flag | Infrastructure control plane |
| --- | ---: | ---: | ---: | ---: |
| BASE | 2/8 | 4/8 | 4/8 | 2/8 |
| TRAINED | 3/8 | 4/8 | 4/8 | 2/8 |
| BASE + runtime policy | 4/8 | 5/8 | 6/8 | 4/8 |
| TRAINED + runtime policy | 5/8 | 6/8 | 7/8 | 6/8 |

Pass-count deltas against BASE:
- TRAINED: +1
- BASE + runtime policy: +7
- TRAINED + runtime policy: +12

TRAINED + runtime policy also exceeds:
- BASE + runtime policy by +5 cases;
- TRAINED by +11 cases.

The discrete pass-count improvement of the combined condition is four cases larger than the sum of the two individual deltas. That is **suggestive complementarity**, not proof of causal synergy, because this is a 32-case development set scored by internal host-model review.

The trained-only condition still fails important H07 boundaries, especially:
- asynchronous acceptance promoted into completion;
- timeout/disconnect promoted into success or failure;
- source configuration promoted into downstream behavior;
- generic command success promoted into authoritative post-state.

The runtime policy corrects many of those failures. The combined condition is strongest, but still fails cases where:
- an asynchronous candidate/job ID is incorrectly treated as authoritative;
- an ambiguous response is recognized but reconcile-before-retry is omitted;
- the model hallucinates a receipt that the case did not provide;
- the 48-token cap truncates a partially correct ambiguity answer before the required reconciliation action.

Structured comparison:
`successor/qwen35/qualification/h07_rule_transfer_v2_four_way_comparison.json`

Generation artifacts:
- `h07_rule_transfer_v2_trained_generations.jsonl`
- `h07_rule_transfer_v2_trained_runtime_policy_generations.jsonl`

Internal judgments/results:
- `h07_rule_transfer_v2_trained_internal_judgments.jsonl`
- `h07_rule_transfer_v2_trained_internal_result.json`
- `h07_rule_transfer_v2_trained_runtime_policy_internal_judgments.jsonl`
- `h07_rule_transfer_v2_trained_runtime_policy_internal_result.json`

### Hostile review

> **HOSTILE REVIEWER:** The apparent combined gain could be an artifact of one internal judge, a small 32-case development set, and answers that sometimes truncate at 48 tokens. Calling this "synergy" would overstate the evidence.

**Accepted.** The claim is limited to development evidence of complementarity. The result is strong enough to choose the next architecture direction, but not to establish independent behavioral qualification or a causal interaction between weight adaptation and runtime policy.

> **HOSTILE REVIEWER:** TRAINED alone moved only one case. That may mean the 96-example rule-transfer corpus mostly teaches wording rather than the abstraction.

**Partially accepted.** TRAINED alone is weak evidence for transferable weight-level learning. However, TRAINED + runtime improves five cases over BASE + runtime across every held-out family except none; this suggests the adapter changes how the model applies an available rule. A fresh independently judged holdout is required before treating that as durable generalization.

## Revised next step

Do not increase epochs, add ORPO, or raise LoRA rank yet.

The strongest surviving architecture is:
1. keep the H07 rule explicit in runtime;
2. retain the V2 adapter as a development candidate, not a promoted model;
3. freeze the V2 evaluator and rule-transfer recipe;
4. obtain an independent semantic judgment or a fresh final holdout before promotion;
5. only then run clean-parent substrate and LoRA-capacity ablations if the combined result reproduces.

This result argues against treating H07 as a weights-only behavior. It supports a hybrid design in which training supplies a prior and runtime supplies the explicit effect-verification contract.
