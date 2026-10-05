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


def _channel_record(channel: ExternalChannelObservation) -> dict[str, object]:
    return {
        "channel_id": channel.channel_id,
        "kind": channel.kind,
        "mutable": channel.mutable,
        "write_capable": channel.write_capable,
        "arm_scoped": channel.arm_scoped,
        "superseded": channel.superseded,
        "observed_active": channel.observed_active,
    }


def _manifest_digest(identity: dict[str, object]) -> str:
    import json
    from hashlib import sha256
    return sha256(
        json.dumps(
            identity,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def build_isolation_manifest(
    *,
    arm_root: Path,
    expected_env: Mapping[str, str],
    observed_env: Mapping[str, str],
    changed_paths: tuple[str, ...],
    external_state_channels: tuple[str, ...],
    external_channel_observations: tuple[ExternalChannelObservation, ...] = (),
    isolation_result: IsolationResult | None = None,
    external_channel_result: IsolationResult | None = None,
    sentinel_results: Mapping[str, str] | None = None,
    source_head: str | None = None,
    runtime_binding_sha256: str | None = None,
) -> dict[str, object]:
    sentinels = dict(sorted((sentinel_results or {}).items()))
    failed_sentinels = sorted(
        name for name, status in sentinels.items() if status != "PASS"
    )
    result_statuses = [
        result.status
        for result in (isolation_result, external_channel_result)
        if result is not None
    ]
    status = (
        "HOLD"
        if failed_sentinels or any(item != "PASS" for item in result_statuses)
        else ("PASS" if sentinels and len(result_statuses) == 2 else "UNKNOWN")
    )
    identity: dict[str, object] = {
        "schema": "LANE_C_ISOLATION_MANIFEST_V2",
        "status": status,
        "arm_root": str(Path(arm_root).resolve()),
        "expected_env": dict(sorted(expected_env.items())),
        "observed_env": dict(sorted(observed_env.items())),
        "changed_paths": sorted(str(Path(path).resolve()) for path in changed_paths),
        "external_state_channels": sorted(external_state_channels),
        "external_channel_observations": sorted(
            (_channel_record(channel) for channel in external_channel_observations),
            key=lambda item: (str(item["kind"]), str(item["channel_id"])),
        ),
        "isolation_result": (
            None
            if isolation_result is None
            else {
                "status": isolation_result.status,
                "violations": list(isolation_result.violations),
            }
        ),
        "external_channel_result": (
            None
            if external_channel_result is None
            else {
                "status": external_channel_result.status,
                "violations": list(external_channel_result.violations),
            }
        ),
        "sentinel_results": sentinels,
        "failed_sentinels": failed_sentinels,
        "source_head": source_head,
        "runtime_binding_sha256": runtime_binding_sha256,
    }
    return {**identity, "manifest_digest": _manifest_digest(identity)}


def validate_isolation_manifest(manifest: Mapping[str, object]) -> IsolationResult:
    violations: list[str] = []
    digest = manifest.get("manifest_digest")
    identity = dict(manifest)
    identity.pop("manifest_digest", None)
    if not isinstance(digest, str) or digest != _manifest_digest(identity):
        violations.append("MANIFEST_DIGEST_MISMATCH")
    if manifest.get("schema") != "LANE_C_ISOLATION_MANIFEST_V2":
        violations.append("MANIFEST_SCHEMA_MISMATCH")
    source_head = manifest.get("source_head")
    if source_head is not None and (
        not isinstance(source_head, str)
        or len(source_head) != 40
        or any(ch not in "0123456789abcdef" for ch in source_head)
    ):
        violations.append("SOURCE_HEAD_INVALID")
    runtime_digest = manifest.get("runtime_binding_sha256")
    if runtime_digest is not None and (
        not isinstance(runtime_digest, str)
        or len(runtime_digest) != 64
        or any(ch not in "0123456789abcdef" for ch in runtime_digest)
    ):
        violations.append("RUNTIME_BINDING_SHA256_INVALID")
    if manifest.get("status") == "PASS" and manifest.get("failed_sentinels"):
        violations.append("PASS_WITH_FAILED_SENTINELS")
    return IsolationResult(
        status="HOLD" if violations else "PASS",
        violations=tuple(violations),
    )
