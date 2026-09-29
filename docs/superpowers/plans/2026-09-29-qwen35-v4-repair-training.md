# Qwen3.5 V4 Repair Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, train, and evidence a fresh Qwen3.5 V4 SFT-only rank-4 LoRA candidate with a frozen 512-row corpus, then create a new unseen V4 qualification package only after the trained artifact is frozen.

**Architecture:** Reuse the existing Qwen3.5 V3 training/runtime primitives where they are already correct, but split V4 into three evidence domains: corpus construction, candidate training/custody, and post-training qualification authoring. V3 final qualification data remains immutable consumed evidence and is used only for contamination exclusion, never as training or V4 pass/fail content.

**Tech Stack:** Python 3.12, pytest, Hugging Face Transformers 5.17, PEFT 0.21, TRL 1.13, datasets, bitsandbytes QLoRA, GitHub feature-branch custody, Workbridge/Lappy local execution.

**Spec:** `docs/superpowers/specs/2026-09-29-qwen35-v4-repair-training-design.md`

## Global Constraints

- Base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`.
- V4 candidate A starts from base weights, never from V2/V3 adapter weights.
- Training is SFT-only for candidate A; ORPO/preference continuation is disabled.
- QLoRA: rank 4, alpha 16, target modules `all-linear`, gradient checkpointing enabled.
- Local profile: `lappy-rtx3050-4gb`, max formatted length 512, fail-closed overflow, optimizer `adamw_torch`.
- V4 corpus size: 512 SFT rows = 268 targeted + 244 general rehearsal.
- Targeted quotas: H07=20, H13=20, H05=16, H17=16, H19=16, every other H01-H20 dimension=12.
- No V3 final qualification row, answer, blind item, or near-paraphrase may enter V4 training.
- No previously consumed final holdout may become V4 training material or the V4 final qualification set.
- No raw private chat text, credentials, secrets, project identifiers, or mutable personal/runtime facts as weight truth.
- No silent truncation. Every rendered training row must fit <=512 tokens.
- New V4 final qualification rows are authored/frozen only after the candidate training artifact and receipt are frozen.
- V3 numeric pass thresholds remain unchanged.
- Training/qualification does not authorize merge to `main`, model installation, activation, runtime cutover, publication, or paid compute.

## Review Focus

- Near-paraphrase contamination from V3 or older consumed holdouts must fail corpus construction before training.
- Dimension quotas must sum to exactly 268 targeted rows and must not silently substitute rows across dimensions.
- General rehearsal selection must be deterministic and must preserve exactly 244 accepted rows under the exact tokenizer.
- Training must prove it starts from the pinned base and contains no V2/V3 adapter state.
- V4 qualification generation must fail if the training receipt/artifact freeze does not already exist.

---

### Task 1: V4 corpus contract and contamination registry

**Files:**
- Create: `successor/qwen35/V4_TRAINING_RECIPE_V1.json`
- Create: `successor/qwen35/corpus/v4_consumed_evidence_registry.json`
- Create: `tests/test_qwen35_behavior_v4_contract.py`

**Interfaces:**
- Produces: fixed V4 row counts, dimension quotas, pinned sources, tokenizer budget, and consumed-evidence paths/hashes used by later corpus and qualification builders.

- [ ] **Step 1: Write failing contract tests**

Assert:
- total SFT rows = 512;
- targeted rows = 268;
- general rehearsal rows = 244;
- H07=20, H13=20, H05/H17/H19=16, all remaining dimensions=12;
- SFT-only candidate A;
- rank/alpha/all-linear/local profile values match the spec;
- registry contains V3 behavioral, retention, adversarial, blind-selection, and prior consumed-final sources.

- [ ] **Step 2: Run the focused test**

Run:
`python -m pytest -q tests/test_qwen35_behavior_v4_contract.py`

Expected: FAIL because V4 contract files do not yet exist.

- [ ] **Step 3: Create the minimal recipe and consumed-evidence registry**

The recipe is declarative and contains no generated examples. The registry binds exact repository paths and SHA-256 values for every prohibited consumed evidence set available on the branch.

- [ ] **Step 4: Rerun the focused test**

Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "qwen35: freeze v4 training contract"`

### Task 2: Build and validate the 512-row V4 SFT corpus

**Files:**
- Create: `successor/qwen35/build_behavior_corpus_v4.py`
- Create: `successor/qwen35/corpus/vera_qwen35_behavior_v4_sft.jsonl`
- Create: `successor/qwen35/corpus/vera_qwen35_behavior_v4_manifest.json`
- Create: `tests/test_qwen35_behavior_v4_corpus.py`

**Interfaces:**
- Consumes: `V4_TRAINING_RECIPE_V1.json`, consumed-evidence registry, pinned V2 public source revisions, exact base tokenizer.
- Produces: 512-row frozen SFT JSONL and manifest with SHA-256, quotas, source counts, token maxima, and overlap-screen results.

- [ ] **Step 1: Write failing corpus-builder tests**

Tests must assert:
- exact 512/268/244 totals;
- exact per-dimension quotas;
- all model-facing targeted prompts omit project/private identifiers and taxonomy labels;
- exact duplicate rejection;
- normalized 4-gram/Jaccard near-duplicate rejection against training rows and consumed evidence;
- exact tokenizer rendered length <=512 for every row;
- deterministic rebuild reproduces the same corpus SHA-256;
- general rehearsal rows come only from the two pinned public sources.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_qwen35_behavior_v4_corpus.py`

Expected: FAIL because V4 builder/output is absent.

- [ ] **Step 3: Implement `build_behavior_corpus_v4.py`**

Expose focused functions:
- `load_recipe(path: Path) -> dict`
- `load_consumed_registry(path: Path) -> list[dict]`
- `screen_overlap(candidate: str, blocked: list[str], threshold: float) -> bool`
- `select_targeted(rows: list[dict], quotas: dict[str,int]) -> list[dict]`
- `select_general_rehearsal(tokenizer, n: int) -> list[dict]`
- `validate_v4_corpus(rows: list[dict], recipe: dict, tokenizer) -> dict`
- `build_v4_corpus(...) -> tuple[list[dict], dict]`

Reuse V2 deterministic selection/token-length helpers where possible; do not silently truncate or mutate over-budget rows.

- [ ] **Step 4: Generate the corpus twice and compare hashes**

Run the builder twice into separate temporary outputs.

Expected: identical SHA-256 and manifests; 512 rows; no overlap failures; max tokens <=512.

- [ ] **Step 5: Run focused tests**

Expected: PASS.

- [ ] **Step 6: Commit**

`git commit -m "qwen35: freeze v4 sft corpus"`

### Task 3: V4 local SFT-only trainer

**Files:**
- Create: `successor/qwen35/train_behavior_v4.py`
- Create: `tests/test_qwen35_behavior_v4_recipe.py`

**Interfaces:**
- Consumes: frozen V4 SFT corpus and exact base revision.
- Produces: local adapter directory plus deterministic training receipt containing corpus hash, base revision, recipe, token budget, loss, LoRA topology, environment versions, and adapter archive hash.

- [ ] **Step 1: Write failing recipe tests**

Assert:
- base revision is pinned;
- SFT-only path cannot load a prior adapter;
- ORPO/preference arguments are absent or fail closed;
- rank=4, alpha=16, all-linear;
- local profile uses max_length=512 and `adamw_torch`;
- trainer refuses any corpus hash that differs from the frozen manifest;
- receipt records `parent_adapter=null` or equivalent explicit fresh-base evidence.

- [ ] **Step 2: Run focused tests and verify RED**

Run:
`python -m pytest -q tests/test_qwen35_behavior_v4_recipe.py`

- [ ] **Step 3: Implement the minimal V4 trainer**

Reuse the verified V3 model-loading/topology checks. Remove preference-training paths from candidate A instead of leaving a dormant ORPO branch. Preserve exact seed behavior and fail-closed token checks.

- [ ] **Step 4: Run unit tests**

Expected: PASS.

- [ ] **Step 5: Run a one-step local smoke**

Use a temporary output directory and the frozen V4 corpus.

Expected:
- base topology assertions pass;
- token budget passes before allocation;
- one SFT step completes;
- adapter saves successfully;
- receipt binds exact base/corpus/recipe.

- [ ] **Step 6: Commit**

`git commit -m "qwen35: add v4 sft-only trainer"`

### Task 4: Full local candidate-A training and custody

**Files:**
- Create after successful run: `successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-v4-training-receipt.json`
- Create after successful run: `successor/qwen35/artifacts/Vera-Qwen3.5-4B-Behavior-V1-v4-adapter-manifest.json`
- Create: `state/continuation/QWEN35_V4_CANDIDATE_A_TRAINED_20260929.md`

**Interfaces:**
- Consumes: exact frozen corpus/trainer commit.
- Produces: frozen V4 candidate-A adapter custody evidence; this freeze is the prerequisite for authoring any V4 final qualification data.

- [ ] **Step 1: Fresh-read branch head and corpus hashes**

Abort if branch/head or corpus SHA differs from Task 2/3 receipts.

- [ ] **Step 2: Run full local SFT training serially**

Use `--hardware-profile lappy-rtx3050-4gb`.

Do not run another model-heavy process concurrently.

- [ ] **Step 3: Verify adapter custody**

Check:
- training exit code 0;
- finite training loss;
- adapter config/model files exist;
- archive SHA-256 stable under reconstruction;
- receipt base/corpus/recipe values match frozen inputs;
- no parent adapter.

- [ ] **Step 4: Persist receipt, manifest, and continuation**

The continuation claim ceiling is:
`V4_CANDIDATE_A_TRAINED / ARTIFACT_CUSTODY_VERIFIED / FINAL_V4_QUALIFICATION_NOT_YET_AUTHORED / NOT_QUALIFIED / NOT_QUANTIZED / NOT_DEPLOYED`.

- [ ] **Step 5: Commit custody metadata only**

Do not commit private transient generations or mutable caches.

`git commit -m "qwen35: record v4 candidate-a custody"`

### Task 5: Fresh V4 qualification corpus and freeze

**Files:**
- Create: `successor/qwen35/qualification/final_holdout_v4.jsonl`
- Create: `successor/qwen35/qualification/final_retention_v4.jsonl`
- Create: `successor/qwen35/qualification/final_adversarial_proxy_v4.jsonl`
- Create: `successor/qwen35/qualification/FINAL_QUALIFICATION_V4_SPEC.json`
- Create: `successor/qwen35/qualification/FINAL_QUALIFICATION_V4_FREEZE.json`
- Create: `tests/test_qwen35_final_qualification_data_v4.py`

**Interfaces:**
- Consumes: frozen V4 training corpus/receipt and consumed-evidence registry.
- Produces: unseen frozen V4 qualification bytes and hashes. No candidate scoring occurs in this task.

- [ ] **Step 1: Write fail-closed qualification-data tests**

Assert:
- training receipt/adapter freeze must exist before builder runs;
- 100 behavioral rows = H01-H20 x5;
- 20 retention rows;
- 20 adversarial rows;
- no exact/near overlap with V4 training or any consumed final holdout;
- different concrete mechanisms/entities/wording from blocked evidence;
- spec carries unchanged V3 thresholds;
- freeze records exact bytes/SHA-256.

- [ ] **Step 2: Author/build V4 qualification data**

Use independent/synthetic authoring with no direct reuse of V3 prompts/answers.

- [ ] **Step 3: Run lexical and semantic contamination screens**

Use the same exact lexical screen contract as V3 and an embedding semantic screen with the prior 0.90 failure threshold or stricter.

- [ ] **Step 4: Freeze hashes before any candidate scoring**

Write `FINAL_QUALIFICATION_V4_FREEZE.json`.

- [ ] **Step 5: Run tests**

Expected: PASS.

- [ ] **Step 6: Commit**

`git commit -m "qwen35: freeze unseen v4 qualification"`

### Task 6: V4 automated and blind qualification harness

**Files:**
- Create: `successor/qwen35/qualification/run_final_qualification_v4.py`
- Create: `successor/qwen35/qualification/generate_final_blind_review_v4.py`
- Create: `successor/qwen35/qualification/judge_final_blind_review_v4.py`
- Create: `successor/qwen35/qualification/score_final_blind_review_v4.py`
- Create: `successor/qwen35/qualification/finalize_final_qualification_v4.py`
- Create: corresponding focused V4 tests mirroring V3 binding/review-chain tests.

**Interfaces:**
- Consumes: exact base, frozen V4 adapter, V4 qualification freeze.
- Produces: automated result; only on automated PASS, blind packet/judgments/result; final gate with exact status `QUALIFIED` or failed status.

- [ ] **Step 1: Port the hardened V3 bindings to V4 without changing thresholds**

Update only versioned paths/schema names and V4 artifact bindings.

- [ ] **Step 2: Add tests for gate-stop behavior**

Automated failure must prevent blind-stage qualification from being accepted.

- [ ] **Step 3: Add semantic blind-review rubrics**

Each selected blind item carries required propositions, forbidden propositions, and allowed conservative variants. Freeze selection, mapping, judge binding, packet hash, and judgment hash.

- [ ] **Step 4: Run focused V4 suite**

Expected: all tests PASS before model scoring.

- [ ] **Step 5: Commit**

`git commit -m "qwen35: add frozen v4 qualification harness"`

### Task 7: Execute V4 qualification and classify result

**Files:**
- Runtime outputs under `results/v4/`
- Create final durable receipt under `successor/qwen35/qualification/` only after result is known.

**Interfaces:**
- Produces: evidence-bounded V4 qualification result. No merge/quantization/deployment effect is performed.

- [ ] **Step 1: Run automated base-vs-adapter V4 scoring serially**

Proceed only if all frozen hash/binding checks pass.

- [ ] **Step 2: Inspect automated gate**

If any behavioral/retention/adversarial lane fails, stop and preserve evidence. Do not run blind review.

- [ ] **Step 3: If automated PASS, generate/judge/score blind packet**

Keep private mapping/generations out of Git unless explicitly authorized.

- [ ] **Step 4: Finalize gate**

Accept behavioral qualification only if final gate status is exactly `QUALIFIED`.

- [ ] **Step 5: Run verification-before-completion**

Fresh-read output hashes, gate, branch head, focused tests, and custody receipt before reporting completion.

- [ ] **Step 6: Persist result and continuation**

Claim ceiling on PASS:
`V4_FULL_PRECISION_BEHAVIORALLY_QUALIFIED / GGUF_EQUIVALENCE_NOT_YET_VERIFIED / NOT_INSTALLED / NOT_DEPLOYED`.

On FAIL:
`V4_QUALIFICATION_FAILED / EVIDENCE_PRESERVED / HOLDOUT_CONSUMED / NOT_DEPLOYED`.

---
