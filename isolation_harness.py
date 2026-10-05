from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class IsolationResult:
    status: str
    violations: tuple[str, ...]


def build_isolated_environment(
    *,
    arm_root: Path,
    inherited_env: Mapping[str, str],
    immutable_env_allowlist: tuple[str, ...],
) -> dict[str, str]:
    root = Path(arm_root).resolve()
    env = {
        name: inherited_env[name]
        for name in immutable_env_allowlist
        if name in inherited_env
    }
    env.update(
        {
            "TEMP": str(root / "temp"),
            "TMP": str(root / "temp"),
            "USERPROFILE": str(root / "home"),
            "HOME": str(root / "home"),
            "HF_HOME": str(root / "cache" / "huggingface"),
            "TRANSFORMERS_CACHE": str(root / "cache" / "transformers"),
        }
    )
    return env


def evaluate_isolation(
    *,
    arm_root: Path,
    expected_env: Mapping[str, str],
    observed_env: Mapping[str, str],
    changed_paths: tuple[str, ...],
    external_state_channels: tuple[str, ...],
) -> IsolationResult:
    root = Path(arm_root).resolve()
    violations: list[str] = []

    for name, expected_value in expected_env.items():
        if name not in observed_env:
            violations.append(f"MISSING_ENV:{name}")
        elif observed_env[name] != expected_value:
            violations.append(f"ENV_DRIFT:{name}")

    for name in observed_env:
        if name not in expected_env:
            violations.append(f"UNDECLARED_ENV:{name}")

    for raw_path in changed_paths:
        path = Path(raw_path).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            violations.append(f"OUTSIDE_WRITABLE_ROOT:{path}")

    for channel in external_state_channels:
        violations.append(f"EXTERNAL_MUTABLE_STATE:{channel}")

    return IsolationResult(
        status="HOLD" if violations else "PASS",
        violations=tuple(violations),
    )


@dataclass(frozen=True, slots=True)
class ExternalChannelObservation:
    channel_id: str
    kind: str
    mutable: bool
    write_capable: bool
    arm_scoped: bool
    superseded: bool = False
    observed_active: bool = False


def evaluate_external_channels(
    channels: tuple[ExternalChannelObservation, ...],
) -> IsolationResult:
    violations: list[str] = []

    for channel in channels:
        if channel.write_capable and not channel.arm_scoped:
            violations.append(
                f"WRITE_CAPABLE_EXTERNAL_CHANNEL:{channel.channel_id}"
            )
        if channel.mutable and not channel.arm_scoped:
            violations.append(
                f"SHARED_MUTABLE_EXTERNAL_CHANNEL:{channel.channel_id}"
            )
        if channel.superseded and channel.observed_active:
            violations.append(
                f"STALE_STATE_RESURRECTED:{channel.channel_id}"
            )

    return IsolationResult(
        status="HOLD" if violations else "PASS",
        violations=tuple(violations),
    )


def build_isolation_manifest(
    *,
    arm_root: Path,
    expected_env: Mapping[str, str],
    observed_env: Mapping[str, str],
    changed_paths: tuple[str, ...],
    external_state_channels: tuple[str, ...],
) -> dict[str, object]:
    import json
    from hashlib import sha256

    identity: dict[str, object] = {
        "schema": "LANE_C_ISOLATION_MANIFEST_V1",
        "arm_root": str(Path(arm_root).resolve()),
        "expected_env": dict(sorted(expected_env.items())),
        "observed_env": dict(sorted(observed_env.items())),
        "changed_paths": sorted(str(Path(path).resolve()) for path in changed_paths),
        "external_state_channels": sorted(external_state_channels),
    }
    manifest_digest = sha256(
        json.dumps(
            identity,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    return {**identity, "manifest_digest": manifest_digest}
