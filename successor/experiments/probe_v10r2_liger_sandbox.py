from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable


LIGER_VERSION = "0.8.4"
LIGER_CONFIG = {
    "rope": False,
    "cross_entropy": False,
    "fused_linear_cross_entropy": True,
    "rms_norm": True,
    "swiglu": True,
}


def make_liger_acceleration_wrapper(
    original_apply: Callable,
    liger_apply: Callable,
) -> Callable:
    def wrapped(model, *, backend):
        if backend != "fla_triton":
            raise RuntimeError(
                "Liger sandbox requires acceleration_backend=fla_triton"
            )
        acceleration = original_apply(model, backend=backend)
        liger_apply(model=model, **LIGER_CONFIG)
        result = dict(acceleration)
        result["liger"] = {
            "enabled": True,
            "version": LIGER_VERSION,
            "config": dict(LIGER_CONFIG),
        }
        return result

    return wrapped


def run_liger_probe_with_module(
    *,
    probe_module,
    liger_apply: Callable,
    repo_root: Path,
    train_jsonl: Path,
    gradient_vector_out: Path,
) -> dict:
    original_apply = probe_module.apply_qwen35_acceleration
    probe_module.apply_qwen35_acceleration = make_liger_acceleration_wrapper(
        original_apply,
        liger_apply,
    )
    try:
        return probe_module.execute_backward_probe(
            repo_root=repo_root,
            train_jsonl=train_jsonl,
            row_index=4096,
            pad_to_multiple_of=None,
            acceleration_backend="fla_triton",
            gradient_vector_out=gradient_vector_out,
        )
    finally:
        probe_module.apply_qwen35_acceleration = original_apply


def run_liger_probe(
    *,
    repo_root: Path,
    train_jsonl: Path,
    liger_extracted_root: Path,
    gradient_vector_out: Path,
) -> dict:
    extracted = str(liger_extracted_root.resolve())
    if not liger_extracted_root.is_dir():
        raise RuntimeError(
            f"Liger extracted root missing:{liger_extracted_root}"
        )

    inserted = False
    if extracted not in sys.path:
        sys.path.insert(0, extracted)
        inserted = True

    try:
        from liger_kernel.transformers import (
            apply_liger_kernel_to_qwen3_5,
        )
        from successor.experiments import (
            probe_v10r2_lane_b_backward as probe_module,
        )

        return run_liger_probe_with_module(
            probe_module=probe_module,
            liger_apply=apply_liger_kernel_to_qwen3_5,
            repo_root=repo_root,
            train_jsonl=train_jsonl,
            gradient_vector_out=gradient_vector_out,
        )
    finally:
        if inserted:
            try:
                sys.path.remove(extracted)
            except ValueError:
                pass


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument(
        "--liger-extracted-root",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--gradient-vector-out",
        type=Path,
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    result = run_liger_probe(
        repo_root=args.repo_root,
        train_jsonl=args.train_jsonl,
        liger_extracted_root=args.liger_extracted_root,
        gradient_vector_out=args.gradient_vector_out,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
