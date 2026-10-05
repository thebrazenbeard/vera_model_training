from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "training" / "h3_rdme_protocol.py"
PROTOCOL_PATH = ROOT / "training" / "H3_RDME_MVE_V1.json"


def _load_module():
    assert MODULE_PATH.exists(), "RDME protocol validator module must exist"
    spec = importlib.util.spec_from_file_location("h3_rdme_protocol", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_protocol():
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def test_validator_public_seam_exists():
    module = _load_module()
    assert hasattr(module, "validate_protocol"), "validator must expose validate_protocol(protocol)"


def test_rejects_routing_information_asymmetry():
    module = _load_module()
    protocol = _valid_protocol()
    protocol["arms"]["H3"]["information_exposure"]["task_descriptor_fields"] = [
        "family_id",
        "oracle_rule_id",
    ]
    errors = module.validate_protocol(protocol)
    assert any("routing information parity" in error.lower() for error in errors)


def test_rejects_missing_required_rdme_control():
    module = _load_module()
    protocol = _valid_protocol()
    protocol["controls"]["wrong_route"] = False
    errors = module.validate_protocol(protocol)
    assert any("wrong_route" in error for error in errors)


def test_rejects_protected_or_private_training_material():
    module = _load_module()
    protocol = _valid_protocol()
    protocol["data_admission"]["protected_final_bank"] = True
    protocol["data_admission"]["private_autobiographical"] = True
    errors = module.validate_protocol(protocol)
    assert any("protected_final_bank" in error for error in errors)
    assert any("private_autobiographical" in error for error in errors)


def test_rejects_mutable_preregistration():
    module = _load_module()
    protocol = _valid_protocol()
    protocol["preregistration"]["thresholds_frozen"] = False
    errors = module.validate_protocol(protocol)
    assert any("thresholds_frozen" in error for error in errors)


def test_rejects_incomplete_cost_accounting():
    module = _load_module()
    protocol = _valid_protocol()
    protocol["accounting"]["include_context_memory_stops"] = False
    errors = module.validate_protocol(protocol)
    assert any("include_context_memory_stops" in error for error in errors)


def test_valid_protocol_has_no_errors():
    module = _load_module()
    assert module.validate_protocol(_valid_protocol()) == []


def test_frozen_protocol_file_is_valid():
    module = _load_module()
    assert PROTOCOL_PATH.exists(), "frozen RDME preregistration must exist"
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert module.validate_protocol(protocol) == []


def test_rejects_unsafe_authority_and_nonfrozen_status():
    module = _load_module()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol["status"] = "DRAFT"
    protocol["authority"]["protected_final_bank_access_authorized"] = True
    protocol["authority"]["merge_main_authorized"] = True
    errors = module.validate_protocol(protocol)
    assert any("status" in error.lower() for error in errors)
    assert any("protected_final_bank" in error for error in errors)
    assert any("merge_main" in error for error in errors)


def test_rejects_non_synthetic_mutable_or_current_factual_data():
    module = _load_module()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol["data_admission"]["development_synthetic_only"] = False
    protocol["data_admission"]["mutable_project_state"] = True
    protocol["data_admission"]["current_factual_knowledge"] = True
    errors = module.validate_protocol(protocol)
    assert any("development_synthetic_only" in error for error in errors)
    assert any("mutable_project_state" in error for error in errors)
    assert any("current_factual_knowledge" in error for error in errors)


def test_rejects_incomplete_isolation_and_resource_accounting():
    module = _load_module()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol["isolation"]["fresh_process_required"] = False
    protocol["isolation"]["stale_adapter_cache_probe_required"] = False
    protocol["accounting"]["count_peak_ram_vram"] = False
    protocol["accounting"]["count_wall_time"] = False
    errors = module.validate_protocol(protocol)
    assert any("fresh_process_required" in error for error in errors)
    assert any("stale_adapter_cache_probe_required" in error for error in errors)
    assert any("count_peak_ram_vram" in error for error in errors)
    assert any("count_wall_time" in error for error in errors)


def test_rejects_h3_router_or_sequence_drift():
    module = _load_module()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol["arms"]["H3"]["router"] = "LEARNED_UNFROZEN"
    protocol["arms"]["H3"]["active_adapter_limit"] = 2
    protocol["sequence"].remove("TEST_WRONG_ROUTE")
    errors = module.validate_protocol(protocol)
    assert any("router" in error.lower() for error in errors)
    assert any("active_adapter_limit" in error for error in errors)
    assert any("TEST_WRONG_ROUTE" in error for error in errors)


def test_rejects_preregistration_mutation_escape_hatches():
    module = _load_module()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol["preregistration"]["post_result_threshold_edits_forbidden"] = False
    protocol["preregistration"]["new_mechanism_after_feedback_requires_new_subject"] = False
    errors = module.validate_protocol(protocol)
    assert any("post_result_threshold_edits_forbidden" in error for error in errors)
    assert any("new_mechanism_after_feedback_requires_new_subject" in error for error in errors)
