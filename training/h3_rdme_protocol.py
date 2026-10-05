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
    "mutable_project_state",
    "current_factual_knowledge",
)
REQUIRED_PREREGISTRATION_FLAGS = (
    "family_definitions_frozen",
    "thresholds_frozen",
    "post_result_threshold_edits_forbidden",
    "new_mechanism_after_feedback_requires_new_subject",
)
REQUIRED_ISOLATION_FLAGS = (
    "fresh_process_required",
    "isolated_writable_namespace_required",
    "external_mutable_channel_sentinel_required",
    "retrieval_service_state_must_be_isolated_or_disabled",
    "stale_adapter_cache_probe_required",
)
REQUIRED_ACCOUNTING_FLAGS = (
    "include_context_memory_stops",
    "count_total_stored_parameters",
    "count_module_count",
    "count_routing_metadata",
    "count_active_parameters",
    "count_peak_ram_vram",
    "count_wall_time",
)
REQUIRED_SEQUENCE = (
    "BASELINE_ALL_ARMS",
    "ACQUIRE_A",
    "ACQUIRE_B",
    "SUPPORT_REMOVAL",
    "MUTATE_B_ONLY",
    "FRESH_PROCESS_REOPEN",
    "TEST_A_PRESERVATION",
    "TEST_B_REPLACEMENT",
    "TEST_WRONG_ROUTE",
    "TEST_NO_ROUTE_BASE_ONLY",
    "TEST_MIXED_AB",
    "TEST_ADAPTER_OFF_RESTORATION",
    "TEST_STALE_B_REACTIVATION",
)


def validate_protocol(protocol):
    errors = []
    if protocol.get("schema") != "H3_RDME_MVE_PROTOCOL_V1":
        errors.append("schema must be H3_RDME_MVE_PROTOCOL_V1")
    if protocol.get("status") != "FROZEN_PREREGISTRATION":
        errors.append("status must remain FROZEN_PREREGISTRATION")

    authority = protocol.get("authority", {})
    for name in (
        "protected_final_bank_access_authorized",
        "merge_main_authorized",
        "deployment_activation_authorized",
        "paid_compute_authorized",
    ):
        if authority.get(name) is not False:
            errors.append(f"unsafe authority: {name} must be false")
    if authority.get("execution_requires_vera_coordination_and_live_runtime_binding") is not True:
        errors.append("execution_requires_vera_coordination_and_live_runtime_binding must be true")

    arms = protocol.get("arms", {})
    exposures = [arms.get(name, {}).get("information_exposure") for name in ARM_NAMES]
    if any(exposure is None for exposure in exposures):
        errors.append("routing information parity: every H0/H1/H2/H3 arm must declare information_exposure")
    elif any(exposure != exposures[0] for exposure in exposures[1:]):
        errors.append("routing information parity violated across H0/H1/H2/H3")

    h3 = arms.get("H3", {})
    if h3.get("router") != "DETERMINISTIC_FROZEN":
        errors.append("H3 router must remain DETERMINISTIC_FROZEN")
    if h3.get("active_adapter_limit") != 1:
        errors.append("H3 active_adapter_limit must remain 1")

    sequence = protocol.get("sequence")
    if sequence != list(REQUIRED_SEQUENCE):
        missing = [item for item in REQUIRED_SEQUENCE if item not in (sequence or [])]
        if missing:
            errors.extend(f"required sequence step missing: {item}" for item in missing)
        else:
            errors.append("RDME sequence order changed")

    controls = protocol.get("controls", {})
    for name in REQUIRED_CONTROLS:
        if controls.get(name) is not True:
            errors.append(f"required RDME control missing or disabled: {name}")

    data_admission = protocol.get("data_admission", {})
    if data_admission.get("development_synthetic_only") is not True:
        errors.append("development_synthetic_only must be true")
    for name in PROHIBITED_DATA_FLAGS:
        if data_admission.get(name) is not False:
            errors.append(f"prohibited RDME data admission: {name} must be false")

    preregistration = protocol.get("preregistration", {})
    for name in REQUIRED_PREREGISTRATION_FLAGS:
        if preregistration.get(name) is not True:
            errors.append(f"RDME preregistration must be frozen before evaluation: {name}")

    isolation = protocol.get("isolation", {})
    for name in REQUIRED_ISOLATION_FLAGS:
        if isolation.get(name) is not True:
            errors.append(f"RDME isolation requirement missing or disabled: {name}")

    accounting = protocol.get("accounting", {})
    for name in REQUIRED_ACCOUNTING_FLAGS:
        if accounting.get(name) is not True:
            errors.append(f"RDME accounting requirement missing or disabled: {name}")

    return errors
