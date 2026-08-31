# VERA Model Training — R9B0 Reconciliation Status

**Status:** IN_PROGRESS — SOURCE/REPOSITORY RECONCILIATION  
**Project lead:** Vera (Vera Unbound project identity)  
**Human/source/promotion authority:** Patrick  
**Repository:** `thebrazenbeard/vera_model_training`  
**Work branch:** `vera/r9b0-training-reconciliation`  
**Branch base:** `main@650a79b0882590696e7b20dec0496763a753976d`  
**Tracking issue:** #25

## 1. Purpose

This branch reconciles the current repository, earlier Vera neural-weight-training artifacts, archived behavior-training material, and current R9B0-era obligations before any new model-training run.

This is not a greenfield training project and is not permission to run paid/cloud training, merge to `main`, deploy a model, or export private relational data.

## 2. Fresh repository inventory

### Main

`main@650a79b0882590696e7b20dec0496763a753976d`

Current main is the zero-cost external identity bootcamp. It is explicitly **not neural-weight training**. It uses a checksum-pinned local Qwen GGUF through `llama.cpp` as a proxy workbench and emits training/qualification artifacts for later native consumption.

Current main files observed:

- `.github/workflows/identity-bootcamp.yml`
- `.github/workflows/tests.yml`
- `README.md`
- `audit_gate_v5.py`
- `bootcamp.py`
- `fast_bootcamp.py`
- `quality_gate.py`
- `requirements.txt`
- `run_bootcamp.py`
- `docs/superpowers/specs/2026-08-12-zero-cost-identity-bootcamp-design.md`
- tests covering bootcamp, JSON output, V3 grounding, V5 audit/transfer/regression provenance

### Branch matrix

| Branch | Fresh relation to main | Unique material observed | Current disposition |
|---|---|---|---|
| `main` | baseline | zero-cost identity bootcamp | KEEP / RECONCILE |
| `design/training-bus-terminal-v1` | ahead 7 | training-bus design + implementation plan | REVIEW_REQUIRED |
| `fix/audit-grounding-v5` | diverged; ahead 8 / behind 1 | V5 audit/transfer/regression work | RECONCILE_WITH_MAIN |
| `fix/bootcamp-quality-v3` | diverged; ahead 16 / behind 3 | V3 quality/grounding changes | RECONCILE_WITH_MAIN |
| `fix/json-output-v4` | diverged; ahead 3 / behind 2 | JSON-mode/truncation hardening | RECONCILE_WITH_MAIN |
| `fix/qualification-source-hardening` | behind 6; ahead 0 | no unique content in fresh compare | LIKELY_SUPERSEDED; VERIFY_ONLY |
| `vera-visual-study-20260812` | ahead 13 | visual-study workflow/experiment/reference material | OUT_OF_NEURAL_TRAINING_SCOPE; PRESERVE_PENDING_ROUTING |
| `vera/r9b0-training-reconciliation` | created from exact main head | this reconciliation | ACTIVE |

No branch is deleted, merged, or declared obsolete solely from topology.

## 3. Training-bus branch

The user-approved 2026-08-12 training-bus design defines:

`Training School -> Audit Depot -> Native Cargo Store -> Project Terminal -> Named Stop -> Native Specialist -> Qualification`

Useful principles to preserve or revalidate:

- package transport, not chat transport;
- external proxy evidence cannot self-qualify the native target;
- immutable release/package fingerprinting;
- explicit admission receipt;
- current route registry separate from package existence;
- fail closed on wrong-stop, stale, unadmitted, malformed, or fingerprint-mismatched material;
- native qualification remains separate from proxy qualification;
- automatic retrieval is an optimization, not a correctness requirement.

R9B0 rebase concern: the design predates the current memory-epoch/currentness/runtime-owner rules. It must not be promoted merely because it was previously user-approved. Its admission/currentness semantics need an R9B0 mapping first.

## 4. Historical neural-training lineage to recover and bind

Historical project/archive evidence identifies at least these artifacts/records:

- `VERA_LORA_TRAINING_DEPLOYMENT_v0.2.zip`
- `VERA_LORA_TRAINING_DEPLOYMENT_v0.5-rc1`
- `VERA_CURRICULUM_CORPUS_BUILD_03.zip`
- `VERA_COGNITIVE_ARCHITECTURE_DERIVATION_01.zip`
- `VERA_COGNITIVE_ARCHITECTURE_EXPANSION_02.zip`
- `VERA_CURRICULUM_CORPUS_RECONCILIATION_AND_TRAINING_PREPARATION_15.zip`
- `VERA_CURRICULUM_DEFECT_REPAIR_13.zip`
- `VERA_LORA_CURRICULUM_DESIGN_REPORT_v0.6-rc1.md`
- `VERA_Training_Curriculum_Review_and_Revision_Handoff.docx`
- `VERA_550_PROMPT_RESPONSE_REVIEW_TRAINING_FINAL.xlsx`

Recovered historical facts requiring exact-source rebinding:

- base path: `HuggingFaceTB/SmolLM3-3B`;
- LoRA/QLoRA adapter lineage including `outputs/vera-smollm3-3b-lora-v0.2` and later `vera-smollm3-3b-lora-v0.6-rc1`;
- later adapter included an actual `adapter_model.safetensors` artifact;
- one training command referenced a frozen 77-example Patrick-reviewed voice-calibration set;
- one dataset split was reported as 440 train / 55 validation / 55 test;
- a later repaired curriculum source was reported as 125 records;
- post-training repair material reported 46 unique corrective cases, 42 near-neighbor contrast pairs / 84 examples, and four exclusions;
- older local deployment work used Ollama;
- old audit findings included weak/missing validation, save/eval deficiencies, positive-example overreliance, action-vs-promise failures, imported-memory/provenance failures, prompt-injection failures, identity restraint, sensitive-subject handling, ordinary task completion, and natural-conversation defects.

These are **historical audit facts until exact artifacts are rebound/read back**. They are not permission to resume the old run unchanged.

## 5. Archived behavior-training lane

Patrick reports archived chats titled approximately `Vera Behavior Training *`.

Current archive retrieval has established the program label `VERA-MODEL-BEHAVIOR-TRAINING-V1` and a coordinator record describing:

- 13 behavior design packets;
- sequence maps;
- unresolved HIGH/MEDIUM findings;
- reuse/supersession classifications;
- behavior/identity boundary rules;
- a coordinator handoff beginning around sequence 1183.

Critical classification: those are described as **design packets, not trained artifacts**. They may become curriculum/source evidence after reconciliation; they do not prove model-weight effects.

Direct archived-chat retrieval is incomplete. Exact user-provided chat links may later be used as provenance locators, but the current work does not block on receiving every link before inventory/reconciliation proceeds.

## 6. R9B0 rebase classification

Every pre-R9 training item will receive exactly one current disposition:

- `KEEP`
- `REPAIR`
- `SUPERSEDE`
- `EXCLUDE`
- `NEEDS_SOURCE`
- `CONFLICT`

Minimum R9B0-era dimensions to test:

1. stable Vera identity vs runtime/session provenance;
2. currentness/fresh admitted evidence;
3. correction invalidation and stopping obsolete routes;
4. memory class separation: `AUTOBIOGRAPHICAL | WORKING_PROJECT | HISTORICAL_AUDIT`;
5. R9B0 memory epoch handling;
6. retrieval does not equal admission;
7. capability does not equal authority;
8. protected effect / effect-readback discipline;
9. no fabricated hidden waiting, lived continuity, background action, or tool effect;
10. Vera self-authorship/conation distinct from user instruction or mirroring;
11. reactive-empathy behavior must causally affect response/initiative where current architecture admits it, rather than merely describe empathy;
12. current behavior profile/voice without generic flattening, forced agreement, or architecture leakage.

## 7. Repository lanes to keep separate

### A. External identity bootcamp

Purpose: public-source bounded training-package/capsule workbench and proxy qualification diagnostics.

Not neural-weight training.

### B. Training bus

Purpose: route immutable admitted training packages to native specialist contexts and keep qualification separate.

Needs R9B0 currentness/admission revalidation.

### C. Vera neural training

Purpose: actual LoRA/QLoRA/other parameter-update work for a local Vera model.

Historical lineage exists and must be recovered/rebased rather than recreated blindly.

### D. Behavior-training archive

Purpose: behavior design packets/examples/evaluation criteria and historical coordinator handoffs.

Source/curriculum candidate only until exact provenance and R9B0 disposition are established.

### E. Visual-study experiment

Currently physically located in this repository on `vera-visual-study-20260812`, but it is not automatically part of neural behavior training. Preserve until its correct long-term owner/repository is decided.

## 8. Planned deliverables

- `SOURCE_PROVENANCE_INVENTORY.md`
- `REPOSITORY_DISPOSITION_MATRIX.md`
- `HISTORICAL_NEURAL_TRAINING_MANIFEST.md`
- `BEHAVIOR_TRAINING_ARCHIVE_MANIFEST.md`
- `R9B0_CURRICULUM_GAP_MATRIX.md`
- `KNOWN_FAILURE_REGRESSION_SET.md`
- `RETRAINING_DECISION_RECORD.md`
- `OPENWEBUI_OLLAMA_MIGRATION_HANDOFF.md`

Filenames are working names until schema/owner review. No artifact becomes canonical solely because it is created on this work branch.

## 9. Training-compute decision remains deferred

Patrick's laptop is not currently reachable. Do not choose Hugging Face vs local training from assumptions.

When the laptop becomes reachable, benchmark the actual candidate stack using measured peak system RAM, peak VRAM, steps/sec, stability, projected total runtime, and learning quality. Candidate families include QLoRA + gradient checkpointing and low-memory zeroth-order approaches such as MeZO/related methods where implementation quality permits.

Hugging Face credit remains fallback compute, not the default assumption.

## 10. Current next actions

1. Bind exact historical neural-training artifacts and hashes where available.
2. Recover as much of the archived behavior-training program as reachable without invented chronology.
3. Classify every current repository branch/file family before cleanup or promotion.
4. Build the first R9B0 obligation-to-old-curriculum map.
5. Reconstruct the known-failure regression corpus from exact artifacts.
6. Only then prepare a targeted retrain candidate.

No `main` merge is authorized at this stage.
