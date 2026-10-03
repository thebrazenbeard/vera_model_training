from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class AccelerationHold(RuntimeError):
    """Fail-closed refusal for unsupported Lane B runtime choices."""


ALLOWED_OPTIMIZERS = {'adamw_bnb_8bit', 'adamw_torch_8bit'}
ALLOWED_BACKENDS = {'torch_reference', 'torch_compile_reference', 'fla_triton'}


def validate_lane_b_optimizer(name: str) -> str:
    if not isinstance(name, str) or not name:
        raise AccelerationHold('optimizer missing')
    if 'paged' in name.casefold():
        raise AccelerationHold('paged optimizers are forbidden on Lappy')
    if name not in ALLOWED_OPTIMIZERS:
        raise AccelerationHold(f'unsupported Lane B optimizer:{name}')
    return name


def _delta_modules(model) -> list[tuple[str, Any]]:
    modules = []
    for name, module in model.named_modules():
        if not name.endswith('.linear_attn'):
            continue
        required = (
            'chunk_gated_delta_rule',
            'recurrent_gated_delta_rule',
            'causal_conv1d_update',
        )
        if all(hasattr(module, field) for field in required):
            modules.append((name, module))
    return modules


def apply_qwen35_acceleration(
    model,
    *,
    backend: str,
    torch_chunk=None,
    torch_recurrent=None,
    torch_conv_update=None,
    fla_chunk=None,
    fla_recurrent=None,
    fla_conv=None,
    fla_conv_update=None,
    compiler: Callable | None = None,
) -> dict:
    if backend not in ALLOWED_BACKENDS:
        raise AccelerationHold(f'unsupported acceleration backend:{backend}')

    if backend == 'torch_reference':
        if any(x is None for x in (torch_chunk, torch_recurrent, torch_conv_update)):
            from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen35
            torch_chunk = torch_chunk or qwen35.torch_chunk_gated_delta_rule
            torch_recurrent = torch_recurrent or qwen35.torch_recurrent_gated_delta_rule
            torch_conv_update = torch_conv_update or qwen35.torch_causal_conv1d_update
        chunk = torch_chunk
        recurrent = torch_recurrent
        conv = None
        conv_update = torch_conv_update
    elif backend == 'fla_triton':
        if fla_chunk is None or fla_recurrent is None:
            try:
                from fla.ops.gated_delta_rule import (
                    chunk_gated_delta_rule,
                    fused_recurrent_gated_delta_rule,
                )
            except Exception as exc:
                raise AccelerationHold(f'FLA backend unavailable:{exc}') from exc
            fla_chunk = fla_chunk or chunk_gated_delta_rule
            fla_recurrent = fla_recurrent or fused_recurrent_gated_delta_rule
        if torch_conv_update is None:
            from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen35
            torch_conv_update = qwen35.torch_causal_conv1d_update
        chunk = fla_chunk
        recurrent = fla_recurrent
        conv = None
        conv_update = torch_conv_update
    else:
        if any(x is None for x in (torch_chunk, torch_recurrent, torch_conv_update)):
            from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen35
            torch_chunk = torch_chunk or qwen35.torch_chunk_gated_delta_rule
            torch_recurrent = torch_recurrent or qwen35.torch_recurrent_gated_delta_rule
            torch_conv_update = torch_conv_update or qwen35.torch_causal_conv1d_update
        if compiler is None:
            import torch
            compiler = torch.compile
        chunk = compiler(torch_chunk, dynamic=False, fullgraph=False)
        recurrent = compiler(torch_recurrent, dynamic=False, fullgraph=False)
        conv = None
        conv_update = compiler(torch_conv_update, dynamic=False, fullgraph=False)

    patched = _delta_modules(model)
    for _, module in patched:
        module.chunk_gated_delta_rule = chunk
        module.recurrent_gated_delta_rule = recurrent
        module.causal_conv1d_fn = conv
        module.causal_conv1d_update = conv_update

    if not patched:
        raise AccelerationHold('no Qwen3.5 DeltaNet modules found')

    return {
        'backend': backend,
        'patched_delta_modules': len(patched),
        'module_names': [name for name, _ in patched],
        'causal_conv_backend': 'fla_triton' if conv is not None else 'torch_reference',
    }