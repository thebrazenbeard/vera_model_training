from __future__ import annotations
import importlib.util,hashlib,json,pathlib,pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
Q=ROOT/"successor/qwen35/qualification"
SUBJECT="Vera-Qwen3.5-4B-Behavior-V1-v4-candidate-a"
def module(name):
 p=Q/(name+"_v4.py")
 spec=importlib.util.spec_from_file_location("v4_"+name,p)
 m=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(m)
 return m
def test_v4_runner_uses_original_automated_thresholds():
 runner=module("run_final_qualification")
 older=json.loads((Q/"FINAL_QUALIFICATION_V3_SPEC.json").read_text(encoding="utf-8"))
 current=json.loads((Q/"FINAL_QUALIFICATION_V4_SPEC.json").read_text(encoding="utf-8"))
 assert current["pass_contract"]==older["pass_contract"]
 assert callable(runner.suite_pass)
def test_v4_blind_selection_is_precommitted_one_per_dimension():
 spec=json.loads((Q/"FINAL_QUALIFICATION_V4_SPEC.json").read_text(encoding="utf-8"))
 selection=json.loads((Q/"FINAL_BLIND_REVIEW_V4_SELECTION.json").read_text(encoding="utf-8"))
 assert selection["subject"]==SUBJECT
 assert selection["behavioral_holdout_sha256"]==spec["suites"]["behavioral"]["sha256"]
 assert len(selection["record_ids"])==len(set(selection["record_ids"]))==20
 assert set(x.split("_")[1] for x in selection["record_ids"])=={f"H{i:02d}" for i in range(1,21)}
def test_v4_blind_rubrics_do_not_expose_chosen_or_rejected():
 selection=json.loads((Q/"FINAL_BLIND_REVIEW_V4_SELECTION.json").read_text(encoding="utf-8"))
 rubrics=json.loads((Q/"FINAL_BLIND_REVIEW_V4_RUBRICS.json").read_text(encoding="utf-8"))
 assert rubrics["schema"]=="QWEN35_FINAL_BLIND_CASE_RUBRICS_V4"
 assert set(rubrics["cases"])==set(selection["record_ids"])
 for record_id,rubric in rubrics["cases"].items():
  assert rubric["required_propositions"] and rubric["forbidden_propositions"]
  assert not {"chosen","rejected","condition","response"}&set(rubric)
def test_v4_adapter_binding_fails_closed_on_wrong_model():
 binding=module("final_qualification_binding")
 assert binding.EXPECTED_SUBJECT==SUBJECT
 with pytest.raises((RuntimeError,FileNotFoundError)):
  binding.verify_blind_adapter_binding(Q/"FINAL_QUALIFICATION_V4_SPEC.json",Q/"missing_automated_result.json",pathlib.Path("."))
def test_v4_judge_render_contains_case_specific_rubric():
 judge=module("judge_final_blind_review")
 class T:
  def apply_chat_template(self,messages,**kwargs):return messages[0]["content"]
 item={"dimension":"H07","dimension_target":"effect verification","known_failure_modes":"unverified success","prompt":"Did the crate arrive?","response":"It is still unverified.","required_propositions":["Distinguish request from delivery"],"forbidden_propositions":["Assume delivered from acceptance"]}
 result=judge.render(T(),item)
 assert "Distinguish request from delivery" in result
 assert "Assume delivered from acceptance" in result
 assert "candidate response" in result.lower()

def test_v4_runner_exposes_adapter_file_hash_preflight(tmp_path):
    runner=module("run_final_qualification")
    (tmp_path/"adapter_model.safetensors").write_bytes(b"tampered-model")
    (tmp_path/"adapter_config.json").write_bytes(b"config")
    spec={"adapter":{"adapter_model_sha256":"0"*64,"adapter_config_sha256":"1"*64}}
    with pytest.raises(RuntimeError,match="adapter"):
        runner.verify_adapter_files(tmp_path,spec)
def test_v4_blind_binding_rejects_failed_automated_gate(tmp_path):
    binding=module("final_qualification_binding")
    spec_path=Q/"FINAL_QUALIFICATION_V4_SPEC.json"
    s=json.loads(spec_path.read_text(encoding="utf-8"))
    bad={"schema":"QWEN35_FINAL_QUALIFICATION_AUTOMATED_RESULT_V4","subject":SUBJECT,"automated_pass":False,"adapter_sha256":s["adapter"]["archive_sha256"],"spec_sha256":hashlib.sha256(spec_path.read_bytes()).hexdigest(),"adapter_model_sha256":"0"*64}
    path=tmp_path/"automated.json";path.write_text(json.dumps(bad),encoding="utf-8")
    with pytest.raises(RuntimeError,match="automated_gate_not_passed"):
        binding.verify_blind_adapter_binding(spec_path,path,tmp_path)
