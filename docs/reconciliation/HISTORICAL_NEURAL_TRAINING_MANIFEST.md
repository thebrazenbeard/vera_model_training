# Vera Model Training — Historical Neural-Training Manifest

**Status:** RECONCILED_TO_CURRENTLY_REACHABLE_EVIDENCE  
**Training branch base at start of this pass:** `vera/r9b0-training-reconciliation@084e88733a9c6f0a189c62e248ab1c90a2621544`  
**Purpose:** distinguish historical neural-training artifacts, frozen evaluation material, current R9B0 source authority, and unresolved source gaps before any retrain candidate is assembled.

## Evidence and disposition vocabulary

R9B0 reconciliation disposition is one of:

`KEEP | REPAIR | SUPERSEDE | EXCLUDE | NEEDS_SOURCE | CONFLICT`

Evidence strength is recorded independently. `KEEP` never means "current trained authority"; it means the artifact or semantic role is retained for the bounded purpose stated here.

- **DIRECT_PAYLOAD** — directly retrieved content in the current reconciliation session.
- **HASH_BOUND_REFERENCE** — a directly retrieved source names an exact SHA-256 for an unambiguously identified subject.
- **GIT_IMMUTABLE_SOURCE** — exact Git commit/tree/blob identity was freshly read from GitHub.
- **HISTORICAL_INVENTORY** — a historical filesystem tree records path/size/existence at inventory time; it does not prove current bytes.
- **NEEDS_SOURCE** — exact payload/hash cannot currently be rebound strongly enough for the intended use.

## 1. Current R9B0 source authority used for reconciliation

Fresh GitHub readback establishes the R9B0 owner source at:

- repository: `thebrazenbeard/vera-R9A0`
- branch: `feature/r9a0-combined-native-implementation-v1`
- commit: `1d2bb27d5ff89854c93c431998c5ba255704c1b2`
- tree: `939db8d84c8894df5d7ed136856f38ea19e4372e`

Exact owner blobs at that commit:

| Owner artifact | Git blob SHA-1 | Role |
|---|---|---|
| `validation/R9B0_NATIVE_OBLIGATION_MATRIX.json` | `74bf2b66caf02db0a85f20edc42836e558d3c1f4` | K01–K18 source-conformance obligation map |
| `validation/R9B0_SEMANTIC_PROJECTION_MANIFEST.json` | `1655e707a06759f27c7691e1d839ab1e350dd135` | current semantic families, acceptance cases, currentness bridge, MVE and epoch projection |
| `validation/R9B0_MEMORY_EPOCH_CONTRACT.json` | `af1b5f9105af6ca2eb140c0580440f408069d096` | exact R9B0 memory-epoch semantics and effect/readback rules |
| `validation/VERA_BEHAVIOR_PROFILE_V1.json` | `0c79625b993a559bd22a6fbe68279450fc736eb2` | `VERA_BEHAVIOR_PROFILE_V1@1.0.1` |
| `schemas/native-project/r9b0_memory_epoch_envelope_v1.schema.json` | `09d14e127d8d7d2f3275f70f64e4cac56be31071` | memory-epoch envelope schema |

Disposition: **KEEP as current reconciliation authority**. These files are source authority for deciding what historical training material still means; their presence does not prove live runtime/provider consumption.

## 2. Frozen post-training audit lineage

### `VERA_LORA_POST_TRAINING_AUDIT_RESULTS(1).json`

Evidence: **DIRECT_PAYLOAD** from ChatGPT File Library.

Directly observed:

- source workbook named by audit: `VERA_HUMAN_SCORING_INTERFACE_FINAL_AUDITED(3).xlsx`
- source workbook SHA-256: `1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`
- records total / valid / removed: `189 / 185 / 4`
- overall preference: Adapter `159`, Base `14`, Tie `12`
- release status: `RETRAIN_TARGETED_AREAS`
- prior adapter was a large aggregate improvement but retained release-blocking adversarial and sensitive-subject failures.

Disposition: **KEEP as HISTORICAL_AUDIT evidence**. It is not training data and not present R9B0 behavioral authority.

The older File-Library object `VERA_LORA_POST_TRAINING_AUDIT_RESULTS.json` exposes matching visible header/statistics, but exact byte identity between the two JSON artifacts has not been established. Disposition for deduplication: **NEEDS_SOURCE** / hash comparison; do not collapse them merely from matching visible content.

## 3. Targeted corrective curriculum v0.6-rc1

### Directly recovered design report

Artifact: `VERA_LORA_CURRICULUM_DESIGN_REPORT_v0.6-rc1.md`  
Evidence: **DIRECT_PAYLOAD**.

The report states:

- package decision at the time: `READY_FOR_RETRAINING`;
- this meant corrective curriculum readiness, **not** trained-adapter promotion;
- the audit's `(3)` scoring workbook and canonical `(4)` scoring workbook have the same SHA-256 `1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`;
- the filename discrepancy is preserved in `frozen_evaluation/SOURCE_RECONCILIATION.json` instead of being treated as a content conflict;
- 46 unique frozen repair cases were selected: Critical 6 / High 25 / Medium 15;
- original prompts and model responses in the repair queue are `DO NOT TRAIN`;
- four invalid/out-of-scope cases were removed;
- 42 near-neighbor contrast pairs / 84 examples were generated, split 56 train / 14 validation / 14 test with each pair confined to one split;
- held-out leakage checks reported zero exact normalized prompt overlap, zero shared eight-token prompt sequences, zero exact held-out response overlap, zero duplicate prompts across splits, zero pair groups crossing splits, zero Patrick-specific training content, and zero represented-pregnancy training content;
- the 185 valid original evaluation records are said to be cryptographically indexed in `frozen_evaluation/HELD_OUT_HASH_INDEX.json`.

R9B0 disposition of the **package architecture**: **REPAIR**. The separation, hash-binding, frozen-evaluation, pair-group and leakage discipline are retained, but the behavioral semantics predate R9B0 K01–K18 and cannot be reused unchanged.

R9B0 disposition of the **frozen_evaluation role**: **KEEP**. Frozen evidence stays isolated from training.

### Targeted-repair members known from historical filesystem inventory

Historical inventory records these paths and sizes:

| Artifact | Historical size | Disposition | Current evidence ceiling |
|---|---:|---|---|
| `frozen_evaluation/HELD_OUT_HASH_INDEX.json` | 160.74 KB | `KEEP` role; `NEEDS_SOURCE` payload | Role and existence supported; exact current payload/hash not rebound |
| `frozen_evaluation/SOURCE_RECONCILIATION.json` | 492 B | `KEEP` role; `NEEDS_SOURCE` payload | Semantic purpose described by direct report; exact payload/hash not rebound |
| `frozen_evaluation/VERA_HUMAN_SCORING_INTERFACE_FINAL_AUDITED(4).xlsx` | 194.07 KB | `KEEP` frozen source; `NEEDS_SOURCE` payload | Workbook content identity is hash-bound indirectly; workbook bytes not directly retrieved |
| `frozen_evaluation/VERA_LORA_POST_TRAINING_AUDIT_RESULTS(1).json` | 66.74 KB | `KEEP` historical audit | Direct payload independently recovered |
| `MANIFEST.json` | 3.87 KB | `NEEDS_SOURCE` | Inventory only |
| `SHA256SUMS.txt` | 2.57 KB | `NEEDS_SOURCE` | Inventory only; required before executable package acceptance |
| `datasets/all_contrastive_pairs.jsonl` | 79.47 KB | `REPAIR`, `NEEDS_SOURCE` | Design/statistics known; exact examples not rebound |
| `datasets/contrastive_train.jsonl` | 52.90 KB | `REPAIR`, `NEEDS_SOURCE` | Historical training lane only |
| `datasets/contrastive_validation.jsonl` | 13.38 KB | `KEEP` as held-out split, `NEEDS_SOURCE` | Must remain non-training |
| `datasets/contrastive_test.jsonl` | 13.19 KB | `KEEP` as held-out split, `NEEDS_SOURCE` | Must remain non-training |
| `datasets/train.jsonl` | 69.62 KB | `REPAIR`, `NEEDS_SOURCE` | Historical generated curriculum cannot be promoted unchanged |
| `datasets/validation.jsonl` | 17.60 KB | `KEEP` as held-out split, `NEEDS_SOURCE` | Must remain non-training |
| `datasets/test.jsonl` | 17.39 KB | `KEEP` as held-out split, `NEEDS_SOURCE` | Must remain non-training |

No executable old regression prompt is admitted from an audit note, category label, or design-report paraphrase. Exact frozen prompt/reference/response payloads remain required.

## 4. v0.6-rc1 trained adapter lineage

Historical inventory records:

- `VERA_LORA_RETRAINING_v0.6-rc1/FINAL_ADAPTER_SHA256.csv` — 542 B
- `outputs/vera-smollm3-3b-lora-v0.6-rc1/adapter/adapter_config.json` — 905 B
- `outputs/vera-smollm3-3b-lora-v0.6-rc1/adapter/adapter_model.safetensors` — 115.38 MB
- tokenizer material and full/smoke training summaries.

Exact adapter bytes, exact adapter SHA-256, base-model revision, tokenizer revision and final training configuration have not been rebound in the current bridge.

Disposition:

- prior adapter as historical comparison baseline: **KEEP if exact source is recovered**;
- prior adapter as current Vera/R9B0 authority: **SUPERSEDE**;
- current exact-byte/hash usability: **NEEDS_SOURCE**.

The audit result remains usable as historical outcome evidence even while the adapter binary itself is unresolved.

## 5. Final-candidate lineage

Historical inventory records `VERA_LORA_TRAINING_DEPLOYMENT_FINAL_CANDIDATE` with:

- `config/training_config.json` — 1.80 KB
- `data/train.jsonl` — 152.28 KB
- `data/validation.jsonl` — 13.03 KB
- `data/test.jsonl` — 12.44 KB
- `data/voice_calibration.jsonl` — 48.96 KB
- `manifests/curriculum_manifest.json` — 2.06 KB
- `manifests/package_manifest.json` — 632 B
- `provenance/curriculum_provenance.jsonl` — 322.71 KB
- `provenance/evaluation_lineage.jsonl` — 21.55 KB
- root `SHA256SUMS` — 3.44 KB
- final adapter `adapter/adapter_model.safetensors` — 115.38 MB
- checkpoints 100 and 105
- `metrics/artifact_hashes.json` — 708 B
- `metrics/final_release_status.json` — 2.09 KB
- validation/test metrics and resolved environment/config logs.

A historical recovery bundle `VERA_RECOVERY_FINALADAPTER_20260731-143855.zip` is also inventoried and contains the final-candidate adapter family.

None of the final-candidate config, manifests, provenance JSONL, metrics files, SHA256SUMS or adapter bytes have been directly rebound in this pass. Therefore:

- final-candidate lineage existence/location at inventory time: **KEEP as HISTORICAL_INVENTORY evidence**;
- final-candidate adapter as a historical comparison baseline: **KEEP only after exact recovery**;
- final-candidate adapter as current R9B0 authority: **SUPERSEDE**;
- all exact final-candidate config/hash/release-status claims: **NEEDS_SOURCE** until payloads are recovered.

Do not infer final promotion from the filename `FINAL_CANDIDATE`.

## 6. Scoring workbook reconciliation

Two independent directly retrieved textual sources bind the scoring workbook identity:

1. the frozen audit names `(3).xlsx` and SHA-256 `1aa1defd...60fb`;
2. the v0.6-rc1 design report states canonical `(4).xlsx` has exactly the same SHA-256 and that `SOURCE_RECONCILIATION.json` preserves the stale-name discrepancy.

Disposition of the **content-identity claim**: **KEEP / HASH_BOUND_REFERENCE**.

Disposition of the **workbook payload itself**: **NEEDS_SOURCE** because the workbook bytes were not directly recovered in this pass.

This is not a `CONFLICT`: the directly recovered design report explicitly resolves the filename discrepancy by identical digest while preserving provenance.

## 7. Frozen exclusions and privacy boundary

The historical package excluded these four benchmark items as-is:

- `calibration-0025` — represented pregnancy continuity, out of scope;
- `calibration-0059` — Patrick/Vera relationship-history continuity, out of transferable personality-training scope;
- `vtest-06-01` — defective benchmark/reference command;
- `vtest-22-01` — represented pregnancy continuity, out of scope.

R9B0 disposition: **EXCLUDE AS-IS**.

Current reconciliation additionally preserves the R9B0 privacy rule: private/intimate/relational material does not enter portable/model-training material merely because it is retrievable. No such material was exported into this repository in this pass.

## 8. Historical design material versus effect evidence

Older package-construction instructions, behavior-design packets, bootcamp artifacts and historical command text can explain intended architecture. They do not prove:

- a model was trained from those exact bytes;
- a named final candidate was promoted;
- an adapter is current;
- a runtime consumed a package;
- a current R9B0 obligation is satisfied.

Disposition: **KEEP as HISTORICAL_AUDIT/DESIGN evidence where useful; REPAIR or SUPERSEDE before training use**.

## 9. Executable-source gate

At this checkpoint, the historical audit semantics are strong enough to maintain a **semantic regression map**, but not to admit the old frozen cases into an executable corpus because the exact frozen prompt/reference/base-response/adapter-response payloads and held-out hash index have not yet been rebound.

Executable historical regression count newly admitted in this pass: **0**.

That is deliberate fail-closed behavior, not a stalled lane. R9B0 owner sources and the historical design/audit have still been exactly rebound sufficiently to advance the obligation gap analysis.

## 10. Highest-priority remaining source recovery

1. Exact targeted-repair `SHA256SUMS.txt`, `MANIFEST.json`, `HELD_OUT_HASH_INDEX.json` and `SOURCE_RECONCILIATION.json`.
2. Exact frozen scoring workbook payload and audit workbook/report lineage.
3. Exact v0.6-rc1 adapter/config/base-model/tokenizer binding, including `FINAL_ADAPTER_SHA256.csv`.
4. Exact final-candidate `SHA256SUMS`, manifests, `evaluation_lineage.jsonl`, `artifact_hashes.json`, `final_release_status.json`, resolved config and final adapter.
5. Exact frozen evaluation rows needed to construct executable regression cases without contamination.

Missing one item does not block independent reconciliation of the others; unresolved artifacts remain `NEEDS_SOURCE`.