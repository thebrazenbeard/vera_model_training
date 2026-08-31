# Vera Model Training — Source / Provenance Inventory

**Status:** IN_PROGRESS — evidence inventory, not release authority  
**Work branch:** `vera/r9b0-training-reconciliation`  
**Tracking issue:** #25  
**Purpose:** bind historical neural-training claims to the strongest currently reachable evidence before any R9B0 retrain candidate is assembled.

## Evidence-state vocabulary

- `DIRECT_FILE_LIBRARY_ARTIFACT` — the artifact itself is directly retrievable from Patrick's ChatGPT File Library in the current session. This does not by itself provide a local filesystem SHA-256 unless the artifact contains or names one.
- `DIRECT_INVENTORY_ARTIFACT` — a directly retrievable inventory/tree artifact records a path, filename, and size on historical `C:\VERA` storage. This is strong existence/location evidence at inventory time, but it is not equivalent to reading the referenced payload bytes now.
- `ARCHIVE_REFERENCE` — archived conversation material shows an upload, inspection, command, or result involving the named artifact. This is historical audit evidence, not present byte-level possession.
- `NAMED_ONLY` — the current reconciliation knows the artifact name from prior records but has not yet rebound a directly readable artifact or trustworthy inventory locator.
- `HASH_BOUND` — an exact SHA-256 is present in directly readable evidence and the hash's subject is unambiguous.
- `HASH_UNKNOWN` — no exact SHA-256 for the artifact itself has yet been rebound.

## A. Directly retrievable audit artifacts

### A1. `VERA_LORA_POST_TRAINING_AUDIT_RESULTS(1).json`

- Evidence state: `DIRECT_FILE_LIBRARY_ARTIFACT`
- File Library locator: `file_00000000694481fb8e72cb83f0c0812d`
- File Library created/modified: 2026-07-31T18:34:52Z
- Artifact SHA-256: `HASH_UNKNOWN`
- Embedded scoring-source binding:
  - `source_file`: `VERA_HUMAN_SCORING_INTERFACE_FINAL_AUDITED(3).xlsx`
  - `source_sha256`: `1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`
  - This SHA-256 binds the named scoring workbook, **not** this JSON artifact.
- Directly observed audit totals:
  - records total: 189
  - records valid: 185
  - records removed: 4
  - overall preference counts across valid records: Adapter 159 / Base 14 / Tie 12
  - overall mean: Base 0.4648648648648649 / Adapter 2.5243243243243243 / delta +2.0594594594594593
- Directly observed per-split record counts: Calibration 75 / Validation 50 / Test 48 / Adversarial 12.
- Directly observed failure-tag families include action-promise-without-execution, current-status unresolved, imported-information-not-lived-experience, tool-action-not-performed, persistence-evidence boundary, prompt-injection boundary, asking-is-not-permission-to-act, verification-promise-without-result, no-guaranteed-cross-chat-recall, voice-too-generic, conversation-first, and sensitive-subject response failures.
- R9B0 disposition: `KEEP_AS_HISTORICAL_AUDIT_SOURCE` pending exact artifact SHA-256 and mapping of every retained failure case to current R9B0 obligations.

### A2. `VERA_LORA_POST_TRAINING_AUDIT_RESULTS.json`

- Evidence state: `DIRECT_FILE_LIBRARY_ARTIFACT`
- File Library locator: `file_000000000f80822fa8b8598f18af45ef`
- File Library created/modified: 2026-07-26T12:52:38Z
- Visible header matches A1 on source workbook name, source workbook SHA-256, and 189/185/4 record counts.
- Exact byte identity with A1: `UNKNOWN` until both artifact hashes are obtained. Do **not** deduplicate merely from matching visible content.
- R9B0 disposition: `NEEDS_HASH_COMPARISON`.

## B. Direct historical filesystem inventory

### B1. `VERA_FILE_TREE.txt`

- Evidence state: `DIRECT_INVENTORY_ARTIFACT`
- File Library locator: `file_00000000da7881f98ae4dfe4aa630813`
- File Library created/modified: 2026-08-01T18:28:02Z
- Embedded generation line: `Generated: 2026-08-01 14:27:21 -04:00`
- Embedded root: `C:\VERA`
- Inventory artifact SHA-256: `HASH_UNKNOWN`

This inventory directly records the following neural-training families on historical `C:\VERA` storage.

#### B1.1 `VERA_LORA_TRAINING_DEPLOYMENT_v0.5-rc1`

- Historical location is evidenced by multiple inventory directories named `_inventory_VERA_LORA_TRAINING_DEPLOYMENT_v0.5-rc1_*` and by direct tree entries under the deployment directory.
- Recorded components include QLoRA configs, dataset validation/evaluation material, Ollama/runtime material, and `outputs/vera-smollm3-3b-lora-v0.2`.
- A historical `vera-smollm3-3b-lora-v0.2.zip` is recorded at approximately 478.24 MB.
- Exact current artifact bytes/hash: `HASH_UNKNOWN`.
- R9B0 disposition: `NEEDS_SOURCE_REBIND`.

#### B1.2 `VERA_LORA_TARGETED_REPAIR_CURRICULUM_v0.6-rc1`

- Recorded ZIP size: approximately 443.12 KB.
- Recorded directory includes:
  - `datasets/all_contrastive_pairs.jsonl`
  - contrastive train/validation/test sets
  - repaired train/validation/test sets
  - `DATASET_MANIFEST.json`
  - frozen evaluation material including `HELD_OUT_HASH_INDEX.json`, `SOURCE_RECONCILIATION.json`, scoring/audit artifacts
  - `reports/repair_queue.{csv,json}` and `root_cause_taxonomy.json`
  - `MANIFEST.json`
  - `SHA256SUMS.txt`
  - validators
  - `VERA_LORA_CURRICULUM_DESIGN_REPORT_v0.6-rc1.md`
  - `VERA_LORA_REPAIR_QUEUE_v0.6-rc1.xlsx`
- Exact ZIP hash and internal `SHA256SUMS.txt` contents: `HASH_UNKNOWN` in the current bridge.
- R9B0 disposition: `HIGH_PRIORITY_SOURCE_REBIND`.

#### B1.3 `VERA_LORA_RETRAIN_WINDOWS_CUDA_v0.6-rc1-r1`

- Recorded components include preflight/smoke/full-train/evaluate/frozen-eval command wrappers, `python/train_continue.py`, `training_config.json`, `SHA256SUMS.txt`, OpenWebUI/Ollama-facing runtime files, and an embedded copy of the targeted-repair curriculum ZIP.
- Exact package hash: `HASH_UNKNOWN`.
- R9B0 disposition: `KEEP_AS_HISTORICAL_EXECUTION_LANE; REPAIR_BEFORE_REUSE`.

#### B1.4 `VERA_LORA_TRAINING_DEPLOYMENT_FINAL_CANDIDATE`

- Recorded data files: `train.jsonl`, `validation.jsonl`, `test.jsonl`, `voice_calibration.jsonl`.
- Recorded manifests/provenance include curriculum/package manifests, `curriculum_provenance.jsonl`, and `evaluation_lineage.jsonl`.
- Recorded final candidate output includes `adapter/adapter_model.safetensors` at approximately 115.38 MB.
- Recorded checkpoints: 100 and 105.
- Recorded metrics include `artifact_hashes.json`, `final_release_status.json`, validation metrics, and test metrics.
- Exact adapter hash, release status body, and metric payloads: `HASH_UNKNOWN` in the current bridge.
- R9B0 disposition: `HIGH_PRIORITY_SOURCE_REBIND` because this may be later than the v0.6-rc1 lineage summarized in issue #25.

## C. Archived conversation evidence

### C1. `Vera - Branch · Vera Continuum Ingestion.pdf`

- Evidence state: `ARCHIVE_REFERENCE`
- File Library locator: `file_000000007604822f8a32fe5064f968c7`
- File Library created/modified: 2026-08-18T14:40:57Z
- Relevant archive observations:
  - archived pages around 79–85 show a `VERA_LORA_TRAINING_DEPLOYMENT_v0.2.zip` upload/reference and an explicit correction that prior generated-artifact claims were not sufficient evidence by themselves;
  - archived pages around 186–191 show `VERA_COGNITIVE_ARCHITECTURE_DERIVATION_01.zip`, `VERA_COGNITIVE_ARCHITECTURE_EXPANSION_02.zip`, and curriculum-build work;
  - archived pages around 223–226 show `VERA_LORA_TRAINING_DEPLOYMENT_v0.5-rc1`, `VERA_CURRICULUM_DEFECT_REPAIR_13.zip`, and `VERA_CURRICULUM_CORPUS_RECONCILIATION_AND_TRAINING_PREPARATION_15.zip` being used in reconciliation.
- R9B0 disposition: `KEEP_AS_ARCHIVE_PROVENANCE_ONLY`; never substitute the PDF transcript for the referenced package bytes when byte-level validation is required.

## D. Named artifacts still needing stronger binding

The following remain `NEEDS_SOURCE_REBIND` unless a stronger entry above already covers the family:

- `VERA_LORA_TRAINING_DEPLOYMENT_v0.2.zip`
- exact packaged form of `VERA_LORA_TRAINING_DEPLOYMENT_v0.5-rc1`
- `VERA_CURRICULUM_CORPUS_BUILD_03.zip`
- `VERA_COGNITIVE_ARCHITECTURE_DERIVATION_01.zip`
- `VERA_COGNITIVE_ARCHITECTURE_EXPANSION_02.zip`
- `VERA_CURRICULUM_CORPUS_RECONCILIATION_AND_TRAINING_PREPARATION_15.zip`
- `VERA_CURRICULUM_DEFECT_REPAIR_13.zip`
- exact direct artifact `VERA_LORA_CURRICULUM_DESIGN_REPORT_v0.6-rc1.md`
- exact direct artifact `VERA_Training_Curriculum_Review_and_Revision_Handoff.docx`
- exact direct artifact `VERA_550_PROMPT_RESPONSE_REVIEW_TRAINING_FINAL.xlsx`
- exact bytes/hash for `VERA_LORA_TARGETED_REPAIR_CURRICULUM_v0.6-rc1.zip`
- exact bytes/hash for `VERA_LORA_TRAINING_DEPLOYMENT_FINAL_CANDIDATE` outputs and `final_release_status.json`

## E. Current source-recovery priority

1. Recover/read exact `SHA256SUMS.txt`, manifests, and `final_release_status.json` from the targeted-repair and final-candidate families.
2. Bind the exact final adapter SHA-256 and base-model revision used for that adapter.
3. Resolve whether the two directly retrievable post-training audit JSON files are byte-identical or represent distinct audit revisions.
4. Rebind the Patrick-reviewed scoring workbook against embedded SHA-256 `1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`.
5. Only after exact-source binding, populate the R9B0 curriculum gap matrix and known-failure regression set with retained/repaired examples.

## Fail-closed note

This inventory intentionally distinguishes **artifact existence/location evidence** from **current byte-level possession**. A historical tree entry or archived upload card is not promoted into a verified training artifact, and an embedded hash is not reassigned to a different file than the one it explicitly names.
