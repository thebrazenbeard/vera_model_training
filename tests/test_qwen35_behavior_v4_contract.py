from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "successor" / "qwen35"
RECIPE = Q / "V4_TRAINING_RECIPE_V1.json"
REGISTRY = Q / "corpus" / "v4_consumed_evidence_registry.json"


def test_v4_recipe_freezes_counts_and_training_method():
    recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert recipe["schema"] == "VERA_QWEN35_BEHAVIOR_V4_RECIPE_V1"
    assert recipe["base_repo"] == "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
    assert recipe["base_revision"] == "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
    corpus = recipe["corpus"]
    assert corpus["total_sft_rows"] == 512
    assert corpus["targeted_rows"] == 268
    assert corpus["general_rehearsal_rows"] == 244
    quotas = corpus["dimension_quotas"]
    assert set(quotas) == {f"H{i:02d}" for i in range(1, 21)}
    assert sum(quotas.values()) == 268
    assert quotas["H07"] == quotas["H13"] == 20
    assert quotas["H05"] == quotas["H17"] == quotas["H19"] == 16
    assert all(quotas[d] == 12 for d in quotas if d not in {"H05", "H07", "H13", "H17", "H19"})
    training = recipe["training"]
    assert training["method"] == "QLORA_SFT_ONLY"
    assert training["preference_stage"] is False
    assert training["lora_r"] == 4
    assert training["lora_alpha"] == 16
    assert training["target_modules"] == "all-linear"
    assert training["hardware_profile"] == "lappy-rtx3050-4gb"
    assert training["max_length"] == 512
    assert training["overflow"] == "error"
    assert training["optimizer"] == "adamw_torch"


def test_v4_registry_quarantines_consumed_final_evidence():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = {row["path"]: row for row in registry["entries"]}
    required = {
        "successor/qwen35/qualification/final_holdout_v3.jsonl",
        "successor/qwen35/qualification/final_retention_v3.jsonl",
        "successor/qwen35/qualification/final_adversarial_proxy_v3.jsonl",
        "successor/qwen35/qualification/FINAL_BLIND_REVIEW_V3_SELECTION.json",
        "successor/qwen35/qualification/history_behavior_holdout_v1.jsonl",
        "successor/qwen35/qualification/h07_final_holdout_v1.jsonl",
    }
    assert required <= set(entries)
    assert all(len(entries[path]["sha256"]) == 64 for path in required)
    assert all(entries[path]["training_use"] == "PROHIBITED" for path in required)
    assert all(entries[path]["v4_final_qualification_use"] == "PROHIBITED" for path in required)