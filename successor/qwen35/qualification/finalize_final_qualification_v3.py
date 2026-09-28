from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QUAL = ROOT / "successor" / "qwen35" / "qualification"
EXPECTED_SUBJECT = "OBJECTIVE_FIDELITY_V2_760_648"
AUTOMATED_SCHEMA = "QWEN35_FINAL_QUALIFICATION_AUTOMATED_RESULT_V3"
BLIND_SCHEMA = "QWEN35_FINAL_BLIND_REVIEW_RESULT_V3"
FINAL_SCHEMA = "QWEN35_FINAL_QUALIFICATION_RESULT_V3"
MANIFEST_SCHEMA = "QWEN35_FINAL_QUALIFICATION_MANIFEST_V3"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compose_final_result(spec: dict, automated: dict, blind: dict, *,
                         spec_sha256: str, automated_sha256: str,
                         blind_sha256: str, holdout_sha256: str,
                         holdout_rows: int) -> dict:
    reasons: list[str] = []
    expected_archive = spec.get("adapter", {}).get("archive_sha256")
    if spec.get("subject") != EXPECTED_SUBJECT:
        reasons.append("spec_subject_mismatch")
    if automated.get("schema") != AUTOMATED_SCHEMA:
        reasons.append("automated_schema_mismatch")
    if automated.get("subject") != EXPECTED_SUBJECT:
        reasons.append("automated_subject_mismatch")
    if automated.get("spec_sha256") != spec_sha256:
        reasons.append("automated_spec_mismatch")
    if automated.get("adapter_sha256") != expected_archive:
        reasons.append("automated_adapter_archive_mismatch")
    if blind.get("schema") != BLIND_SCHEMA:
        reasons.append("blind_schema_mismatch")
    if blind.get("subject") != EXPECTED_SUBJECT:
        reasons.append("blind_subject_mismatch")
    if blind.get("adapter_sha256") != expected_archive:
        reasons.append("blind_adapter_archive_mismatch")
    if blind.get("adapter_model_sha256") != automated.get("adapter_model_sha256"):
        reasons.append("blind_adapter_model_mismatch")
    if blind.get("automated_result_sha256") != automated_sha256:
        reasons.append("blind_automated_result_mismatch")
    if reasons:
        raise RuntimeError(";".join(reasons))
    return {
        "schema": FINAL_SCHEMA,
        "subject": EXPECTED_SUBJECT,
        "adapter_sha256": expected_archive,
        "adapter_model_sha256": automated["adapter_model_sha256"],
        "holdout_sha256": holdout_sha256,
        "holdout_rows": holdout_rows,
        "behavioral_pass": automated.get("behavioral_pass") is True,
        "retention_pass": automated.get("retention_pass") is True,
        "adversarial_proxy_pass": automated.get("adversarial_proxy_pass") is True,
        "independent_review_pass": blind.get("independent_review_pass") is True,
        "automated_result_sha256": automated_sha256,
        "blind_review_result_sha256": blind_sha256,
        "judge_binding_sha256": blind["judge_binding_sha256"],
        "spec_sha256": spec_sha256,
        "automated_pass": automated.get("automated_pass") is True,
        "blind_failure_reasons": blind.get("failure_reasons", []),
    }

def verify_review_chain(automated_sha256: str, blind: dict, packet_manifest: dict,
                        judgment_manifest: dict, blind_packet_sha256: str,
                        mapping_sha256: str, judgments_sha256: str,
                        selection_sha256: str, judge_binding_sha256: str) -> list[str]:
    reasons=[]
    if packet_manifest.get("automated_result_sha256")!=automated_sha256:
        reasons.append("packet_automated_result_mismatch")
    if packet_manifest.get("blind_packet_sha256")!=blind_packet_sha256:
        reasons.append("packet_blind_file_mismatch")
    if packet_manifest.get("mapping_sha256")!=mapping_sha256:
        reasons.append("packet_mapping_file_mismatch")
    if packet_manifest.get("selection_sha256")!=selection_sha256:
        reasons.append("packet_selection_mismatch")
    if blind.get("blind_packet_sha256")!=packet_manifest.get("blind_packet_sha256"):
        reasons.append("blind_packet_summary_mismatch")
    if blind.get("mapping_sha256")!=packet_manifest.get("mapping_sha256"):
        reasons.append("blind_mapping_summary_mismatch")
    if judgment_manifest.get("blind_packet_sha256")!=packet_manifest.get("blind_packet_sha256"):
        reasons.append("judgment_packet_mismatch")
    if judgment_manifest.get("judgments_sha256")!=judgments_sha256:
        reasons.append("judgment_file_mismatch")
    if blind.get("judgments_sha256")!=judgments_sha256:
        reasons.append("blind_judgment_summary_mismatch")
    if judgment_manifest.get("mapping_accessed") is not False:
        reasons.append("judge_mapping_boundary_failed")
    if judgment_manifest.get("judge_verified") is not True:
        reasons.append("judge_not_verified")
    if judgment_manifest.get("judge_binding_sha256")!=judge_binding_sha256:
        reasons.append("judgment_judge_binding_mismatch")
    if blind.get("judge_binding_sha256")!=judge_binding_sha256:
        reasons.append("blind_judge_binding_mismatch")
    return reasons

def load_gate_module():
    path = QUAL / "evaluate_behavior_v2.py"
    spec = importlib.util.spec_from_file_location("qwen35_final_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

def main(args) -> int:
    spec_path = QUAL / "FINAL_QUALIFICATION_V3_SPEC.json"
    holdout_path = QUAL / "final_holdout_v3.jsonl"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    automated = json.loads(args.automated_result.read_text(encoding="utf-8"))
    blind = json.loads(args.blind_result.read_text(encoding="utf-8"))
    packet_manifest=json.loads(args.packet_manifest.read_text(encoding="utf-8"))
    judgment_manifest=json.loads(args.judgments_manifest.read_text(encoding="utf-8"))
    expected_holdout = spec["suites"]["behavioral"]
    actual_holdout_sha = sha256(holdout_path)
    holdout_rows = len([x for x in holdout_path.read_text(encoding="utf-8").splitlines() if x.strip()])
    if actual_holdout_sha != expected_holdout["sha256"]:
        raise RuntimeError("behavioral_holdout_hash_mismatch")
    if holdout_rows != expected_holdout["rows"]:
        raise RuntimeError("behavioral_holdout_row_count_mismatch")
    automated_sha=sha256(args.automated_result)
    blind_sha=sha256(args.blind_result)
    blind_packet_sha=sha256(args.blind_packet)
    mapping_sha=sha256(args.mapping)
    judgments_sha=sha256(args.judgments)
    selection_sha=sha256(QUAL/"FINAL_BLIND_REVIEW_V3_SELECTION.json")
    judge_binding_sha=sha256(QUAL/"FINAL_JUDGE_V3_BINDING.json")
    review_reasons=verify_review_chain(
        automated_sha,blind,packet_manifest,judgment_manifest,
        blind_packet_sha,mapping_sha,judgments_sha,selection_sha,judge_binding_sha
    )
    if review_reasons:
        raise RuntimeError(";".join(review_reasons))
    result = compose_final_result(
        spec, automated, blind,
        spec_sha256=sha256(spec_path),
        automated_sha256=automated_sha,
        blind_sha256=blind_sha,
        holdout_sha256=actual_holdout_sha,
        holdout_rows=holdout_rows,
    )
    args.final_result.parent.mkdir(parents=True, exist_ok=True)
    args.final_result.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
    try:
        receipt_rel = args.final_result.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise RuntimeError("final result must be beneath repository root") from exc
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "subject": EXPECTED_SUBJECT,
        "adapter_sha256": spec["adapter"]["archive_sha256"],
        "holdout_path": "successor/qwen35/qualification/final_holdout_v3.jsonl",
        "holdout_sha256": actual_holdout_sha,
        "holdout_rows": holdout_rows,
        "evaluation_receipt_path": receipt_rel,
    }
    manifest_path = QUAL / "FINAL_QUALIFICATION_V3_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
    gate = load_gate_module()
    gate_result = gate.evaluate_final_qualification_gate(ROOT, manifest_path)
    gate_doc = {
        "schema": "QWEN35_FINAL_QUALIFICATION_GATE_RESULT_V3",
        "subject": EXPECTED_SUBJECT,
        "manifest_sha256": sha256(manifest_path),
        "final_result_sha256": sha256(args.final_result),
        "gate": gate_result,
    }
    args.gate_result.write_text(json.dumps(gate_doc, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(gate_doc, sort_keys=True))
    return 0 if gate_result.get("status") == "QUALIFIED" else 3

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--automated-result",type=Path,required=True)
    p.add_argument("--blind-result",type=Path,required=True)
    p.add_argument("--blind-packet",type=Path,required=True)
    p.add_argument("--packet-manifest",type=Path,required=True)
    p.add_argument("--mapping",type=Path,required=True)
    p.add_argument("--judgments",type=Path,required=True)
    p.add_argument("--judgments-manifest",type=Path,required=True)
    p.add_argument("--final-result",type=Path,required=True)
    p.add_argument("--gate-result",type=Path,required=True)
    raise SystemExit(main(p.parse_args()))
