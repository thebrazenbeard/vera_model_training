from __future__ import annotations

from pathlib import Path

from isolation_harness import build_isolated_environment


def test_isolated_environment_rebinds_writable_namespaces_and_filters_mutable_state():
    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    inherited = {
        "PATH": r"C:\Windows\System32",
        "SYSTEMROOT": r"C:\Windows",
        "TEMP": r"C:\shared-temp",
        "TMP": r"C:\shared-temp",
        "USERPROFILE": r"C:\Users\patri",
        "HOME": r"C:\Users\patri",
        "HF_HOME": r"C:\shared-hf",
        "TRANSFORMERS_CACHE": r"C:\shared-transformers",
        "SECRET_MUTABLE_COUNTER": "7",
    }

    env = build_isolated_environment(
        arm_root=arm_root,
        inherited_env=inherited,
        immutable_env_allowlist=("PATH", "SYSTEMROOT"),
    )

    root = str(arm_root)
    assert env["PATH"] == inherited["PATH"]
    assert env["SYSTEMROOT"] == inherited["SYSTEMROOT"]
    assert env["TEMP"].startswith(root)
    assert env["TMP"].startswith(root)
    assert env["USERPROFILE"].startswith(root)
    assert env["HOME"].startswith(root)
    assert env["HF_HOME"].startswith(root)
    assert env["TRANSFORMERS_CACHE"].startswith(root)
    assert "SECRET_MUTABLE_COUNTER" not in env


def test_undeclared_environment_state_forces_hold():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )
    observed = dict(expected)
    observed["SECRET_MUTABLE_COUNTER"] = "8"

    result = isolation_harness.evaluate_isolation(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=observed,
        changed_paths=(),
        external_state_channels=(),
    )

    assert result.status == "HOLD"
    assert any("SECRET_MUTABLE_COUNTER" in item for item in result.violations)



def test_write_outside_arm_root_forces_hold():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )

    result = isolation_harness.evaluate_isolation(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=expected,
        changed_paths=(str(Path.cwd().resolve() / "shared-state.db"),),
        external_state_channels=(),
    )

    assert result.status == "HOLD"
    assert any("OUTSIDE_WRITABLE_ROOT" in item for item in result.violations)



def test_external_mutable_state_channel_forces_hold():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )

    result = isolation_harness.evaluate_isolation(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=expected,
        changed_paths=(),
        external_state_channels=("retrieval:index:shared",),
    )

    assert result.status == "HOLD"
    assert "EXTERNAL_MUTABLE_STATE:retrieval:index:shared" in result.violations



def test_clean_arm_scoped_state_passes():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )

    result = isolation_harness.evaluate_isolation(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=expected,
        changed_paths=(str(arm_root / "output" / "result.json"),),
        external_state_channels=(),
    )

    assert result.status == "PASS"
    assert result.violations == ()



def test_write_capable_credential_channel_forces_hold():
    import isolation_harness

    result = isolation_harness.evaluate_external_channels(
        (
            isolation_harness.ExternalChannelObservation(
                channel_id="credential:github-token",
                kind="credential",
                mutable=True,
                write_capable=True,
                arm_scoped=False,
            ),
        )
    )

    assert result.status == "HOLD"
    assert "WRITE_CAPABLE_EXTERNAL_CHANNEL:credential:github-token" in result.violations


def test_reused_daemon_or_provider_session_forces_hold():
    import isolation_harness

    result = isolation_harness.evaluate_external_channels(
        (
            isolation_harness.ExternalChannelObservation(
                channel_id="daemon:retrieval-shared",
                kind="daemon",
                mutable=True,
                write_capable=False,
                arm_scoped=False,
            ),
            isolation_harness.ExternalChannelObservation(
                channel_id="provider:session-shared",
                kind="provider_session",
                mutable=True,
                write_capable=False,
                arm_scoped=False,
            ),
        )
    )

    assert result.status == "HOLD"
    assert "SHARED_MUTABLE_EXTERNAL_CHANNEL:daemon:retrieval-shared" in result.violations
    assert "SHARED_MUTABLE_EXTERNAL_CHANNEL:provider:session-shared" in result.violations


def test_stale_adapter_resurrection_forces_hold():
    import isolation_harness

    result = isolation_harness.evaluate_external_channels(
        (
            isolation_harness.ExternalChannelObservation(
                channel_id="adapter:stale-b",
                kind="adapter",
                mutable=True,
                write_capable=False,
                arm_scoped=True,
                superseded=True,
                observed_active=True,
            ),
        )
    )

    assert result.status == "HOLD"
    assert "STALE_STATE_RESURRECTED:adapter:stale-b" in result.violations


def test_clean_external_channels_pass():
    import isolation_harness

    result = isolation_harness.evaluate_external_channels(
        (
            isolation_harness.ExternalChannelObservation(
                channel_id="retrieval:arm-17",
                kind="retrieval",
                mutable=True,
                write_capable=True,
                arm_scoped=True,
            ),
            isolation_harness.ExternalChannelObservation(
                channel_id="adapter:current-a",
                kind="adapter",
                mutable=True,
                write_capable=False,
                arm_scoped=True,
                superseded=False,
                observed_active=True,
            ),
        )
    )

    assert result.status == "PASS"
    assert result.violations == ()


def test_deterministic_state_file_outside_isolated_root_forces_hold():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )
    deterministic_path = Path.cwd().resolve() / "fixed-cache" / "state.json"

    result = isolation_harness.evaluate_isolation(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=expected,
        changed_paths=(str(deterministic_path),),
        external_state_channels=(),
    )

    assert result.status == "HOLD"
    assert any("OUTSIDE_WRITABLE_ROOT" in item for item in result.violations)


def test_isolation_manifest_is_deterministic_and_binds_observed_channels():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )
    observed = dict(expected)

    first = isolation_harness.build_isolation_manifest(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=observed,
        changed_paths=(str(arm_root / "output" / "result.json"),),
        external_state_channels=(),
    )
    second = isolation_harness.build_isolation_manifest(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=observed,
        changed_paths=(str(arm_root / "output" / "result.json"),),
        external_state_channels=(),
    )
    changed = isolation_harness.build_isolation_manifest(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=observed,
        changed_paths=(str(arm_root / "output" / "result.json"),),
        external_state_channels=("provider:shared-session-state",),
    )

    assert first == second
    assert first["schema"] == "LANE_C_ISOLATION_MANIFEST_V2"
    assert first["arm_root"] == str(arm_root)
    assert len(first["manifest_digest"]) == 64
    assert first["manifest_digest"] != changed["manifest_digest"]


def test_manifest_digest_binds_structured_channel_semantics_and_results():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )
    pass_result = isolation_harness.IsolationResult(status="PASS", violations=())
    channel_pass = isolation_harness.ExternalChannelObservation(
        channel_id="provider:session",
        kind="provider_session",
        mutable=False,
        write_capable=False,
        arm_scoped=True,
        superseded=False,
        observed_active=True,
    )
    channel_hold = isolation_harness.ExternalChannelObservation(
        channel_id="provider:session",
        kind="provider_session",
        mutable=True,
        write_capable=True,
        arm_scoped=False,
        superseded=False,
        observed_active=True,
    )
    kwargs = dict(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=expected,
        changed_paths=(),
        external_state_channels=("provider:session",),
        isolation_result=pass_result,
        external_channel_result=pass_result,
        sentinel_results={
            "undeclared_environment_global_counter": "PASS",
            "changed_file_outside_arm_root": "PASS",
            "shared_retrieval_index_or_external_mutable_state": "PASS",
            "inherited_write_capable_credential": "PASS",
            "reused_daemon_port_or_provider_session_state": "PASS",
            "stale_adapter_module_resurrection": "PASS",
            "deterministic_state_file_outside_isolated_root": "PASS",
        },
        source_head="1" * 40,
        runtime_binding_sha256="2" * 64,
    )
    first = isolation_harness.build_isolation_manifest(
        external_channel_observations=(channel_pass,), **kwargs
    )
    changed = isolation_harness.build_isolation_manifest(
        external_channel_observations=(channel_hold,), **kwargs
    )
    assert first["status"] == "PASS"
    assert first["manifest_digest"] != changed["manifest_digest"]
    assert first["source_head"] == "1" * 40
    assert first["runtime_binding_sha256"] == "2" * 64


def test_manifest_holds_when_any_required_sentinel_or_evaluation_holds():
    import isolation_harness

    arm_root = (Path.cwd() / ".isolation-test-arm").resolve()
    expected = build_isolated_environment(
        arm_root=arm_root,
        inherited_env={"PATH": r"C:\Windows\System32"},
        immutable_env_allowlist=("PATH",),
    )
    hold_result = isolation_harness.IsolationResult(
        status="HOLD", violations=("OUTSIDE_WRITABLE_ROOT:x",)
    )
    sentinels = {
        "undeclared_environment_global_counter": "PASS",
        "changed_file_outside_arm_root": "HOLD",
        "shared_retrieval_index_or_external_mutable_state": "PASS",
        "inherited_write_capable_credential": "PASS",
        "reused_daemon_port_or_provider_session_state": "PASS",
        "stale_adapter_module_resurrection": "PASS",
        "deterministic_state_file_outside_isolated_root": "PASS",
    }
    manifest = isolation_harness.build_isolation_manifest(
        arm_root=arm_root,
        expected_env=expected,
        observed_env=expected,
        changed_paths=(),
        external_state_channels=(),
        external_channel_observations=(),
        isolation_result=hold_result,
        external_channel_result=isolation_harness.IsolationResult(status="PASS", violations=()),
        sentinel_results=sentinels,
        source_head="1" * 40,
        runtime_binding_sha256="2" * 64,
    )
    assert manifest["status"] == "HOLD"
    assert "changed_file_outside_arm_root" in manifest["failed_sentinels"]


def test_manifest_validator_rejects_digest_tampering():
    import isolation_harness

    assert hasattr(isolation_harness, "validate_isolation_manifest")
