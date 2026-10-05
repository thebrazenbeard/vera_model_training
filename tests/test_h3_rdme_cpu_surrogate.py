from pathlib import Path
import importlib.util

MODULE_PATH = Path(__file__).resolve().parents[1] / "training" / "h3_rdme_cpu_surrogate.py"


def _load_module():
    assert MODULE_PATH.exists(), "CPU surrogate module must exist"
    spec = importlib.util.spec_from_file_location("h3_rdme_cpu_surrogate", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_surrogate_public_seam_and_cpu_only():
    module = _load_module()
    result = module.run_surrogate(seed=17, steps=120)
    assert result["schema"] == "H3_RDME_CPU_SURROGATE_RESULT_V1"
    assert result["device"] == "cpu"
    assert result["protected_data_used"] is False
    assert result["gpu_used"] is False


def test_surrogate_is_deterministic_for_same_seed():
    module = _load_module()
    first = module.run_surrogate(seed=23, steps=120)
    second = module.run_surrogate(seed=23, steps=120)
    assert first["metrics"] == second["metrics"]


def test_surrogate_reports_interference_and_composition_metrics():
    module = _load_module()
    result = module.run_surrogate(seed=31, steps=120)
    required = {
        "h1_a_mse_after_a",
        "h1_a_mse_after_b2",
        "h3_a_mse_after_b2",
        "h3_b2_mse",
        "h3_wrong_route_a_mse",
        "h3_adapter_off_a_mse",
        "h3_stale_b1_on_b2_mse",
        "h3_mixed_one_active_best_mse",
        "h3_mixed_composed_mse",
    }
    assert required <= set(result["metrics"])
