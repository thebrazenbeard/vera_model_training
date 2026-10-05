import json
from statistics import mean
from training.h3_rdme_cpu_surrogate import run_surrogate

SEEDS = [17, 23, 31, 47, 59]


def main():
    runs = [run_surrogate(seed=seed, steps=240) for seed in SEEDS]
    metric_names = sorted(runs[0]["metrics"])
    ratio_names = sorted(runs[0]["ratios"])
    observation_names = sorted(runs[0]["observations"])
    result = {
        "schema": "H3_RDME_CPU_SURROGATE_MULTI_SEED_V1",
        "seeds": SEEDS,
        "device": "cpu",
        "gpu_used": False,
        "protected_data_used": False,
        "metric_means": {name: mean(run["metrics"][name] for run in runs) for name in metric_names},
        "ratio_minima": {name: min(run["ratios"][name] for run in runs) for name in ratio_names},
        "observation_all_seeds": {name: all(run["observations"][name] for run in runs) for name in observation_names},
        "runs": runs,
        "claim_ceiling": "CPU_SYNTHETIC_MULTI_SEED_SURROGATE_ONLY_NOT_LLM_VALIDATION"
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
