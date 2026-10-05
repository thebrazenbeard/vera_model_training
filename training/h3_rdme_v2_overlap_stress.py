import json
from statistics import mean

import torch

from training.h3_rdme_cpu_surrogate import RankOneAdapter, _mse, _target, _train
from training.h3_rdme_v2_compat_gate import compatibility_decision, PROTOCOL_PATH

SEEDS = [17, 23, 31, 47, 59]


def run_seed(seed, steps=240, dim=8, train_n=512, eval_n=1024):
    gate_protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    thresholds = gate_protocol["thresholds"]
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    generator = torch.Generator(device="cpu").manual_seed(seed + 3000)
    x_train = torch.randn(train_n, dim, generator=generator)
    x_eval = torch.randn(eval_n, dim, generator=generator)

    a_matrix = torch.zeros(dim, dim)
    d_matrix = torch.zeros(dim, dim)
    a_matrix[0, 0] = 1.5
    d_matrix[0, 0] = 0.75
    a_train, d_train = _target(x_train, a_matrix), _target(x_train, d_matrix)
    a_eval, d_eval = _target(x_eval, a_matrix), _target(x_eval, d_matrix)

    adapter_a = _train(RankOneAdapter(dim), x_train, a_train, steps)
    adapter_d = _train(RankOneAdapter(dim), x_train, d_train, steps)
    pred_a, pred_d = adapter_a(x_eval), adapter_d(x_eval)
    mixed_target = a_eval + d_eval
    composed = pred_a + pred_d
    composed_mse = _mse(composed, mixed_target)
    best_single_mse = min(_mse(pred_a, mixed_target), _mse(pred_d, mixed_target))
    metrics = {
        "mixed_composed_mse": composed_mse,
        "best_single_mse": best_single_mse,
        "mixed_gain_ratio": best_single_mse / max(composed_mse, 1e-12),
        "component_x_mse": torch.mean((composed[:, 0] - a_eval[:, 0]) ** 2).item(),
        "component_y_mse": torch.mean((composed[:, 0] - d_eval[:, 0]) ** 2).item(),
        "adapter_a_isolated_mse": _mse(pred_a, a_eval),
        "adapter_d_isolated_mse": _mse(pred_d, d_eval),
    }
    return {"seed": seed, "metrics": metrics, "decision": compatibility_decision(metrics, thresholds)}


def main():
    runs = [run_seed(seed) for seed in SEEDS]
    result = {
        "schema": "H3_RDME_V2_OVERLAP_STRESS_RESULT_V1",
        "seeds": SEEDS,
        "device": "cpu",
        "gpu_used": False,
        "protected_data_used": False,
        "gate_accept_all": all(run["decision"]["accept"] for run in runs),
        "gate_reject_all": all(not run["decision"]["accept"] for run in runs),
        "mixed_gain_ratio_min": min(run["metrics"]["mixed_gain_ratio"] for run in runs),
        "mixed_composed_mse_mean": mean(run["metrics"]["mixed_composed_mse"] for run in runs),
        "isolated_component_mse_max": max(
            max(run["metrics"]["adapter_a_isolated_mse"], run["metrics"]["adapter_d_isolated_mse"])
            for run in runs
        ),
        "component_projection_mse_min": min(
            min(run["metrics"]["component_x_mse"], run["metrics"]["component_y_mse"])
            for run in runs
        ),
        "runs": runs,
        "claim_ceiling": "CPU_SYNTHETIC_GATE_STRESS_ONLY_NOT_LLM_VALIDATION"
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
