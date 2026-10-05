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

