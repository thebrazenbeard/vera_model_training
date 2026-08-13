# Training Bus Terminal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, zero-cost, release-pinned transport layer that moves an independently admitted training release into a native ChatGPT boarding package, routes it through one Project terminal, fails closed on authority/currentness mismatches, and leaves native qualification separate.

**Architecture:** Add a focused `school_bus` Python package beside the current bootcamp. Exact passenger payload bytes are hashed into a canonical manifest. An independently supplied admission receipt must bind that manifest fingerprint before routing. The Project-native terminal is a compact Markdown file with YAML front matter; the cargo is one deterministic JSON envelope usable from ChatGPT Library or direct attachment/upload. Boarding logic has no GitHub, model, or network dependency after admission.

**Tech Stack:** Python 3.12, standard library (`argparse`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`), PyYAML 6.0.2, pytest 8.3.5. No new dependency.

## Global Constraints

- `ZERO_COST` is absolute. No metered API, paid model, paid runner fallback, or billing-dependent service.
- External training evidence may establish package readiness only. It may not qualify the native target identity.
- The bus transports package information. It does not modify model weights or inject messages into another chat.
- GitHub/Qwen/workbench state is not required after admission.
- Boarding is pinned to an exact release ID. The selector `latest` is invalid.
- A package cannot self-authorize. A matching independent admission receipt is mandatory.
- The Project terminal is current-route metadata only and cannot admit a package.
- Wrong release, stop, function, qualification profile, payload hash, receipt hash, route status, or currentness fails closed.
- Rollback is explicit and limited to the immediately previous admitted release recorded by the terminal.
- ChatGPT Library is preferred cargo storage, not authority and not a correctness dependency. Exact file attachment/upload is the fallback.
- Successful boarding sets native qualification to `NOT_RUN`. Only fresh testing of the actual native identity may later produce PASS, CONDITIONAL PASS, or FAIL.
- Passenger-readable cargo contains a qualification **profile**, not hidden answers or a reusable examiner answer key.
- `package_fingerprint` is SHA-256 of the canonical release manifest describing exact passenger payload file names, sizes, and hashes. The admission receipt and outer cargo envelope are excluded from that hash to avoid self-reference. The receipt has its own SHA-256 fingerprint.

## Planned File Structure

```text
school_bus/
  __init__.py
  hashing.py
  models.py
  package.py
  admission.py
  terminal.py
  render.py
  boarding.py
  cli.py

tests/
  bus_support.py
  test_school_bus_models.py
  test_school_bus_package.py
  test_school_bus_admission.py
  test_school_bus_terminal.py
  test_school_bus_render.py
  test_school_bus_boarding.py
  test_school_bus_cli.py
  test_school_bus_end_to_end.py

.github/workflows/tests.yml
README.md
```

Do not commit a live `SB` route until a real SB release independently passes the audit depot. Tests use temporary SB fixtures only.

---

### Task 1: Canonical Hashing and Validated Domain Records

**Files:**
- Create: `school_bus/__init__.py`
- Create: `school_bus/hashing.py`
- Create: `school_bus/models.py`
- Create: `tests/test_school_bus_models.py`

**Interfaces:**
- Produces `canonical_json_bytes(value: object) -> bytes`.
- Produces `sha256_bytes(data: bytes) -> str`.
- Produces immutable `PayloadFile`, `ReleaseManifest`, `AdmissionReceipt`, `RouteRelease`, `StopRoute`, `TerminalState`.
- Produces `ValidationError(ValueError)`.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_school_bus_models.py
import pytest

from school_bus.hashing import canonical_json_bytes, sha256_bytes
from school_bus.models import ReleaseManifest, ValidationError


def test_canonical_json_is_order_independent():
    left = canonical_json_bytes({"b": 2, "a": 1})
    right = canonical_json_bytes({"a": 1, "b": 2})
    assert left == right == b'{"a":1,"b":2}'
    assert sha256_bytes(left) == sha256_bytes(right)


def test_manifest_rejects_latest_release_id():
    with pytest.raises(ValidationError, match="release_id"):
        ReleaseManifest.from_dict({
            "schema_version": 1,
            "release_id": "latest",
            "stop_id": "SB",
            "function": "Supabase Platform Specialist",
            "qualification_profile": "supabase_practitioner_v1",
            "supersedes": None,
            "payload_files": [],
        })
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_models.py -q`

Expected: collection/import failure because `school_bus` does not exist.

- [ ] **Step 3: Implement canonical hashing**

```python
# school_bus/hashing.py
from __future__ import annotations

import hashlib
import json


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
```

- [ ] **Step 4: Implement records and structural validation**

```python
# school_bus/models.py
from __future__ import annotations

from dataclasses import dataclass
import re

from .hashing import canonical_json_bytes, sha256_bytes

HEX64 = re.compile(r"^[0-9a-f]{64}$")
ROUTE_STATES = {
    "ADMITTED", "READY_FOR_BOARDING", "NATIVE_QUALIFICATION", "QUALIFIED",
    "REMEDIATION_REQUIRED", "SUPERSEDED", "ROLLBACK_ELIGIBLE", "RETIRED", "CONFLICTED",
}

class ValidationError(ValueError):
    pass

@dataclass(frozen=True)
class PayloadFile:
    name: str
    sha256: str
    size_bytes: int

@dataclass(frozen=True)
class ReleaseManifest:
    schema_version: int
    release_id: str
    stop_id: str
    function: str
    qualification_profile: str
    supersedes: str | None
    payload_files: tuple[PayloadFile, ...]

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "release_id": self.release_id,
            "stop_id": self.stop_id,
            "function": self.function,
            "qualification_profile": self.qualification_profile,
            "supersedes": self.supersedes,
            "payload_files": [
                {"name": x.name, "sha256": x.sha256, "size_bytes": x.size_bytes}
                for x in self.payload_files
            ],
        }

    def fingerprint(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.to_dict()))

@dataclass(frozen=True)
class AdmissionReceipt:
    schema_version: int
    release_id: str
    stop_id: str
    function: str
    package_fingerprint: str
    audit_outcome: str
    status: str
    qualification_profile: str
    supersedes: str | None
    admitted_at: str
    auditor: str

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "release_id": self.release_id,
            "stop_id": self.stop_id,
            "function": self.function,
            "package_fingerprint": self.package_fingerprint,
            "audit_outcome": self.audit_outcome,
            "status": self.status,
            "qualification_profile": self.qualification_profile,
            "supersedes": self.supersedes,
            "admitted_at": self.admitted_at,
            "auditor": self.auditor,
        }

    def fingerprint(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.to_dict()))

@dataclass(frozen=True)
class RouteRelease:
    release_id: str
    cargo_name: str
    package_fingerprint: str
    receipt_fingerprint: str
    qualification_profile: str
    status: str

@dataclass(frozen=True)
class StopRoute:
    stop_id: str
    function: str
    current: RouteRelease
    rollback: RouteRelease | None

@dataclass(frozen=True)
class TerminalState:
    terminal_version: int
    stops: tuple[StopRoute, ...]
```

Add explicit `from_dict()` methods. Enforce schema version `1`, non-empty identifiers/function/profile, `release_id.lower() != "latest"`, lowercase 64-hex hashes, non-negative file sizes, unique payload names, unique stop IDs, and route status membership in `ROUTE_STATES`. Receipt parsing is structural only: do not treat `PASS` or `ADMITTED` as authority until Task 3.

- [ ] **Step 5: Run focused and full tests**

Run: `python -m pytest tests/test_school_bus_models.py -q && python -m pytest -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add school_bus/__init__.py school_bus/hashing.py school_bus/models.py tests/test_school_bus_models.py
git commit -m "feat: add training bus domain models"
```

---

### Task 2: Exact Passenger Payload, Cargo Parsing, and Rendering

**Files:**
- Create: `school_bus/package.py`
- Create: `school_bus/render.py`
- Create: `tests/test_school_bus_package.py`
- Create: `tests/test_school_bus_render.py`

**Interfaces:**
- Produces `build_manifest(release_id, stop_id, function, qualification_profile, supersedes, payload: dict[str, bytes]) -> ReleaseManifest`.
- Produces `verify_payload(manifest: ReleaseManifest, payload: dict[str, bytes]) -> None`.
- Produces immutable `CargoEnvelope(manifest: ReleaseManifest, receipt: AdmissionReceipt, payload: dict[str, bytes])`.
- Produces `parse_cargo(data: bytes) -> CargoEnvelope`; this performs structural parsing only and does **not** call `verify_payload`.
- Produces `render_cargo(manifest, receipt, payload) -> bytes`.
- Produces `cargo_filename(manifest) -> str`.

Passenger payload V1 is exactly:

```text
IDENTITY_CAPSULE.md
SOURCE_ANCHORS.md
REGRESSION_SET.json
QUALIFICATION_PROFILE.json
```

- [ ] **Step 1: Write RED payload tests**

```python
# tests/test_school_bus_package.py
import pytest

from school_bus.models import ValidationError
from school_bus.package import build_manifest, verify_payload


def sample_payload():
    return {
        "IDENTITY_CAPSULE.md": b"# Identity Capsule\n",
        "SOURCE_ANCHORS.md": b"# Source Anchors\n",
        "REGRESSION_SET.json": b'{"cases":[]}\n',
        "QUALIFICATION_PROFILE.json": b'{"profile_id":"supabase_practitioner_v1"}\n',
    }


def test_manifest_fingerprint_is_stable_for_same_bytes():
    first = sample_payload()
    second = dict(reversed(list(first.items())))
    a = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, first)
    b = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, second)
    assert a.fingerprint() == b.fingerprint()


def test_verify_payload_rejects_tamper():
    payload = sample_payload()
    manifest = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, payload)
    payload["IDENTITY_CAPSULE.md"] = b"tampered"
    with pytest.raises(ValidationError, match="payload hash mismatch: IDENTITY_CAPSULE.md"):
        verify_payload(manifest, payload)
```

- [ ] **Step 2: Run RED payload test**

Run: `python -m pytest tests/test_school_bus_package.py -q`

Expected: FAIL because package module is absent.

- [ ] **Step 3: Implement manifest and payload validation**

```python
REQUIRED_PAYLOAD_FILES = {
    "IDENTITY_CAPSULE.md",
    "SOURCE_ANCHORS.md",
    "REGRESSION_SET.json",
    "QUALIFICATION_PROFILE.json",
}
```

`build_manifest()` requires exact set equality, sorts file names, records exact byte length and SHA-256, and rejects any passenger payload file whose name starts with `ADMISSION_`. `verify_payload()` checks exact set equality, then size, then hash, and names the exact failing file.

- [ ] **Step 4: Write RED cargo round-trip test**

```python
# tests/test_school_bus_render.py
from school_bus.models import AdmissionReceipt
from school_bus.package import build_manifest, parse_cargo
from school_bus.render import cargo_filename, render_cargo
from tests.test_school_bus_package import sample_payload


def test_cargo_round_trip_is_deterministic():
    payload = sample_payload()
    manifest = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, payload)
    receipt = AdmissionReceipt.from_dict({
        "schema_version": 1,
        "release_id": "SUPABASE_R5",
        "stop_id": "SB",
        "function": "Supabase Platform Specialist",
        "package_fingerprint": manifest.fingerprint(),
        "audit_outcome": "PASS",
        "status": "ADMITTED",
        "qualification_profile": "supabase_practitioner_v1",
        "supersedes": None,
        "admitted_at": "2026-08-12T20:00:00-04:00",
        "auditor": "NATIVE_INDEPENDENT_AUDIT",
    })
    first = render_cargo(manifest, receipt, payload)
    second = render_cargo(manifest, receipt, dict(reversed(list(payload.items()))))
    assert first == second
    parsed = parse_cargo(first)
    assert parsed.manifest == manifest
    assert parsed.receipt == receipt
    assert parsed.payload == payload
    assert cargo_filename(manifest) == "BUS_SB_SUPABASE_R5.json"
```

- [ ] **Step 5: Run RED render test**

Run: `python -m pytest tests/test_school_bus_render.py -q`

Expected: FAIL because render/cargo parser is incomplete.

- [ ] **Step 6: Implement cargo structure**

Canonical JSON envelope:

```json
{
  "bus_schema_version": 1,
  "manifest": {},
  "admission_receipt": {},
  "payload": {
    "IDENTITY_CAPSULE.md": "UTF-8 text",
    "SOURCE_ANCHORS.md": "UTF-8 text",
    "REGRESSION_SET.json": "UTF-8 text",
    "QUALIFICATION_PROFILE.json": "UTF-8 text"
  }
}
```

`render_cargo()` uses sorted canonical JSON plus exactly one trailing newline. `parse_cargo()` rejects non-UTF-8 data, invalid JSON, unsupported schema, malformed manifest/receipt, non-object payload, or non-string payload values, then reconstructs UTF-8 bytes. It deliberately leaves payload hash verification to boarding so tampering maps to the specific boarding condition rather than generic malformed cargo.

- [ ] **Step 7: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_package.py tests/test_school_bus_render.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/package.py school_bus/render.py tests/test_school_bus_package.py tests/test_school_bus_render.py
git commit -m "feat: add immutable training cargo format"
```

---

### Task 3: Independent Admission Gate

**Files:**
- Create: `school_bus/admission.py`
- Create: `tests/test_school_bus_admission.py`

**Interfaces:**
- Produces `validate_admission(manifest: ReleaseManifest, receipt: AdmissionReceipt) -> None`.
- Produces `load_admission_receipt(path: Path) -> AdmissionReceipt`.
- Does not expose any function that converts bootcamp `training_package_ready` or proxy scores into admission.

- [ ] **Step 1: Write RED admission tests**

```python
# tests/test_school_bus_admission.py
import pytest

from school_bus.admission import validate_admission
from school_bus.models import AdmissionReceipt, ValidationError
from school_bus.package import build_manifest

PAYLOAD = {
    "IDENTITY_CAPSULE.md": b"capsule",
    "SOURCE_ANCHORS.md": b"anchors",
    "REGRESSION_SET.json": b'{"cases":[]}',
    "QUALIFICATION_PROFILE.json": b'{"profile_id":"supabase_practitioner_v1"}',
}


def make_manifest():
    return build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", "SUPABASE_R4", PAYLOAD)


def make_receipt(manifest, audit_outcome="PASS", status="ADMITTED"):
    return AdmissionReceipt.from_dict({
        "schema_version": 1,
        "release_id": manifest.release_id,
        "stop_id": manifest.stop_id,
        "function": manifest.function,
        "package_fingerprint": manifest.fingerprint(),
        "audit_outcome": audit_outcome,
        "status": status,
        "qualification_profile": manifest.qualification_profile,
        "supersedes": manifest.supersedes,
        "admitted_at": "2026-08-12T20:00:00-04:00",
        "auditor": "NATIVE_INDEPENDENT_AUDIT",
    })


def test_receipt_must_bind_exact_manifest_fingerprint():
    manifest = make_manifest()
    raw = make_receipt(manifest).to_dict()
    raw["package_fingerprint"] = "0" * 64
    with pytest.raises(ValidationError, match="package_fingerprint"):
        validate_admission(manifest, AdmissionReceipt.from_dict(raw))


def test_failed_audit_cannot_admit():
    manifest = make_manifest()
    with pytest.raises(ValidationError, match="audit_outcome"):
        validate_admission(manifest, make_receipt(manifest, audit_outcome="FAIL"))


def test_nonadmitted_status_cannot_board():
    manifest = make_manifest()
    with pytest.raises(ValidationError, match="status"):
        validate_admission(manifest, make_receipt(manifest, status="AUDIT_PENDING"))
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_admission.py -q`

Expected: FAIL because admission module is absent.

- [ ] **Step 3: Implement exact admission checks**

Compare, in order: release ID, stop ID, function, qualification profile, supersedes, package fingerprint, `audit_outcome == "PASS"`, `status == "ADMITTED"`, non-empty auditor, non-empty admitted timestamp. Raise `ValidationError` naming the first field. Return `None` only on exact acceptance.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_admission.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/admission.py tests/test_school_bus_admission.py
git commit -m "feat: require independent training admission receipt"
```

---

### Task 4: Project Terminal and Explicit Rollback

**Files:**
- Create: `school_bus/terminal.py`
- Create: `tests/test_school_bus_terminal.py`

**Interfaces:**
- Produces `render_terminal(state: TerminalState) -> str`.
- Produces `parse_terminal(text: str) -> TerminalState`.
- Produces `resolve_stop(state: TerminalState, stop_id: str) -> StopRoute`.
- Produces `resolve_release(route: StopRoute, requested_release: str | None = None, rollback: bool = False) -> RouteRelease`.

- [ ] **Step 1: Write RED terminal tests**

```python
# tests/test_school_bus_terminal.py
import pytest

from school_bus.models import RouteRelease, StopRoute, TerminalState, ValidationError
from school_bus.terminal import parse_terminal, render_terminal, resolve_release


def release(release_id, status):
    return RouteRelease(
        release_id=release_id,
        cargo_name=f"BUS_SB_{release_id}.json",
        package_fingerprint="a" * 64,
        receipt_fingerprint="b" * 64,
        qualification_profile="supabase_practitioner_v1",
        status=status,
    )


def test_terminal_round_trip_and_explicit_rollback():
    state = TerminalState(1, (StopRoute(
        "SB", "Supabase Platform Specialist",
        release("SUPABASE_R5", "READY_FOR_BOARDING"),
        release("SUPABASE_R4", "ROLLBACK_ELIGIBLE"),
    ),))
    parsed = parse_terminal(render_terminal(state))
    route = parsed.stops[0]
    assert resolve_release(route).release_id == "SUPABASE_R5"
    assert resolve_release(route, "SUPABASE_R4", rollback=True).release_id == "SUPABASE_R4"
    with pytest.raises(ValidationError, match="rollback"):
        resolve_release(route, "SUPABASE_R4", rollback=False)
    with pytest.raises(ValidationError, match="latest"):
        resolve_release(route, "latest")
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_terminal.py -q`

Expected: FAIL because terminal module is absent.

- [ ] **Step 3: Implement terminal renderer/parser**

Render Markdown beginning with YAML front matter:

```yaml
---
terminal_version: 1
stops:
  SB:
    function: Supabase Platform Specialist
    current:
      release_id: SUPABASE_R5
      cargo_name: BUS_SB_SUPABASE_R5.json
      package_fingerprint: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      receipt_fingerprint: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      qualification_profile: supabase_practitioner_v1
      status: READY_FOR_BOARDING
    rollback: null
---
```

Follow with `# Training Bus Terminal` and a generated human summary. `parse_terminal()` reads only the first YAML front matter block as route data and rejects missing delimiters, unsupported version, malformed stop records, or duplicate stop IDs.

- [ ] **Step 4: Implement release resolution exactly**

Omitted requested release resolves current. Explicit current resolves current. Explicit rollback release requires `rollback=True`. Unknown releases reject. `latest` rejects. No automatic substitution or rollback.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_terminal.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/terminal.py tests/test_school_bus_terminal.py
git commit -m "feat: add project training bus terminal"
```

---

### Task 5: Fail-Closed Boarding State Machine

**Files:**
- Create: `tests/bus_support.py`
- Create: `school_bus/boarding.py`
- Create: `tests/test_school_bus_boarding.py`

**Interfaces:**
- Produces protocol `CargoLocator.find(cargo_name: str) -> bytes | None`.
- Produces `FilesystemCargoLocator(root: Path)`.
- Produces immutable `BoardingResult(status, stop_id, release_id, cargo_name, package_fingerprint, receipt_fingerprint, qualification_profile, native_qualification, blocking_condition)`.
- Produces `board(terminal, stop_id, locator, requested_release=None, rollback=False) -> BoardingResult`.

Statuses are exactly `READY_FOR_NATIVE`, `NEEDS_ATTACHMENT`, `BLOCKED`.

Blocking conditions are exactly:

```text
MISSING_STOP
MISSING_CARGO
WRONG_RELEASE
WRONG_STOP
WRONG_FUNCTION
PACKAGE_FINGERPRINT_MISMATCH
RECEIPT_FINGERPRINT_MISMATCH
UNADMITTED_RECEIPT
STALE_ROUTE
QUALIFICATION_PROFILE_MISMATCH
ROLLBACK_NOT_EXPLICIT
MALFORMED_CARGO
```

- [ ] **Step 1: Create deterministic test support**

```python
# tests/bus_support.py
from school_bus.models import AdmissionReceipt, RouteRelease, StopRoute, TerminalState
from school_bus.package import build_manifest
from school_bus.render import cargo_filename, render_cargo


def make_valid_parts(tmp_path):
    payload = {
        "IDENTITY_CAPSULE.md": b"# SB Capsule\n",
        "SOURCE_ANCHORS.md": b"# Sources\n",
        "REGRESSION_SET.json": b'{"cases":[],"status":"PROPOSED_UNVERIFIED"}\n',
        "QUALIFICATION_PROFILE.json": b'{"profile_id":"supabase_practitioner_v1"}\n',
    }
    manifest = build_manifest(
        "SUPABASE_R5", "SB", "Supabase Platform Specialist",
        "supabase_practitioner_v1", "SUPABASE_R4", payload,
    )
    receipt = AdmissionReceipt.from_dict({
        "schema_version": 1,
        "release_id": "SUPABASE_R5",
        "stop_id": "SB",
        "function": "Supabase Platform Specialist",
        "package_fingerprint": manifest.fingerprint(),
        "audit_outcome": "PASS",
        "status": "ADMITTED",
        "qualification_profile": "supabase_practitioner_v1",
        "supersedes": "SUPABASE_R4",
        "admitted_at": "2026-08-12T20:00:00-04:00",
        "auditor": "NATIVE_INDEPENDENT_AUDIT",
    })
    name = cargo_filename(manifest)
    cargo = render_cargo(manifest, receipt, payload)
    (tmp_path / name).write_bytes(cargo)
    current = RouteRelease(
        "SUPABASE_R5", name, manifest.fingerprint(), receipt.fingerprint(),
        "supabase_practitioner_v1", "READY_FOR_BOARDING",
    )
    terminal = TerminalState(1, (StopRoute("SB", "Supabase Platform Specialist", current, None),))
    return payload, manifest, receipt, name, cargo, terminal
```

- [ ] **Step 2: Write RED boarding tests**

```python
# tests/test_school_bus_boarding.py
import json
from pathlib import Path

import pytest

from school_bus.boarding import FilesystemCargoLocator, board
from school_bus.models import RouteRelease, StopRoute, TerminalState
from school_bus.render import render_cargo
from tests.bus_support import make_valid_parts


def test_manual_fallback_names_exact_cargo(tmp_path):
    _, manifest, receipt, name, _, terminal = make_valid_parts(tmp_path)
    result = board(terminal, "SB", locator=None)
    assert result.status == "NEEDS_ATTACHMENT"
    assert result.cargo_name == name
    assert result.package_fingerprint == manifest.fingerprint()
    assert result.receipt_fingerprint == receipt.fingerprint()
    assert result.native_qualification == "NOT_RUN"


def test_valid_cargo_reaches_native_gate(tmp_path):
    _, _, _, _, _, terminal = make_valid_parts(tmp_path)
    result = board(terminal, "SB", FilesystemCargoLocator(tmp_path))
    assert result.status == "READY_FOR_NATIVE"
    assert result.blocking_condition is None
    assert result.native_qualification == "NOT_RUN"


def test_missing_stop_blocks(tmp_path):
    _, _, _, _, _, terminal = make_valid_parts(tmp_path)
    result = board(terminal, "SECURITY", FilesystemCargoLocator(tmp_path))
    assert (result.status, result.blocking_condition) == ("BLOCKED", "MISSING_STOP")


def test_payload_tamper_blocks_as_package_fingerprint_mismatch(tmp_path):
    _, _, _, name, cargo, terminal = make_valid_parts(tmp_path)
    raw = json.loads(cargo.decode("utf-8"))
    raw["payload"]["IDENTITY_CAPSULE.md"] = "tampered"
    (tmp_path / name).write_text(json.dumps(raw, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    result = board(terminal, "SB", FilesystemCargoLocator(tmp_path))
    assert (result.status, result.blocking_condition) == ("BLOCKED", "PACKAGE_FINGERPRINT_MISMATCH")


def test_stale_route_blocks(tmp_path):
    _, manifest, receipt, name, _, terminal = make_valid_parts(tmp_path)
    stale = RouteRelease(
        "SUPABASE_R5", name, manifest.fingerprint(), receipt.fingerprint(),
        "supabase_practitioner_v1", "SUPERSEDED",
    )
    state = TerminalState(1, (StopRoute("SB", "Supabase Platform Specialist", stale, None),))
    result = board(state, "SB", FilesystemCargoLocator(tmp_path))
    assert (result.status, result.blocking_condition) == ("BLOCKED", "STALE_ROUTE")


def test_boarding_module_has_no_external_runtime_client():
    source = Path("school_bus/boarding.py").read_text(encoding="utf-8")
    for forbidden in ("requests", "LLM_URL", "Qwen", "api.github.com", "supabase.com"):
        assert forbidden not in source
```

Add exact mutation tests in the same file for wrong embedded release (`WRONG_RELEASE`), stop (`WRONG_STOP`), function (`WRONG_FUNCTION`), qualification profile (`QUALIFICATION_PROFILE_MISMATCH`), terminal receipt fingerprint (`RECEIPT_FINGERPRINT_MISMATCH`), failed/non-admitted receipt (`UNADMITTED_RECEIPT`), absent cargo (`MISSING_CARGO`), malformed JSON (`MALFORMED_CARGO`), and attempted rollback without `rollback=True` (`ROLLBACK_NOT_EXPLICIT`). Each test must mutate one field only and assert the exact blocking condition named here.

- [ ] **Step 3: Run RED boarding tests**

Run: `python -m pytest tests/test_school_bus_boarding.py -q`

Expected: FAIL because boarding module is absent.

- [ ] **Step 4: Implement boarding in fixed order**

```text
resolve stop; missing -> MISSING_STOP
resolve requested release; implicit rollback -> ROLLBACK_NOT_EXPLICIT; unknown -> WRONG_RELEASE
locator is None -> NEEDS_ATTACHMENT with exact route metadata
locate exact cargo name; absent -> MISSING_CARGO
parse cargo structurally; failure -> MALFORMED_CARGO
verify payload hashes against manifest; failure -> PACKAGE_FINGERPRINT_MISMATCH
validate admission receipt; PASS/status failure -> UNADMITTED_RECEIPT
compare embedded release -> WRONG_RELEASE
compare embedded stop -> WRONG_STOP
compare embedded function -> WRONG_FUNCTION
compare qualification profile -> QUALIFICATION_PROFILE_MISMATCH
compare manifest fingerprint with terminal -> PACKAGE_FINGERPRINT_MISMATCH
compare receipt fingerprint with terminal -> RECEIPT_FINGERPRINT_MISMATCH
require current route status ADMITTED or READY_FOR_BOARDING -> STALE_ROUTE
success -> READY_FOR_NATIVE, native_qualification NOT_RUN
```

Expected route/cargo/authority mismatches return `BoardingResult(status="BLOCKED", ...)`. Unexpected programming exceptions propagate so CI cannot disguise defects as route failures.

- [ ] **Step 5: Run focused/full tests and commit**

Run: `python -m pytest tests/test_school_bus_boarding.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add tests/bus_support.py school_bus/boarding.py tests/test_school_bus_boarding.py
git commit -m "feat: add fail-closed training boarding protocol"
```

---

### Task 6: Native Boarding Instructions and Deterministic CLI

**Files:**
- Modify: `school_bus/render.py`
- Create: `school_bus/cli.py`
- Modify: `tests/test_school_bus_render.py`
- Create: `tests/test_school_bus_cli.py`

**Interfaces:**
- Produces `render_boarding_instruction(route: StopRoute) -> str`.
- CLI commands: `build-candidate`, `verify-admission`, `render-terminal`, `board`.
- There is no `auto-admit` command.

- [ ] **Step 1: Add RED boarding-instruction test**

```python
# append to tests/test_school_bus_render.py
from school_bus.render import render_boarding_instruction
from tests.bus_support import make_valid_parts


def test_boarding_instruction_preserves_native_qualification_boundary(tmp_path):
    _, _, _, _, _, terminal = make_valid_parts(tmp_path)
    text = render_boarding_instruction(terminal.stops[0])
    assert "BUS::BOARD::SB" in text
    assert "native qualification is NOT_RUN" in text
    assert "proxy" in text.lower()
    assert "GitHub" not in text
```

- [ ] **Step 2: Implement boarding instruction**

The instruction names exact stop, release, cargo, package fingerprint, receipt fingerprint, and qualification profile. It tells the target to verify terminal/package/receipt agreement, preserve epistemic labels, treat proxy scores as diagnostic only, leave native qualification `NOT_RUN` until fresh evaluation, and stop on mismatch. The manual fallback instructs attachment/upload of that exact cargo artifact and does not require GitHub or Library.

- [ ] **Step 3: Write RED CLI tests**

```python
# tests/test_school_bus_cli.py
import json

from school_bus.cli import main
from tests.bus_support import make_valid_parts


def test_build_candidate_never_creates_admission_receipt(tmp_path):
    payload_dir = tmp_path / "inputs"
    payload_dir.mkdir()
    files = {
        "IDENTITY_CAPSULE.md": "capsule",
        "SOURCE_ANCHORS.md": "anchors",
        "REGRESSION_SET.json": '{"cases":[]}',
        "QUALIFICATION_PROFILE.json": '{"profile_id":"supabase_practitioner_v1"}',
    }
    for name, text in files.items():
        (payload_dir / name).write_text(text, encoding="utf-8")
    out = tmp_path / "candidate"
    code = main([
        "build-candidate",
        "--release-id", "SUPABASE_R5",
        "--stop-id", "SB",
        "--function", "Supabase Platform Specialist",
        "--qualification-profile", "supabase_practitioner_v1",
        "--capsule", str(payload_dir / "IDENTITY_CAPSULE.md"),
        "--source-anchors", str(payload_dir / "SOURCE_ANCHORS.md"),
        "--regression-set", str(payload_dir / "REGRESSION_SET.json"),
        "--qualification-profile-file", str(payload_dir / "QUALIFICATION_PROFILE.json"),
        "--out-dir", str(out),
    ])
    assert code == 0
    assert (out / "MANIFEST.json").exists()
    assert (out / "PAYLOAD_FINGERPRINT.txt").exists()
    assert not (out / "ADMISSION_RECEIPT.json").exists()


def test_board_without_cargo_root_requests_attachment(tmp_path, capsys):
    _, _, _, _, _, terminal = make_valid_parts(tmp_path)
    terminal_path = tmp_path / "TRAINING_BUS_TERMINAL.md"
    from school_bus.terminal import render_terminal
    terminal_path.write_text(render_terminal(terminal), encoding="utf-8")
    code = main(["board", "--terminal", str(terminal_path), "--stop-id", "SB"])
    result = json.loads(capsys.readouterr().out)
    assert code == 0
    assert result["status"] == "NEEDS_ATTACHMENT"
    assert result["native_qualification"] == "NOT_RUN"
```

- [ ] **Step 4: Run RED CLI tests**

Run: `python -m pytest tests/test_school_bus_render.py tests/test_school_bus_cli.py -q`

Expected: FAIL because instruction/CLI behavior is incomplete.

- [ ] **Step 5: Implement CLI commands**

`build-candidate` requires `--release-id`, `--stop-id`, `--function`, `--qualification-profile`, `--capsule`, `--source-anchors`, `--regression-set`, `--qualification-profile-file`, `--out-dir`; optional `--supersedes`. It writes canonical `MANIFEST.json`, exact `PAYLOAD_FINGERPRINT.txt`, and `candidate_payload/`, but never creates an admission receipt.

`verify-admission` loads manifest + externally supplied receipt and calls `validate_admission()`.

`render-terminal` accepts one or more validated route JSON files and writes `TRAINING_BUS_TERMINAL.md` through `render_terminal()`.

`board` accepts `--terminal`, `--stop-id`, optional exact `--release-id`, optional `--rollback`, optional `--cargo-root`; it prints canonical `BoardingResult` JSON. Return code `0` for `READY_FOR_NATIVE` or `NEEDS_ATTACHMENT`, `2` for `BLOCKED`.

- [ ] **Step 6: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_render.py tests/test_school_bus_cli.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/render.py school_bus/cli.py tests/test_school_bus_render.py tests/test_school_bus_cli.py
git commit -m "feat: add training bus native handoff cli"
```

---

### Task 7: End-to-End Acceptance, CI, and Documentation

**Files:**
- Create: `tests/test_school_bus_end_to_end.py`
- Modify: `.github/workflows/tests.yml`
- Modify: `README.md`

**Interfaces:**
- Proves `candidate payload -> external admission receipt -> cargo -> terminal -> SB boarding -> native qualification NOT_RUN` with local deterministic files only.

- [ ] **Step 1: Write complete end-to-end test**

```python
# tests/test_school_bus_end_to_end.py
from school_bus.admission import validate_admission
from school_bus.boarding import FilesystemCargoLocator, board
from school_bus.terminal import parse_terminal, render_terminal
from tests.bus_support import make_valid_parts


def test_sb_release_reaches_native_gate_without_external_runtime(tmp_path):
    _, manifest, receipt, name, _, terminal = make_valid_parts(tmp_path)
    validate_admission(manifest, receipt)
    terminal_text = render_terminal(terminal)
    parsed_terminal = parse_terminal(terminal_text)
    result = board(parsed_terminal, "SB", FilesystemCargoLocator(tmp_path))
    assert result.status == "READY_FOR_NATIVE"
    assert result.release_id == "SUPABASE_R5"
    assert result.cargo_name == name
    assert result.package_fingerprint == manifest.fingerprint()
    assert result.receipt_fingerprint == receipt.fingerprint()
    assert result.native_qualification == "NOT_RUN"
```

- [ ] **Step 2: Run end-to-end test**

Run: `python -m pytest tests/test_school_bus_end_to_end.py -q`

Expected: PASS after Tasks 1-6. If it fails, fix only the demonstrated transport defect under TDD. Do not weaken the test.

- [ ] **Step 3: Update CI compile/test block**

Change `.github/workflows/tests.yml` to run:

```bash
python -m py_compile bootcamp.py fast_bootcamp.py quality_gate.py audit_gate_v5.py run_bootcamp.py school_bus/*.py
python -m pytest -q
```

Do not add a new runner, secret, service, paid dependency, or model invocation for bus tests.

- [ ] **Step 4: Update README**

Add `## Training bus handoff` with this route:

```text
external bootcamp candidate
        ↓
independent audit + admission receipt
        ↓
immutable cargo + Project terminal route
        ↓
BUS::BOARD::<STOP_ID>
        ↓
native specialist consumes exact package
        ↓
fresh native qualification
```

State that Library is preferred storage only, attachment/upload is the guaranteed fallback, cargo existence does not confer authority, the terminal cannot admit a package, and local proxy scores never become native qualification.

- [ ] **Step 5: Run complete verification**

Run:

```bash
python -m py_compile bootcamp.py fast_bootcamp.py quality_gate.py audit_gate_v5.py run_bootcamp.py school_bus/*.py
python -m pytest -q
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_school_bus_end_to_end.py .github/workflows/tests.yml README.md
git commit -m "test: verify training bus end to end"
```

---

## Post-Implementation Review Gate

Before merge, inspect the full diff and verify:

1. No path converts `training_package_ready`, a local-model score, or a bootcamp outcome directly into `ADMITTED` or `QUALIFIED`.
2. Candidate building cannot create its own authoritative admission receipt.
3. Receipt validation binds exact release, stop, function, qualification profile, supersession, and manifest fingerprint.
4. Manifest fingerprint covers exact payload file names, sizes, and hashes and excludes receipt/outer envelope to avoid recursive hashing.
5. Terminal stores both package and receipt fingerprints and never resolves `latest`.
6. Wrong passenger, stale route, tamper, forged receipt, and implicit rollback fail closed.
7. Manual fallback reports exact cargo identity without requiring GitHub or Library.
8. Passenger cargo contains no hidden native answer key.
9. `READY_FOR_NATIVE` still reports `native_qualification = NOT_RUN`.
10. A clean checkout/worktree passes compilation and the complete pytest suite before any PASS claim or merge.

## Acceptance Evidence Required

A successful implementation earns **PASS only for the transport mechanism** after the deterministic hostile/end-to-end suite passes on the reviewed bytes. It does not qualify SB. SB remains `NOT_RUN` for a release until a real admitted cargo package reaches the actual native SB identity and that identity passes the separate Project G1-G7 cold, false-premise, correction, boundary, adversarial, and transfer evaluation.
