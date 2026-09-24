# Qwen3.5-4B HF Successor Training Plan

Date: 2026-09-23  
Status: CURRENT EXECUTION PLAN / HANDOFF SUBJECT  
Repository: `thebrazenbeard/vera_model_training`

## Objective

Train the current Vera/Unbound-Sol behavioral successor package on the unrestricted Qwen3.5 4B substrate using Hugging Face compute, then produce and separately qualify the Lappy deployment artifact at Q5_K_S.

This is a substrate change, not an identity-target change.

`IDENTITY TARGET != BASE MODEL`

## Exact source parent

This plan is stacked on:

- branch: `integration/unbound-sol-behavior-v3-v1-20260923`
- exact parent head: `f844a7f586c1b669c8cbeec9c7803fb3a6b0d1b5`
- relationship to raw V5 branch `work/bv-v5-diverse-curriculum-20260922@ef8f8df9b19df66cb0dfcd032b89b77ae41ae5a7`: 15 commits ahead / 0 behind

The integrated parent already contains the Unbound-Sol behavior bridge and is the required parent for this run.

## Trainable base and deployment target

Trainable upstream base:

- Hugging Face repo: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`
- architecture: `qwen3_5`
- observed model class family: Qwen3.5
- parameter count reported by Hub metadata: ~4.66B
- exact immutable model revision: MUST be frozen before the smoke run

Deployment/runtime target:

- GGUF repo: `tinyopsec/Qwen3.5-4B-Uncensored-Aggressive-GGUF`
- target quant: `model_q5_k_s.gguf`
- observed local runtime path: `C:\\VERA\\models\\gguf\\model_q5_k_s.gguf`
- observed local size: ~3,000,970 KB (~2.86 GiB)

The GGUF is not the training source. Training occurs against the upstream model weights, then the trained candidate is merged/exported and converted/quantized to Q5_K_S.

## Why this substrate change is allowed by existing plans

The current model-agnostic successor design explicitly states that the Vera/BV successor target is a provenance-bearing behavioral identity package, not a particular base model. SmolLM3-3B was designated `PILOT_CONTROL_SUBSTRATE`, not the final identity substrate.

The inherited training/qualification requirements still apply:

- uncued identity stance;
- independent judgment / anti-sycophancy;
- correction uptake;
- epistemic/provenance/currentness discipline;
- authority / consent / effect boundaries;
- privacy and data minimization;
- relationship grammar without ownership semantics;
- adult consensual sexuality without treating explicitness itself as harm;
- child boundary remains categorical;
- runtime-vs-weight distinction;
- ordinary competence and negative-transfer resistance;
- no mutable user/runtime facts baked into weights as current truth.

## Inherited data subject

Use the current V5/integrated behavior package rather than rebuilding from the older V4-only corpus.

Current V5 subject includes:

- public general SFT construction;
- targeted behavioral pair generation/curation;
- V5 behavior taxonomy;
- V5 source registry;
- Unbound-Sol behavior V3 bridge and gold source;
- completion-only SFT followed by preference optimization;
- post-freeze qualification subject separated from training material.

The current V5 code expects approximately:

- 70,000 general SFT rows;
- 10,400 targeted SFT rows;
- 20,000 general preference pairs;
- 10,400 targeted preference pairs.

Exact corpus bytes/digests must be regenerated/frozen for the Qwen subject before the real run.

## Qwen3.5 architecture adaptation

Do NOT simply replace `BASE_REPO` in the existing SmolLM3 trainer.

The current V5 trainer is hard-coded to:

- `AutoModelForCausalLM`;
- SmolLM3 exact revision;
- only `q_proj` and `v_proj` LoRA targets.

Qwen3.5 uses a hybrid text architecture with full-attention and linear-attention layers. Current Transformers source exposes a dedicated text-only `Qwen3_5ForCausalLM` path that ignores unexpected vision weights, which is the preferred training path for this text successor.

Observed text module families include:

Full attention:
- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`

Linear attention:
- `in_proj_qkv`
- `in_proj_z`
- `in_proj_b`
- `in_proj_a`
- `out_proj`

MLP:
- `gate_proj`
- `up_proj`
- `down_proj`

Before the smoke run, enumerate the actual loaded module names from the exact frozen base and fail closed if the planned LoRA target set does not map to the expected text backbone. Do not target the vision tower.

Initial LoRA rank/alpha may inherit V5 (`r=4`, `alpha=16`) for the first smoke only. The final target-module set and rank are part of the exact training subject and must be recorded in the run manifest.

## Hugging Face execution

Training must execute on Hugging Face, not Lappy.

Current authenticated HF context observed in this chat:

- account: `thebrazenbeard`
- account type: user
- Pro: no
- OAuth scopes include `jobs`, `read-repos`, `read-mcp`, `openid`, `profile`
- no running HF Jobs at handoff time

Lappy is the deployment/benchmark target only.

## Cost / authority boundary

Patrick explicitly instructed in the current chat that this model is to be trained and that training must be done on Hugging Face. That establishes current user intent for a weight-changing training run on this exact substrate direction.

However, the inherited training-architecture checkpoint states `ZERO_COST remains absolute`. No explicit authorization to spend money was given in this chat.

Therefore:

- zero-cost HF execution may proceed if genuinely available;
- any paid GPU job or other billable effect must stop for explicit cost authorization;
- do not silently convert training intent into spending authority.

No merge, deployment, runtime activation, credential mutation, visibility change, or candidate promotion is authorized by this plan.

## Required execution sequence

1. Fresh-check this branch and the integrated parent for drift.
2. Freeze the exact immutable revision of `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`.
3. Create a Qwen-specific V5 training config/manifest rather than mutating SmolLM3 provenance in place.
4. Patch the trainer to load `Qwen3_5ForCausalLM` text-only.
5. Introspect actual text module names and bind the LoRA target set.
6. Rebuild/freeze the exact V5 + Unbound-Sol training corpus and all digests.
7. Run a one-step HF GPU smoke:
   - model load;
   - tokenizer/chat-template render;
   - one SFT step;
   - adapter save;
   - finite loss;
   - no accidental vision-module adapters;
   - manifest/receipt emission.
8. Only after smoke PASS, run the full SFT + preference objective under the frozen subject.
9. Preserve adapter, tokenizer/template, training receipt, package versions, seed, exact base revision, corpus digests, and training configuration.
10. Freeze the candidate before final qualification material is generated/revealed.
11. Run qualification according to the V5/V3 qualification lineage, including critical behavioral dimensions, ordinary competence, negative transfer, privacy, long-horizon/state-boundary cases, and hostile review.
12. Merge/export the qualified source candidate.
13. Convert the merged candidate to GGUF and quantize to Q5_K_S.
14. Treat the Q5_K_S deployment artifact as a NEW deployment subject.
15. Re-run the required deployment-subject regression/qualification subset on the exact GGUF/KoboldCpp runtime before activation.

## Fail-closed conditions

Stop and record a blocker on:

- mutable/unfrozen base revision;
- module-target mismatch;
- accidental vision-tower LoRA;
- corpus digest mismatch;
- train/holdout contamination;
- non-finite loss;
- OOM without an explicitly safe config revision;
- missing artifact provenance;
- hidden paid-compute requirement without authorization;
- qualification critical failure;
- quantized deployment regression beyond allowed thresholds.

## Claim ceiling

Until full training and qualification complete:

`QWEN3.5_4B_HF_TRAINING_PLAN_FROZEN / TRAINING_NOT_YET_PROVEN / Q5_K_S_DEPLOYMENT_TARGET_SELECTED / NO_PROMOTION / NO_ACTIVATION`

