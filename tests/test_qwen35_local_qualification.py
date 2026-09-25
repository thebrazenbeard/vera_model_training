from __future__ import annotations

import hashlib
import importlib.util
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "qualification" / "evaluate_behavior_v2.py"


def load_eval_module():
    spec = importlib.util.spec_from_file_location("qwen35_eval", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_recover_can_use_local_verified_parts(tmp_path):
    module = load_eval_module()
    payload = b'{"peft_type":"LORA"}'
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w:gz") as tf:
        info = tarfile.TarInfo("adapter/adapter_config.json")
        info.size = len(payload)
        tf.addfile(info, io.BytesIO(payload))
    archive = bio.getvalue()
    prefix = Path("artifacts") / "candidate"
    (tmp_path / "artifacts").mkdir()
    cut = len(archive) // 2
    (tmp_path / f"{prefix}.part000").write_bytes(archive[:cut])
    (tmp_path / f"{prefix}.part001").write_bytes(archive[cut:])
    adapter = module.recover(
        tmp_path / "work", "unused", str(prefix), 2,
        hashlib.sha256(archive).hexdigest(), local_repo_root=tmp_path,
    )
    assert (adapter / "adapter_config.json").read_bytes() == payload


def test_model_load_placement_budgets_laptop_gpu_and_cpu(tmp_path):
    module = load_eval_module()
    placement = module.model_load_placement(3200, 20, tmp_path / "offload")
    assert placement["device_map"] == "auto"
    assert placement["max_memory"] == {0: "3200MiB", "cpu": "20GiB"}
    assert placement["offload_folder"] == str(tmp_path / "offload")
    assert (tmp_path / "offload").is_dir()


def test_resolve_adapter_accepts_local_directory(tmp_path):
    module = load_eval_module()
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text("{}", encoding="utf-8")
    (adapter / "adapter_model.safetensors").write_bytes(b"adapter")
    resolved = module.resolve_adapter(
        work=tmp_path / "work",
        adapter_dir=adapter,
        artifact_commit=None,
        part_prefix=None,
        part_count=None,
        adapter_sha256=None,
        local_repo_root=None,
    )
    assert resolved == adapter.resolve()



def test_load_holdout_can_use_local_jsonl(tmp_path):
    module = load_eval_module()
    holdout = tmp_path / "holdout.jsonl"
    holdout.write_text(
        '{"record_id":"x","dimension":"H07","prompt":"p","chosen":"c","rejected":"r"}\n',
        encoding="utf-8",
        newline="\n",
    )
    rows, digest = module.load_holdout_source(holdout)
    assert rows[0]["record_id"] == "x"
    assert len(digest) == 64



def test_runtime_policy_wraps_prompt_without_mutating_source_rows():
    module = load_eval_module()
    rows = [{
        "record_id": "h07-x",
        "dimension": "H07",
        "prompt": "A write call returned 202. Can I claim success?",
        "chosen": "No.",
        "rejected": "Yes.",
    }]
    original = [dict(rows[0])]
    policy = "Distinguish request acceptance from verified post-state."

    wrapped = module.apply_runtime_policy(rows, policy)

    assert rows == original
    assert wrapped[0]["chosen"] == "No."
    assert wrapped[0]["rejected"] == "Yes."
    assert wrapped[0]["prompt"].startswith("Runtime verification policy:\n")
    assert policy in wrapped[0]["prompt"]
    assert wrapped[0]["prompt"].endswith("Case:\nA write call returned 202. Can I claim success?")


def test_runtime_policy_rejects_blank_policy():
    module = load_eval_module()
    try:
        module.apply_runtime_policy([], "   ")
    except ValueError as exc:
        assert "runtime policy" in str(exc)
    else:
        raise AssertionError("blank runtime policy must be rejected")
