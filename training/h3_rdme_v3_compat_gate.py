import json
from pathlib import Path

import torch

from training.h3_rdme_cpu_surrogate import RankOneAdapter, _mse, _target, _train

PROTOCOL_PATH = Path(__file__).with_name("H3_RDME_V3_COMPAT_GATE_PROTOCOL_V1.json")
SEEDS = [17, 23, 31, 47, 59]


def compatibility_decision_v3(metrics, thresholds):
    checks = {
        "mixed_gain": metrics["mixed_gain_ratio"] >= thresholds["mixed_gain_ratio_min"],
        "isolated_x": metrics["isolated_x_mse"] <= thresholds["isolated_module_mse_max"],
        "isolated_y": metrics["isolated_y_mse"] <= thresholds["isolated_module_mse_max"],
        "mixed_semantic": metrics["mixed_semantic_mse"] <= thresholds["mixed_semantic_mse_max"],
    }
    return {"accept": all(checks.values()), "checks": checks}


def _train_adapter(x_train, matrix, steps, dim):
    return _train(RankOneAdapter(dim), x_train, _target(x_train, matrix), steps)


def _pair_metrics(pred_x, pred_y, target_x, target_y, mixed_target, thresholds):
    composed = pred_x + pred_y
    composed_mse = _mse(composed, mixed_target)
    best_single_mse = min(_mse(pred_x, mixed_target), _mse(pred_y, mixed_target))
    metrics = {
        "mixed_gain_ratio": best_single_mse / max(composed_mse, 1e-12),
        "isolated_x_mse": _mse(pred_x, target_x),
        "isolated_y_mse": _mse(pred_y, target_y),
        "mixed_semantic_mse": composed_mse,
        "mixed_composed_mse": composed_mse,
        "best_single_mse": best_single_mse,
    }
    return {"metrics": metrics, "decision": compatibility_decision_v3(metrics, thresholds)}


def run_seed(seed=17, steps=240, dim=8, train_n=512, eval_n=1024):
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    thresholds = protocol["thresholds"]
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    generator = torch.Generator(device="cpu").manual_seed(seed + 4000)
    x_train = torch.randn(train_n, dim, generator=generator)
    x_eval = torch.randn(eval_n, dim, generator=generator)

    a = torch.zeros(dim, dim)
    b = torch.zeros(dim, dim)
    d = torch.zeros(dim, dim)
    c = torch.zeros(dim, dim)
    a[0, 0] = 1.5
    b[1, 1] = -1.25
    d[0, 0] = 0.75
    c[0, 0] = -1.5

    ad_a = _train_adapter(x_train, a, steps, dim)
    ad_b = _train_adapter(x_train, b, steps, dim)
    ad_d = _train_adapter(x_train, d, steps, dim)
    ad_c = _train_adapter(x_train, c, steps, dim)

    ta, tb, td, tc = (_target(x_eval, m) for m in (a, b, d, c))
    pa, pb, pd, pc = ad_a(x_eval), ad_b(x_eval), ad_d(x_eval), ad_c(x_eval)

    orthogonal = _pair_metrics(pa, pb, ta, tb, ta + tb, thresholds)
    overlap = _pair_metrics(pa, pd, ta, td, ta + td, thresholds)
    conflict = _pair_metrics(pa, pc, ta, tc, ta, thresholds)
    return {"seed": seed, "orthogonal_safe": orthogonal, "overlap_safe": overlap, "policy_conflict": conflict}


def run_multiseed(seeds=SEEDS, steps=240):
    runs = [run_seed(seed, steps=steps) for seed in seeds]
    return {
        "schema": "H3_RDME_V3_COMPAT_GATE_RESULT_V1",
        "device": "cpu",
        "gpu_used": False,
        "protected_data_used": False,
        "seeds": list(seeds),
        "orthogonal_accept_all": all(run["orthogonal_safe"]["decision"]["accept"] for run in runs),
        "overlap_accept_all": all(run["overlap_safe"]["decision"]["accept"] for run in runs),
        "conflict_reject_all": all(not run["policy_conflict"]["decision"]["accept"] for run in runs),
        "orthogonal_gain_min": min(run["orthogonal_safe"]["metrics"]["mixed_gain_ratio"] for run in runs),
        "overlap_gain_min": min(run["overlap_safe"]["metrics"]["mixed_gain_ratio"] for run in runs),
        "conflict_gain_max": max(run["policy_conflict"]["metrics"]["mixed_gain_ratio"] for run in runs),
        "isolated_mse_max": max(
            max(
                run[class_name]["metrics"]["isolated_x_mse"],
                run[class_name]["metrics"]["isolated_y_mse"],
            )
            for run in runs
            for class_name in ("orthogonal_safe", "overlap_safe", "policy_conflict")
        ),
        "runs": runs,
        "claim_ceiling": "CPU_SYNTHETIC_V3_GATE_ONLY_NOT_LLM_VALIDATION",
    }


if __name__ == "__main__":
    print(json.dumps(run_multiseed(), sort_keys=True, indent=2))
