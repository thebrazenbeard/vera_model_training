ARM_NAMES = ("H0", "H1", "H2", "H3")
REQUIRED_CONTROLS = (
    "wrong_route",
    "no_route_base_only",
    "mixed_task",
    "adapter_off_restoration",
    "support_removal",
    "stale_reactivation_fresh_process",
)
PROHIBITED_DATA_FLAGS = (
    "protected_final_bank",
    "private_autobiographical",
)
REQUIRED_PREREGISTRATION_FLAGS = (
    "family_definitions_frozen",
    "thresholds_frozen",
)
REQUIRED_ACCOUNTING_FLAGS = (
    "include_context_memory_stops",
    "count_total_stored_parameters",
    "count_module_count",
    "count_routing_metadata",
)


def validate_protocol(protocol):
    errors = []
    arms = protocol.get("arms", {})
    exposures = [arms.get(name, {}).get("information_exposure") for name in ARM_NAMES]

    if any(exposure is None for exposure in exposures):
        errors.append("routing information parity: every H0/H1/H2/H3 arm must declare information_exposure")
    elif any(exposure != exposures[0] for exposure in exposures[1:]):
        errors.append("routing information parity violated across H0/H1/H2/H3")

    controls = protocol.get("controls", {})
    for name in REQUIRED_CONTROLS:
        if controls.get(name) is not True:
            errors.append(f"required RDME control missing or disabled: {name}")

    data_admission = protocol.get("data_admission", {})
    for name in PROHIBITED_DATA_FLAGS:
        if data_admission.get(name) is not False:
            errors.append(f"prohibited RDME data admission: {name} must be false")

    preregistration = protocol.get("preregistration", {})
    for name in REQUIRED_PREREGISTRATION_FLAGS:
        if preregistration.get(name) is not True:
            errors.append(f"RDME preregistration must be frozen before evaluation: {name}")

    accounting = protocol.get("accounting", {})
    for name in REQUIRED_ACCOUNTING_FLAGS:
        if accounting.get(name) is not True:
            errors.append(f"RDME accounting requirement missing or disabled: {name}")

    return errors
