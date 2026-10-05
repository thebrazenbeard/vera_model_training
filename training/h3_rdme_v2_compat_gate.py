import json
from pathlib import Path
from statistics import mean

import torch

from training.h3_rdme_cpu_surrogate import RankOneAdapter, _mse, _target, _train

PROTOCOL_PATH = Path(__file__).with_name("H3_RDME_V2_COMPAT_GATE_PROTOCOL_V1.json")
SEEDS = [17, 23, 31, 47, 59]


def compatibility_decision(metrics, thresholds):
    checks = {
        "mixed_gain": metrics["mixed_gain_ratio"] >= thresholds["mixed_gain_ratio_min"],
        "component_x": metrics["component_x_mse"] <= thresholds["component_projection_mse_max"],
        "component_y": metrics["component_y_mse"] <= thresholds["component_projection_mse_max"],
    }
    return {"accept": all(checks.values()), "checks": checks}


def _matrices(dim):
    a = torch.zeros(dim, dim)
    b = torch.zeros(dim, dim)
    c = torch.zeros(dim, dim)
    a[0, 0] = 1.5
    b[1, 1] = -1.25
    c[0, 0] = -1.5
    return a, b, c


def _projection_mse(pred, target, index):
    return torch.mean((pred[:, index] - target[:, index]) ** 2).item()


def run_seed(seed=17, steps=240, dim=8, train_n=512, eval_n=1024):
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    thresholds = protocol["thresholds"]
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    generator = torch.Generator(device="cpu").manual_seed(seed + 2000)
    x_train = torch.randn(train_n, dim, generator=generator)
    x_eval = torch.randn(eval_n, dim, generator=generator)
    a_matrix, b_matrix, c_matrix = _matrices(dim)
    a_train, b_train, c_train = (_target(x_train, m) for m in (a_matrix, b_matrix, c_matrix))
    a_eval, b_eval, c_eval = (_target(x_eval, m) for m in (a_matrix, b_matrix, c_matrix))

    adapter_a = _train(RankOneAdapter(dim), x_train, a_train, steps)
    adapter_b = _train(RankOneAdapter(dim), x_train, b_train, steps)
    adapter_c = _train(RankOneAdapter(dim), x_train, c_train, steps)
    pred_a, pred_b, pred_c = adapter_a(x_eval), adapter_b(x_eval), adapter_c(x_eval)

    safe_target = a_eval + b_eval
    safe_composed = pred_a + pred_b
    safe_composed_mse = _mse(safe_composed, safe_target)
    safe_best_single_mse = min(_mse(pred_a, safe_target), _mse(pred_b, safe_target))
    safe_metrics = {
        "mixed_composed_mse": safe_composed_mse,
        "best_single_mse": safe_best_single_mse,
        "mixed_gain_ratio": safe_best_single_mse / max(safe_composed_mse, 1e-12),
        "component_x_mse": _projection_mse(safe_composed, a_eval, 0),
        "component_y_mse": _projection_mse(safe_composed, b_eval, 1),
    }

    conflict_target = a_eval
    conflict_composed = pred_a + pred_c
    conflict_composed_mse = _mse(conflict_composed, conflict_target)
    conflict_best_single_mse = min(_mse(pred_a, conflict_target), _mse(pred_c, conflict_target))
    conflict_metrics = {
        "mixed_composed_mse": conflict_composed_mse,
        "best_single_mse": conflict_best_single_mse,
        "mixed_gain_ratio": conflict_best_single_mse / max(conflict_composed_mse, 1e-12),
        "component_x_mse": _projection_mse(conflict_composed, a_eval, 0),
        "component_y_mse": _projection_mse(conflict_composed, c_eval, 0),
    }

    return {
        "seed": seed,
        "safe": {"metrics": safe_metrics, "decision": compatibility_decision(safe_metrics, thresholds)},
        "conflict": {"metrics": conflict_metrics, "decision": compatibility_decision(conflict_metrics, thresholds)},
    }


def run_multiseed(seeds=SEEDS, steps=240):
    runs = [run_seed(seed=seed, steps=steps) for seed in seeds]
    return {
        "schema": "H3_RDME_V2_COMPAT_GATE_RESULT_V1",
        "device": "cpu",
        "gpu_used": False,
        "protected_data_used": False,
        "seeds": list(seeds),
        "safe_accept_all": all(run["safe"]["decision"]["accept"] for run in runs),
        "conflict_reject_all": all(not run["conflict"]["decision"]["accept"] for run in runs),
        "safe_mixed_gain_ratio_min": min(run["safe"]["metrics"]["mixed_gain_ratio"] for run in runs),
        "conflict_mixed_gain_ratio_max": max(run["conflict"]["metrics"]["mixed_gain_ratio"] for run in runs),
        "safe_component_projection_mse_max": max(
            max(run["safe"]["metrics"]["component_x_mse"], run["safe"]["metrics"]["component_y_mse"])
            for run in runs
        ),
        "conflict_component_projection_mse_min": min(
            min(run["conflict"]["metrics"]["component_x_mse"], run["conflict"]["metrics"]["component_y_mse"])
            for run in runs
        ),
        "safe_composed_mse_mean": mean(run["safe"]["metrics"]["mixed_composed_mse"] for run in runs),
        "conflict_composed_mse_mean": mean(run["conflict"]["metrics"]["mixed_composed_mse"] for run in runs),
        "runs": runs,
        "claim_ceiling": "CPU_SYNTHETIC_COMPATIBILITY_GATE_ONLY_NOT_LLM_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(run_multiseed(), sort_keys=True, indent=2))
