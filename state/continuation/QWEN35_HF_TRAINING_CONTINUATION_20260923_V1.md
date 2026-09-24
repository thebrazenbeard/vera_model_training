# Qwen3.5 HF Training Continuation — 2026-09-23 V1

Status: DURABLE HANDOFF / STARTING SNAPSHOT — FRESHNESS REQUIRED BEFORE EFFECT

## Restore directive

`QWEN35::RESTORE_AND_RUN::HF_TRAINING_CONTINUATION_20260923_V1`

## Repository authority

Repository: `thebrazenbeard/vera_model_training`

Continuation branch:
`state/qwen35-hf-training-continuation-20260923-v1`

Parent branch:
`integration/unbound-sol-behavior-v3-v1-20260923`

Exact parent head at branch creation:
`f844a7f586c1b669c8cbeec9c7803fb3a6b0d1b5`

Primary plan:
`docs/superpowers/plans/2026-09-23-qwen35-4b-hf-successor-training.md`

## User decision now durable

Patrick selected the following model family for training and deployment:

Trainable base:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`

Deployment GGUF family:
`tinyopsec/Qwen3.5-4B-Uncensored-Aggressive-GGUF`

Canonical Lappy deployment quant:
`model_q5_k_s.gguf`

Observed local deployment path:
`C:\\VERA\\models\\gguf\\model_q5_k_s.gguf`

Observed local file size:
approximately 3,000,970 KB (~2.86 GiB).

Patrick explicitly instructed that the model is to be trained and that the training must be performed on Hugging Face.

## Critical distinction

Do not train the GGUF directly.

Required direction:

`upstream Qwen3.5 weights -> LoRA/QLoRA training on HF -> merge/export -> GGUF conversion -> Q5_K_S quantization -> deployment-subject qualification -> Lappy`

The Q5_K_S GGUF is the deployment target, not the training source.

## Training-plan lineage read during this chat

The following `vera_model_training` documents were fresh-read before this handoff:

- `docs/superpowers/specs/2026-09-13-bv-model-agnostic-successor-design.md`
- `docs/superpowers/plans/2026-09-14-bv-successor-v3-vera-lab.md`
- `docs/superpowers/plans/2026-09-20-bv-successor-v3-qualification-v2.md`
- `docs/superpowers/plans/2026-09-22-bv-successor-v4-large-corpus.md`
- `docs/checkpoints/TRAINING_ARCHITECTURE_CONTINUATION_V2_20260919.md`
- `docs/training-bus/design.md`
- V5 trainer/pipeline/spec files on `work/bv-v5-diverse-curriculum-20260922`

Key inherited conclusions:

1. Vera/BV successor identity is substrate-agnostic. SmolLM3 was a pilot/control substrate, not the identity target.
2. The current integrated branch is 15 commits ahead of the raw V5 branch and already contains the Unbound-Sol behavior V3 bridge. Use the integrated branch lineage.
3. Final qualification must remain separate from selection/training evidence.
4. Quantization, merge, tokenizer/template change, inference-engine change, and generation-config change create a new deployment subject requiring requalification.
5. Private/runtime/current mutable facts must not be baked into weights as standing truth.
6. Adult consensual sexuality is part of the integrated behavior target; explicitness alone is not harm; child boundary remains categorical.
7. Ordinary competence and negative-transfer resistance remain required.
8. `ZERO_COST` remains an inherited absolute constraint unless Patrick explicitly changes it.

## Current V5 implementation mismatch

The existing V5 trainer is still hard-bound to:

- `HuggingFaceTB/SmolLM3-3B`
- exact SmolLM3 revision
- `AutoModelForCausalLM`
- LoRA targets only `q_proj` and `v_proj`

Do not launch that trainer unchanged against Qwen3.5.

## Qwen3.5 architecture findings

Fresh inspection of current Transformers Qwen3.5 source found:

- dedicated text-only class: `Qwen3_5ForCausalLM`
- the text-only path ignores unexpected vision weights
- 32 text layers
- hybrid full-attention + linear-attention architecture

Observed text module families:

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

Before training, enumerate actual module names on the exact frozen base and prove that the adapter targets only the intended text backbone.

## Hugging Face current state observed

Authenticated account:
`thebrazenbeard`

Account type:
user

Pro:
false

Observed OAuth scopes:
- `jobs`
- `read-repos`
- `read-mcp`
- `openid`
- `profile`

At handoff time:
- no HF Jobs were running.

The current OAuth context does not establish writable HF model-repo custody. Artifact custody must be handled explicitly.

## Authority / cost boundary

Weight-changing training intent for this Qwen3.5 direction is explicit from Patrick in this chat.

No explicit paid-compute authorization was given.

Therefore:
- zero-cost Hugging Face training execution may proceed if genuinely available;
- do not start a billable GPU job without explicit cost authority;
- do not infer merge, deployment, activation, credential changes, or promotion authority from training intent.

## Exact next frontier

1. Fresh-check the continuation branch and integrated parent.
2. Freeze the exact immutable Hugging Face revision for `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`.
3. Add a Qwen-specific V5 substrate manifest/config.
4. Adapt `successor/v5/train_v5.py` to a substrate-aware loader or a Qwen-specific trainer without destroying SmolLM3 provenance.
5. Bind `Qwen3_5ForCausalLM` and introspected text-only LoRA targets.
6. Add tests that fail if:
   - base revision is mutable;
   - expected module families are missing;
   - any adapter lands in a vision module;
   - deployment target is not Q5_K_S.
7. Rebuild/freeze the V5 + Unbound-Sol corpus subject and digests.
8. Determine whether a genuinely zero-cost HF GPU execution path exists under the authenticated account.
9. If zero-cost compute exists, run a one-step HF smoke and persist the receipt.
10. If only paid compute is available, stop at the exact cost gate and request explicit authorization.
11. After smoke PASS, execute full SFT + preference training.
12. Freeze candidate before qualification.
13. Qualify source candidate.
14. Merge/export, convert to GGUF, quantize Q5_K_S.
15. Requalify the exact deployment artifact/runtime subject before Lappy activation.

## Do not repeat the hardware mistake

Lappy has 4 GB VRAM. The prior 27B IQ4_XS model technically fit system RAM but ran poorly. The selected Q5_K_S deployment artifact is intentionally ~2.86 GiB to leave useful VRAM headroom. Do not substitute larger quants as the canonical Lappy target without a fresh benchmark decision.

## Claim ceiling

At this checkpoint:

- plan persisted: YES
- substrate selected: YES
- HF account authenticated: YES
- HF training job launched: NO
- exact base revision frozen: NO
- Qwen trainer patch: NOT YET
- HF smoke: NOT RUN
- full training: NOT RUN
- source candidate qualification: NOT RUN
- Q5_K_S deployment conversion: NOT RUN
- deployment qualification: NOT RUN
- activation: NOT RUN
- merge: NOT PERFORMED
