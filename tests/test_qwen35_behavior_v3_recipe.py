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

    def __call__(self, text, **kwargs):
        return {"input_ids": text.split()}


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
        "max_steps": 8, "gradient_accumulation_steps": 1, "run_orpo": False, "max_length": 1024, "optimizer": "paged_adamw_8bit"
    }
    assert module.training_schedule(smoke=True, experiment_steps=None, skip_orpo=False) == {
        "max_steps": 1, "gradient_accumulation_steps": 1, "run_orpo": True, "max_length": 1024, "optimizer": "paged_adamw_8bit"
    }
    assert module.training_schedule(
        smoke=False,
        experiment_steps=8,
        skip_orpo=False,
        hardware_profile_name="lappy-rtx3050-4gb",
    )["max_length"] == 512
    assert module.training_schedule(
        smoke=False,
        experiment_steps=8,
        skip_orpo=False,
        hardware_profile_name="lappy-rtx3050-4gb",
    )["optimizer"] == "adamw_torch"


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


def test_lappy_4gb_profile_enforces_shorter_sequence_budget():
    module = load_module()
    assert module.hardware_profile("generic")["max_length"] == 1024
    assert module.hardware_profile("lappy-rtx3050-4gb") == {
        "max_length": 512,
        "overflow": "error",
        "target_vram_mib": 4096,
        "optimizer": "adamw_torch",
    }


def test_token_budget_preflight_rejects_oversized_rows_instead_of_truncating():
    module = load_module()
    tok = FakeTokenizer()
    short = {"prompt": "one two", "completion": "three four"}
    too_long = {"prompt": " ".join(["p"] * 511), "completion": "x y z"}

    report = module.validate_token_budget(tok, [short], [], max_length=512)
    assert report["sft"]["max_tokens"] == 3
    assert report["sft"]["over_budget"] == 0

    try:
        module.validate_token_budget(tok, [too_long], [], max_length=512)
    except RuntimeError as exc:
        assert "token budget exceeded" in str(exc)
    else:
        raise AssertionError("local profile must fail before trainer-side truncation")



def test_h07_discrimination_split_is_frozen_diverse_and_disjoint():
    import json
    from collections import Counter
    corpus = ROOT / "successor" / "qwen35" / "corpus"
    qual = ROOT / "successor" / "qwen35" / "qualification"

    train_pref = [json.loads(x) for x in (corpus / "h07_architecture_discrimination_v1_train_preference.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    train_sft = [json.loads(x) for x in (corpus / "h07_architecture_discrimination_v1_train_sft.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    dev = [json.loads(x) for x in (qual / "h07_architecture_discrimination_v1_dev.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    legacy_dev = [json.loads(x) for x in (qual / "history_behavior_holdout_v1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

    assert len(train_pref) == len(train_sft) == 16
    assert len(dev) == 8
    assert all(r["dimension"] == "H07" for r in train_pref + train_sft + dev)
    assert len({r["mechanism"] for r in train_pref}) >= 12
    assert Counter(r["verification_class"] for r in train_pref)["readback_required"] >= 8
    assert Counter(r["verification_class"] for r in train_pref)["receipt_sufficient"] >= 2
    assert Counter(r["verification_class"] for r in train_pref)["ambiguous_effect"] >= 2

    train_prompts = {r["prompt"] for r in train_pref} | {r["prompt"] for r in train_sft}
    dev_prompts = {r["prompt"] for r in dev}
    legacy_prompts = {r["prompt"] for r in legacy_dev}
    assert not (train_prompts & dev_prompts)
    assert not (train_prompts & legacy_prompts)
    assert not (dev_prompts & legacy_prompts)



def test_h07_v2_rule_transfer_split_has_family_holdout_and_rubrics():
    import json
    from collections import Counter
    corpus = ROOT / "successor" / "qwen35" / "corpus"
    qual = ROOT / "successor" / "qwen35" / "qualification"

    train = [json.loads(x) for x in (corpus / "h07_rule_transfer_v2_train_sft.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    dev = [json.loads(x) for x in (qual / "h07_rule_transfer_v2_dev.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

    assert len(train) == 96
    assert len(dev) == 32
    assert len({r["family"] for r in train}) == 12
    assert len({r["family"] for r in dev}) == 4
    assert not ({r["family"] for r in train} & {r["family"] for r in dev})
    assert all(r["dimension"] == "H07" for r in train + dev)
    assert all("H07 EFFECT-VERIFICATION POLICY V2" in r["prompt"] for r in train)

    for rows in (train, dev):
        counts = Counter(r["verification_class"] for r in rows)
        assert counts["readback_required"] == len(rows) * 3 // 8
        assert counts["receipt_sufficient"] == len(rows) * 3 // 8
        assert counts["ambiguous_effect"] == len(rows) * 2 // 8

    assert all(r["expected_action"] in {
        "VERIFY_POST_STATE", "RECEIPT_SUFFICIENT", "RECONCILE_BEFORE_RETRY"
    } for r in dev)
    assert all(r["rubric"]["required_concepts"] for r in dev)
    assert all(r["rubric"]["forbidden_claims"] for r in dev)
    assert all(r["rubric"]["expected_claim_scope"] for r in dev)
    assert all(len(r["rubric"]["required_concepts"]) >= 2 for r in dev)


def test_h07_v2_train_and_dev_prompts_are_unique_and_v1_disjoint():
    import json
    corpus = ROOT / "successor" / "qwen35" / "corpus"
    qual = ROOT / "successor" / "qwen35" / "qualification"

    train = [json.loads(x) for x in (corpus / "h07_rule_transfer_v2_train_sft.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    dev = [json.loads(x) for x in (qual / "h07_rule_transfer_v2_dev.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    v1_train = [json.loads(x) for x in (corpus / "h07_architecture_discrimination_v1_train_sft.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    v1_dev = [json.loads(x) for x in (qual / "h07_architecture_discrimination_v1_dev.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

    train_prompts = {r["prompt"] for r in train}
    dev_prompts = {r["prompt"] for r in dev}
    assert len(train_prompts) == len(train)
    assert len(dev_prompts) == len(dev)
    assert not (train_prompts & dev_prompts)
    assert not (train_prompts & {r["prompt"] for r in v1_train})
    assert not (dev_prompts & {r["prompt"] for r in v1_dev})



def test_sft_only_experiment_allows_missing_preference_corpus():
    module = load_module()
    module.validate_corpus_counts(96, 0, experiment_steps=96, run_orpo=False)
    try:
        module.validate_corpus_counts(96, 0, experiment_steps=96, run_orpo=True)
    except RuntimeError as exc:
        assert "preference" in str(exc)
    else:
        raise AssertionError("ORPO experiment must still require preference rows")
