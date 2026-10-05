from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "training" / "h3_rdme_v3_compat_gate.py"
PROTOCOL_PATH = ROOT / "training" / "H3_RDME_V3_COMPAT_GATE_PROTOCOL_V1.json"


def _load_module():
    assert MODULE_PATH.exists(), "V3 compatibility gate module must exist"
    spec = importlib.util.spec_from_file_location("h3_rdme_v3_compat_gate", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v3_protocol_thresholds_are_frozen():
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert protocol["thresholds"] == {
        "mixed_gain_ratio_min": 5.0,
        "isolated_module_mse_max": 0.001,
        "mixed_semantic_mse_max": 0.001,
    }


def test_v3_accepts_valid_overlap_shape():
    module = _load_module()
    metrics = {
        "mixed_gain_ratio": 100.0,
        "isolated_x_mse": 1e-6,
        "isolated_y_mse": 2e-6,
        "mixed_semantic_mse": 3e-6,
    }
    thresholds = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))["thresholds"]
    assert module.compatibility_decision_v3(metrics, thresholds)["accept"] is True


def test_v3_rejects_semantic_conflict():
    module = _load_module()
    metrics = {
        "mixed_gain_ratio": 0.01,
        "isolated_x_mse": 1e-6,
        "isolated_y_mse": 2e-6,
        "mixed_semantic_mse": 0.2,
    }
    thresholds = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))["thresholds"]
    assert module.compatibility_decision_v3(metrics, thresholds)["accept"] is False
