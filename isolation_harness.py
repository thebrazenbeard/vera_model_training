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
