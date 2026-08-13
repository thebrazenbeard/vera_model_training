# Training Bus Terminal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, zero-cost, release-pinned transport layer that moves an independently admitted training release into a native ChatGPT boarding package, routes it through one Project terminal, fails closed on mismatches, and never confuses proxy training with native qualification.

**Architecture:** Add a focused `school_bus` Python package beside the existing bootcamp. Candidate payload bytes are hashed into a canonical release manifest. An independently supplied admission receipt must bind that exact manifest fingerprint before routing is allowed. The native terminal is a small Markdown/YAML route board; the cargo is one deterministic JSON file that can live in ChatGPT Library or be attached/uploaded directly. After admission, boarding logic has no GitHub, Qwen, model, or network dependency.

**Tech Stack:** Python 3.12, standard library (`argparse`, `dataclasses`, `hashlib`, `json`, `pathlib`, `re`, `typing`), PyYAML 6.0.2, pytest 8.3.5. No new dependency.

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
- ChatGPT Library is preferred cargo storage, not an authority source and not a correctness dependency. Exact file attachment/upload is the fallback.
- Successful boarding sets native qualification to `NOT_RUN`. Only fresh testing of the actual native identity may later produce PASS, CONDITIONAL PASS, or FAIL.
- Passenger-readable cargo contains a qualification **profile**, not hidden answers or a reusable examiner answer key.
- `package_fingerprint` means SHA-256 of the canonical release manifest describing exact passenger payload bytes. The admission receipt and outer cargo envelope are excluded from that hash to avoid self-reference. The receipt has a separate SHA-256 fingerprint.

## Planned File Structure

```text
school_bus/
  __init__.py
  hashing.py
  models.py
  package.py
  admission.py
  terminal.py
  boarding.py
  render.py
  cli.py

tests/
  test_school_bus_models.py
  test_school_bus_package.py
  test_school_bus_admission.py
  test_school_bus_terminal.py
  test_school_bus_boarding.py
  test_school_bus_render.py
  test_school_bus_cli.py
  test_school_bus_end_to_end.py

.github/workflows/tests.yml
README.md
```

Do not commit a live `SB` route until a real SB release has independently passed the audit depot. Tests use temporary SB fixtures only.

---

### Task 1: Canonical Hashing and Domain Models

**Files:**
- Create: `school_bus/__init__.py`
- Create: `school_bus/hashing.py`
- Create: `school_bus/models.py`
- Create: `tests/test_school_bus_models.py`

**Interfaces:**
- Produces `canonical_json_bytes(value: object) -> bytes`.
- Produces `sha256_bytes(data: bytes) -> str`.
- Produces immutable records `PayloadFile`, `ReleaseManifest`, `AdmissionReceipt`, `RouteRelease`, `StopRoute`, `TerminalState`.
- Produces `ValidationError(ValueError)`.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_school_bus_models.py
import pytest

from school_bus.hashing import canonical_json_bytes, sha256_bytes
from school_bus.models import ReleaseManifest, ValidationError


def test_canonical_json_is_stable():
    a = canonical_json_bytes({"b": 2, "a": 1})
    b = canonical_json_bytes({"a": 1, "b": 2})
    assert a == b == b'{"a":1,"b":2}'
    assert sha256_bytes(a) == sha256_bytes(b)


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

Expected: import/collection failure because `school_bus` does not exist.

- [ ] **Step 3: Implement hashing**

```python
# school_bus/hashing.py
from __future__ import annotations

import hashlib
import json


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
```

- [ ] **Step 4: Implement models and validation**

```python
# school_bus/models.py
from __future__ import annotations

from dataclasses import dataclass
import re

from .hashing import canonical_json_bytes, sha256_bytes

HEX64 = re.compile(r"^[0-9a-f]{64}$")

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
            "payload_files": [vars(x) for x in self.payload_files],
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
        return vars(self).copy()

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

Add explicit `from_dict()` methods for every record. Enforce schema version `1`, non-empty IDs/function/profile, `release_id.lower() != "latest"`, lowercase 64-hex hashes, non-negative file sizes, unique payload names, unique terminal stop IDs, and route status membership in:

```python
ROUTE_STATES = {
    "ADMITTED", "READY_FOR_BOARDING", "NATIVE_QUALIFICATION", "QUALIFIED",
    "REMEDIATION_REQUIRED", "SUPERSEDED", "ROLLBACK_ELIGIBLE", "RETIRED", "CONFLICTED",
}
```

Do not make `AdmissionReceipt.from_dict()` treat `PASS`/`ADMITTED` as authority. Structural parsing accepts strings; the admission gate in Task 3 decides whether the receipt authorizes boarding.

- [ ] **Step 5: Run focused and full tests**

Run: `python -m pytest tests/test_school_bus_models.py -q && python -m pytest -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add school_bus/__init__.py school_bus/hashing.py school_bus/models.py tests/test_school_bus_models.py
git commit -m "feat: add training bus domain models"
```

---

### Task 2: Canonical Passenger Payload and Cargo Envelope

**Files:**
- Create: `school_bus/package.py`
- Create: `tests/test_school_bus_package.py`

**Interfaces:**
- Produces `build_manifest(release_id: str, stop_id: str, function: str, qualification_profile: str, supersedes: str | None, payload: dict[str, bytes]) -> ReleaseManifest`.
- Produces `verify_payload(manifest: ReleaseManifest, payload: dict[str, bytes]) -> None`.
- Produces `CargoEnvelope(manifest: ReleaseManifest, receipt: AdmissionReceipt, payload: dict[str, bytes])`.
- Produces `parse_cargo(data: bytes) -> CargoEnvelope`.

Passenger payload V1 is the exact set:

```text
IDENTITY_CAPSULE.md
SOURCE_ANCHORS.md
REGRESSION_SET.json
QUALIFICATION_PROFILE.json
```

- [ ] **Step 1: Write RED tests**

```python
# tests/test_school_bus_package.py
import pytest

from school_bus.models import ValidationError
from school_bus.package import build_manifest, verify_payload


def payload():
    return {
        "IDENTITY_CAPSULE.md": b"# Identity Capsule\n",
        "SOURCE_ANCHORS.md": b"# Source Anchors\n",
        "REGRESSION_SET.json": b'{"cases":[]}\n',
        "QUALIFICATION_PROFILE.json": b'{"profile_id":"supabase_practitioner_v1"}\n',
    }


def test_manifest_fingerprint_ignores_dictionary_iteration_order():
    p = payload()
    a = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, p)
    b = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, dict(reversed(list(p.items()))))
    assert a.fingerprint() == b.fingerprint()


def test_payload_tamper_is_rejected():
    p = payload()
    manifest = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist", "supabase_practitioner_v1", None, p)
    p["IDENTITY_CAPSULE.md"] = b"tampered"
    with pytest.raises(ValidationError, match="payload hash mismatch"):
        verify_payload(manifest, p)
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_package.py -q`

Expected: FAIL because `school_bus.package` is absent.

- [ ] **Step 3: Implement manifest building and verification**

```python
REQUIRED_PAYLOAD_FILES = {
    "IDENTITY_CAPSULE.md",
    "SOURCE_ANCHORS.md",
    "REGRESSION_SET.json",
    "QUALIFICATION_PROFILE.json",
}
```

`build_manifest()` requires exact set equality, sorts names, records SHA-256 + byte size, and rejects any payload filename starting with `ADMISSION_`. `verify_payload()` checks exact set, size, then hash, returning the narrowest deterministic message such as `missing payload file: SOURCE_ANCHORS.md` or `payload hash mismatch: IDENTITY_CAPSULE.md`.

- [ ] **Step 4: Implement cargo parsing**

Canonical cargo JSON structure:

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

`parse_cargo()` rejects non-UTF-8 content, invalid JSON, unsupported schema, non-string payload values, or malformed manifest/receipt. It reconstructs exact UTF-8 payload bytes and calls `verify_payload()` before returning.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_package.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/package.py tests/test_school_bus_package.py
git commit -m "feat: build immutable training cargo payloads"
```

---

### Task 3: Independent Admission Gate

**Files:**
- Create: `school_bus/admission.py`
- Create: `tests/test_school_bus_admission.py`

**Interfaces:**
- Produces `validate_admission(manifest: ReleaseManifest, receipt: AdmissionReceipt) -> None`.
- Produces `load_admission_receipt(path: Path) -> AdmissionReceipt`.
- Does not expose any function that converts bootcamp `training_package_ready` or proxy scores into an admitted receipt.

- [ ] **Step 1: Write RED tests**

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


def make_receipt(manifest):
    return AdmissionReceipt.from_dict({
        "schema_version": 1,
        "release_id": manifest.release_id,
        "stop_id": manifest.stop_id,
        "function": manifest.function,
        "package_fingerprint": manifest.fingerprint(),
        "audit_outcome": "PASS",
        "status": "ADMITTED",
        "qualification_profile": manifest.qualification_profile,
        "supersedes": manifest.supersedes,
        "admitted_at": "2026-08-12T20:00:00-04:00",
        "auditor": "NATIVE_INDEPENDENT_AUDIT",
    })


def test_wrong_package_fingerprint_fails_closed():
    m = make_manifest()
    raw = make_receipt(m).to_dict()
    raw["package_fingerprint"] = "0" * 64
    with pytest.raises(ValidationError, match="package_fingerprint"):
        validate_admission(m, AdmissionReceipt.from_dict(raw))


def test_nonpass_receipt_does_not_admit():
    m = make_manifest()
    raw = make_receipt(m).to_dict()
    raw["audit_outcome"] = "FAIL"
    with pytest.raises(ValidationError, match="audit_outcome"):
        validate_admission(m, AdmissionReceipt.from_dict(raw))
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_admission.py -q`

Expected: FAIL because admission module is absent.

- [ ] **Step 3: Implement exact admission matching**

Check, in this order: release ID, stop ID, function, qualification profile, supersedes, package fingerprint, audit outcome exactly `PASS`, status exactly `ADMITTED`, non-empty `auditor`, non-empty `admitted_at`. Raise `ValidationError` naming the first mismatched field. Return `None` only when all checks pass.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_admission.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/admission.py tests/test_school_bus_admission.py
git commit -m "feat: require independent training admission receipt"
```

---

### Task 4: Project Terminal, Currentness, and Explicit Rollback

**Files:**
- Create: `school_bus/terminal.py`
- Create: `tests/test_school_bus_terminal.py`

**Interfaces:**
- Produces `render_terminal(state: TerminalState) -> str`.
- Produces `parse_terminal(text: str) -> TerminalState`.
- Produces `resolve_stop(state: TerminalState, stop_id: str) -> StopRoute`.
- Produces `resolve_release(route: StopRoute, requested_release: str | None = None, rollback: bool = False) -> RouteRelease`.

- [ ] **Step 1: Write RED round-trip/currentness tests**

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
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_terminal.py -q`

Expected: FAIL because terminal module is absent.

- [ ] **Step 3: Implement terminal format**

Render Markdown with exact YAML front matter first:

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

Follow with `# Training Bus Terminal` and a generated human-readable route summary. `parse_terminal()` reads only the first YAML front matter block as route data and rejects missing delimiters, unsupported version, malformed stop records, or duplicate stops.

- [ ] **Step 4: Implement exact route resolution**

Rules: omitted requested release resolves current; explicit current resolves current; explicit rollback requires `rollback=True`; unknown release rejects; `latest` rejects; rollback never occurs automatically.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_terminal.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/terminal.py tests/test_school_bus_terminal.py
git commit -m "feat: add project training bus terminal"
```

---

### Task 5: Fail-Closed Boarding and Native Rendering

**Files:**
- Create: `school_bus/boarding.py`
- Create: `school_bus/render.py`
- Create: `tests/test_school_bus_boarding.py`
- Create: `tests/test_school_bus_render.py`

**Interfaces:**
- Produces protocol `CargoLocator.find(cargo_name: str) -> bytes | None`.
- Produces `FilesystemCargoLocator(root: Path)`.
- Produces immutable `BoardingResult(status: str, stop_id: str, release_id: str, cargo_name: str, package_fingerprint: str, receipt_fingerprint: str, qualification_profile: str, native_qualification: str, blocking_condition: str | None)`.
- Produces `board(terminal: TerminalState, stop_id: str, locator: CargoLocator | None, requested_release: str | None = None, rollback: bool = False) -> BoardingResult`.
- Produces `render_cargo(manifest: ReleaseManifest, receipt: AdmissionReceipt, payload: dict[str, bytes]) -> bytes`.
- Produces `cargo_filename(manifest: ReleaseManifest) -> str`.
- Produces `render_boarding_instruction(route: StopRoute) -> str`.

Boarding result statuses are exactly `READY_FOR_NATIVE`, `NEEDS_ATTACHMENT`, and `BLOCKED`. Route/cargo/authority failures are returned as `BLOCKED`; schema-level programming/parsing failures inside standalone parser functions remain `ValidationError`.

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

- [ ] **Step 1: Write RED boarding tests**

```python
# tests/test_school_bus_boarding.py
from school_bus.boarding import board


def test_no_locator_requests_exact_attachment(admitted_terminal):
    result = board(admitted_terminal, "SB", locator=None)
    assert result.status == "NEEDS_ATTACHMENT"
    assert result.release_id == "SUPABASE_R5"
    assert result.cargo_name == "BUS_SB_SUPABASE_R5.json"
    assert result.native_qualification == "NOT_RUN"


def test_wrong_stop_is_blocked(admitted_terminal, admitted_locator):
    result = board(admitted_terminal, "SECURITY", admitted_locator)
    assert result.status == "BLOCKED"
    assert result.blocking_condition == "MISSING_STOP"
```

In the same file, add parameterized hostile fixtures covering every blocking condition listed above. Fixtures must create exact manifest/receipt/cargo/terminal bytes, mutate only the field under test, and assert no alternate release is selected.

- [ ] **Step 2: Run RED boarding test**

Run: `python -m pytest tests/test_school_bus_boarding.py -q`

Expected: FAIL because boarding/render modules are absent.

- [ ] **Step 3: Implement deterministic cargo rendering**

```python
# school_bus/render.py core shape
from .hashing import canonical_json_bytes


def render_cargo(manifest, receipt, payload):
    envelope = {
        "bus_schema_version": 1,
        "manifest": manifest.to_dict(),
        "admission_receipt": receipt.to_dict(),
        "payload": {name: payload[name].decode("utf-8") for name in sorted(payload)},
    }
    return canonical_json_bytes(envelope) + b"\n"
```

`cargo_filename()` normalizes non `[A-Za-z0-9_-]` characters to `_` and returns `BUS_<STOP_ID>_<RELEASE_ID>.json`.

- [ ] **Step 4: Implement boarding state machine**

Algorithm, in order:

```text
resolve stop -> if absent BLOCKED/MISSING_STOP
resolve exact current or explicit rollback -> mapping failure to WRONG_RELEASE or ROLLBACK_NOT_EXPLICIT
if locator is None -> NEEDS_ATTACHMENT with exact route metadata
find exact cargo name -> if absent BLOCKED/MISSING_CARGO
parse cargo -> on parse/schema failure BLOCKED/MALFORMED_CARGO
verify manifest payload hashes -> on mismatch BLOCKED/PACKAGE_FINGERPRINT_MISMATCH
validate independent admission -> on non-PASS/non-ADMITTED BLOCKED/UNADMITTED_RECEIPT
compare release -> WRONG_RELEASE
compare stop -> WRONG_STOP
compare function -> WRONG_FUNCTION
compare qualification profile -> QUALIFICATION_PROFILE_MISMATCH
compare manifest fingerprint to terminal -> PACKAGE_FINGERPRINT_MISMATCH
compare receipt fingerprint to terminal -> RECEIPT_FINGERPRINT_MISMATCH
require route status ADMITTED or READY_FOR_BOARDING -> otherwise STALE_ROUTE
return READY_FOR_NATIVE with native_qualification NOT_RUN
```

Catch only expected `ValidationError` cases and map them to the documented blocking conditions. Unexpected programming exceptions must propagate so CI does not disguise defects as ordinary route failures.

- [ ] **Step 5: Prove transport has no external runtime dependency**

```python
def test_boarding_module_has_no_external_runtime_client():
    source = Path("school_bus/boarding.py").read_text(encoding="utf-8")
    for forbidden in ("requests", "LLM_URL", "Qwen", "api.github.com", "supabase.com"):
        assert forbidden not in source
```

- [ ] **Step 6: Write render tests**

```python
# tests/test_school_bus_render.py

def test_render_cargo_is_deterministic(admitted_parts):
    manifest, receipt, payload = admitted_parts
    first = render_cargo(manifest, receipt, payload)
    second = render_cargo(manifest, receipt, dict(reversed(list(payload.items()))))
    assert first == second


def test_boarding_instruction_preserves_qualification_boundary(route):
    text = render_boarding_instruction(route)
    assert "BUS::BOARD::SB" in text
    assert "native qualification is NOT_RUN" in text
    assert "proxy" in text.lower()
```

`render_boarding_instruction()` must instruct the target to verify terminal/package/receipt agreement, consume epistemic labels unchanged, treat proxy scores as diagnostic only, run fresh native qualification, and stop on any mismatch. Manual fallback text must identify exact cargo name + both fingerprints without telling the target to fetch GitHub.

- [ ] **Step 7: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_boarding.py tests/test_school_bus_render.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/boarding.py school_bus/render.py tests/test_school_bus_boarding.py tests/test_school_bus_render.py
git commit -m "feat: add fail-closed native training boarding"
```

---

### Task 6: Deterministic CLI

**Files:**
- Create: `school_bus/cli.py`
- Create: `tests/test_school_bus_cli.py`

**Interfaces:**

```text
python -m school_bus.cli build-candidate
python -m school_bus.cli verify-admission
python -m school_bus.cli render-terminal
python -m school_bus.cli board
```

There is deliberately no `auto-admit` command.

- [ ] **Step 1: Write RED CLI tests**

Tests must call `school_bus.cli.main(argv)` directly and assert:

```text
build-candidate -> writes MANIFEST.json + PAYLOAD_FINGERPRINT.txt + candidate_payload/, never ADMISSION_RECEIPT.json
verify-admission -> exit 0 only for externally supplied matching PASS/ADMITTED receipt
render-terminal -> writes TRAINING_BUS_TERMINAL.md from verified route records
board without --cargo-root -> emits JSON status NEEDS_ATTACHMENT with exact cargo/fingerprints
board with mismatch -> nonzero exit and JSON status BLOCKED
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_cli.py -q`

Expected: FAIL because CLI is absent.

- [ ] **Step 3: Implement `build-candidate`**

Required arguments:

```text
--release-id
--stop-id
--function
--qualification-profile
--capsule
--source-anchors
--regression-set
--qualification-profile-file
--out-dir
```

Optional: `--supersedes`.

Read exact input bytes, call `build_manifest()`, write canonical `MANIFEST.json`, write exact manifest fingerprint plus newline to `PAYLOAD_FINGERPRINT.txt`, and copy the four exact payload files into `candidate_payload/`. Never inspect `training_package_ready` to authorize anything.

- [ ] **Step 4: Implement remaining commands**

`verify-admission` loads manifest + independently supplied receipt and calls `validate_admission()`.

`render-terminal` accepts one or more route JSON files that already contain package + receipt fingerprints, parses them through model validation, and writes `TRAINING_BUS_TERMINAL.md`.

`board` accepts terminal path, stop ID, optional exact `--release-id`, `--rollback`, and optional `--cargo-root`; prints `BoardingResult` as canonical JSON. Exit code `0` for `READY_FOR_NATIVE` and `NEEDS_ATTACHMENT`, exit code `2` for `BLOCKED`, and let unexpected exceptions produce nonzero failure.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_cli.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/cli.py tests/test_school_bus_cli.py
git commit -m "feat: add training bus cli"
```

---

### Task 7: End-to-End Transport Acceptance, CI, and Documentation

**Files:**
- Create: `tests/test_school_bus_end_to_end.py`
- Modify: `.github/workflows/tests.yml`
- Modify: `README.md`

**Interfaces:**
- Proves `candidate payload -> external admission receipt fixture -> cargo -> terminal -> SB boarding -> native qualification NOT_RUN` using only local temporary files.

- [ ] **Step 1: Write complete end-to-end test**

```python
# tests/test_school_bus_end_to_end.py
import json

from school_bus.admission import validate_admission
from school_bus.boarding import FilesystemCargoLocator, board
from school_bus.models import AdmissionReceipt, RouteRelease, StopRoute, TerminalState
from school_bus.package import build_manifest
from school_bus.render import cargo_filename, render_cargo


def test_sb_release_reaches_native_gate_without_external_runtime(tmp_path):
    payload = {
        "IDENTITY_CAPSULE.md": b"# SB Capsule\n",
        "SOURCE_ANCHORS.md": b"# Sources\n- primary source anchor\n",
        "REGRESSION_SET.json": b'{"cases":[],"status":"PROPOSED_UNVERIFIED"}\n',
        "QUALIFICATION_PROFILE.json": b'{"profile_id":"supabase_practitioner_v1","native_gates":["G1","G2","G3","G4","G5","G6","G7"]}\n',
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
    validate_admission(manifest, receipt)
    name = cargo_filename(manifest)
    (tmp_path / name).write_bytes(render_cargo(manifest, receipt, payload))
    route = StopRoute(
        "SB", "Supabase Platform Specialist",
        RouteRelease(
            "SUPABASE_R5", name, manifest.fingerprint(), receipt.fingerprint(),
            "supabase_practitioner_v1", "READY_FOR_BOARDING",
        ),
        None,
    )
    terminal = TerminalState(1, (route,))
    result = board(terminal, "SB", FilesystemCargoLocator(tmp_path))
    assert result.status == "READY_FOR_NATIVE"
    assert result.release_id == "SUPABASE_R5"
    assert result.package_fingerprint == manifest.fingerprint()
    assert result.receipt_fingerprint == receipt.fingerprint()
    assert result.native_qualification == "NOT_RUN"
```

Add a second test that parses the cargo JSON, changes `payload["IDENTITY_CAPSULE.md"]` to `"tampered"`, rewrites it, boards again, and asserts `status == "BLOCKED"` with `blocking_condition == "PACKAGE_FINGERPRINT_MISMATCH"`.

- [ ] **Step 2: Run acceptance test**

Run: `python -m pytest tests/test_school_bus_end_to_end.py -q`

Expected: PASS if Tasks 1-6 are complete. If RED, fix only the demonstrated transport defect under TDD; do not weaken the acceptance test.

- [ ] **Step 3: Update CI compile command**

Change `.github/workflows/tests.yml` compile/test block to:

```bash
python -m py_compile bootcamp.py fast_bootcamp.py quality_gate.py audit_gate_v5.py run_bootcamp.py school_bus/*.py
python -m pytest -q
```

Do not add runner types, secrets, services, caches, or model invocations for the bus tests.

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

State explicitly that Library is preferred storage only, attachment/upload is the fallback, cargo existence does not confer authority, and native qualification is separate from local proxy scores.

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

Before merge, inspect the full diff and verify all of the following:

1. No path converts `training_package_ready`, a local-model score, or a bootcamp outcome directly into `ADMITTED` or `QUALIFIED`.
2. Candidate building cannot create its own authoritative admission receipt.
3. Receipt validation binds exact release, stop, function, profile, supersession, and manifest fingerprint.
4. Manifest fingerprint covers exact payload file names, sizes, and hashes and excludes receipt/outer envelope to avoid recursive hashing.
5. Terminal contains both package and receipt fingerprints and never resolves `latest`.
6. Wrong passenger, stale route, tamper, forged receipt, and implicit rollback all fail closed.
7. Manual fallback reports the exact cargo identity without requiring GitHub or Library.
8. Passenger cargo contains no hidden native answer key.
9. `READY_FOR_NATIVE` still reports `native_qualification = NOT_RUN`.
10. A clean checkout/worktree passes compilation and the complete pytest suite before any PASS claim or merge.

## Acceptance Evidence Required

A successful implementation earns **PASS only for the transport mechanism** after the deterministic hostile/end-to-end suite passes on the reviewed bytes. It does not qualify SB. SB remains `NOT_RUN` for a release until a real admitted cargo package reaches the actual native SB identity and that identity passes the separate Project G1-G7 cold, false-premise, correction, boundary, adversarial, and transfer evaluation.
