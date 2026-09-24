from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

SPEC_PATH = Path(__file__).with_name("QWEN35_HF_SUBSTRATE_V1.json")

REQUIRED_LORA_SUFFIXES = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "in_proj_qkv",
    "in_proj_z",
    "in_proj_b",
    "in_proj_a",
    "out_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)

REQUIRED_FAMILY_TOKENS = (
    ".self_attn.",
    ".linear_attn.",
    ".mlp.",
)

FORBIDDEN_TEXT_ONLY_TOKENS = (
    ".visual.",
    ".vision.",
    "vision_tower",
)


def load_spec(path: Path = SPEC_PATH) -> dict:
    spec = json.loads(path.read_text(encoding="utf-8"))
    if spec.get("schema") != "VERA_QWEN35_HF_SUBSTRATE_V1":
        raise ValueError("unexpected Qwen3.5 substrate schema")
    revision = spec.get("revision")
    if not isinstance(revision, str) or len(revision) != 40:
        raise ValueError("Qwen3.5 substrate revision must be an immutable 40-hex Git commit")
    try:
        int(revision, 16)
    except ValueError as exc:
        raise ValueError("Qwen3.5 substrate revision is not hexadecimal") from exc
    if spec.get("training_modality") != "TEXT_ONLY":
        raise ValueError("Qwen3.5 successor training must remain TEXT_ONLY")
    if spec.get("allow_vision_adapters") is not False:
        raise ValueError("vision adapters must remain disabled")
    targets = tuple(spec.get("lora", {}).get("target_modules", ()))
    if targets != REQUIRED_LORA_SUFFIXES:
        raise ValueError("Qwen3.5 LoRA target set differs from the reviewed smoke subject")
    return spec


def validate_text_module_inventory(
    module_names: Iterable[str],
    *,
    spec: dict | None = None,
) -> tuple[str, ...]:
    spec = load_spec() if spec is None else spec
    names = tuple(str(name) for name in module_names)
    if not names:
        raise ValueError("Qwen3.5 module inventory is empty")

    lowered = tuple(name.lower() for name in names)
    forbidden = sorted(
        name
        for name, low in zip(names, lowered)
        if any(token in low for token in FORBIDDEN_TEXT_ONLY_TOKENS)
    )
    if forbidden:
        raise ValueError(
            "text-only Qwen3.5 load contains forbidden vision modules: "
            + ", ".join(forbidden[:8])
        )

    for family in REQUIRED_FAMILY_TOKENS:
        if not any(family in name for name in names):
            raise ValueError(f"Qwen3.5 text module family missing: {family}")

    targets = tuple(spec["lora"]["target_modules"])
    missing = [
        suffix
        for suffix in targets
        if not any(name == suffix or name.endswith("." + suffix) for name in names)
    ]
    if missing:
        raise ValueError(
            "Qwen3.5 LoRA targets missing from loaded text backbone: "
            + ", ".join(missing)
        )

    return targets


def load_qwen35_text_model():
    import torch
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    spec = load_spec()
    repo = spec["repo"]
    revision = spec["revision"]

    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(repo, revision=revision)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        repo,
        revision=revision,
        quantization_config=quant,
        device_map={"": 0},
        dtype=torch.bfloat16,
    )

    observed_model_class = type(model).__name__
    observed_config_class = type(model.config).__name__
    if observed_model_class != spec["expected_text_model_class"]:
        raise RuntimeError(
            "unexpected Qwen3.5 text model class: "
            f"{observed_model_class} != {spec['expected_text_model_class']}"
        )
    if observed_config_class != spec["expected_text_config_class"]:
        raise RuntimeError(
            "unexpected Qwen3.5 text config class: "
            f"{observed_config_class} != {spec['expected_text_config_class']}"
        )

    target_modules = validate_text_module_inventory(
        (name for name, _module in model.named_modules()),
        spec=spec,
    )

    model.config.use_cache = False
    peft = LoraConfig(
        r=int(spec["lora"]["r"]),
        lora_alpha=int(spec["lora"]["alpha"]),
        lora_dropout=float(spec["lora"]["dropout"]),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(target_modules),
    )
    return model, tokenizer, peft


def lora_receipt_fields(spec: dict | None = None) -> dict:
    spec = load_spec() if spec is None else spec
    return {
        "r": int(spec["lora"]["r"]),
        "alpha": int(spec["lora"]["alpha"]),
        "dropout": float(spec["lora"]["dropout"]),
        "target_modules": list(spec["lora"]["target_modules"]),
        "training_modality": spec["training_modality"],
        "expected_text_model_class": spec["expected_text_model_class"],
        "expected_text_config_class": spec["expected_text_config_class"],
        "allow_vision_adapters": spec["allow_vision_adapters"],
    }
