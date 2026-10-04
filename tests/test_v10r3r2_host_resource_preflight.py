from __future__ import annotations

import pytest

from successor.experiments.preflight_v10r3r2_host_resources import (
    HostResourceHold,
    validate_host_resources,
)


def test_host_resource_gate_passes_with_safe_headroom() -> None:
    result = validate_host_resources(
        {
            "available_physical_gib": 12.0,
            "commit_headroom_gib": 14.0,
            "committed_percent": 62.0,
            "gpu_memory_used_mib": 0,
            "gpu_memory_total_mib": 4096,
            "gpu_utilization_percent": 0,
            "competing_trainers": [],
        },
        min_available_physical_gib=8.0,
        min_commit_headroom_gib=8.0,
    )

    assert result["status"] == "PASS"
    assert result["available_physical_gib"] == 12.0
    assert result["commit_headroom_gib"] == 14.0


@pytest.mark.parametrize(
    ("metrics", "reason"),
    [
        (
            {
                "available_physical_gib": 7.9,
                "commit_headroom_gib": 14.0,
                "committed_percent": 62.0,
                "gpu_memory_used_mib": 0,
                "gpu_memory_total_mib": 4096,
                "gpu_utilization_percent": 0,
                "competing_trainers": [],
            },
            "available physical memory below minimum",
        ),
        (
            {
                "available_physical_gib": 12.0,
                "commit_headroom_gib": 7.9,
                "committed_percent": 88.0,
                "gpu_memory_used_mib": 0,
                "gpu_memory_total_mib": 4096,
                "gpu_utilization_percent": 0,
                "competing_trainers": [],
            },
            "commit headroom below minimum",
        ),
        (
            {
                "available_physical_gib": 12.0,
                "commit_headroom_gib": 14.0,
                "committed_percent": 62.0,
                "gpu_memory_used_mib": 256,
                "gpu_memory_total_mib": 4096,
                "gpu_utilization_percent": 0,
                "competing_trainers": [],
            },
            "gpu memory is not free",
        ),
        (
            {
                "available_physical_gib": 12.0,
                "commit_headroom_gib": 14.0,
                "committed_percent": 62.0,
                "gpu_memory_used_mib": 0,
                "gpu_memory_total_mib": 4096,
                "gpu_utilization_percent": 0,
                "competing_trainers": [{"pid": 1234, "command": "train_v10r2_dev.py"}],
            },
            "competing trainer detected",
        ),
    ],
)
def test_host_resource_gate_holds_unsafe_launch(metrics: dict, reason: str) -> None:
    with pytest.raises(HostResourceHold, match=reason):
        validate_host_resources(
            metrics,
            min_available_physical_gib=8.0,
            min_commit_headroom_gib=8.0,
        )


def test_trainer_scan_filters_wmi_before_commandline_match(monkeypatch) -> None:
    import successor.experiments.preflight_v10r3r2_host_resources as host

    captured = {}

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return Result()

    monkeypatch.setattr(host.subprocess, "run", fake_run)

    assert host.read_competing_trainers() == []
    command = captured["args"][-1]
    assert "Get-CimInstance Win32_Process -Filter" in command
    assert "Name LIKE 'python%'" in command
    assert "Get-CimInstance Win32_Process |" not in command
    assert captured["kwargs"]["timeout"] == 15
