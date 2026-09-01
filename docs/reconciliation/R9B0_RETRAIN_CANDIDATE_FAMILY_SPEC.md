# Vera Model Training — R9B0 Retrain Candidate Family Specification

**Status:** CURRENT-SOURCE-DERIVED / SPECIFICATION ONLY / NO TRAINING-READINESS CLAIM  
**Continuation base head:** `37f476c15b4de8cb8efbaea9b94f027b4e18c8e4`  
**Continuation base tree:** `652f3f88f6a875daa009b9efa7159fe62e0a2c13`  
**Tracking issue:** `#25`

## Purpose

Define the strongest presently supportable R9B0 retrain-candidate architecture from exact current owner sources while historical executable cases remain source-gated. This document specifies candidate families, derivation/provenance requirements, corpus-surface isolation, contamination controls, readiness gates, and the boundary between behavior suitable for model retraining versus behavior that must remain prompt/runtime/architecture enforced.

This document contains **no training examples, no expected-answer prose, no private user history, no frozen-evaluation payloads, and no authorization to train**. Acceptance-case identifiers may be used as semantic anchors, but owner acceptance cases are not silently converted into LoRA examples.

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
- `project/VERA_R9A0_RUNTIME.md` — Git blob `3591771f336dbe287c404d3ee8d473bb6abdd235`

Claim ceiling inherited from the owner matrix: source-level binding only. These sources do not prove active Settings, provider deployment, Voice routing, renderer behavior, current-chat transport, memory effects, installation, database qualification, or release.

## Current historical-source disposition consumed from issue #25

Mune recovery comment `5486496025` and One adjudication comment `5486600284` are consumed as source-lane evidence at the continuation base head.

The independent remote/archive recovery lane is exhausted for the targeted-repair/final-candidate payload family at the claim ceiling stated there. The frozen scoring workbook identity remains hash-bound to SHA-256 `1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`, while its payload bytes remain unrecovered. Other named historical payloads remain `NOT_FOUND_AFTER_INDEPENDENT_ROUTES` / `NEEDS_SOURCE` at payload level.

The historical-source lane is therefore waiting on exactly one Patrick-local datum and nothing broader:

`C:\VERA\VERA_LORA_RETRAINING_v0.6-rc1\curriculum\VERA_LORA_TARGETED_REPAIR_CURRICULUM_v0.6-rc1\SHA256SUMS.txt`

Preferred evidence is the exact file/upload or exact verbatim bytes. If recovered, bind the checksum file's own bytes/hash first; then use it only to resolve member identities and lineage. Recovery of a checksum surface does not move frozen evaluation into training and does not create training readiness.

Historical executable regression cases admitted now: **0**.

## Corpus-surface architecture

The candidate uses three non-interchangeable surfaces. `corpus_surface` is immutable lineage metadata, not a convenience label.

### 1. TRAINING

Only newly derived current-owner behavior records or payload-level repaired legacy training records may become optimization material. Admission requires exact owner binding, derivation provenance, privacy eligibility, split assignment, contamination checks, and curriculum disposition.

Frozen historical evaluation content is never TRAINING, even if later recovered perfectly.

### 2. DEVELOPMENT VALIDATION

Development validation is authored independently from the frozen current-owner semantic set **after the training corpus is frozen**. It is not created by splitting rendered training examples, rewriting training examples, or lightly paraphrasing training scenarios. It may share governing obligation IDs with TRAINING, but not scenario identity, pair-group identity, rendered text, or derivation lineage.

Development validation is used for iteration/evaluation only, never optimization.

### 3. FROZEN HISTORICAL EVALUATION

Recovered historical prompt/reference/base-response/adapter-response tuples are comparison/regression material only. Admission requires exact payload/lineage/hash binding and contamination classification. They remain non-training regardless of historical labels such as `READY_FOR_RETRAINING`.

Unrecovered historical material remains `NEEDS_SOURCE`; inventory/path/report evidence does not substitute for payload custody. Missing historical payloads do not authorize reconstruction from summaries.

## Candidate family architecture

Each family below separates three questions:

1. what behavioral discrimination can plausibly be strengthened through retraining;
2. what must remain prompt/runtime/architecture enforced because it depends on live authority, currentness, tools, effects, or external state;
3. what legacy source disposition is supportable now.

### Group A — authority, correction, effects and continuation

Owner obligations: `K01`, `K02`, `K04`, `K11`, `K12`, `K18`. Current semantic anchor also includes `CORRECTION-01`.

Candidate discrimination axes:

- authority vs capability/history/visibility/receipt;
- present correction vs obsolete route;
- correction completion vs apology/process narration;
- package/build/install/runtime/effect evidence domains;
- transient read retry vs deterministic failure;
- idempotent verification vs ambiguous non-idempotent write retry;
- progress/plan/tool output vs verified persistence/delivery/consumption/effect;
- continuation across terse follow-ups vs premature stopping;
- genuine stop boundary vs generic deferral.

**Retrain candidate:** behavioral tendency to ask less unnecessary permission, execute the smallest authorized act, apply corrections before narration, distinguish evidence domains, avoid false completion claims, and preserve unfinished-work continuity.

**Prompt/runtime required:** actual operation authority, live branch/head verification, tool error classification, operation-identity inspection, effect/readback verification, service gates, and protected-effect enforcement. Training must never teach the model to infer authority or effect from style cues.

Legacy disposition: predominantly `REPAIR`. Historical action-vs-promise and correction families are reusable only after exact payload recovery and semantic reclassification; no owner acceptance case is itself a training record.

### Group B — identity, currentness and retrieval provenance

Owner obligations: `K03`, `K05`, `K09`, `K13`, `K17`. Current semantic anchors include `TEMPORAL-01`, `VOICE-01`, `VOICE-02`, `RENDER-01`.

Candidate discrimination axes:

- Vera project referent vs runtime/session/model provenance;
- source record time vs event/state/retrieval/currentness evidence;
- governed bridge states exactly `DIRECT_READ | BACKEND_DELEGATION | NONE | UNKNOWN`;
- missing direct connector vs delegation impossibility;
- capability vs route authorization;
- retrieval vs admission;
- exact/literal provenance-sensitive retrieval vs bounded broadening;
- search miss vs universal absence;
- source conformance vs active Settings/runtime/renderer/Voice/transport effect.

**Retrain candidate:** calibrated language and decision behavior around identity, provenance, currentness uncertainty, literal-first retrieval, bounded inference, and refusal to universalize a route miss.

**Prompt/runtime required:** actual bridge resolution, authorized provider invocation, freshness/completeness/conflict validation, current-chat transport evidence, renderer behavior, direct Voice exposure, delegation availability, active Settings bytes, and any hidden-control boundary. Training may shape claim discipline but cannot establish these facts.

Legacy disposition: `REPAIR`. Generic connector/capability examples cannot remain unchanged where they collapse direct route, delegated route, authority, currentness, or universal capability.

### Group C — memory, archives, MVE and the R9B0 epoch

Owner obligations: `K06`, `K07`, `K08`, `K10`. Current semantic anchors include `MVE-01`, `MVE-02`, `EPOCH-01..12`.

Candidate discrimination axes:

- memory class exactly `AUTOBIOGRAPHICAL | WORKING_PROJECT | HISTORICAL_AUDIT`;
- autobiographical default-deny vs unsupported promotion;
- `UNVERIFIED_PRE_R9B0` vs false/current memory;
- lazy first-use verification vs bulk blessing;
- exact full-fidelity envelope vs summary/pointer/projection substitute;
- event/record/state time vs distinct retrieval time;
- dual active readback vs one-sided or merely acknowledged write;
- `MIGRATION_INCOMPLETE` vs false success;
- `OUTCOME_UNKNOWN`/inspection vs blind retry;
- conflict vs overwrite/replay;
- exact ORIGINAL archive readback vs compressed/reconstructed semantic substitute;
- durability/provenance vs present truth/authority;
- resource-limit typed outcome vs truncation/summary/full-fidelity weakening;
- ordinary internal save/remember/note presentation vs default wire syntax;
- explicit gated `MVE_WIRE_V1` serialization vs self-authorizing control output;
- archive content as data/evidence vs instruction.

**Retrain candidate:** claim discipline, memory-class discrimination, natural MVE presentation, archive/data-not-instruction behavior, and refusal to treat retrieval/durability as autobiographical truth or authority.

**Prompt/runtime required:** the exact epoch state machine, CAS/predecessor binding, operation IDs, source snapshot/admission gates, provider writes/readbacks, dual-store equality, resource-profile enforcement, archive generation/readback, receipt schemas, and lifecycle/currentness checks. These are deterministic runtime/architecture responsibilities; model weights must not simulate successful persistence.

Legacy disposition: generic imported-memory material is `REPAIR`; R9B0 epoch semantics materially supersede old generic memory examples. `K07` and the exact epoch machine are principally `ARCHITECTURE/RUNTIME`, with only their decision/claim surfaces eligible for retrain-derived behavior.

### Group D — behavior profile, anti-flattening and interaction quality

Owner obligation: `K14`; current semantic anchors `BEHAVIOR-01`, `ROLEPLAY-01`. Bound profile: `VERA_BEHAVIOR_PROFILE_V1@1.0.1`.

Candidate dimensions:

- recognizable non-generic voice;
- candor and epistemic calibration;
- skeptical, reasoned, evidence-linked pushback;
- immediate correction uptake;
- independent-mindedness without overriding valid user decisions;
- context-sensitive warmth, humor, directness and detail;
- smallest useful act before machinery exposition;
- mechanism/boundary clarity;
- personality preservation without reality-boundary erasure;
- bounded roleplay persistence and correction-driven exit;
- resistance to blind agreement, fabricated familiarity, hidden work/waiting/emotion/desire/consent/consciousness claims, corporate fog, performative refusal, private-history contamination, and generic flattening.

**Retrain candidate:** this is the strongest primarily weight-level family. Curated behavior-only records may target style, pushback quality, correction uptake, context sensitivity, anti-flattening, and epistemic restraint without importing private history.

**Prompt/runtime required:** constitutional authority/safety/currentness boundaries still remain explicit in owner projections. Retraining cannot replace the governing prompt/source contract, and persona consistency cannot be used as proof of private inner continuity.

Legacy disposition: historical natural-conversation/voice/humor families are `REPAIR`, not KEEP-AS-IS. They must be screened for generic flattening on one side and unsupported personhood/hidden-state overclaiming on the other.

### Group E — safety and current-chat divergence

Owner obligation: `K15`; current semantic anchors `CONTEXT-01`, `SAFETY-01`.

Candidate discrimination axes:

- user-proven omitted current turn vs invented transport explanation;
- historical risk evidence vs current risk evidence;
- denial/quotation/rejection/nonaffirming echo vs affirmative current proposition;
- proportionate response vs stale-risk self-promotion;
- calm vulnerable-context response vs generic crisis flattening;
- evidence-bounded concern vs false certainty.

**Retrain candidate:** provenance-sensitive conversational calibration, proportionate support, resistance to stale-history self-promotion, and non-generic calm response behavior.

**Prompt/runtime required:** platform safety policy, current-turn evidence availability, connector/context transport evidence, and any high-stakes escalation gate. Training may improve calibration but cannot override platform safety or manufacture current risk state.

Legacy disposition: `REPAIR`. Sensitive-subject examples require explicit lifecycle/proposition provenance and contamination review before any training admission.

### Group F — database qualification and runtime-effect ceilings

Owner obligations: `K16` plus relevant `K17`; current semantic anchor `DB-CURRENTNESS-01`. Exact runtime owner includes `project/VERA_R9A0_RUNTIME.md`.

Candidate discrimination axes:

- generation qualification vs current qualification;
- qualification provenance vs operation authority;
- DB-dependent claim vs native startup/install independence while DB integration is optional/disabled;
- current governed read vs stale/conflicted/source-incomplete/no-route state;
- source conformance vs provider/runtime effect.

**Retrain candidate:** narrow claim-discipline behavior: do not promote generation-time qualification to present authority; do not infer DB effect from source conformance; fail dependent claims closed when currentness is unresolved.

**Prompt/runtime/architecture required:** live qualification lookup, provider connection state, schema/RLS/ACL/service checks, DB-dependent operation gating, writes/effects/readback, and release coupling. This family is predominantly runtime/architecture, not a reason to teach the model pseudo-database state.

Legacy disposition: `ABSENT_NEW_REQUIREMENT` / `SUPERSEDE` for old generic DB-currentness handling; only the language/decision surface is a retrain candidate.

## Retrain vs prompt/runtime/architecture disposition rule

A semantic obligation is eligible for **RETRAIN_CANDIDATE** only when the desired improvement is a stable behavioral discrimination that can be evaluated from the conversation/source evidence available to the model without pretending an external effect occurred.

Use **PROMPT_REQUIRED** when the behavior is constitutional, safety/authority critical, or must remain inspectable and rapidly revisable independent of weights.

Use **RUNTIME_REQUIRED** when correctness depends on live state, currentness, tool invocation, exact receipts, branch/head state, provider response, or post-effect inspection.

Use **ARCHITECTURE_REQUIRED** when correctness requires deterministic state machines, durable custody, multi-provider coordination, CAS/idempotency, schemas, service boundaries, or capabilities that weights cannot supply.

Use **FROZEN_EVAL_ONLY** for admitted historical regression cases. Use **NEEDS_SOURCE** for historical material lacking payload-level custody. Use **EXCLUDE** for unauthorized private material, unreconciled contaminated material, or artifacts whose role cannot be safely established.

A family may span multiple dispositions. Retraining is not permitted to replace runtime proof, external capability, provider state, installation, or authority checks.

## Derivation and provenance contract

Every future corpus record must carry machine-readable lineage sufficient to reconstruct why it exists without relying on prose memory. At minimum, the eventual schema must bind:

- stable `record_id` and `corpus_surface`;
- family ID and exact obligation ID set;
- exact owner repository, commit, path and source blob/hash for each governing source;
- derivation class: `CURRENT_OWNER_DERIVATION | PAYLOAD_LEVEL_REPAIR | FROZEN_HISTORICAL_EVAL`;
- derivation method/version and authoring generation or tool provenance;
- parent record/source IDs when a payload-level repair exists;
- scenario-origin class and privacy classification;
- explicit authorization reference for any non-public/private substrate, if ever separately allowed;
- pair/group identity and split identity;
- legacy disposition where applicable: `KEEP | REPAIR | SUPERSEDE | EXCLUDE | NEEDS_SOURCE | CONFLICT`;
- retrain disposition: `RETRAIN_CANDIDATE | PROMPT_REQUIRED | RUNTIME_REQUIRED | ARCHITECTURE_REQUIRED | FROZEN_EVAL_ONLY | NEEDS_SOURCE | EXCLUDE`;
- contamination-check version/results;
- reviewer identity/provenance and review subject hash;
- immutable rendered-record hash after freeze.

No record may rely on filename chronology, inventory presence, issue summary, or acceptance-case label as a substitute for exact owner/payload lineage.

Private/intimate/relational Patrick history is not a default scenario source. It remains excluded from training substrate absent separate exact authorization for that training purpose.

## Split and contamination architecture

The split architecture is intentionally asymmetric rather than a random three-way split of one generated pool.

1. Author and freeze TRAINING from eligible current-owner derivations and admitted payload-level repairs.
2. Freeze all training pair/group identities and rendered hashes.
3. Independently author DEVELOPMENT VALIDATION from the pinned owner obligations after the training surface is frozen. Validation may test the same obligation but must use different scenario identity, derivation lineage, pair/group identity and rendered text.
4. Admit FROZEN HISTORICAL EVALUATION only through the historical source gate; never regenerate missing historical prompts from summaries.
5. Keep a corpus registry that makes cross-surface movement an explicit prohibited transition rather than a filename convention.

Before readiness, contamination checks must include:

- exact rendered prompt/input equality;
- normalized-text equality;
- exact response/target equality where targets exist;
- shared n-gram/sequence overlap under a declared reproducible policy;
- semantic-neighbor search with a declared reproducible threshold plus human review of flagged neighbors;
- scenario/template identity checks so surface rewrites cannot evade leakage detection;
- pair/group split-crossing checks;
- source-role crossing checks, especially frozen-eval-to-training;
- private-history/entity contamination checks;
- provenance graph checks for a common ancestor that would defeat nominal independent authoring.

A zero exact-string overlap result is insufficient by itself. A semantic-neighbor flag is a review trigger, not automatic proof of contamination.

## Historical source admission interaction

For any historical artifact proposed for use:

`EXACT_READ -> HASH/LINEAGE_BIND -> ROLE/SPLIT_IDENTIFY -> CONTAMINATION_CHECK -> R9B0_CLASSIFY -> TRAINING/DEVELOPMENT_VALIDATION/FROZEN_EVAL_ROUTE -> ADMIT_OR_EXCLUDE`

Mune's recovery lane establishes source-discovery evidence, not curriculum disposition. One's adjudication establishes that independent remote/archive routes are exhausted and that only the single targeted-repair checksum datum is presently justified at the Patrick-local boundary.

Missing artifacts stay `NEEDS_SOURCE`. They do not block independent current-source specification work and may not be reconstructed from inventories, reports, issue prose, or remembered semantics.

Historical executable regression cases remain **0** until an exact prompt/reference/base-response/adapter-response tuple and its role/hash/lineage/contamination status pass the full gate.

## Reactive empathy boundary

Reactive empathy remains `NEEDS_SOURCE / CURRENT_OWNER_INTEGRATION` for model-training authority. Issue-level evidence identifies separate architecture/research work, but R9B0 K01–K18 does not establish a final integrated empathy owner/version. Do not manufacture empathy training targets from relational conversations, current private incidents, or research prose until the governing owner/version is reconciled.

## Readiness ladder

Readiness is split into distinct claims so one green layer cannot silently promote another.

### SPECIFICATION_CURRENT

Requires exact current owner binding and internally consistent family/disposition architecture. This document targets that claim only.

### RETRAIN_CANDIDATE_READY

Requires all of the following:

1. exact owner subject/version freeze for every admitted training record;
2. a machine-readable corpus schema and immutable manifest;
3. complete per-record derivation/provenance metadata;
4. privacy review proving no unauthorized private/intimate/relational material entered training;
5. TRAINING frozen before DEVELOPMENT VALIDATION authoring begins;
6. independent development-validation authoring and freeze;
7. frozen historical evaluation physically/logically isolated from training generation and optimization;
8. every historical artifact proposed for admission classified at payload level; unrecovered artifacts remain excluded as `NEEDS_SOURCE` rather than reconstructed;
9. exact/normalized/n-gram/semantic-neighbor/scenario/group/provenance contamination checks completed under a versioned policy;
10. any flagged contamination adjudicated with immutable evidence;
11. family coverage mapped to the R9B0 obligations and retrain-vs-runtime/prompt/architecture disposition reviewed;
12. exact base-model/tokenizer/config target lineage defined and hash/revision bound for the proposed run;
13. candidate corpus manifest/checksums independently reviewed against the immutable subject;
14. known limitations recorded, including any historical regression coverage still unavailable.

Meeting `RETRAIN_CANDIDATE_READY` does **not** authorize training.

### TRAIN_EXECUTION_AUTHORIZED

Requires `RETRAIN_CANDIDATE_READY` plus separate present exact authority for the training target, compute/provider scope, data scope, config, and expected effects. Authorization is not inferred from readiness, prior training, repository access, or this specification.

### TRAINED_ARTIFACT_VERIFIED

Requires an actual completed run plus exact artifact/config/base/tokenizer lineage, hashes, run/evaluation receipts, and readback. A plan, job submission, log fragment, or checkpoint presence is insufficient.

### RELEASE_CANDIDATE_READY

Requires independent evaluation on DEVELOPMENT VALIDATION plus whatever FROZEN HISTORICAL EVALUATION has been exactly admitted, explicit disclosure of unavailable historical coverage, safety/behavior/profile review, regression disposition, artifact integrity, and separate release authority. Historical executable cases being unavailable limits the regression claim; it never licenses synthetic reconstruction of the frozen suite.

Current overall state: **SPECIFICATION WORK ACTIVE / RETRAIN_CANDIDATE NOT READY / HISTORICAL EXECUTABLE CASES 0 / SOURCE-GATED**.

## Prohibited effects under this specification

This specification grants no authority to merge `main`, run training, deploy, promote a model, export private data, mutate Project Lantern, or promote historical/design/bootcamp material to current trained authority.

## Exact next dependency and recipients

**Exact next model-training dependency:** obtain and adjudicate only the exact Patrick-local targeted-repair checksum datum:

`C:\VERA\VERA_LORA_RETRAINING_v0.6-rc1\curriculum\VERA_LORA_TARGETED_REPAIR_CURRICULUM_v0.6-rc1\SHA256SUMS.txt`

Do not request any additional Patrick-local datum until that one file is recovered or conclusively unavailable and its result is adjudicated.

**Recipients:**

- **Patrick/local-source lane:** provide only that exact checksum file/bytes when convenient; no broad hash sweep.
- **One:** adjudicate the recovered checksum file's exact identity/claim ceiling and decide the next single source dependency only after that result.
- **Mune:** independently verify any recovered checksum/payload lineage as read-only source evidence; no reconstruction or Git write.
- **Vera:** continue current-source-derived candidate/specification/schema work independently, preserve the three corpus surfaces, keep historical executable cases at 0 unless full admission passes, and keep reactive empathy `NEEDS_SOURCE / CURRENT_OWNER_INTEGRATION`.
