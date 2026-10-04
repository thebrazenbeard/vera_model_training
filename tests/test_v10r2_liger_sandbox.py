from __future__ import annotations

from types import SimpleNamespace

import pytest

from successor.experiments.probe_v10r2_liger_sandbox import (
    LIGER_CONFIG,
    make_liger_acceleration_wrapper,
    run_liger_probe_with_module,
)


def test_liger_wrapper_preserves_fla_and_records_patch() -> None:
    calls: list[dict] = []

    def original(model, *, backend):
        assert model == "MODEL"
        assert backend == "fla_triton"
        return {"backend": backend, "patched_delta_modules": 24}

    def apply_liger(**kwargs):
        calls.append(kwargs)

    wrapped = make_liger_acceleration_wrapper(original, apply_liger)
    result = wrapped("MODEL", backend="fla_triton")

    assert result["backend"] == "fla_triton"
    assert result["patched_delta_modules"] == 24
    assert result["liger"] == {
        "enabled": True,
        "version": "0.8.4",
        "config": LIGER_CONFIG,
    }
    assert calls == [{"model": "MODEL", **LIGER_CONFIG}]


def test_liger_wrapper_rejects_other_acceleration_backend() -> None:
    def original(model, *, backend):
        return {"backend": backend}

    def apply_liger(**kwargs):
        raise AssertionError("must not be called")

    wrapped = make_liger_acceleration_wrapper(original, apply_liger)
    with pytest.raises(RuntimeError, match="fla_triton"):
        wrapped("MODEL", backend="fla_triton_full")


def test_runner_restores_probe_hook_after_success(tmp_path) -> None:
    original_calls: list[str] = []

    def original(model, *, backend):
        original_calls.append(backend)
        return {"backend": backend}

    probe_module = SimpleNamespace(apply_qwen35_acceleration=original)

    def execute_backward_probe(**kwargs):
        acc = probe_module.apply_qwen35_acceleration(
            "MODEL", backend=kwargs["acceleration_backend"]
        )
        return {"status": "PASS", "acceleration": acc}

    probe_module.execute_backward_probe = execute_backward_probe

    applied: list[dict] = []

    def apply_liger(**kwargs):
        applied.append(kwargs)

    result = run_liger_probe_with_module(
        probe_module=probe_module,
        liger_apply=apply_liger,
        repo_root=tmp_path,
        train_jsonl=tmp_path / "train.jsonl",
        gradient_vector_out=tmp_path / "grad.pt",
    )

    assert result["status"] == "PASS"
    assert result["acceleration"]["liger"]["enabled"] is True
    assert applied == [{"model": "MODEL", **LIGER_CONFIG}]
    assert probe_module.apply_qwen35_acceleration is original


def test_runner_restores_probe_hook_after_failure(tmp_path) -> None:
    def original(model, *, backend):
        return {"backend": backend}

    probe_module = SimpleNamespace(apply_qwen35_acceleration=original)

    def execute_backward_probe(**kwargs):
        probe_module.apply_qwen35_acceleration(
            "MODEL", backend=kwargs["acceleration_backend"]
        )
        raise RuntimeError("boom")

    probe_module.execute_backward_probe = execute_backward_probe

    def apply_liger(**kwargs):
        pass

    with pytest.raises(RuntimeError, match="boom"):
        run_liger_probe_with_module(
            probe_module=probe_module,
            liger_apply=apply_liger,
            repo_root=tmp_path,
            train_jsonl=tmp_path / "train.jsonl",
            gradient_vector_out=tmp_path / "grad.pt",
        )

    assert probe_module.apply_qwen35_acceleration is original
