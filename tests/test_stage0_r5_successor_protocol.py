import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    ROOT
    / "successor"
    / "experiments"
    / "V10R3R5_STAGE0_SUCCESSOR_PROTOCOL_20261006_V1.json"
)


def _load():
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def test_r5_is_distinct_high_headroom_successor_with_same_training_math():
    protocol = _load()
    assert protocol["schema"] == "V10R3R5_STAGE0_SUCCESSOR_PROTOCOL_V1"
    assert protocol["status"] == "AUTHORIZED_LOCAL_DEVELOPMENT_STAGE0_HOST_HEADROOM_GATED"
    assert protocol["claim_ceiling"] == (
        "STAGE0_HOST_RESOURCE_QUALIFICATION_ONLY_NOT_CORPUS_TRAINING_NOT_DEPLOYMENT"
    )

    predecessor = protocol["predecessor"]
    assert predecessor["head"] == "4f2aa26f50ce723bf32774238f6fb55b531dc5ad"
    assert predecessor["r4_attempt_status"] == "CONSUMED_FAILED_RESOURCE_HOLD"    
    assert predecessor["retry_r4_in_place"] is False
    assert predecessor["r4_optimizer_steps_completed_before_hold"] == 5
    assert predecessor["r4_commit_headroom_mib_at_hold"] == 6928.4

    change = protocol["successor_change"]
    assert change["training_math_change"] == "NONE"
    assert change["runtime_package_change"] == "NONE"
    assert change["stage0_mechanism_change"] == "NONE"
    assert change["host_gate_change"] == "MIN_PRELAUNCH_COMMIT_HEADROOM_36_GIB"

    gate = protocol["host_resource_gate"]
    assert gate["min_prelaunch_commit_headroom_gib"] == 36.0
    assert gate["min_available_physical_gib"] == 8.0
    assert gate["in_run_min_commit_headroom_mib"] == 8192.0
    assert gate["gpu_memory_used_mib_required"] == 0
    assert gate["competing_trainers_required"] == []
    assert gate["commit_limit_change_required"] is False

    observation = protocol["changed_host_condition"]
    assert observation["r4_preflight_commit_headroom_gib"] == 31.809
    assert observation["r5_observed_commit_headroom_gib"] == 37.814
    assert observation["headroom_delta_gib"] == 6.005
    assert observation["commit_limit_gib"] == 54.729

    execution = protocol["execution"]
    assert execution["attempt_limit"] == 1
    assert execution["attempt_status"] == "UNUSED"
    assert execution["automatic_retry"] is False
    assert execution["optimizer_steps"] == 20
    assert execution["synthetic_input_only"] is True
    assert execution["corpus_bearing_input_prohibited"] is True
    assert execution["runtime_python_path"] == (
        r"C:\ProgramData\ProRun\model-env\Scripts\python.exe"
    )

    assert protocol["system_mutation"]["pagefile_change"] is False
    assert protocol["system_mutation"]["preactive_policy_change"] is False
    assert protocol["promotion"]["on_stage0_pass"] == (
        "PREPARE_SEPARATE_FRESH_CORPUS_TRAINING_SUBJECT_ONLY"
    )
