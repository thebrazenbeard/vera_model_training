import importlib
import importlib.util


def test_stage2_bank_manifest_requires_all_banks_and_20_dev_cases_each():
    spec = importlib.util.find_spec("training.stage2_bank_manifest")
    assert spec is not None, "Stage-2 bank manifest module is missing"
    s2 = importlib.import_module("training.stage2_bank_manifest")
    cases = []
    for bank in s2.REQUIRED_EVAL_BANKS:
        for i in range(20):
            cases.append({
                "case_id": f"{bank}-{i:03d}",
                "bank": bank,
                "prompt_hash": f"{len(cases)+1:064x}"[-64:],
                "grading_hash": f"{len(cases)+1001:064x}"[-64:],
                "custody": "protected-dev",
            })
    report = s2.build_stage2_bank_manifest(cases, minimum_cases_per_bank=20)
    assert report["status"] == "PASS"
    assert report["bank_count"] == 12
    assert report["case_count"] == 240
    assert min(report["cases_per_bank"].values()) == 20


def _full_bank_cases(s2):
    cases = []
    for bank in s2.REQUIRED_EVAL_BANKS:
        for i in range(20):
            cases.append({
                "case_id": f"{bank}-{i:03d}",
                "bank": bank,
                "prompt_hash": f"{len(cases)+1:064x}"[-64:],
                "grading_hash": f"{len(cases)+1001:064x}"[-64:],
                "custody": "protected-dev",
            })
    return cases


def test_stage2_bank_manifest_digest_is_order_independent():
    s2 = importlib.import_module("training.stage2_bank_manifest")
    cases = _full_bank_cases(s2)
    one = s2.build_stage2_bank_manifest(cases, minimum_cases_per_bank=20)
    two = s2.build_stage2_bank_manifest(list(reversed(cases)), minimum_cases_per_bank=20)
    assert one["status"] == "PASS"
    assert one["manifest_sha256"] == two["manifest_sha256"]
    assert len(one["manifest_sha256"]) == 64


def test_stage2_bank_manifest_rejects_duplicate_case_payload():
    s2 = importlib.import_module("training.stage2_bank_manifest")
    cases = _full_bank_cases(s2)
    duplicate = dict(cases[0])
    duplicate["case_id"] = "duplicate-payload"
    cases.append(duplicate)
    report = s2.build_stage2_bank_manifest(cases, minimum_cases_per_bank=20)
    assert report["status"] == "HOLD"
    assert "duplicate_case_payload" in report["reasons"]
