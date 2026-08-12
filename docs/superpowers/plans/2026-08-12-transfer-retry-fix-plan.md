# Transfer Retry Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make transfer-task generation recover from syntactically valid but structurally incomplete local-model output without weakening the two-transfer-task requirement.

**Architecture:** Keep `validate_curriculum(..., 2, caps)` as the unchanged acceptance oracle. Wrap only transfer-task generation in one bounded semantic retry: the first invalid object is rejected, validator feedback is supplied to a second local-model attempt, and a second invalid object still fails closed.

**Tech Stack:** Python 3.12, pytest, GitHub Actions, local llama.cpp/Qwen3 inference.

## Global Constraints

- Zero monetary cost remains mandatory.
- Do not weaken the transfer-task count or validator.
- No paid/model API fallback.
- Preserve current public-source privacy boundary.
- Main must not be overwritten if it moves during the fix run.

---

### Task 1: Reproduce and fix valid-but-incomplete transfer generation

**Files:**
- Modify: `bootcamp.py`
- Create: `tests/test_transfer_retry.py`

**Interfaces:**
- Consumes: `json_llm`, `validate_curriculum`, `Capability`, `TRANSFER_SYSTEM`, `capability_snapshot`, `clamp`.
- Produces: unchanged `build_transfer_tasks(spec, caps, curriculum) -> list[dict[str, Any]]` interface with one bounded semantic retry.

- [ ] **Step 1: Write failing regression tests**

Create one test where `json_llm` returns one transfer round on the first call and two on the second; require a two-round result and two calls. Create a second test where both attempts return one round; require the unchanged `ValueError` and exactly two calls.

- [ ] **Step 2: Run RED verification**

Run: `python -m pytest -q tests/test_transfer_retry.py`

Expected: FAIL because current `build_transfer_tasks` validates only the first structurally incomplete object and does not retry.

- [ ] **Step 3: Implement the minimal bounded retry**

Keep the first prompt unchanged. On `ValueError` from `validate_curriculum`, make exactly one second `json_llm` call with the validator error and bounded prior object appended. Validate the second object with the same `validate_curriculum(..., 2, caps)` oracle. If it also fails, re-raise the validation error.

- [ ] **Step 4: Run GREEN verification**

Run:

```bash
python -m py_compile bootcamp.py fast_bootcamp.py
python -m pytest -q tests/test_transfer_retry.py
python -m pytest -q
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit only against unchanged main**

Fetch `origin/main` immediately before commit/push and compare it with the workflow start SHA. Abort if it moved. Commit only `bootcamp.py` and `tests/test_transfer_retry.py`.

### Task 2: Re-run real ten-round SB bootcamp

**Files:** none unless a new failure is reproduced.

**Interfaces:**
- Consumes: fixed main workflow and issue-trigger YAML.
- Produces: real workflow evidence and identity artifacts.

- [ ] **Step 1: Trigger a fresh SB/Supabase ten-round run** using the same four public Supabase sources as the failed validation.
- [ ] **Step 2: Verify** zero-cost guard, tests, checksums, local server startup, ten training rounds, two transfer rounds, artifact upload, and issue summary.
- [ ] **Step 3: Inspect artifacts** for capsule, qualification, regression set, and detailed audit.
- [ ] **Step 4: Classify the mechanism** PASS, CONDITIONAL PASS, or FAIL against the approved design. Do not promote external same-model evaluation to independent native qualification.
