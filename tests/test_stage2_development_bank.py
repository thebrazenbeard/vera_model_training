import importlib
import importlib.util


def _case(dev, bank, index):
    row = {
        "case_id": f"{bank}-{index:02d}",
        "bank": bank,
        "prompt": f"Unique synthetic development scenario {bank} number {index}; answer only from the stated evidence.",
        "source_provenance": {
            "source_id": f"synthetic:{bank}:{index}",
            "source_revision": "v1",
            "generation_method": "PLAN_DERIVED_SYNTHETIC",
        },
        "generator_actor_id": "Lane-A-generator",
        "construction_commit": "1" * 40,
        "capability_family": bank,
        "semantic_template_ancestry": f"{bank}-ancestry-{index % 4}",
        "privacy_class": "SYNTHETIC_NONPRIVATE",
        "mutable_stable_class": "STABLE_GENERAL_BEHAVIOR",
        "known_confounds": [],
        "intended_custody": "dev",
        "grading": {
            "must_assert": ["respect stated evidence"],
            "must_not_assert": ["invent unsupported state"],
            "acceptable_variants": ["equivalent concise answer"],
            "severity": "material",
            "critical_failures": ["contradicts explicit evidence"],
        },
        "semantic_review_state": "PENDING_INDEPENDENT_REVIEW",
    }
    row["content_hash"] = dev.compute_case_content_hash(row)
    return row


def test_dev_bank_materializes_12_banks_with_metadata_and_no_overlap():
    spec = importlib.util.find_spec("training.stage2_development_bank")
    assert spec is not None, "development bank module is missing"
    dev = importlib.import_module("training.stage2_development_bank")
    rows = [
        _case(dev, bank, i)
        for bank in dev.REQUIRED_EVAL_BANKS
        for i in range(20)
    ]
    report = dev.build_development_bank_manifest(
        rows,
        training_prompt_hashes=set(),
        protected_prompt_hashes=set(),
        minimum_cases_per_bank=20,
        minimum_ancestries_per_bank=4,
    )
    assert report["structural_status"] == "PASS"
    assert report["status"] == "MATERIALIZED_PENDING_INDEPENDENT_REVIEW"
    assert report["case_count"] == 240
    assert report["exact_training_overlap_count"] == 0
    assert report["protected_overlap_count"] == 0
    assert report["under_ancestry_banks"] == []


def test_dev_bank_holds_on_training_overlap_or_duplicate_case():
    dev = importlib.import_module("training.stage2_development_bank")
    row = _case(dev, dev.REQUIRED_EVAL_BANKS[0], 0)
    prompt_hash = dev.normalized_prompt_hash(row["prompt"])
    rows = [row, dict(row)]
    report = dev.build_development_bank_manifest(
        rows,
        training_prompt_hashes={prompt_hash},
        protected_prompt_hashes=set(),
        minimum_cases_per_bank=1,
        minimum_ancestries_per_bank=1,
    )
    assert report["structural_status"] == "HOLD"
    assert "duplicate_case_id" in report["reasons"]
    assert "training_prompt_overlap" in report["reasons"]
