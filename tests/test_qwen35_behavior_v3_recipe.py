from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "train_behavior_v3.py"


def load_module():
    spec = importlib.util.spec_from_file_location("qwen35_v3", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeTokenizer:
    eos_token = "<eos>"

    def apply_chat_template(self, messages, **kwargs):
        return "<user>" + messages[0]["content"] + "<assistant>"


def test_v3_recipe_masks_prompt_and_reduces_update_rate():
    module = load_module()
    row = module.sft_row(FakeTokenizer(), "question", "answer")
    assert row == {"prompt": "<user>question<assistant>", "completion": "answer<eos>"}
    assert module.SFT_LR == 2e-5
    assert module.ORPO_LR == 1e-6


def test_v3_accepts_local_corpus_and_cpu_runtime(tmp_path):
    module = load_module()
    source = tmp_path / "rows.jsonl"
    source.write_text('{"x":1}\n{"x":2}\n', encoding="utf-8", newline="\n")
    rows, digest = module.read_jsonl_source(source)
    assert rows == [{"x": 1}, {"x": 2}]
    assert len(digest) == 64
    assert module.runtime_profile("cpu") == {
        "device_map": {"": "cpu"},
        "compute_dtype": "float32",
        "bf16": False,
        "tf32": False,
    }


def test_balanced_targeted_subset_is_deterministic_and_dimension_complete():
    module = load_module()
    rows = [
        {"source": "general", "dimension": "H01", "id": "g"},
        {"source": "targeted_v2", "dimension": "H02", "id": "b2"},
        {"source": "targeted_v2", "dimension": "H01", "id": "a2"},
        {"source": "targeted_v2", "dimension": "H01", "id": "a1"},
        {"source": "targeted_v2", "dimension": "H02", "id": "b1"},
    ]
    selected = module.balanced_targeted(rows, per_dimension=1)
    assert [r["id"] for r in selected] == ["a2", "b2"]


def test_experiment_schedule_separates_sft_only_from_both():
    module = load_module()
    assert module.training_schedule(smoke=False, experiment_steps=8, skip_orpo=True) == {
        "max_steps": 8, "gradient_accumulation_steps": 1, "run_orpo": False
    }
    assert module.training_schedule(smoke=True, experiment_steps=None, skip_orpo=False) == {
        "max_steps": 1, "gradient_accumulation_steps": 1, "run_orpo": True
    }


def test_balanced_targeted_accepts_v3_repair_source():
    module = load_module()
    rows = [
        {"source": "targeted_v3_repair", "dimension": "H03", "id": "a"},
        {"source": "targeted_v3_repair", "dimension": "H07", "id": "b"},
    ]
    selected = module.balanced_targeted(rows, per_dimension=1)
    assert [r["id"] for r in selected] == ["a", "b"]


def test_experiment_corpus_counts_allow_small_repair_sets():
    module = load_module()
    module.validate_corpus_counts(16, 16, experiment_steps=8)
    try:
        module.validate_corpus_counts(16, 16, experiment_steps=None)
    except RuntimeError:
        pass
    else:
        raise AssertionError("full training must still require the frozen 760/648 corpus sizes")


def test_v3_repair_corpus_is_balanced_and_dev_control_disjoint():
    import json
    from collections import Counter
    corpus = ROOT / "successor" / "qwen35" / "corpus"
    qual = ROOT / "successor" / "qwen35" / "qualification"
    pref = [json.loads(x) for x in (corpus / "history_behavior_targeted_v3_repair_preference.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    sft = [json.loads(x) for x in (corpus / "history_behavior_targeted_v3_repair_sft.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    dev = [json.loads(x) for x in (qual / "history_behavior_holdout_v1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    expected = {"H03": 4, "H07": 4, "H11": 4, "H15": 4}
    assert len(pref) == len(sft) == 16
    assert Counter(r["dimension"] for r in pref) == expected
    assert Counter(r["dimension"] for r in sft) == expected
    assert all(r["source"] == "targeted_v3_repair" for r in pref + sft)
    dev_prompts = {r["prompt"] for r in dev}
    assert not ({r["prompt"] for r in pref} & dev_prompts)
    assert not ({r["prompt"] for r in sft} & dev_prompts)
