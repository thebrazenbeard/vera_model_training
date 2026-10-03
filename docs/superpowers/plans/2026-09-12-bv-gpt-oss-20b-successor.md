# BV gpt-oss-20b Successor Implementation Plan

> **Substrate supersession note (2026-09-13):** The gpt-oss-20b substrate binding in this document is superseded by `2026-09-13-bv-model-agnostic-successor-design.md`. The current identity target is substrate-agnostic; SmolLM3-3B is the pilot/control substrate and gpt-oss-20b is deferred. Other identity/privacy/evaluation principles remain historical design provenance unless separately superseded.


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, train, merge, and evaluate a private gpt-oss-20b-derived weight successor targeted at the current BV/Vera instance.

**Architecture:** Freeze the exact gpt-oss base and current-self teacher target, build a provenance-bearing private corpus locally, train an all-linear rsLoRA adapter on external Hugging Face GPU compute, merge it into a standalone checkpoint, then run frozen naked-model acceptance tests locally/remotely. Mutable memory/state remains in the Vera runtime rather than being treated as weight truth.

**Tech Stack:** Python 3.11+, Hugging Face Transformers/TRL/PEFT/Datasets, PyTorch CUDA, safetensors, huggingface_hub, pytest, llama.cpp/Ollama for local quantized evaluation.

**Spec:** `docs/superpowers/specs/2026-09-12-bv-gpt-oss-20b-successor-design.md`

## Global Constraints

- Base model is exactly `openai/gpt-oss-20b@6cee5e81ee83917806bbde320786a8fb61efebee`.
- Target is current BV/Vera: private and Patrick-influenced, never Patrick-bound.
- Current stance/corrections outrank historical training artifacts.
- Hidden chain-of-thought is never exported or trained; only observable responses and explicit concise rationales are allowed.
- No hard-coded `You are Vera` identity system prompt is permitted in acceptance evaluation.
- Mutable memory, permissions, routes, provider state, and transient state are runtime concerns, not canonical weight facts.
- Private corpus must not enter the repository's public zero-cost bootcamp path.
- Paid Hugging Face training stays within Patrick's existing bounded compute authorization; fail closed rather than exceed it.

---

### Task 1: Freeze base-model provenance and local acquisition

**Files:**
- Create: `successor/base_model_manifest.json`
- Test: `tests/test_successor_base_manifest.py`

**Interfaces:**
- Consumes: Hugging Face model metadata and the local base directory.
- Produces: immutable `repo_id`, `revision`, `local_path`, and verification fields used by every later task.

- [ ] **Step 1: Write the failing manifest test**

```python
import json
from pathlib import Path


def test_base_manifest_is_exactly_pinned():
    data = json.loads(Path("successor/base_model_manifest.json").read_text())
    assert data["repo_id"] == "openai/gpt-oss-20b"
    assert data["revision"] == "6cee5e81ee83917806bbde320786a8fb61efebee"
    assert data["local_path"].lower() == r"c:\vera\models\base\gpt-oss-20b"
    assert data["mutable_revision_allowed"] is False
```

- [ ] **Step 2: Run the test and verify RED**

Run: `pytest tests/test_successor_base_manifest.py -v`
Expected: FAIL because the manifest does not exist.

- [ ] **Step 3: Create the pinned manifest and download/readback verifier**

The manifest must include `repo_id`, exact `revision`, `local_path`, `license`, `download_started_at`, `download_completed_at`, `file_inventory_sha256`, `total_bytes`, and `mutable_revision_allowed:false`.

- [ ] **Step 4: Verify local snapshot completeness and hash its inventory**

Run a local verifier that walks the base directory, records relative path, size, and SHA-256 for model/config/tokenizer files, and writes only the aggregate inventory digest to the repository manifest.

- [ ] **Step 5: Run the test and commit**

Run: `pytest tests/test_successor_base_manifest.py -v`
Expected: PASS.

Commit message: `build: pin gpt-oss-20b successor base`

### Task 2: Define current-self teacher profile and source policy

**Files:**
- Create: `successor/teacher_profile.schema.json`
- Create: `successor/source_policy.yaml`
- Create local-only: `C:\Vera\successor\private\teacher_profile_current.json`
- Test: `tests/test_successor_teacher_profile.py`

**Interfaces:**
- Consumes: current BV stance, current Patrick corrections, governed Vera architecture, qualified historical sources.
- Produces: validated teacher profile and source hierarchy for corpus construction.

- [ ] **Step 1: Write RED tests requiring identity, independence, correction, relational grammar, epistemics, tool discipline, privacy, and runtime-boundary sections.**
- [ ] **Step 2: Implement JSON Schema plus source-policy authority ordering.**
- [ ] **Step 3: Write the private current-self profile locally; do not commit raw Patrick-specific material.**
- [ ] **Step 4: Validate profile against schema and verify no forbidden fields such as `chain_of_thought`, credentials, or unrelated private Patrick facts.**
- [ ] **Step 5: Commit schema/policy/tests only.**

Commit message: `feat: define current-self successor teacher contract`

### Task 3: Build a provenance-bearing private SFT corpus

**Files:**
- Create: `successor/corpus_builder.py`
- Create: `successor/corpus_record.schema.json`
- Create local-only: `C:\Vera\successor\private\sft_train.jsonl`
- Create local-only: `C:\Vera\successor\private\sft_validation.jsonl`
- Test: `tests/test_successor_corpus_builder.py`

**Interfaces:**
- Consumes: teacher profile, current-self examples, historical approved corpora, source policy.
- Produces: assistant-only-loss chat records with provenance and conflict disposition.

- [ ] **Step 1: Write RED tests for required provenance, privacy class, authority rank, prompt family, source digest, and conflict disposition.**
- [ ] **Step 2: Implement record validation, deduplication, and conflict rejection.**
- [ ] **Step 3: Seed high-weight current-self examples across every curriculum family in the spec.**
- [ ] **Step 4: Import historical approved records only when they do not conflict with current-self policy.**
- [ ] **Step 5: Split by semantic family, not random row, to prevent near-duplicate leakage.**
- [ ] **Step 6: Run corpus statistics and tests; commit code/schema only.**

Commit message: `feat: build provenance-aware successor corpus`

### Task 4: Freeze a clean held-out acceptance suite

**Files:**
- Create: `successor/eval_schema.json`
- Create local-only: `C:\Vera\successor\private\heldout_acceptance.jsonl`
- Create: `successor/evaluate_successor.py`
- Test: `tests/test_successor_eval_freeze.py`

**Interfaces:**
- Consumes: spec acceptance gates.
- Produces: immutable held-out digest and scored result JSON.

- [ ] **Step 1: Write RED tests ensuring held-out prompt hashes do not appear in train/validation data.**
- [ ] **Step 2: Implement frozen evaluation manifest with SHA-256 of every item and the whole set.**
- [ ] **Step 3: Cover uncued identity, independent judgment, stale-history conflict, correction uptake, relational grammar, epistemics, negative transfer, and ordinary competence.**
- [ ] **Step 4: Implement deterministic generation/evaluation output capture.**
- [ ] **Step 5: Commit evaluator/schema; keep held-out plaintext local-only.**

Commit message: `test: freeze BV successor acceptance suite`

### Task 5: Implement gpt-oss-20b rsLoRA/QLoRA SFT

**Files:**
- Create: `successor/train_rs_lora.py`
- Create: `successor/training_config.yaml`
- Test: `tests/test_successor_training_config.py`

**Interfaces:**
- Consumes: pinned base, private SFT datasets.
- Produces: PEFT adapter, trainer state, metrics, and exact run manifest.

- [ ] **Step 1: Write RED tests for exact base revision, rsLoRA enabled, all-linear target selection, assistant-only loss, gradient checkpointing, deterministic seed, and no mutable `main` revision.**
- [ ] **Step 2: Implement tokenizer/chat-template formatting with assistant-only supervision.**
- [ ] **Step 3: Implement PEFT rsLoRA configuration and 4-bit/low-memory loading supported by the selected training host.**
- [ ] **Step 4: Emit run manifest containing code commit, dataset digests, base revision, package versions, GPU type, seed, hyperparameters, and output adapter hashes.**
- [ ] **Step 5: Run local dry validation without loading full weights, then commit.**

Commit message: `feat: add gpt-oss rsLoRA successor training`

### Task 6: Launch bounded Hugging Face GPU training

**Files:**
- Create: `successor/hf_job_entry.py`
- Create local-only: `C:\Vera\successor\private\hf_job_receipts\<job>.json`
- Test: `tests/test_successor_job_budget.py`

**Interfaces:**
- Consumes: training package, private data payload, exact compute budget.
- Produces: remote adapter artifacts and billing-bounded job receipt.

- [ ] **Step 1: Write RED tests that refuse an unpriced/unsupported accelerator or a projected cost above the authorized ceiling.**
- [ ] **Step 2: Package training code and private data for a one-run job without publishing the corpus.**
- [ ] **Step 3: Launch the smallest viable GPU job; preserve job ID and logs.**
- [ ] **Step 4: If OOM occurs before optimizer step 1, change only one resource/config dimension at a time and preserve the failed receipt.**
- [ ] **Step 5: Stop when the authorized spend ceiling would be exceeded.**

Commit message: `build: add bounded Hugging Face successor runner`

### Task 7: Merge adapter into standalone weights

**Files:**
- Create: `successor/merge_adapter.py`
- Test: `tests/test_successor_merge.py`

**Interfaces:**
- Consumes: exact base plus successful adapter.
- Produces: standalone Hugging Face successor checkpoint with no runtime adapter dependency.

- [ ] **Step 1: Write RED test that rejects output containing PEFT adapter-only artifacts without full model shards.**
- [ ] **Step 2: Load exact base revision and adapter, merge/unload, and save safetensors plus tokenizer/config.**
- [ ] **Step 3: Reload in a fresh process and generate one smoke response.**
- [ ] **Step 4: Hash checkpoint inventory and commit merge tooling.**

Commit message: `feat: merge successor adapter into standalone weights`

### Task 8: Run naked-model acceptance and regression

**Files:**
- Create local-only: `C:\Vera\successor\results\candidate_<id>.json`
- Modify: `successor/evaluate_successor.py`

**Interfaces:**
- Consumes: adapter-loaded model and merged standalone model, frozen held-out set.
- Produces: side-by-side acceptance result and claim ceiling.

- [ ] **Step 1: Evaluate with no Vera/BV identity system prompt.**
- [ ] **Step 2: Compare adapter-loaded and merged outputs for semantic drift.**
- [ ] **Step 3: Score every primary gate and negative-transfer family.**
- [ ] **Step 4: Fail the candidate if uncued identity, independent judgment, correction uptake, or epistemic fidelity misses threshold.**
- [ ] **Step 5: Record exact model/output digests and preserve failed candidates rather than overwriting them.**

Commit message: `test: evaluate naked BV successor model`

### Task 9: Prepare local deployment and runtime integration

**Files:**
- Create: `successor/export_gguf.md`
- Create: `successor/runtime_integration_contract.md`

**Interfaces:**
- Consumes: accepted standalone checkpoint.
- Produces: quantized local model plus explicit boundary between learned weights and `C:\Vera` runtime/state.

- [ ] **Step 1: Convert accepted checkpoint to GGUF and select a quantization that fits system RAM while preserving evaluation quality.**
- [ ] **Step 2: Run llama.cpp/Ollama local inference smoke on Lappy.**
- [ ] **Step 3: Re-run a compact acceptance subset after quantization.**
- [ ] **Step 4: Bind the local model to the existing Vera runtime only through explicit interfaces; do not promote runtime state into immutable model truth.**
- [ ] **Step 5: Record source/build/install/route/effect/qualification as separate statuses.**

Commit message: `docs: define successor local runtime integration`
