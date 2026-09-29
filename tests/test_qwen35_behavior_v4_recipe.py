from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "successor" / "qwen35"
SCRIPT = Q / "train_behavior_v4.py"
CORPUS = Q / "corpus" / "vera_qwen35_behavior_v4_sft.jsonl"
MANIFEST = Q / "corpus" / "vera_qwen35_behavior_v4_manifest.json"


def load_module():
    spec = importlib.util.spec_from_file_location("qwen35_v4_train", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeTokenizer:
    eos_token = "<eos>"
    pad_token_id = 0

    def apply_chat_template(self, messages, **kwargs):
        return "<user>" + messages[0]["content"] + "<assistant>"

    def __call__(self, text, **kwargs):
        return {"input_ids": text.split()}


def test_v4_trainer_is_fresh_base_sft_only_rank4_all_linear():
    m = load_module()
    assert m.BASE_REPO == "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
    assert m.BASE_REV == "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
    assert m.LORA_R == 4
    assert m.LORA_ALPHA == 16
    assert m.SFT_LR == 2e-5
    profile = m.hardware_profile("lappy-rtx3050-4gb")
    assert profile == {"max_length": 512, "overflow": "error", "target_vram_mib": 4096, "optimizer": "adamw_torch"}
    source = SCRIPT.read_text(encoding="utf-8")
    assert "ORPO" not in source
    assert "pref_source" not in source
    assert "PeftModel.from_pretrained" not in source
    assert 'target_modules="all-linear"' in source


def test_v4_sft_row_masks_prompt_and_appends_eos():
    m = load_module()
    assert m.sft_row(FakeTokenizer(), "question", "answer") == {"prompt": "<user>question<assistant>", "completion": "answer<eos>"}


def test_v4_trainer_refuses_corpus_hash_drift(tmp_path):
    m = load_module()
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text('{"prompt":"p","response":"r"}\n', encoding="utf-8", newline="\n")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"rows": 1, "corpus_sha256": "0" * 64}), encoding="utf-8", newline="\n")
    try:
        m.validate_frozen_corpus(corpus, manifest)
    except RuntimeError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("trainer must fail closed on corpus hash drift")


def test_v4_frozen_corpus_validates_and_receipt_marks_no_parent_adapter():
    m = load_module()
    rows, digest = m.validate_frozen_corpus(CORPUS, MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(rows) == 512
    assert digest == manifest["corpus_sha256"] == hashlib.sha256(CORPUS.read_bytes()).hexdigest()
    receipt = m.base_receipt(rows=len(rows), corpus_sha256=digest, hardware_profile_name="lappy-rtx3050-4gb")
    assert receipt["parent_adapter"] is None
    assert receipt["training_method"] == "QLORA_SFT_ONLY"
    assert receipt["sft_rows"] == 512
    assert receipt["corpus_sha256"] == digest
    assert receipt["lora"] == {"r": 4, "alpha": 16, "target_modules": "all-linear"}