from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "training" / "h3_rdme_v2_compat_gate.py"
PROTOCOL_PATH = ROOT / "training" / "H3_RDME_V2_COMPAT_GATE_PROTOCOL_V1.json"


def _load_module():
    assert MODULE_PATH.exists(), "compatibility gate module must exist"
    spec = importlib.util.spec_from_file_location("h3_rdme_v2_compat_gate", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_protocol_thresholds_are_frozen():
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert protocol["status"] == "FROZEN_PREREGISTRATION"
    assert protocol["thresholds"] == {
        "mixed_gain_ratio_min": 5.0,
        "component_projection_mse_max": 0.001,
    }


def test_gate_accepts_safe_metrics():
    module = _load_module()
    decision = module.compatibility_decision(
        {"mixed_gain_ratio": 20.0, "component_x_mse": 1e-5, "component_y_mse": 2e-5},
        {"mixed_gain_ratio_min": 5.0, "component_projection_mse_max": 0.001},
    )
    assert decision["accept"] is True


def test_gate_rejects_conflicting_metrics():
    module = _load_module()
    decision = module.compatibility_decision(
        {"mixed_gain_ratio": 0.25, "component_x_mse": 0.2, "component_y_mse": 0.2},
        {"mixed_gain_ratio_min": 5.0, "component_projection_mse_max": 0.001},
    )
    assert decision["accept"] is False
