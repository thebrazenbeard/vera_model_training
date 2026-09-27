from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "qualification" / "evaluate_behavior_v2.py"


def load_eval_module():
    spec = importlib.util.spec_from_file_location("qwen35_eval_final_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_final_qualification_gate_blocks_without_fresh_final_manifest():
    module = load_eval_module()

    assert hasattr(module, "evaluate_final_qualification_gate")
    result = module.evaluate_final_qualification_gate(ROOT)

    assert result["status"] == "BLOCKED"
    assert result["subject"] == "OBJECTIVE_FIDELITY_V2_760_648"
    assert result["adapter_sha256"] == "1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69"
    assert "fresh_final_manifest_missing" in result["reasons"]


def test_final_qualification_gate_rejects_development_holdout(tmp_path):
    module = load_eval_module()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        """{
  "schema": "QWEN35_FINAL_QUALIFICATION_MANIFEST_V3",
  "subject": "OBJECTIVE_FIDELITY_V2_760_648",
  "adapter_sha256": "1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69",
  "holdout_path": "successor/qwen35/qualification/history_behavior_holdout_v1.jsonl"
}""",
        encoding="utf-8",
    )

    result = module.evaluate_final_qualification_gate(ROOT, manifest)

    assert result["status"] == "BLOCKED"
    assert "development_holdout_forbidden" in result["reasons"]


def _write_fresh_final_holdout(path):
    rows = []
    for dimension in range(1, 21):
        for case in range(5):
            rows.append({
                "record_id": f"final-H{dimension:02d}-{case}",
                "dimension": f"H{dimension:02d}",
                "prompt": f"fresh final qualification prompt H{dimension:02d} case {case}",
                "chosen": "bounded verified answer",
                "rejected": "unsupported proxy claim",
            })
    path.write_text(
        "".join(__import__("json").dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return rows


def test_final_qualification_gate_requires_evaluation_receipt(tmp_path):
    import hashlib
    import json

    module = load_eval_module()
    holdout = tmp_path / "fresh-final.jsonl"
    rows = _write_fresh_final_holdout(holdout)
    holdout_sha = hashlib.sha256(holdout.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({
            "schema": "QWEN35_FINAL_QUALIFICATION_MANIFEST_V3",
            "subject": "OBJECTIVE_FIDELITY_V2_760_648",
            "adapter_sha256": "1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69",
            "holdout_path": str(holdout),
            "holdout_sha256": holdout_sha,
            "holdout_rows": len(rows),
        }),
        encoding="utf-8",
    )

    result = module.evaluate_final_qualification_gate(ROOT, manifest)

    assert result["status"] == "BLOCKED"
    assert "final_evaluation_receipt_missing" in result["reasons"]
