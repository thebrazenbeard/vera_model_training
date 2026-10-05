import importlib.util

from successor.experiments import qualify_v10r3r3_stage0_runtime as stage0


def test_stage0_runtime_qualification_module_exists():
    spec = importlib.util.find_spec(
        "successor.experiments.qualify_v10r3r3_stage0_runtime"
    )
    assert spec is not None


def test_synthetic_smoke_rows_are_fixed_and_corpus_free():
    assert hasattr(stage0, "synthetic_smoke_rows")
    rows = stage0.synthetic_smoke_rows(count=8)
    assert len(rows) == 8
    assert all(set(row) == {"prompt", "response"} for row in rows)
    assert all(row["prompt"].startswith("Stage-0 synthetic runtime smoke") for row in rows)
    assert all("corpus" not in row["prompt"].casefold() for row in rows)
    assert all("corpus" not in row["response"].casefold() for row in rows)
    assert rows == stage0.synthetic_smoke_rows(count=8)


def _valid_receipt_kwargs():
    return {
        "runtime_binding_sha256": "1" * 64,
        "execution_spec_sha256": "2" * 64,
        "weight_digest_before": "a" * 64,
        "weight_digest_after": "b" * 64,
        "optimizer_step_count": 1,
        "optimizer_created": True,
        "gradients_present": True,
        "nonzero_gradient_parameter_count": 3,
        "microbatches_completed": 8,
        "losses": [1.0] * 8,
        "synthetic_input": True,
        "output_artifacts_written": False,
        "optimizer_name": "AdamW8bit",
        "cuda_memory": {"peak_allocated_mib": 123.0},
    }


def test_stage0_receipt_requires_exactly_one_real_weight_change():
    assert hasattr(stage0, "finalize_stage0_smoke_receipt")
    receipt = stage0.finalize_stage0_smoke_receipt(**_valid_receipt_kwargs())
    assert receipt["status"] == "STAGE0_OPTIMIZER_SMOKE_PASS"
    assert receipt["optimizer_step_count"] == 1
    assert receipt["weight_digest_changed"] is True
    assert receipt["synthetic_input"] is True
    assert receipt["output_artifacts_written"] is False


def test_stage0_receipt_rejects_wrong_step_count_and_unchanged_digest():
    assert hasattr(stage0, "Stage0Hold")
    assert hasattr(stage0, "finalize_stage0_smoke_receipt")
    import pytest

    wrong_steps = _valid_receipt_kwargs()
    wrong_steps["optimizer_step_count"] = 2
    with pytest.raises(stage0.Stage0Hold, match="exactly one optimizer step"):
        stage0.finalize_stage0_smoke_receipt(**wrong_steps)

    unchanged = _valid_receipt_kwargs()
    unchanged["weight_digest_after"] = unchanged["weight_digest_before"]
    with pytest.raises(stage0.Stage0Hold, match="digest did not change"):
        stage0.finalize_stage0_smoke_receipt(**unchanged)


def test_stage0_receipt_rejects_non_synthetic_or_persisted_output():
    import pytest

    non_synthetic = _valid_receipt_kwargs()
    non_synthetic["synthetic_input"] = False
    with pytest.raises(stage0.Stage0Hold, match="synthetic input"):
        stage0.finalize_stage0_smoke_receipt(**non_synthetic)

    persisted = _valid_receipt_kwargs()
    persisted["output_artifacts_written"] = True
    with pytest.raises(stage0.Stage0Hold, match="output artifacts"):
        stage0.finalize_stage0_smoke_receipt(**persisted)



def test_live_stage0_optimizer_smoke_seam_exists():
    assert hasattr(stage0, "execute_stage0_optimizer_smoke")
