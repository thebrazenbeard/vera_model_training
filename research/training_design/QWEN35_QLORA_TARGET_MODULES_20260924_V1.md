# Qwen3.5 QLoRA Target-Module Research

Date: 2026-09-24
Subject: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

Live config readback:
- text layers: 32
- `linear_attention`: 24
- `full_attention`: 8

V1 smoke/training introspection found only 8 `q_proj` and 8 `v_proj` modules. Those names belong to the full-attention blocks, so V1's LoRA coverage omitted the 24 linear-attention blocks.

Current Transformers Qwen3.5 source exposes linear-attention projections:
- `in_proj_qkv`
- `in_proj_z`
- `in_proj_b`
- `in_proj_a`
- `out_proj`

It also exposes conventional full-attention `q_proj/k_proj/v_proj/o_proj` and MLP `gate_proj/up_proj/down_proj`.

Current PEFT QLoRA documentation recommends `target_modules="all-linear"` when doing QLoRA-style 4-bit adaptation, both to avoid architecture-name omissions and because adapting all linear layers can approach full-finetuning performance.

Sources:
- https://github.com/huggingface/transformers/blob/main/src/transformers/models/qwen3_5/modeling_qwen3_5.py
- https://github.com/huggingface/transformers/blob/main/src/transformers/models/qwen3_5/configuration_qwen3_5.py
- https://huggingface.co/docs/peft/en/package_reference/lora
- https://huggingface.co/docs/peft/developer_guides/quantization

Decision:
- V2 uses `Qwen3_5ForCausalLM`, so the loaded subject is text-only and vision modules are absent.
- V2 uses LoRA rank 4 / alpha 16 with `target_modules="all-linear"`.
- Runtime must enumerate the resulting targeted module names and fail if vision modules appear or the exact 32-layer topology does not match 24 linear-attention + 8 full-attention.
- The larger adapter is accepted because V1's narrow q/v-only adapter showed no held-out accuracy gain and structurally touched only one quarter of the hybrid attention stack.

Claim ceiling:
`TARGET_COVERAGE_DESIGN_SELECTED / RUNTIME_ASSERTION_REQUIRED / V2_TRAINING_NOT_YET_QUALIFIED`
