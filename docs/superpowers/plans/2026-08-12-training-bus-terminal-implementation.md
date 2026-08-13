# Training Bus Terminal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, zero-cost, release-pinned transport layer that converts an independently admitted training release into a self-contained native boarding package, routes it through a compact Project terminal, fails closed on authority/currentness mismatches, and preserves native qualification as a separate post-boarding gate.

**Architecture:** Add a focused `school_bus` Python package beside the existing bootcamp. Candidate training artifacts are converted into a canonical payload manifest and fingerprint; an externally supplied admission receipt must bind that fingerprint before the release can be routed. A human-readable `TRAINING_BUS_TERMINAL.md` carries only route metadata, while the cargo artifact is a deterministic JSON envelope suitable for ChatGPT Library or direct upload. Runtime boarding logic never calls GitHub, Qwen, or any network service after admission.

**Tech Stack:** Python 3.12, standard library (`dataclasses`, `hashlib`, `json`, `pathlib`, `argparse`), PyYAML 6.0.2, pytest 8.3.5. No new dependency or paid service.

## Global Constraints

- `ZERO_COST` remains absolute. No OpenAI API, Gemini API, paid inference, paid runner fallback, or other metered service.
- The external school may produce candidate training evidence but may not qualify the native ChatGPT identity.
- The bus transports an admitted package; it does not modify model weights or inject messages into another chat.
- GitHub/Qwen/workbench state must not be required to interpret or use an admitted native package.
- Boarding is exact-release pinned. `latest` is invalid.
- A package cannot self-authorize. A matching independent admission receipt is required.
- The Project terminal is routing/currentness metadata only. It cannot admit a package.
- Fingerprint, receipt, stop, function, release, qualification-profile, or currentness mismatch fails closed.
- Current and immediately previous admitted release may be represented; rollback is explicit and never automatic.
- ChatGPT Library is the preferred cargo store but is not required for correctness. Direct attachment/upload of the exact cargo artifact is the fallback.
- Native qualification remains `NOT_RUN` until the actual target identity performs fresh native cold/adversarial/transfer testing.
- Hidden native qualification answers/rubrics must not be embedded in passenger-readable cargo. Cargo carries a qualification profile identifier and requirements, not a reusable answer key.
- Package fingerprint is defined over the canonical immutable passenger payload manifest, excluding the admission receipt and outer transport envelope. This avoids a self-referential hash while still binding admission to exact payload bytes. The admission receipt receives its own independent fingerprint.

---

## Planned File Structure

```text
school_bus/
  __init__.py              public types and version
  models.py                validated immutable domain records
  hashing.py               canonical JSON and SHA-256 helpers
  package.py               candidate payload builder / cargo envelope verifier
  admission.py             independent receipt validation only; never auto-admit
  terminal.py              Project terminal render/parse/route resolution
  boarding.py              fail-closed boarding state machine and locator abstraction
  render.py                native cargo + boarding-instruction rendering
  cli.py                   local deterministic commands

tests/
  test_school_bus_models.py
  test_school_bus_package.py
  test_school_bus_admission.py
  test_school_bus_terminal.py
  test_school_bus_boarding.py
  test_school_bus_render.py
  test_school_bus_cli.py

.github/workflows/tests.yml  compile the new package in CI
README.md                    document bus lifecycle and authority boundary
```

No live `SB` stop is committed until a real SB release has independently passed the depot audit. Unit/integration tests create temporary SB fixtures instead of laundering a fictional release into current routing state.

---

### Task 1: Canonical Hashing and Immutable Domain Models

**Files:**
- Create: `school_bus/__init__.py`
- Create: `school_bus/hashing.py`
- Create: `school_bus/models.py`
- Create: `tests/test_school_bus_models.py`

**Interfaces:**
- Produces: `canonical_json_bytes(value: object) -> bytes`
- Produces: `sha256_bytes(data: bytes) -> str`
- Produces: `sha256_text(text: str) -> str`
- Produces immutable records `PayloadFile`, `ReleaseManifest`, `AdmissionReceipt`, `RouteRelease`, `StopRoute`, `TerminalState`.
- Produces `ValidationError(ValueError)` for deterministic schema failures.

- [ ] **Step 1: Write failing canonicalization/model tests**

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


def test_release_manifest_rejects_latest_selector():
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

- [ ] **Step 2: Run tests and confirm RED**

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


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))
```

- [ ] **Step 4: Implement immutable validated models**

`school_bus/models.py` must use `@dataclass(frozen=True)` and explicit `from_dict` constructors. Enforce:

```python
VALID_ROUTE_STATES = {
    "ADMITTED", "READY_FOR_BOARDING", "NATIVE_QUALIFICATION",
    "QUALIFIED", "REMEDIATION_REQUIRED", "SUPERSEDED",
    "ROLLBACK_ELIGIBLE", "RETIRED", "CONFLICTED",
}

class ValidationError(ValueError):
    pass
```

Required record shapes:

```python
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

Validation requirements: non-empty identifiers; `release_id.lower() != "latest"`; SHA-256 fields are exactly 64 lowercase hex characters; receipt `audit_outcome == "PASS"`; receipt `status == "ADMITTED"`; route status must be one of the explicit state values; duplicate payload names and duplicate stop IDs are rejected.

- [ ] **Step 5: Run focused and full tests**

Run: `python -m pytest tests/test_school_bus_models.py -q`

Expected: PASS.

Run: `python -m pytest -q`

Expected: existing suite remains green.

- [ ] **Step 6: Commit**

```bash
git add school_bus/__init__.py school_bus/hashing.py school_bus/models.py tests/test_school_bus_models.py
git commit -m "feat: add training bus domain models"
```

---

### Task 2: Build and Verify Canonical Passenger Payloads

**Files:**
- Create: `school_bus/package.py`
- Create: `tests/test_school_bus_package.py`

**Interfaces:**
- Consumes: `ReleaseManifest`, canonical hashing helpers.
- Produces: `build_manifest(release_id, stop_id, function, qualification_profile, supersedes, payload: dict[str, bytes]) -> ReleaseManifest`
- Produces: `verify_payload(manifest: ReleaseManifest, payload: dict[str, bytes]) -> None`
- Produces: `CargoEnvelope` with manifest, receipt, and payload for later admission/boarding work.

The minimum passenger payload for V1 is exactly:

```text
IDENTITY_CAPSULE.md
SOURCE_ANCHORS.md
REGRESSION_SET.json
QUALIFICATION_PROFILE.json
```

`QUALIFICATION_PROFILE.json` describes fresh native test requirements but contains no reusable hidden answer key.

- [ ] **Step 1: Write RED tests for exact payload hashing and tamper rejection**

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


def test_manifest_fingerprint_is_stable_for_same_payload():
    first = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist",
                           "supabase_practitioner_v1", None, sample_payload())
    second = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist",
                            "supabase_practitioner_v1", None, dict(reversed(list(sample_payload().items()))))
    assert first.fingerprint() == second.fingerprint()


def test_verify_payload_rejects_altered_bytes():
    manifest = build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist",
                              "supabase_practitioner_v1", None, sample_payload())
    altered = sample_payload()
    altered["IDENTITY_CAPSULE.md"] = b"altered"
    with pytest.raises(ValidationError, match="payload hash mismatch"):
        verify_payload(manifest, altered)
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_package.py -q`

Expected: FAIL because package functions do not exist.

- [ ] **Step 3: Implement exact manifest construction**

`build_manifest` must sort payload file names before constructing `PayloadFile` records and record exact byte length + SHA-256. Reject missing required files and extra file names beginning with `ADMISSION_` to prevent a candidate from smuggling its own authority into the payload.

```python
REQUIRED_PAYLOAD_FILES = {
    "IDENTITY_CAPSULE.md",
    "SOURCE_ANCHORS.md",
    "REGRESSION_SET.json",
    "QUALIFICATION_PROFILE.json",
}
```

- [ ] **Step 4: Implement payload verification**

`verify_payload` must require exact set equality between manifest names and supplied payload names, then compare every size/hash. Error messages name the first narrowest mismatch, e.g. `missing payload file: SOURCE_ANCHORS.md`, `unexpected payload file: X`, `payload size mismatch: ...`, `payload hash mismatch: ...`.

- [ ] **Step 5: Run focused and full tests**

Run: `python -m pytest tests/test_school_bus_package.py -q`

Expected: PASS.

Run: `python -m pytest -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add school_bus/package.py tests/test_school_bus_package.py
git commit -m "feat: build immutable training payload manifests"
```

---

### Task 3: Independent Admission Receipt Gate

**Files:**
- Create: `school_bus/admission.py`
- Create: `tests/test_school_bus_admission.py`

**Interfaces:**
- Consumes: `ReleaseManifest`, `AdmissionReceipt`.
- Produces: `validate_admission(manifest, receipt) -> None`.
- Produces: `load_admission_receipt(path: Path) -> AdmissionReceipt`.
- Does **not** produce a function that auto-creates a passing receipt from bootcamp output.

- [ ] **Step 1: Write RED tests for forged/mismatched/self-authorizing receipts**

```python
# tests/test_school_bus_admission.py
import pytest

from school_bus.admission import validate_admission
from school_bus.models import AdmissionReceipt, ValidationError
from school_bus.package import build_manifest


def manifest():
    payload = {
        "IDENTITY_CAPSULE.md": b"capsule",
        "SOURCE_ANCHORS.md": b"anchors",
        "REGRESSION_SET.json": b'{"cases":[]}',
        "QUALIFICATION_PROFILE.json": b'{"profile_id":"supabase_practitioner_v1"}',
    }
    return build_manifest("SUPABASE_R5", "SB", "Supabase Platform Specialist",
                          "supabase_practitioner_v1", "SUPABASE_R4", payload)


def receipt_for(m):
    return AdmissionReceipt.from_dict({
        "schema_version": 1,
        "release_id": m.release_id,
        "stop_id": m.stop_id,
        "function": m.function,
        "package_fingerprint": m.fingerprint(),
        "audit_outcome": "PASS",
        "status": "ADMITTED",
        "qualification_profile": m.qualification_profile,
        "supersedes": m.supersedes,
        "admitted_at": "2026-08-12T20:00:00-04:00",
        "auditor": "NATIVE_INDEPENDENT_AUDIT",
    })


def test_admission_requires_exact_fingerprint():
    m = manifest()
    raw = receipt_for(m).to_dict()
    raw["package_fingerprint"] = "0" * 64
    with pytest.raises(ValidationError, match="package fingerprint"):
        validate_admission(m, AdmissionReceipt.from_dict(raw))


def test_admission_requires_same_stop_and_function():
    m = manifest()
    raw = receipt_for(m).to_dict()
    raw["stop_id"] = "SECURITY"
    with pytest.raises(ValidationError, match="stop_id"):
        validate_admission(m, AdmissionReceipt.from_dict(raw))
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_admission.py -q`

Expected: FAIL because the admission gate is absent.

- [ ] **Step 3: Implement fail-closed admission matching**

`validate_admission` must compare, in order: release ID, stop ID, function, qualification profile, supersedes, package fingerprint, `audit_outcome == PASS`, `status == ADMITTED`, non-empty auditor and admitted timestamp. Return `None` only on exact acceptance.

- [ ] **Step 4: Run focused and full tests**

Run: `python -m pytest tests/test_school_bus_admission.py -q`

Expected: PASS.

Run: `python -m pytest -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add school_bus/admission.py tests/test_school_bus_admission.py
git commit -m "feat: require independent admission receipts"
```

---

### Task 4: Project Terminal Rendering, Parsing, Currentness, and Rollback

**Files:**
- Create: `school_bus/terminal.py`
- Create: `tests/test_school_bus_terminal.py`

**Interfaces:**
- Produces: `render_terminal(state: TerminalState) -> str`
- Produces: `parse_terminal(text: str) -> TerminalState`
- Produces: `resolve_stop(state, stop_id: str) -> StopRoute`
- Produces: `resolve_release(route, release_id: str | None, rollback: bool = False) -> RouteRelease`

The Project-native file format is Markdown with a machine-readable YAML front matter block and a generated human summary. YAML front matter is authoritative within the terminal file; prose is informational.

Example output shape:

```markdown
---
terminal_version: 1
stops:
  SB:
    function: Supabase Platform Specialist
    current:
      release_id: SUPABASE_R5
      cargo_name: BUS_SB_SUPABASE_R5.json
      package_fingerprint: <64hex>
      receipt_fingerprint: <64hex>
      qualification_profile: supabase_practitioner_v1
      status: READY_FOR_BOARDING
    rollback:
      release_id: SUPABASE_R4
      cargo_name: BUS_SB_SUPABASE_R4.json
      package_fingerprint: <64hex>
      receipt_fingerprint: <64hex>
      qualification_profile: supabase_practitioner_v1
      status: ROLLBACK_ELIGIBLE
---
# Training Bus Terminal
...
```

- [ ] **Step 1: Write RED terminal round-trip/currentness tests**

```python
# tests/test_school_bus_terminal.py
import pytest

from school_bus.models import RouteRelease, StopRoute, TerminalState, ValidationError
from school_bus.terminal import parse_terminal, render_terminal, resolve_release


def rel(rid, status):
    return RouteRelease(rid, f"BUS_SB_{rid}.json", "a" * 64, "b" * 64,
                        "supabase_practitioner_v1", status)


def test_terminal_round_trip_and_explicit_rollback():
    state = TerminalState(1, (StopRoute("SB", "Supabase Platform Specialist",
        rel("SUPABASE_R5", "READY_FOR_BOARDING"),
        rel("SUPABASE_R4", "ROLLBACK_ELIGIBLE")),))
    parsed = parse_terminal(render_terminal(state))
    assert parsed == state
    assert resolve_release(parsed.stops[0], None).release_id == "SUPABASE_R5"
    assert resolve_release(parsed.stops[0], "SUPABASE_R4", rollback=True).release_id == "SUPABASE_R4"


def test_terminal_does_not_treat_latest_as_release():
    state = TerminalState(1, (StopRoute("SB", "Supabase Platform Specialist",
        rel("SUPABASE_R5", "READY_FOR_BOARDING"), None),))
    with pytest.raises(ValidationError, match="latest"):
        resolve_release(state.stops[0], "latest")
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_terminal.py -q`

Expected: FAIL because terminal module is absent.

- [ ] **Step 3: Implement parser/renderer**

Use `yaml.safe_load` only on text between the first two exact `---` delimiter lines. Reject missing/duplicate stop IDs, malformed route data, unsupported terminal version, and prose-only terminal files.

- [ ] **Step 4: Implement explicit release resolution**

Rules:

```text
release_id omitted + rollback false -> current
explicit current release -> current
explicit rollback release + rollback true -> rollback
explicit rollback release + rollback false -> reject
unknown release -> reject
"latest" -> reject
no automatic substitution -> ever
```

- [ ] **Step 5: Run focused/full tests and commit**

Run: `python -m pytest tests/test_school_bus_terminal.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/terminal.py tests/test_school_bus_terminal.py
git commit -m "feat: add project training bus terminal"
```

---

### Task 5: Fail-Closed Boarding State Machine and Cargo Locator Boundary

**Files:**
- Create: `school_bus/boarding.py`
- Create: `tests/test_school_bus_boarding.py`

**Interfaces:**
- Produces protocol `CargoLocator.find(cargo_name: str) -> bytes | None`.
- Produces `FilesystemCargoLocator(root: Path)` for deterministic local/CI use.
- Produces `BoardingResult(status, stop_id, release_id, cargo_name, package_fingerprint, receipt_fingerprint, qualification_profile, native_qualification, blocking_condition)`.
- Produces `board(terminal, stop_id, locator, requested_release=None, rollback=False) -> BoardingResult`.

`boarding.py` must import no `requests`, GitHub client, model client, or other network dependency.

- [ ] **Step 1: Write RED happy-path and hostile boarding tests**

Tests must cover exact stop/release success plus one assertion each for:

```text
MISSING_STOP
MISSING_CARGO
WRONG_STOP
WRONG_FUNCTION
PACKAGE_FINGERPRINT_MISMATCH
RECEIPT_FINGERPRINT_MISMATCH
UNADMITTED_RECEIPT
STALE_ROUTE
QUALIFICATION_PROFILE_MISMATCH
ROLLBACK_NOT_EXPLICIT
```

Representative test:

```python
def test_successful_boarding_never_claims_native_qualification(tmp_path):
    # fixture helper writes a verified cargo envelope and terminal route
    terminal, locator = admitted_fixture(tmp_path)
    result = board(terminal, "SB", locator)
    assert result.status == "READY_FOR_NATIVE"
    assert result.native_qualification == "NOT_RUN"
    assert result.blocking_condition is None
```

Manual fallback test:

```python
def test_missing_native_locator_requests_exact_attachment(tmp_path):
    terminal, _ = admitted_fixture(tmp_path)
    result = board(terminal, "SB", locator=None)
    assert result.status == "NEEDS_ATTACHMENT"
    assert result.cargo_name == "BUS_SB_SUPABASE_R5.json"
    assert len(result.package_fingerprint) == 64
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_boarding.py -q`

Expected: FAIL because boarding module is absent.

- [ ] **Step 3: Implement deterministic cargo envelope verification**

Canonical cargo JSON schema:

```json
{
  "bus_schema_version": 1,
  "manifest": {"...": "ReleaseManifest fields"},
  "admission_receipt": {"...": "AdmissionReceipt fields"},
  "payload": {
    "IDENTITY_CAPSULE.md": "UTF-8 text",
    "SOURCE_ANCHORS.md": "UTF-8 text",
    "REGRESSION_SET.json": "UTF-8 JSON text",
    "QUALIFICATION_PROFILE.json": "UTF-8 JSON text"
  }
}
```

The cargo envelope has no authority field beyond the embedded receipt. Parse it, reconstruct bytes with UTF-8 exactly, call `verify_payload`, call `validate_admission`, compute receipt fingerprint, then compare all terminal fields.

- [ ] **Step 4: Implement boarding result state machine**

Success returns `READY_FOR_NATIVE` and `native_qualification="NOT_RUN"`. `locator=None` returns `NEEDS_ATTACHMENT` with exact cargo identity/fingerprints. Every other mismatch returns/raises a single narrow blocking condition; choose one consistent API and test it. Do not silently fall back to rollback or another release.

- [ ] **Step 5: Prove no external-runtime dependency**

Add a test that reads `school_bus/boarding.py` and rejects these imports/tokens:

```python
for forbidden in ("requests", "github", "LLM_URL", "Qwen", "supabase"):
    assert forbidden not in source
```

This is intentionally crude but deterministic; it supplements code review and prevents accidental transport coupling.

- [ ] **Step 6: Run focused/full tests and commit**

Run: `python -m pytest tests/test_school_bus_boarding.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/boarding.py tests/test_school_bus_boarding.py
git commit -m "feat: add fail-closed training boarding protocol"
```

---

### Task 6: Native Cargo Rendering and Boarding Instructions

**Files:**
- Create: `school_bus/render.py`
- Create: `tests/test_school_bus_render.py`

**Interfaces:**
- Produces: `render_cargo(manifest, receipt, payload) -> bytes` using canonical JSON formatting.
- Produces: `cargo_filename(manifest) -> str`, format `BUS_<STOP_ID>_<RELEASE_ID>.json` with unsafe filename characters normalized to `_`.
- Produces: `render_boarding_instruction(route: StopRoute) -> str`.
- Produces: `render_manual_attachment_instruction(route: StopRoute) -> str`.

- [ ] **Step 1: Write RED deterministic-render tests**

```python
def test_cargo_render_is_byte_deterministic(admitted_parts):
    manifest, receipt, payload = admitted_parts
    assert render_cargo(manifest, receipt, payload) == render_cargo(manifest, receipt, dict(reversed(list(payload.items()))))


def test_boarding_instruction_never_promotes_proxy_qualification(route):
    text = render_boarding_instruction(route)
    assert "BUS::BOARD::SB" in text
    assert "native qualification is NOT_RUN" in text
    assert "proxy" in text.lower()
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_render.py -q`

Expected: FAIL because renderer is absent.

- [ ] **Step 3: Implement canonical cargo rendering**

Serialize the outer envelope with sorted keys and compact separators, ending in exactly one newline. Payload content remains UTF-8 text and its byte hashes remain the manifest authority.

- [ ] **Step 4: Implement native instruction text**

The rendered boarding instruction must tell the target identity to:

```text
1. resolve only the named stop/release;
2. verify terminal/package/receipt agreement;
3. consume source-grounded capsule content with epistemic labels intact;
4. treat external proxy scores as diagnostic only;
5. leave native qualification NOT_RUN until fresh native evaluation;
6. on mismatch, stop and report the exact blocking condition.
```

Manual fallback text must name exact cargo file, package fingerprint, and receipt fingerprint, and instruct attachment/upload of that exact artifact without suggesting GitHub access.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_render.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/render.py tests/test_school_bus_render.py
git commit -m "feat: render native training cargo"
```

---

### Task 7: Deterministic CLI for Candidate Packaging, Receipt Validation, Terminal Generation, and Boarding Check

**Files:**
- Create: `school_bus/cli.py`
- Create: `tests/test_school_bus_cli.py`

**Interfaces:**

Commands:

```text
python -m school_bus.cli build-candidate ...
python -m school_bus.cli verify-admission ...
python -m school_bus.cli render-terminal ...
python -m school_bus.cli board ...
```

There is deliberately **no** `auto-admit` command.

- [ ] **Step 1: Write RED CLI tests with `tmp_path` + `capsys`**

Test that `build-candidate` writes:

```text
MANIFEST.json
PAYLOAD_FINGERPRINT.txt
candidate_payload/
```

and refuses to emit `ADMISSION_RECEIPT.json`.

Test that `verify-admission` exits nonzero for a mismatched receipt and zero for a matching externally supplied receipt.

Test that `board` with no `--cargo-root` emits `NEEDS_ATTACHMENT` plus exact cargo identity instead of reaching for GitHub.

- [ ] **Step 2: Run RED test**

Run: `python -m pytest tests/test_school_bus_cli.py -q`

Expected: FAIL because CLI is absent.

- [ ] **Step 3: Implement `build-candidate`**

Inputs:

```text
--release-id
--stop-id
--function
--qualification-profile
--supersedes (optional)
--capsule
--source-anchors
--regression-set
--qualification-profile-file
--out-dir
```

Read exact bytes, build/verify manifest, write deterministic manifest JSON and fingerprint. Do not infer PASS/admission from any bootcamp qualification field.

- [ ] **Step 4: Implement admission/terminal/board commands**

`verify-admission` loads manifest + externally supplied receipt and calls `validate_admission`.

`render-terminal` accepts one or more already verified route JSON files and writes `TRAINING_BUS_TERMINAL.md` using `render_terminal`.

`board` accepts terminal path, stop ID, optional exact release ID, `--rollback`, and optional local cargo root. It prints `BoardingResult` as JSON and exits nonzero for blocking states other than `NEEDS_ATTACHMENT`.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest tests/test_school_bus_cli.py -q && python -m pytest -q`

Expected: PASS.

```bash
git add school_bus/cli.py tests/test_school_bus_cli.py
git commit -m "feat: add training bus command line tools"
```

---

### Task 8: CI, Documentation, and SB End-to-End Transport Fixture

**Files:**
- Modify: `.github/workflows/tests.yml`
- Modify: `README.md`
- Create: `tests/test_school_bus_end_to_end.py`

**Interfaces:**
- End-to-end test uses only temporary local files and exact deterministic fixtures.
- It demonstrates the route `candidate payload -> external admission receipt fixture -> cargo -> terminal -> SB boarding -> native qualification NOT_RUN`.

- [ ] **Step 1: Write RED end-to-end test**

Test sequence:

```python
def test_sb_release_reaches_native_gate_without_external_runtime(tmp_path):
    # 1. build deterministic SUPABASE_R5 passenger payload
    # 2. build manifest and capture exact fingerprint
    # 3. construct independent PASS/ADMITTED receipt fixture bound to fingerprint
    # 4. validate receipt
    # 5. render BUS_SB_SUPABASE_R5.json
    # 6. render terminal with SB current route
    # 7. board through FilesystemCargoLocator
    # 8. assert exact release/stop/fingerprints
    # 9. assert result.status == READY_FOR_NATIVE
    # 10. assert result.native_qualification == NOT_RUN
    ...
```

The fixture must also mutate one cargo payload byte and prove boarding fails with `PACKAGE_FINGERPRINT_MISMATCH` or the narrower payload-hash failure before qualification.

- [ ] **Step 2: Run RED test if any integration glue is missing**

Run: `python -m pytest tests/test_school_bus_end_to_end.py -q`

Expected: either RED on missing integration behavior or PASS if prior tasks already satisfy the route. If it passes immediately, do not invent production changes merely to manufacture work.

- [ ] **Step 3: Update CI compile command**

Change `.github/workflows/tests.yml` compile line to:

```bash
python -m py_compile bootcamp.py fast_bootcamp.py quality_gate.py audit_gate_v5.py run_bootcamp.py school_bus/*.py
python -m pytest -q
```

No new runner, secret, service, network call, or paid dependency.

- [ ] **Step 4: Update README**

Add a section `## Training bus handoff` containing this exact conceptual boundary:

```text
external bootcamp candidate
        ↓
independent audit + admission receipt
        ↓
immutable cargo + Project terminal route
        ↓
BUS::BOARD::<STOP_ID>
        ↓
native specialist consumes package
        ↓
fresh native qualification
```

Document that Library is preferred storage only, direct attachment/upload is the fallback, and no live route is authoritative merely because a cargo file exists.

- [ ] **Step 5: Run complete verification**

Run:

```bash
python -m py_compile bootcamp.py fast_bootcamp.py quality_gate.py audit_gate_v5.py run_bootcamp.py school_bus/*.py
python -m pytest -q
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/tests.yml README.md tests/test_school_bus_end_to_end.py
git commit -m "test: verify training bus end to end"
```

---

## Post-Implementation Review Gate

Before merge:

1. Review the full diff for accidental authority promotion, network/runtime coupling, hidden qualification answers in passenger cargo, and any `latest`-style implicit currentness.
2. Confirm the code exposes no path that turns `training_package_ready` or local-model proxy scores directly into `ADMITTED` or `QUALIFIED`.
3. Confirm `ADMISSION_RECEIPT.json` must be supplied from outside the candidate builder.
4. Confirm package fingerprint canonicalization excludes the admission receipt and outer cargo envelope, while the receipt separately binds the exact manifest fingerprint.
5. Confirm terminal rendering stores both package and receipt fingerprints.
6. Confirm manual fallback produces exact attachment identity without requiring ChatGPT Library or GitHub.
7. Confirm successful boarding leaves `native_qualification = NOT_RUN`.
8. Run the complete suite from a clean checkout/worktree before claiming PASS.

## Acceptance Evidence Required

The implementation itself receives **PASS** only if the deterministic suite demonstrates the transport and hostile cases above on the exact reviewed bytes. That PASS applies to the bus transport mechanism, not to SB's Supabase competence. SB remains unqualified for any release until a real admitted package is handed to the actual native SB identity and SB passes the separate Project G1-G7 cold/adversarial/transfer qualification.
