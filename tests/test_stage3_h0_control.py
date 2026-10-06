import importlib


def _valid_kwargs(h0):
    return {
        "controls": list(h0.REQUIRED_H0_CONTROLS),
        "context_enabled": True,
        "governed_external_memory_enabled": True,
        "weight_updates_authorized": False,
        "frozen_base_verified": True,
        "additional_mutable_state_enabled": False,
    }


def test_h0_control_contract_freezes_base_and_allows_only_context_and_governed_memory():
    h0 = importlib.import_module("training.stage3_h0_control")
    contract = h0.build_h0_control_contract(**_valid_kwargs(h0))
    assert contract["status"] == "PASS"
    assert contract["weight_updates_authorized"] is False
    assert contract["frozen_base_verified"] is True
    assert contract["additional_mutable_state_enabled"] is False
    assert contract["missing_controls"] == []
    assert contract["unknown_controls"] == []


def test_h0_control_contract_holds_on_weight_mutation_unfrozen_base_or_unknown_state():
    h0 = importlib.import_module("training.stage3_h0_control")
    cases = [
        ({"weight_updates_authorized": True}, "h0_weight_updates_forbidden"),
        ({"frozen_base_verified": False}, "h0_frozen_base_not_verified"),
        ({"additional_mutable_state_enabled": True}, "h0_unapproved_mutable_state_enabled"),
        ({"controls": list(h0.REQUIRED_H0_CONTROLS) + ["hidden_adapter"]}, "unknown_h0_control"),
    ]
    for override, reason in cases:
        kwargs = _valid_kwargs(h0)
        kwargs.update(override)
        contract = h0.build_h0_control_contract(**kwargs)
        assert contract["status"] == "HOLD"
        assert reason in contract["reasons"]
