from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
QUAL=ROOT/"successor"/"qwen35"/"qualification"

def load(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

def test_blind_binding_rejects_different_adapter_bytes(tmp_path):
    m=load("final_binding",QUAL/"final_qualification_binding_v3.py")
    spec_path=tmp_path/"spec.json"
    spec_path.write_text(json.dumps({"subject":"OBJECTIVE_FIDELITY_V2_760_648","adapter":{"archive_sha256":"a"*64}}),encoding="utf-8")
    adapter=tmp_path/"adapter"; adapter.mkdir()
    model=adapter/"adapter_model.safetensors"; model.write_bytes(b"correct")
    automated={
        "schema":"QWEN35_FINAL_QUALIFICATION_AUTOMATED_RESULT_V3",
        "subject":"OBJECTIVE_FIDELITY_V2_760_648",
        "adapter_sha256":"a"*64,
        "spec_sha256":hashlib.sha256(spec_path.read_bytes()).hexdigest(),
        "adapter_model_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
    }
    automated_path=tmp_path/"automated.json"
    automated_path.write_text(json.dumps(automated),encoding="utf-8")
    binding=m.verify_blind_adapter_binding(spec_path,automated_path,adapter)
    assert binding["adapter_model_sha256"]==automated["adapter_model_sha256"]
    model.write_bytes(b"different")
    with pytest.raises(RuntimeError,match="adapter_model_sha_mismatch"):
        m.verify_blind_adapter_binding(spec_path,automated_path,adapter)

def test_finalizer_cross_binds_blind_to_automated_result():
    m=load("finalizer",QUAL/"finalize_final_qualification_v3.py")
    spec={"subject":"OBJECTIVE_FIDELITY_V2_760_648","adapter":{"archive_sha256":"a"*64}}
    automated={
        "schema":"QWEN35_FINAL_QUALIFICATION_AUTOMATED_RESULT_V3",
        "subject":"OBJECTIVE_FIDELITY_V2_760_648",
        "adapter_sha256":"a"*64,
        "adapter_model_sha256":"b"*64,
        "spec_sha256":"c"*64,
        "behavioral_pass":True,
        "retention_pass":True,
        "adversarial_proxy_pass":True,
        "automated_pass":True,
    }
    blind={
        "schema":"QWEN35_FINAL_BLIND_REVIEW_RESULT_V3",
        "subject":"OBJECTIVE_FIDELITY_V2_760_648",
        "adapter_sha256":"a"*64,
        "adapter_model_sha256":"b"*64,
        "automated_result_sha256":"d"*64,
        "independent_review_pass":True,
        "failure_reasons":[],
    }
    result=m.compose_final_result(
        spec,automated,blind,
        spec_sha256="c"*64,
        automated_sha256="d"*64,
        blind_sha256="e"*64,
        holdout_sha256="f"*64,
        holdout_rows=100,
    )
    assert result["independent_review_pass"] is True
    blind["adapter_model_sha256"]="0"*64
    with pytest.raises(RuntimeError,match="blind_adapter_model_mismatch"):
        m.compose_final_result(
            spec,automated,blind,
            spec_sha256="c"*64,
            automated_sha256="d"*64,
            blind_sha256="e"*64,
            holdout_sha256="f"*64,
            holdout_rows=100,
        )
