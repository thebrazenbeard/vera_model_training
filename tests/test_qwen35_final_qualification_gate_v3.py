from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "qualification" / "evaluate_behavior_v2.py"


def load_eval_module():
    spec = importlib.util.spec_from_file_location("qwen35_eval_final_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_final_qualification_gate_blocks_without_fresh_final_manifest():
    module = load_eval_module()

    assert hasattr(module, "evaluate_final_qualification_gate")
    result = module.evaluate_final_qualification_gate(ROOT)

    assert result["status"] == "BLOCKED"
    assert result["subject"] == "OBJECTIVE_FIDELITY_V2_760_648"
    assert result["adapter_sha256"] == "1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69"
    assert "fresh_final_manifest_missing" in result["reasons"]
