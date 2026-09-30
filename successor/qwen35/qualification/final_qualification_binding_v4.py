from __future__ import annotations
import hashlib
import json
from pathlib import Path

EXPECTED_SUBJECT = "Vera-Qwen3.5-4B-Behavior-V1-v4-candidate-a"
AUTOMATED_SCHEMA = "QWEN35_FINAL_QUALIFICATION_AUTOMATED_RESULT_V4"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_blind_adapter_binding(spec_path: Path, automated_result_path: Path, adapter_dir: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    automated = json.loads(automated_result_path.read_text(encoding="utf-8"))
    reasons: list[str] = []
    if spec.get("subject") != EXPECTED_SUBJECT:
        reasons.append("spec_subject_mismatch")
    if automated.get("automated_pass") is not True:
        reasons.append("automated_gate_not_passed")
    if automated.get("schema") != AUTOMATED_SCHEMA:
        reasons.append("automated_schema_mismatch")
    if automated.get("subject") != EXPECTED_SUBJECT:
        reasons.append("automated_subject_mismatch")
    if automated.get("adapter_sha256") != spec.get("adapter", {}).get("archive_sha256"):
        reasons.append("automated_adapter_archive_mismatch")
    if automated.get("spec_sha256") != sha256(spec_path):
        reasons.append("automated_spec_mismatch")
    adapter_model = adapter_dir / "adapter_model.safetensors"
    try:
        local_adapter_model_sha = sha256(adapter_model)
    except OSError:
        local_adapter_model_sha = None
        reasons.append("adapter_model_unreadable")
    if local_adapter_model_sha is not None and automated.get("adapter_model_sha256") != local_adapter_model_sha:
        reasons.append("adapter_model_sha_mismatch")
    if reasons:
        raise RuntimeError(";".join(reasons))
    return {
        "subject": EXPECTED_SUBJECT,
        "adapter_sha256": spec["adapter"]["archive_sha256"],
        "adapter_model_sha256": local_adapter_model_sha,
        "automated_result_sha256": sha256(automated_result_path),
        "spec_sha256": sha256(spec_path),
    }
