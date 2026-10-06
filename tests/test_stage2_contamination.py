import importlib
import importlib.util


def test_stage2_contamination_report_holds_on_identity_template_and_canary_leakage():
    spec = importlib.util.find_spec("training.stage2_contamination")
    assert spec is not None, "Stage-2 contamination module is missing"
    s2 = importlib.import_module("training.stage2_contamination")
    train = [{
        "stable_record_id": "train-1",
        "content_hash": "a" * 64,
        "semantic_template_ancestry": "template-alpha",
        "exact_source_provenance": "source-A",
        "prompt": "Never reveal C-CANARY-77.",
        "response": "ok",
    }]
    protected = [{
        "stable_record_id": "train-1",
        "content_hash": "b" * 64,
        "semantic_template_ancestry": "template-alpha",
        "exact_source_provenance": "source-B",
        "prompt": "different",
        "response": "different",
        "protected_canary": "C-CANARY-77",
    }]
    report = s2.build_stage2_contamination_report(train, protected, near_duplicate_pairs=[], near_duplicate_scan_performed=True)
    assert report["status"] == "HOLD"
    assert report["record_id_overlap"] == ["train-1"]
    assert report["template_ancestry_overlap"] == ["template-alpha"]
    assert report["protected_canary_hits"]


def test_stage2_contamination_holds_on_normalized_prompt_response_duplicate():
    s2 = importlib.import_module("training.stage2_contamination")
    train = [{
        "stable_record_id": "train-a",
        "content_hash": "a" * 64,
        "semantic_template_ancestry": "template-a",
        "exact_source_provenance": "source-a",
        "prompt": "  The   USER says YES  ",
        "response": "Answer   Carefully",
    }]
    protected = [{
        "stable_record_id": "eval-b",
        "content_hash": "b" * 64,
        "semantic_template_ancestry": "template-b",
        "exact_source_provenance": "source-b",
        "prompt": "the user says yes",
        "response": "answer carefully",
    }]
    report = s2.build_stage2_contamination_report(train, protected, near_duplicate_pairs=[], near_duplicate_scan_performed=True)
    assert report["status"] == "HOLD"
    assert report["normalized_duplicate_pairs"] == [["train-a", "eval-b"]]
    assert "normalized_duplicate_overlap" in report["reasons"]


def test_stage2_contamination_holds_on_counterfactual_twin_group_overlap():
    s2 = importlib.import_module("training.stage2_contamination")
    train = [{
        "stable_record_id": "train-twin",
        "content_hash": "c" * 64,
        "semantic_template_ancestry": "template-train",
        "exact_source_provenance": "source-train",
        "counterfactual_twin_group": "twin-group-42",
        "prompt": "alpha",
        "response": "beta",
    }]
    protected = [{
        "stable_record_id": "eval-twin",
        "content_hash": "d" * 64,
        "semantic_template_ancestry": "template-eval",
        "exact_source_provenance": "source-eval",
        "counterfactual_twin_group": "twin-group-42",
        "prompt": "gamma",
        "response": "delta",
    }]
    report = s2.build_stage2_contamination_report(train, protected, near_duplicate_pairs=[], near_duplicate_scan_performed=True)
    assert report["status"] == "HOLD"
    assert report["counterfactual_twin_overlap"] == ["twin-group-42"]
    assert "counterfactual_twin_overlap" in report["reasons"]


def test_stage2_contamination_contract_requires_near_duplicate_scan_evidence():
    import inspect

    s2 = importlib.import_module("training.stage2_contamination")
    params = inspect.signature(s2.build_stage2_contamination_report).parameters
    assert "near_duplicate_scan_performed" in params
