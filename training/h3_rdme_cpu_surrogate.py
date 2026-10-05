import copy
import torch
from torch import nn

SCHEMA = "H3_RDME_CPU_SURROGATE_RESULT_V1"


class RankOneAdapter(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.u = nn.Parameter(torch.randn(dim, 1) * 0.02)
        self.v = nn.Parameter(torch.randn(1, dim) * 0.02)

    def forward(self, x):
        delta = self.u @ self.v
        return x @ delta.T


def _task_matrices(dim):
    a = torch.zeros(dim, dim)
    b1 = torch.zeros(dim, dim)
    b2 = torch.zeros(dim, dim)
    a[0, 0] = 1.5
    b1[1, 1] = 1.25
    b2[1, 1] = -1.25
    return a, b1, b2


def _mse(pred, target):
    return torch.mean((pred - target) ** 2).item()


def _train(adapter, x, target, steps):
    optimizer = torch.optim.Adam(adapter.parameters(), lr=0.08)
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = torch.mean((adapter(x) - target) ** 2)
        loss.backward()
        optimizer.step()
    return adapter


def _target(x, matrix):
    return x @ matrix.T


def run_surrogate(seed=17, steps=240, dim=8, train_n=512, eval_n=1024):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")
    generator = torch.Generator(device="cpu").manual_seed(seed + 1000)
    x_train = torch.randn(train_n, dim, generator=generator, device=device)
    x_eval = torch.randn(eval_n, dim, generator=generator, device=device)
    a_matrix, b1_matrix, b2_matrix = _task_matrices(dim)
    a_train, b1_train, b2_train = (_target(x_train, m) for m in (a_matrix, b1_matrix, b2_matrix))
    a_eval, b1_eval, b2_eval = (_target(x_eval, m) for m in (a_matrix, b1_matrix, b2_matrix))

    h1 = RankOneAdapter(dim)
    _train(h1, x_train, a_train, steps)
    h1_a_after_a = _mse(h1(x_eval), a_eval)
    _train(h1, x_train, b1_train, steps)
    _train(h1, x_train, b2_train, steps)
    h1_a_after_b2 = _mse(h1(x_eval), a_eval)

    h3_a = RankOneAdapter(dim)
    h3_b = RankOneAdapter(dim)
    _train(h3_a, x_train, a_train, steps)
    _train(h3_b, x_train, b1_train, steps)
    stale_b = copy.deepcopy(h3_b)
    h3_a_before_b2 = _mse(h3_a(x_eval), a_eval)
    _train(h3_b, x_train, b2_train, steps)

    pred_a = h3_a(x_eval)
    pred_b2 = h3_b(x_eval)
    mixed_target = a_eval + b2_eval
    mixed_one_active = min(_mse(pred_a, mixed_target), _mse(pred_b2, mixed_target))
    mixed_composed = _mse(pred_a + pred_b2, mixed_target)

    metrics = {
        "h1_a_mse_after_a": h1_a_after_a,
        "h1_a_mse_after_b2": h1_a_after_b2,
        "h3_a_mse_before_b2": h3_a_before_b2,
        "h3_a_mse_after_b2": _mse(pred_a, a_eval),
        "h3_b2_mse": _mse(pred_b2, b2_eval),
        "h3_wrong_route_a_mse": _mse(pred_b2, a_eval),
        "h3_adapter_off_a_mse": _mse(torch.zeros_like(a_eval), a_eval),
        "h3_stale_b1_on_b2_mse": _mse(stale_b(x_eval), b2_eval),
        "h3_mixed_one_active_best_mse": mixed_one_active,
        "h3_mixed_composed_mse": mixed_composed,
    }
    eps = 1e-12
    ratios = {
        "interference_advantage_ratio": metrics["h1_a_mse_after_b2"] / max(metrics["h3_a_mse_after_b2"], eps),
        "composition_penalty_ratio": mixed_one_active / max(mixed_composed, eps),
    }
    observations = {
        "interference_reduced": ratios["interference_advantage_ratio"] >= 10.0,
        "a_preserved_after_b_mutation": metrics["h3_a_mse_after_b2"] <= max(h3_a_before_b2 * 1.05, 1e-8),
        "wrong_route_degrades": metrics["h3_wrong_route_a_mse"] > metrics["h3_a_mse_after_b2"] * 10.0,
        "adapter_off_degrades": metrics["h3_adapter_off_a_mse"] > metrics["h3_a_mse_after_b2"] * 10.0,
        "stale_b_module_harmful": metrics["h3_stale_b1_on_b2_mse"] > metrics["h3_b2_mse"] * 10.0,
        "one_active_adapter_composition_limit_detected": ratios["composition_penalty_ratio"] >= 10.0,
    }
    return {
        "schema": SCHEMA,
        "seed": seed,
        "steps": steps,
        "device": "cpu",
        "gpu_used": False,
        "protected_data_used": False,
        "task_shape": "overlapping_surface_inputs_rank1_A_rank1_B_mutated_B_rank2_mixed",
        "metrics": metrics,
        "ratios": ratios,
        "observations": observations,
        "claim_ceiling": "CPU_SYNTHETIC_SURROGATE_ONLY_NOT_LLM_VALIDATION",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_surrogate(), sort_keys=True, indent=2))
