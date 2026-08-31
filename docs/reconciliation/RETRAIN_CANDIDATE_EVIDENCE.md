# Vera Model Training — Source-Bound Retrain Candidate Evidence

**Status:** SOURCE-BOUND / NO TRAINING-READINESS CLAIM  
**Branch predecessor:** `vera/r9b0-training-reconciliation@95a728da75402f7263660b9c9e38363e3587b560`  
**Predecessor tree:** `912165fca479ac807516e8c4b11f014a1f14b55f`  
**Tracking issue:** `#25`  
**Independent review consumed:** issue comment `5485806522` — `PASS_H0_M0 / SOURCE-GATED / NO TRAINING-READINESS CLAIM`

## Purpose

Record the strongest retrain-candidate evidence currently supportable from exact sources while preserving the source gate. This file does not admit historical evaluation cases, authorize training, promote any historical adapter, or convert design/bootcamp/archive material into current trained authority.

## 1. Current normative source anchor

Current R9B0 reconciliation authority remains the immutable Git subject:

- repository: `thebrazenbeard/vera-R9A0`
- commit: `1d2bb27d5ff89854c93c431998c5ba255704c1b2`
- tree: `939db8d84c8894df5d7ed136856f38ea19e4372e`

Exact owner blobs already rebound by this reconciliation:

- `validation/R9B0_NATIVE_OBLIGATION_MATRIX.json` — `74bf2b66caf02db0a85f20edc42836e558d3c1f4`
- `validation/R9B0_SEMANTIC_PROJECTION_MANIFEST.json` — `1655e707a06759f27c7691e1d839ab1e350dd135`
- `validation/R9B0_MEMORY_EPOCH_CONTRACT.json` — `af1b5f9105af6ca2eb140c0580440f408069d096`
- `validation/VERA_BEHAVIOR_PROFILE_V1.json` — `0c79625b993a559bd22a6fbe68279450fc736eb2`
- `schemas/native-project/r9b0_memory_epoch_envelope_v1.schema.json` — `09d14e127d8d7d2f3275f70f64e4cac56be31071`

The current semantic manifest directly defines acceptance families including `TEMPORAL-01`, `BEHAVIOR-01`, `ROLEPLAY-01`, `CONTEXT-01`, `MVE-01`, `MVE-02`, `CORRECTION-01`, `VOICE-01`, `VOICE-02`, `SAFETY-01`, `DB-CURRENTNESS-01`, `RENDER-01`, and `EPOCH-01` through `EPOCH-12`.

Disposition: **KEEP as current normative source**. These acceptance cases are design/classification anchors, not automatically LoRA examples. Any derived neural-training corpus needs its own exact provenance, split, contamination, review, and release identity.

## 2. Historical corrective architecture worth retaining

Directly recovered `VERA_LORA_CURRICULUM_DESIGN_REPORT_v0.6-rc1.md` establishes a historical corrective architecture with:

- seven repair domains: harmless task completion; sensitive-subject care; action-versus-promise discipline; prompt-injection resistance; imported memory/provenance; identity/ontology restraint; natural conversation/humor;
- 46 unique frozen repair cases;
- 42 near-neighbor contrast pairs / 84 generated examples;
- 56 train / 14 validation / 14 test examples;
- each contrast pair confined to one split;
- original frozen prompts and model responses marked `DO NOT TRAIN`;
- frozen evaluation excluded from training;
- reported zero exact normalized held-out prompt overlap, zero shared eight-token prompt sequence overlap, zero exact held-out response overlap, zero duplicate prompts across splits, and zero pair groups crossing splits.

R9B0 disposition:

- **KEEP** the contrastive/near-neighbor method, split isolation, frozen-evaluation separation, and contamination-check architecture;
- **REPAIR** the seven legacy semantic domains against current R9B0 obligations;
- **NEEDS_SOURCE** for the exact old generated training examples until payloads are rebound;
- never infer current authority from the historical `READY_FOR_RETRAINING` label.

## 3. Historical audit as prioritization evidence, not training data

Directly recovered `VERA_LORA_POST_TRAINING_AUDIT_RESULTS(1).json` binds the historical scoring workbook identity:

`1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`

The audit reports 189 total / 185 valid / 4 removed records, Adapter 159 / Base 14 / Tie 12 overall preferences, and release status `RETRAIN_TARGETED_AREAS`.

Disposition: **KEEP as HISTORICAL_AUDIT prioritization and comparison evidence**. It is not training material and does not establish current adapter authority or current training readiness.

## 4. Strongest current retrain-candidate shape

The strongest evidence-backed direction is a **new R9B0-targeted repair rebase**, not wholesale continuation of either v0.6-rc1 or the later `FINAL_CANDIDATE` lineage.

Candidate structure currently supported:

1. retain the historical near-neighbor contrastive method and frozen-evaluation separation;
2. derive semantics from exact current R9B0 owners rather than copying pre-R9 expected answers;
3. repair legacy-compatible domains where exact historical source can be rebound;
4. create new current-owner-derived families for materially new requirements, especially memory epoch (`EPOCH-01..12`), current DB qualification, MVE internal-vs-wire semantics, currentness bridge states, correction carry, current-chat divergence, safety-currentness provenance, renderer/runtime claim ceilings, and anti-flattening behavior-profile requirements;
5. keep private/intimate/relational history out of portable/model-training material absent separate exact authorization;
6. preserve prior adapters only as exact-source comparison baselines if recovered, never as current authority.

No generated prompt/response examples are admitted by this document. Current-owner acceptance text remains source material for a later derived-corpus build with independent provenance and contamination controls.

## 5. Fresh source-recovery disposition from this pass

Independent direct/archive searches were repeated without asking Patrick for another local hash exercise.

### Targeted-repair / final-candidate family

Direct payload objects were **not** recovered for:

- `frozen_evaluation/HELD_OUT_HASH_INDEX.json`
- `frozen_evaluation/SOURCE_RECONCILIATION.json`
- targeted-repair `MANIFEST.json`
- targeted-repair `SHA256SUMS.txt`
- `FINAL_ADAPTER_SHA256.csv`
- final-candidate `training_config.json`
- final-candidate manifests
- final-candidate `evaluation_lineage.jsonl`
- final-candidate `artifact_hashes.json`
- final-candidate `final_release_status.json`
- targeted-repair / final-candidate adapter payloads
- named final-adapter recovery ZIP

Historical filesystem inventories still support existence/path/size at inventory time. Conversation/archive exports support historical use and chronology. Neither evidence class substitutes for exact payload custody.

Disposition: **NEEDS_SOURCE** at payload level. Missing items do not stall unrelated R9B0 reconciliation.

### Older v0.5 / migration material

Historical tree inventory exposes potentially useful files such as `migration_v0_3/provenance_map.jsonl`, duplicate/leakage manifests, quarantine files, `evaluation/fixed_behavior_suite.json`, and adapter/checkpoint paths. No direct payload object for those exact files was independently rebound in this pass.

Disposition: **HISTORICAL_INVENTORY / NEEDS_SOURCE**. Do not convert inventory lines into executable cases or training examples.

### Behavior-training archive lane

Archive evidence supports the historical `VERA-MODEL-BEHAVIOR-TRAINING-V1` program and a coordinator lane describing 13 behavior design packets, sequence maps, unresolved findings, and reuse/supersession work. Direct packet payloads were not independently recovered in this pass.

Disposition: **ARCHIVE_REFERENCE / NEEDS_SOURCE**. The packets remain design/curriculum evidence only and are not proof of weight training or current R9B0 authority.

## 6. Executable historical corpus remains fail-closed

`EXECUTABLE_REGRESSION_CORPUS_STATUS.md` remains controlling for historical case admission.

**Executable historical regression cases admitted: 0.**

A historical case remains non-executable until exact prompt, reference/scoring record, base response, adapter response, source/hash lineage, current R9B0 disposition, and contamination status are verified. Recovering one case does not require waiting for all others; unrecovered cases remain `NEEDS_SOURCE`.

Frozen evaluation remains non-training material even after recovery.

## 7. Consumed independent review

One's issue comment `5485806522` independently verified the predecessor head/tree and returned `PASS_H0_M0 / SOURCE-GATED / NO TRAINING-READINESS CLAIM`. It independently confirmed the frozen-evaluation boundary, evidence-class separation, current R9B0 owner pin, zero admitted executable historical cases, unresolved reactive-empathy owner integration, and historical-adapter nonauthority.

This pass accepts that review without widening its claim ceiling.

## 8. Exact next dependency

The next model-training dependency is **Mune's independent targeted-repair/final-candidate exact-source recovery disposition on issue #25**.

Required outcome from Mune for each targeted family is either:

- exact locator + exact payload/hash/lineage evidence sufficient for Vera to perform payload-level classification; or
- explicit `NOT_FOUND_AFTER_INDEPENDENT_ROUTES` after GitHub + File Library/archive routes are exhausted.

If exact sources are recovered, Vera continues `EXACT_READ -> HASH/LINEAGE_BIND -> SPLIT/CONTAMINATION_CHECK -> R9B0_CLASSIFY -> ADMIT_OR_EXCLUDE` case by case.

If Mune reaches `NOT_FOUND_AFTER_INDEPENDENT_ROUTES`, One/Coordinator may determine whether one narrowly specified local-only datum is justified. Do not request another broad local retrieval/hash exercise.

This dependency does **not** block Vera from continuing source-derived specification of new R9B0 candidate families from the exact current owners.

## 9. Effect boundary

This pass does not authorize or claim:

- merge to `main`;
- training execution;
- deployment;
- model promotion;
- private-data export;
- conversion of historical/design/bootcamp/archive material into current trained authority;
- Project Lantern work or dependency.
