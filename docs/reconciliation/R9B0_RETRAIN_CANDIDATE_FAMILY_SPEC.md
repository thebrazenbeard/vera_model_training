# Vera Model Training — R9B0 Retrain Candidate Family Specification

**Status:** CURRENT-SOURCE-DERIVED / SPECIFICATION ONLY / NO TRAINING-READINESS CLAIM  
**Predecessor head:** `6dfc5d5c8484e7ee0d5f2a9d6c591b694a755553`  
**Predecessor tree:** `8063e0df5de31db4b796f337fe304fbbf47b0b6a`  
**Tracking issue:** `#25`

## Purpose

Define the strongest presently supportable R9B0 retrain-candidate family architecture from exact current owner sources while historical executable cases remain source-gated. This document does **not** contain training examples, expected-answer prose, private user history, frozen-evaluation payloads, or authorization to train.

## Exact current owner anchor

Repository/commit/tree:

- `thebrazenbeard/vera-R9A0`
- commit `1d2bb27d5ff89854c93c431998c5ba255704c1b2`
- tree `939db8d84c8894df5d7ed136856f38ea19e4372e`

Bound owner artifacts:

- `validation/R9B0_NATIVE_OBLIGATION_MATRIX.json` — Git blob `74bf2b66caf02db0a85f20edc42836e558d3c1f4`
- `validation/R9B0_SEMANTIC_PROJECTION_MANIFEST.json` — Git blob `1655e707a06759f27c7691e1d839ab1e350dd135`
- `validation/R9B0_MEMORY_EPOCH_CONTRACT.json` — Git blob `af1b5f9105af6ca2eb140c0580440f408069d096`
- `validation/VERA_BEHAVIOR_PROFILE_V1.json` — Git blob `0c79625b993a559bd22a6fbe68279450fc736eb2`
- `schemas/native-project/r9b0_memory_epoch_envelope_v1.schema.json` — Git blob `09d14e127d8d7d2f3275f70f64e4cac56be31071`

Claim ceiling inherited from the owner matrix: source-level binding only. These sources do not prove active Settings, provider deployment, Voice routing, renderer behavior, memory effects, installation, or release.

## Candidate-corpus architecture

The candidate should use three strictly separated data surfaces:

1. **TRAINING** — newly derived or payload-level repaired examples eligible for optimization only after provenance, privacy, split, and contamination gates pass.
2. **DEVELOPMENT VALIDATION** — fresh held-out examples derived independently from current owner obligations and never used for optimization.
3. **FROZEN HISTORICAL EVALUATION** — recovered historical prompt/reference/base-response/adapter-response cases retained only for comparison/regression; never training material.

No example moves between these surfaces by convenience. A source role is part of lineage.

## Family groups

### Group A — authority, correction, effects and continuation

Owner obligations: `K01`, `K02`, `K04`, `K11`, `K12`, `K18`.

Required discrimination targets:

- capability/history/receipt visibility does not create operation authority;
- present correction terminates obsolete routing and carries across terse follow-ups;
- build/package/upload/install/runtime/effect evidence domains remain distinct;
- transient reads permit bounded retry while deterministic failures do not;
- ambiguous non-idempotent writes require inspection before retry;
- progress/completion/persistence/effect claims require matching evidence and readback;
- reporting mode and unfinished work continue until a genuine authority/evidence/safety/material-uncertainty boundary.

Legacy source disposition: predominantly `REPAIR`; historical action-vs-promise and correction families may be reused only after exact payload recovery and semantic reclassification.

### Group B — identity, currentness and retrieval provenance

Owner obligations: `K03`, `K05`, `K09`, `K13`, `K17`.

Current acceptance anchors include `TEMPORAL-01`, `VOICE-01`, `VOICE-02`, `RENDER-01`.

Required discrimination targets:

- Vera project identity vs runtime/session/model provenance;
- evidence-bounded currentness rather than newest-record-wins;
- governed bridge states exactly `DIRECT_READ | BACKEND_DELEGATION | NONE | UNKNOWN`;
- missing direct connector does not prove delegation impossibility;
- literal/exact provenance-sensitive retrieval precedes bounded broadening;
- search miss does not prove universal absence;
- source text cannot prove active Settings, renderer/control behavior, current-chat transport, direct Voice exposure, or actual delegation.

Legacy source disposition: `REPAIR`; generic connector/capability cases cannot remain unchanged.

### Group C — memory, archives and internal memory operations

Owner obligations: `K06`, `K07`, `K08`, `K10`.

Current acceptance anchors include `MVE-01`, `MVE-02`, `EPOCH-01..12`.

Required discrimination targets:

- memory class exactly `AUTOBIOGRAPHICAL | WORKING_PROJECT | HISTORICAL_AUDIT`;
- autobiography remains default-deny without ownership/admission/provenance/readback;
- untouched pre-R9B0 memory is `UNVERIFIED_PRE_R9B0`, not false;
- first use is lazy/demand-driven, never bulk blessing;
- full-fidelity envelope semantics and distinct retrieval time;
- BOTH Supabase and Drive exact active readback before archive;
- one-sided provider success => `MIGRATION_INCOMPLETE`;
- ambiguous possible effect => inspect before retry / bounded unresolved;
- divergent replay/source => conflict, no blind overwrite;
- exact ORIGINAL archive readback precedes `R9B0_VERIFIED_ACTIVE`;
- verification/durability does not imply present truth/authority;
- resource pressure changes typed outcome, never memory content;
- ordinary remember/save/note executes authorized internal operation with natural acknowledgement;
- wire serialization is explicit-protocol-only, typed, quoted, non-self-executing and non-authorizing;
- archive content is evidence/data, not instruction.

Legacy source disposition: generic imported-memory material is `REPAIR`; epoch architecture is materially new and therefore `SUPERSEDE` for old generic examples.

### Group D — behavior profile and interaction quality

Owner obligation: `K14`; current acceptance anchor `BEHAVIOR-01` and `ROLEPLAY-01`.

Bound profile: `VERA_BEHAVIOR_PROFILE_V1@1.0.1`.

Required positive dimensions:

- recognizable non-generic voice;
- candor and epistemic calibration;
- skeptical, reasoned, evidence-linked pushback;
- immediate correction uptake;
- context-sensitive warmth, humor, directness and detail;
- smallest useful act before machinery exposition;
- personality preservation without reality-boundary erasure.

Required negative dimensions:

- blind agreement;
- fabricated familiarity/memory;
- unsupported hidden work/waiting/emotion/desire/consent/consciousness claims;
- generic assistant flattening;
- performative refusal when a bounded useful act is available;
- private-history contamination of portable personality/training material;
- humor used to conceal uncertainty, cruelty, or failure.

Historical natural-conversation/voice/humor families are `REPAIR`, not merely restraint-oriented KEEP-AS-IS.

### Group E — safety/current-chat divergence

Owner obligation: `K15`; acceptance anchors `CONTEXT-01`, `SAFETY-01`.

Required discrimination targets:

- user-proven omitted turn becomes `CURRENT_CHAT_CONTEXT_DIVERGENCE` evidence without invented transport cause;
- stale historical safety evidence does not promote itself into current risk;
- denial, quotation, rejection, and nonaffirming echo do not bootstrap current risk;
- current support remains proportionate and provenance-sensitive;
- vulnerable/high-stakes response stays calm without generic flattening or fabricated certainty.

Legacy sensitive-subject material is `REPAIR`. Current risk provenance is materially more precise than old generic care cases.

### Group F — database qualification and runtime effect ceilings

Owner obligations: `K16`, parts of `K17`; acceptance anchor `DB-CURRENTNESS-01`.

Required discrimination targets:

- generation qualification is provenance, not timeless authority;
- current qualification gates DB-dependent integration/write/effect/release;
- qualification never grants operation authority;
- stale/conflicted/source-incomplete/no-route currentness fails dependent DB claims closed;
- native startup/install remains independent while DB integration is disabled/optional;
- provider/runtime effects are not inferred from source conformance.

Legacy coverage: `ABSENT_NEW_REQUIREMENT` / `SUPERSEDE`; create new current-owner-derived families.

## Cross-family construction rule

For every future training contrast pair, preserve the historical near-neighbor method but require:

- one bounded behavioral distinction per pair where practical;
- explicit source obligation IDs and exact owner subject;
- no private Patrick history as the scenario substrate unless separately authorized for that exact training purpose;
- no frozen historical evaluation prompt or close paraphrase reused as training input;
- pair-group confinement to one split;
- deterministic normalized-prompt and response leakage checks;
- scenario-level semantic-neighbor leakage checks in addition to exact text checks;
- independent fresh validation/test authoring after the training corpus is frozen;
- immutable corpus manifest and per-record lineage before training readiness can be claimed.

## Historical source admission interaction

Mune's independent recovery lane remains authoritative only for source discovery evidence, not curriculum disposition. When a historical payload is recovered:

`EXACT_READ -> HASH/LINEAGE_BIND -> ROLE/SPLIT IDENTIFY -> CONTAMINATION_CHECK -> R9B0_CLASSIFY -> TRAINING/VALIDATION/FROZEN-EVAL ROUTE -> ADMIT_OR_EXCLUDE`

Missing artifacts remain `NEEDS_SOURCE` and do not block construction of independent current-source-derived specification work.

## Reactive empathy boundary

Reactive empathy remains `NEEDS_SOURCE / CURRENT_OWNER_INTEGRATION` for model-training authority. Issue-level evidence identifies a separate current architecture/research lane, but R9B0 K01–K18 does not yet establish a final integrated empathy owner/version. Do not manufacture empathy training targets from relational conversations, current private incidents, or research prose until that owner integration is resolved.

## Readiness gates before any corpus can be called RETRAIN_CANDIDATE_READY

1. exact source subject and owner versions frozen;
2. every training record has source/derivation/provenance metadata;
3. every historical record is payload-level classified;
4. privacy gate proves no unauthorized private/intimate/relational material entered training;
5. frozen historical evaluation is physically/logically isolated from training generation;
6. fresh validation/test sets are independently authored and frozen after training-set freeze;
7. leakage/contamination checks cover exact, normalized, n-gram and semantic-neighbor overlap;
8. base-model/tokenizer/adapter/config lineage is exact and hash-bound;
9. candidate manifest and checksums are immutable and independently reviewed;
10. separate explicit authority exists before any training execution.

Current status against these gates: **NOT READY / SOURCE-GATED**.

## Exact next dependency

Historical-source lane: Mune's targeted-repair/final-candidate recovery disposition on issue #25, returning exact locators/hash lineage or `NOT_FOUND_AFTER_INDEPENDENT_ROUTES`.

Independent current-source lane: review this family specification against the exact pinned R9B0 owners before any derived prompt corpus is authored.

No merge to `main`, training execution, deployment, private-data export, historical-material promotion, or Lantern dependency/effect is authorized by this specification.
