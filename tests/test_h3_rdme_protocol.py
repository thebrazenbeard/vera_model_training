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
    common_info = {
        "task_descriptor_fields": ["family_id"],
        "support_examples_available": 64,
        "feedback_rounds_available": 1,
    }
    return {
        "schema": "H3_RDME_MVE_PROTOCOL_V1",
        "status": "FROZEN_PREREGISTRATION",
        "arms": {
            "H0": {"information_exposure": dict(common_info)},
            "H1": {"information_exposure": dict(common_info)},
            "H2": {"information_exposure": dict(common_info)},
            "H3": {"information_exposure": dict(common_info)},
        },
        "controls": {
            "wrong_route": True,
            "no_route_base_only": True,
            "mixed_task": True,
            "adapter_off_restoration": True,
            "support_removal": True,
            "stale_reactivation_fresh_process": True,
        },
        "data_admission": {
            "protected_final_bank": False,
            "private_autobiographical": False,
        },
        "preregistration": {
            "family_definitions_frozen": True,
            "thresholds_frozen": True,
        },
        "accounting": {
            "include_context_memory_stops": True,
            "count_total_stored_parameters": True,
            "count_module_count": True,
            "count_routing_metadata": True,
        },
    }


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
