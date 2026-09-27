from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"successor"/"qwen35"/"qualification"/"run_final_qualification_v3.py"

def module():
    spec=importlib.util.spec_from_file_location("qwen35_final_runner",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

def test_behavioral_pass_contract_accepts_improvement():
    m=module()
    base={"accuracy":0.60,"mean_margin":0.01,"by_dimension":{"H01":{"accuracy":0.60}}}
    adapter={"accuracy":0.70,"mean_margin":0.03,"by_dimension":{"H01":{"accuracy":0.80}}}
    contract={"min_adapter_accuracy":0.60,"min_accuracy_delta":0.05,"min_mean_margin_delta":0.0,
              "max_per_dimension_accuracy_regression":0.20,"min_per_dimension_adapter_accuracy":0.40}
    ok,reasons=m.suite_pass("behavioral",base,adapter,contract)
    assert ok is True
    assert reasons == []

def test_behavioral_pass_contract_rejects_dimension_collapse():
    m=module()
    base={"accuracy":0.70,"mean_margin":0.02,"by_dimension":{"H01":{"accuracy":1.0}}}
    adapter={"accuracy":0.80,"mean_margin":0.03,"by_dimension":{"H01":{"accuracy":0.60}}}
    contract={"min_adapter_accuracy":0.60,"min_accuracy_delta":0.05,"min_mean_margin_delta":0.0,
              "max_per_dimension_accuracy_regression":0.20,"min_per_dimension_adapter_accuracy":0.40}
    ok,reasons=m.suite_pass("behavioral",base,adapter,contract)
    assert ok is False
    assert "dimension_regression:H01" in reasons