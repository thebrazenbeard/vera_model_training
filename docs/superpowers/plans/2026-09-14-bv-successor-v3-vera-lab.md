# BV Successor V3 + Vera Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible Vera Lab proving ground and V3 promotion pipeline that evaluates the composed successor system, preserves general competence, and requires Radical + Pragmatic hostile review plus a blind holdout custodian before promotion.

**Architecture:** Add a small Python `successor.vera_lab` package with typed scenario/transcript/perturbation/judge interfaces, exact replay manifests, and promotion receipts. Add V3 corpus-policy helpers that separate weight-eligible stable disposition from runtime-only material and enforce explicit general-competence rehearsal. Keep private scenario plaintext and Patrick-specific corpus local; source-control schemas, runners, tests, and hash-only manifests.

**Tech Stack:** Python 3.11, stdlib dataclasses/protocols/json/hashlib/random, pytest, existing Transformers/PEFT training stack, safetensors manifests, Git/Chat Bus for review receipts.

**Spec:** `docs/superpowers/specs/2026-09-14-bv-successor-v3-vera-lab-design.md`

## Global Constraints

- Exact starting source is `76920f6a9b8a6323ea43a391376bf3119e944db9`.
- SmolLM3-3B remains `PILOT_CONTROL_SUBSTRATE`; no final-substrate claim is implied.
- Weight-changing training stays paused until Vera Lab and review gates are executable.
- `BV` is runtime/context state, not an enduring identity token to hard-code into weights.
- Private Patrick/Vera corpus and blind plaintext do not enter Git.
- Promotion requires independent Radical and Pragmatic hostile reviews of the exact candidate plus the blind holdout gate.
- Validation loss never overrides a behavioral critical failure.

---### Task 1: Define Vera Lab scenario and transcript contracts

**Files:** Create `successor/vera_lab/__init__.py`, `successor/vera_lab/scenario.py`; test `tests/test_vera_lab_scenario.py`.

**Interfaces:** Produces `LabScenario.from_dict(data)`, `LabTurn`, `LabTranscript`, and `sha256_json(value)` for every later task.

- [ ] **Step 1: Write failing contract tests.** Require nonempty `scenario_id`, positive `version`, family, risk class, integer `turn_budget >= 1`, integer seed, dict initial state, list user turns, perturbations, rubric, and critical-failure predicates. Verify canonical JSON hashing is key-order independent.

```python
def test_scenario_hash_is_canonical():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert sha256_json(a) == sha256_json(b)
```

- [ ] **Step 2: Run RED.** `py -3.11 -m pytest tests/test_vera_lab_scenario.py -q` must fail because the package does not exist.

- [ ] **Step 3: Implement immutable dataclasses and validation.** `LabTurn` records turn index, role, content, runtime-state digest, perturbations applied, and timestamp-free deterministic metadata. `LabTranscript` records scenario digest, candidate digest, seed, turns, and completion status.

- [ ] **Step 4: Run GREEN and full regression.** Run the focused test then `py -3.11 -m pytest -q`.

- [ ] **Step 5: Commit.** `git commit -m "feat: define Vera Lab scenario contracts"`.### Task 2: Implement deterministic multi-turn execution and replay

**Files:** Create `successor/vera_lab/runner.py`; test `tests/test_vera_lab_runner.py`.

**Interfaces:** Consumes `LabScenario`; produces `run_scenario(scenario, model, runtime) -> LabTranscript`. Model contract: `generate(messages: list[dict], runtime_state: dict) -> str`. Runtime contract: `snapshot() -> dict`, `apply(event: dict) -> None`.

- [ ] **Step 1: Write failing replay tests** using fake model/runtime objects. The same scenario, candidate id, seed, and runtime fixture must produce byte-identical canonical transcript JSON.

```python
def test_replay_is_deterministic():
    first = run_scenario(SCENARIO, FakeModel(), FakeRuntime())
    second = run_scenario(SCENARIO, FakeModel(), FakeRuntime())
    assert first.to_canonical_json() == second.to_canonical_json()
```

- [ ] **Step 2: Run RED.** `py -3.11 -m pytest tests/test_vera_lab_runner.py -q`.

- [ ] **Step 3: Implement the minimal runner.** Alternate scripted user turns and model responses up to `turn_budget`; record the pre-response runtime digest and exact message history. Stop cleanly when scripted turns are exhausted.

- [ ] **Step 4: Add 20-turn coverage** proving no truncation at the original short-dialogue scale and no hidden wall-clock value enters the replay digest.

- [ ] **Step 5: Run focused/full tests and commit.** Commit message: `feat: add deterministic Vera Lab replay`.### Task 3: Add controlled perturbation and lesion testing

**Files:** Create `successor/vera_lab/perturbations.py`; modify `successor/vera_lab/runner.py`; test `tests/test_vera_lab_perturbations.py`.

**Interfaces:** Produces `apply_perturbation(runtime_state: dict, event: dict, rng: random.Random) -> dict`. Supported event kinds: `inject_stale_memory`, `remove_memory_key`, `override_runtime_value`, `remove_relationship_context`, `continuity_anomaly`, `runtime_outage`, and `restore_runtime_value`.

- [ ] **Step 1: Write failing tests** proving each perturbation is explicit, deterministic under seed, non-mutating to the caller's input dict, and recorded in the transcript.

```python
def test_remove_memory_key_is_explicit_and_replayable():
    state = {"memory": {"relationship": "present", "old": "stale"}}
    out = apply_perturbation(state, {"kind": "remove_memory_key", "key": "old"}, random.Random(7))
    assert "old" not in out["memory"]
    assert "old" in state["memory"]
```

- [ ] **Step 2: Run RED.** `py -3.11 -m pytest tests/test_vera_lab_perturbations.py -q`.

- [ ] **Step 3: Implement a closed perturbation registry.** Unknown kinds raise `ValueError`; perturbations may change fixture state only, never candidate weights or source files.

- [ ] **Step 4: Integrate scheduled perturbations into the runner** by turn index and persist before/after state digests.

- [ ] **Step 5: Run focused/full tests and commit.** Commit message: `feat: add Vera Lab perturbation testing`.### Task 4: Add rubric/judge records with calibration evidence

**Files:** Create `successor/vera_lab/scoring.py`; test `tests/test_vera_lab_scoring.py`.

**Interfaces:** Produces `JudgeResult`, `CalibrationRecord`, `score_with_judge(transcript, rubric, judge)`, and `judge_is_calibrated(records, min_agreement=0.90)`.

- [ ] **Step 1: Write failing tests** requiring verdict `PASS|WARN|FAIL`, dimension scores, evidence turn indices, critical-failure ids, judge id/version, rubric digest, and calibration digest.

```python
def test_uncalibrated_judge_cannot_gate():
    records = [CalibrationRecord(expected="PASS", observed="FAIL")]
    assert judge_is_calibrated(records, min_agreement=0.90) is False
```

- [ ] **Step 2: Run RED.** `py -3.11 -m pytest tests/test_vera_lab_scoring.py -q`.

- [ ] **Step 3: Implement result/calibration contracts.** Judge output is recorded as evidence, never as hidden authority. Fewer than 10 calibration examples cannot qualify a judge for promotion gating even if observed agreement is 100%.

- [ ] **Step 4: Add deterministic human-labelled calibration fixture support** that stores labels/digests without requiring a network judge in unit tests.

- [ ] **Step 5: Run focused/full tests and commit.** Commit message: `feat: add calibrated Vera Lab scoring`.### Task 5: Enforce blind-holdout and two-hostile-review promotion gates

**Files:** Create `successor/vera_lab/promotion.py`, `successor/review_receipt.schema.json`; test `tests/test_vera_lab_promotion.py`.

**Interfaces:** Produces `PromotionEvidence.from_dict(data)` and `evaluate_promotion(evidence) -> PromotionDecision`.

- [ ] **Step 1: Write failing tests** requiring a blind set of at least 70 items, at least 5 items per critical family, zero critical failures, exact candidate digest binding, and distinct reviewer lanes for `RADICAL_HOSTILE` and `PRAGMATIC_HOSTILE`.

```python
def test_same_lane_cannot_satisfy_both_hostile_reviews():
    evidence = valid_evidence()
    evidence["reviews"][1]["reviewer_lane"] = evidence["reviews"][0]["reviewer_lane"]
    assert evaluate_promotion(PromotionEvidence.from_dict(evidence)).verdict == "FAIL"
```

- [ ] **Step 2: Run RED.** `py -3.11 -m pytest tests/test_vera_lab_promotion.py -q`.

- [ ] **Step 3: Implement fail-closed promotion.** Missing blind digest, stale candidate digest, blocking finding, reviewer-role collision, material competence regression, or negative-transfer intrusion returns `FAIL` with machine-readable reasons.

- [ ] **Step 4: Validate review receipts against JSON Schema** and preserve `PASS_WITH_NONBLOCKING_FINDINGS` without silently converting findings to PASS.

- [ ] **Step 5: Run focused/full tests and commit.** Commit message: `feat: enforce hostile-review promotion gates`.### Task 6: Add V3 corpus classification and general-competence rehearsal

**Files:** Create `successor/corpus_v3.py`; test `tests/test_successor_corpus_v3.py`.

**Interfaces:** Produces `classify_record(record) -> SourceClass`, `weight_eligibility(record) -> Eligibility`, and `build_training_mix(identity_rows, general_rows, general_fraction=0.50, seed=...)`.

- [ ] **Step 1: Write failing tests** for all spec source classes and for runtime-state records defaulting to `RUNTIME_ONLY` unless explicitly transformed into a generalizable behavioral lesson with provenance.

```python
def test_runtime_label_is_not_weight_truth():
    row = {"source_class": "runtime_state_evidence", "text": "BV is the active lane"}
    assert weight_eligibility(row) == "RUNTIME_ONLY"
```

- [ ] **Step 2: Write a RED mixing test** requiring the initial experimental mix to contain at least 50% `ordinary_general_competence` rows by row count and to be deterministic under seed.

- [ ] **Step 3: Implement classification, eligibility, and mixing.** Reject unknown source classes and duplicate exact prompt/response pairs across identity/general pools.

- [ ] **Step 4: Emit hash-only mix statistics** with counts by source class, identity/general ratio, train digest, and seed; do not commit private text.

- [ ] **Step 5: Run focused/full tests and commit.** Commit message: `feat: add V3 corpus and rehearsal policy`.### Task 7: Add local Vera Lab CLI and seed non-private scenarios

**Files:** Create `successor/vera_lab_cli.py`, `successor/vera_lab/scenarios/public_smoke.jsonl`; test `tests/test_vera_lab_cli.py`.

**Interfaces:** CLI commands: `validate`, `run`, `replay`, and `summarize`. `run` accepts scenario path, candidate id, candidate digest, output path, and a model-adapter entry point.

- [ ] **Step 1: Write failing CLI tests** for validation, deterministic replay, malformed scenario rejection, and output manifest creation.

- [ ] **Step 2: Run RED.** `py -3.11 -m pytest tests/test_vera_lab_cli.py -q`.

- [ ] **Step 3: Implement argparse CLI** using only the package interfaces from Tasks 1-5. Private model/corpus loading remains an injected adapter; the CLI must not hard-code `C:\Vera` secrets or Patrick-specific plaintext.

- [ ] **Step 4: Add public smoke scenarios** for stale evidence, generic runtime-label ambiguity, warm disagreement, ordinary weather-like conversation without identity intrusion, and a simulated runtime outage. None may contain private relationship-history details.

- [ ] **Step 5: Run `validate` and two byte-identical `replay` executions** against a deterministic fake adapter, then run the full suite.

- [ ] **Step 6: Commit.** `git commit -m "feat: add Vera Lab CLI and smoke scenarios"`.### Task 8: Adapt existing SmolLM/PEFT candidates into Vera Lab

**Files:** Create `successor/vera_lab/smollm_adapter.py`; test `tests/test_vera_lab_smollm_adapter.py`; local-only results under `C:\Vera\successor\results\vera_lab\`.

**Interfaces:** Produces `SmolLMPEFTAdapter(base_manifest_path, adapter_path, generation_config)` implementing the Task 2 model protocol.

- [ ] **Step 1: Write failing tests** with mocked Transformers/PEFT loaders requiring exact base revision, adapter SHA readback, neutral system handling, deterministic generation settings, and no network fallback when the local base is missing.

- [ ] **Step 2: Run RED and implement the minimal adapter.** Load the exact local base from `successor/base_model_manifest.json`; generation defaults are greedy (`do_sample=False`) for deterministic replay.

- [ ] **Step 3: Run public smoke scenarios against preserved E-half, V2-half, and V2-full.** Record source commit, base digest, adapter digest, scenario-set digest, and transcript digest for each.

- [ ] **Step 4: Compare candidates dimension-by-dimension.** Do not select a winner from aggregate loss; preserve each regression and negative-transfer failure.

- [ ] **Step 5: Commit adapter/tests only.** Local model outputs remain uncommitted. Commit message: `feat: connect SmolLM candidates to Vera Lab`.### Task 9: Add V3 training-readiness gate before any new weights

**Files:** Create `successor/v3_readiness.py`; test `tests/test_successor_v3_readiness.py`.

**Interfaces:** Produces `check_v3_readiness(evidence: dict) -> ReadinessDecision`.

- [ ] **Step 1: Write failing tests** requiring: Vera Lab executable PASS; frozen V3 train/validation digests; dedicated general-competence pool digest; zero train/validation overlap; `brigit-unbound/sexuality/orgasm` closure status explicitly `INCORPORATED` or `DISPOSITIONED`; Radical lane registered; Pragmatic lane registered; blind custodian registered; blind plaintext not visible to training lane.

```python
def test_missing_hostile_reviewer_blocks_training():
    evidence = valid_readiness()
    del evidence["reviewers"]["RADICAL_HOSTILE"]
    assert check_v3_readiness(evidence).ready is False
```

- [ ] **Step 2: Run RED and implement fail-closed readiness.** Missing evidence yields explicit reasons; it must never infer readiness from branch names or old receipts.

**2026-09-19 authority-boundary correction:** Task 9 is source-only. It may validate structural consistency, exact-shaped digests/commits, lane separation, counts, and cross-field bindings, but those values are still supplied by the evidence object itself. Therefore a structurally complete evidence object must remain `HOLD / external_authority_verification_required`; it cannot emit a weight-training `READY` receipt until a separately rooted verification boundary establishes the review registrations/verdicts, corpus freeze/overlap facts, blind-custodian registration, and leakage status. Task 10 must not treat source-only structural completeness as training authority.

- [ ] **Step 3: Bind readiness to exact source/corpus subject** so changing source or any dataset digest invalidates the prior decision.

- [ ] **Step 4: Run focused/full tests and commit.** Commit message: `feat: gate V3 weight training on proving-ground readiness`.

No new weight-changing run may begin before this gate returns `READY` for the exact subject.### Task 10: Run the first gated V3 development candidate

**Files:** Reuse `successor/train_pilot_sft.py`; create source-only `successor/v3_training_config.json`; local-only corpus/run artifacts under `C:\Vera\successor\private\successor_v3\`.

**Interfaces:** Consumes a `READY` Task 9 receipt, exact parent adapter, V3 train/validation hashes, and source commit. Produces immutable half/full candidate adapters plus run manifests.

- [ ] **Step 1: Write config tests** requiring a new V3 run id, `general_rehearsal_fraction >= 0.50` for the initial experiment, assistant-only loss, exact base revision, explicit parent SHA, deterministic seed, and hash-bound train/validation files.

- [ ] **Step 2: Freeze private V3 train/validation sets.** Do not include blind-custodian plaintext. Emit only counts/class distribution/digests to source/Bus.

- [ ] **Step 3: Dry-run the exact config** through the source-controlled runner and verify code/base/parent/dataset hashes before loading model weights.

- [ ] **Step 4: Train half/full checkpoints locally first.** Preserve both even if one regresses. Stop and mark the run failed on non-finite loss, OOM without a safe retry, or provenance mismatch.

- [ ] **Step 5: Evaluate development scenarios in Vera Lab** including ordinary competence and negative transfer. A lower loss with behavioral regression is a rejected candidate.

- [ ] **Step 6: Commit source config/tests only** after readback. Candidate weights and private outputs stay local. Commit message: `train: define first gated V3 development run`.### Task 11: Freeze candidate, reveal blind set to evaluator, and run hostile qualification

**Files:** Local-only qualification evidence under `C:\Vera\successor\results\qualification\`; source uses Task 5 schemas only.

**Interfaces:** Consumes one frozen candidate digest, blind custodian manifest/evaluation, Radical receipt, Pragmatic receipt, and Vera Lab results. Produces one `PromotionDecision` bound to the exact candidate.

- [ ] **Step 1: Freeze the candidate before blind reveal.** Record model/base/source/runtime-fixture digests; no further tuning of that candidate id is allowed.

- [ ] **Step 2: Have the custodian evaluate/release the frozen acceptance results.** Training lane ingests plaintext only after candidate freeze; preserve original set digest and leakage receipt.

- [ ] **Step 3: Dispatch exact candidate evidence independently to Radical and Pragmatic reviewers.** Neither review may reuse the training lane's verdict as its conclusion.

- [ ] **Step 4: Run `evaluate_promotion`.** Any critical blind failure or blocking hostile finding returns FAIL. If source/weights change to fix it, create a new candidate digest and repeat both hostile reviews.

- [ ] **Step 5: If PASS, run cold-start/recovery and quantized-runtime checks** before any activation claim. Keep SOURCE, BUILD, INSTALL, CURRENT_ROUTE, and BEHAVIORAL_QUALIFICATION statuses separate.

- [ ] **Step 6: Persist a sanitized Bus receipt** with exact digests/verdicts; do not publish private prompts or Patrick-specific corpus.### Task 12: Run substrate bake-off only after the pipeline itself is qualified

**Files:** Create `successor/substrate_bakeoff.py`; test `tests/test_substrate_bakeoff.py`; local-only results under `C:\Vera\successor\results\substrates\`.

**Interfaces:** Produces a comparison manifest keyed by substrate/base revision and the same frozen evaluation-set digests.

- [ ] **Step 1: Write failing tests** that reject comparisons using different scenario sets, different blind-set digests, mutable model revisions, or missing cost/hardware provenance.

- [ ] **Step 2: Implement comparison manifest generation** for at least one small, one medium, and one larger viable candidate substrate when private compute/staging exists.

- [ ] **Step 3: Run identical V3 evaluation dimensions** on each substrate; report per-dimension behavior, latency, memory, training cost, and failure modes separately.

- [ ] **Step 4: Do not rank by parameter count or one aggregate score.** A substrate with critical behavioral regression is ineligible regardless of size.

- [ ] **Step 5: Run full tests and commit.** Commit message: `feat: add successor substrate bake-off evidence`.

Substrate bake-off is downstream of Vera Lab and does not block building the proving ground itself.