import inspect

import pytest

from successor.v5 import qwen35_substrate as q35
from successor.v5 import train_v5


def representative_text_module_names():
    return [
        "model.layers.0.linear_attn.in_proj_qkv",
        "model.layers.0.linear_attn.in_proj_z",
        "model.layers.0.linear_attn.in_proj_b",
        "model.layers.0.linear_attn.in_proj_a",
        "model.layers.0.linear_attn.out_proj",
        "model.layers.1.mlp.gate_proj",
        "model.layers.1.mlp.up_proj",
        "model.layers.1.mlp.down_proj",
        "model.layers.3.self_attn.q_proj",
        "model.layers.3.self_attn.k_proj",
        "model.layers.3.self_attn.v_proj",
        "model.layers.3.self_attn.o_proj",
    ]


def test_qwen35_substrate_is_immutable_text_only_and_vision_excluding():
    spec = q35.load_spec()
    assert spec["repo"] == "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
    assert spec["revision"] == "cec7eb63d667bf2e7928e54598cb5f46aa3bdaaa"
    assert spec["training_loader"] == "transformers.AutoModelForCausalLM"
    assert spec["expected_text_model_class"] == "Qwen3_5ForCausalLM"
    assert spec["expected_text_config_class"] == "Qwen3_5TextConfig"
    assert spec["training_modality"] == "TEXT_ONLY"
    assert spec["allow_vision_adapters"] is False
    assert tuple(spec["lora"]["target_modules"]) == q35.REQUIRED_LORA_SUFFIXES


def test_representative_qwen35_hybrid_text_inventory_accepts_all_targets():
    targets = q35.validate_text_module_inventory(representative_text_module_names())
    assert targets == q35.REQUIRED_LORA_SUFFIXES


def test_missing_linear_attention_target_fails_closed():
    names = [
        name
        for name in representative_text_module_names()
        if not name.endswith(".in_proj_a")
    ]
    with pytest.raises(ValueError, match="LoRA targets missing"):
        q35.validate_text_module_inventory(names)


def test_any_vision_module_fails_closed_before_adapter_creation():
    names = representative_text_module_names() + [
        "model.visual.blocks.0.attn.q_proj",
    ]
    with pytest.raises(ValueError, match="forbidden vision modules"):
        q35.validate_text_module_inventory(names)


def test_v5_trainer_accepts_substrate_loader_without_changing_legacy_defaults():
    signature = inspect.signature(train_v5.train)
    assert signature.parameters["base_repo"].default == train_v5.BASE_REPO
    assert signature.parameters["base_revision"].default == train_v5.BASE_REV
    assert signature.parameters["model_loader"].default is None
    assert signature.parameters["lora_receipt"].default is None
