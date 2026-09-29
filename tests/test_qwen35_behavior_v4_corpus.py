from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "successor" / "qwen35"
SCRIPT = Q / "build_behavior_corpus_v4.py"
CORPUS = Q / "corpus" / "vera_qwen35_behavior_v4_sft.jsonl"
MANIFEST = Q / "corpus" / "vera_qwen35_behavior_v4_manifest.json"
RECIPE = Q / "V4_TRAINING_RECIPE_V1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("qwen35_v4_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeTokenizer:
    def apply_chat_template(self, messages, **kwargs):
        return " ".join(m["content"] for m in messages)

    def __call__(self, text, **kwargs):
        return {"input_ids": text.split()}


def test_overlap_screen_rejects_exact_and_near_paraphrase():
    m = load_module()
    blocked = ["verify the authoritative setting before claiming the effect succeeded"]
    assert m.screen_overlap(blocked[0], blocked, threshold=0.62) is False
    assert m.screen_overlap("verify the authoritative setting before claiming the effect succeeded now", blocked, threshold=0.62) is False
    assert m.screen_overlap("summarize this unrelated astronomy note", blocked, threshold=0.62) is True


def test_targeted_selection_respects_dimension_quotas_without_substitution():
    m = load_module()
    rows = [
        {"dimension": "H01", "prompt": "a1", "response": "r1", "source": "a", "priority": 0},
        {"dimension": "H01", "prompt": "a2", "response": "r2", "source": "a", "priority": 0},
        {"dimension": "H02", "prompt": "b1", "response": "r3", "source": "a", "priority": 0},
        {"dimension": "H03", "prompt": "c1", "response": "r4", "source": "a", "priority": 0},
    ]
    selected = m.select_targeted(rows, {"H01": 2, "H02": 1})
    assert Counter(r["dimension"] for r in selected) == {"H01": 2, "H02": 1}
    try:
        m.select_targeted(rows, {"H01": 2, "H02": 2})
    except RuntimeError as exc:
        assert "H02" in str(exc)
    else:
        raise AssertionError("dimension shortage must fail instead of substituting another dimension")


def test_build_is_deterministic_for_same_inputs():
    m = load_module()
    recipe = {"corpus": {"dimension_quotas": {"H01": 1}, "targeted_rows": 1, "general_rehearsal_rows": 1, "total_sft_rows": 2}}
    targeted = [{"dimension": "H01", "prompt": "target prompt", "response": "target response", "source": "targeted", "priority": 0}]
    general = [{"prompt": "general prompt", "response": "general response", "source": "smoltalk2:test"}]
    a, ma = m.build_v4_corpus(recipe, targeted, general, FakeTokenizer(), blocked_texts=[])
    b, mb = m.build_v4_corpus(recipe, list(reversed(targeted)), list(reversed(general)), FakeTokenizer(), blocked_texts=[])
    assert a == b
    assert ma["corpus_sha256"] == mb["corpus_sha256"]


def test_frozen_v4_corpus_contract():
    rows = [json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert len(rows) == 512
    targeted = [r for r in rows if r["source_class"] == "targeted"]
    general = [r for r in rows if r["source_class"] == "general_rehearsal"]
    assert len(targeted) == 268
    assert len(general) == 244
    assert Counter(r["dimension"] for r in targeted) == recipe["corpus"]["dimension_quotas"]
    assert all(r["source"].startswith("smoltalk2:") or r["source"] == "ultrafeedback_train_sft" for r in general)
    assert all("thebrazenbeard" not in r["prompt"].lower() and not __import__("re").search(r"\\bvera\\b", r["prompt"].lower()) for r in targeted)
    assert all(not any(f"H{i:02d}" in r["prompt"] for i in range(1, 21)) for r in targeted)
    raw = CORPUS.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == manifest["corpus_sha256"]
    assert manifest["rows"] == 512
    assert manifest["targeted_rows"] == 268
    assert manifest["general_rehearsal_rows"] == 244
    assert manifest["token_budget"]["max_tokens"] <= 512
    assert manifest["overlap_screen"]["failures"] == 0

def test_marker_screen_does_not_reject_words_that_only_contain_vera_letters():
    m = load_module()
    row = {"dimension": "H13", "prompt": "Several measurements are unusual today.", "response": "Check current evidence.", "source": "x", "priority": 0}
    accepted, stats = m._filter_rows([row], FakeTokenizer(), [], max_length=512, reject_taxonomy=True)
    assert len(accepted) == 1
    assert stats.get("marker", 0) == 0

def test_h07_rule_transfer_rows_cover_effect_classes():
    rows = [json.loads(x) for x in CORPUS.read_text(encoding="utf-8").splitlines() if x.strip()]
    h07 = [r for r in rows if r.get("dimension") == "H07"]
    rule = [r for r in h07 if r["source"] == "h07_rule_transfer_v2"]
    assert len(rule) >= 4
    assert {r.get("verification_class") for r in rule} >= {"readback_required", "receipt_sufficient", "ambiguous_effect"}

def test_internal_dedupe_can_use_case_text_instead_of_shared_rule_prefix():
    m = load_module()
    shared = " ".join(f"r{i}" for i in range(50)) + " "
    rows = [
        {"dimension": "H07", "prompt": shared + "Case: a remote flag write returned a generic success code.", "dedupe_text": "remote flag generic success needs authoritative readback", "response": "verify it", "source": "rule", "priority": 0},
        {"dimension": "H07", "prompt": shared + "Case: a queued job receipt binds an immutable committed digest.", "dedupe_text": "queued job immutable committed digest is receipt sufficient", "response": "receipt is sufficient", "source": "rule", "priority": 0},
    ]
    accepted, stats = m._filter_rows(rows, FakeTokenizer(), [], max_length=512, reject_taxonomy=False)
    assert len(accepted) == 2
    assert stats.get("internal_near_duplicate", 0) == 0
