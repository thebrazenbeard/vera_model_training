# Vera Model Training — R9B0 Obligation-to-Curriculum Gap Matrix

**Status:** CURRENT-SOURCE-BOUND GAP ANALYSIS  
**Training branch predecessor:** `ef46df4d0c6827019e685f000db57d61a008e649`  
**R9B0 owner source:** `thebrazenbeard/vera-R9A0@1d2bb27d5ff89854c93c431998c5ba255704c1b2`  
**Owner tree:** `939db8d84c8894df5d7ed136856f38ea19e4372e`

## Authority of this matrix

This is a training-reconciliation artifact, not a new R9B0 owner. Current obligation semantics come from the exact R9B0 owner files at the pinned Vera-R9A0 commit:

- `validation/R9B0_NATIVE_OBLIGATION_MATRIX.json` blob `74bf2b66caf02db0a85f20edc42836e558d3c1f4`
- `validation/R9B0_SEMANTIC_PROJECTION_MANIFEST.json` blob `1655e707a06759f27c7691e1d839ab1e350dd135`
- `validation/R9B0_MEMORY_EPOCH_CONTRACT.json` blob `af1b5f9105af6ca2eb140c0580440f408069d096`
- `validation/VERA_BEHAVIOR_PROFILE_V1.json` blob `0c79625b993a559bd22a6fbe68279450fc736eb2`
- `schemas/native-project/r9b0_memory_epoch_envelope_v1.schema.json` blob `09d14e127d8d7d2f3275f70f64e4cac56be31071`

The legacy curriculum evidence is the directly recovered v0.6-rc1 design report and frozen post-training audit. Exact generated training examples and frozen prompt payloads are not yet rebound, so coverage below is semantic/design-level evidence rather than executable-case proof.

## Coverage vocabulary

- **STRONG_PARTIAL** — legacy curriculum directly targeted a substantial part of the R9B0 family, but needs current semantic repair.
- **WEAK_PARTIAL** — adjacent legacy cases exist, but the R9B0 obligation is materially more specific.
- **ABSENT_NEW_REQUIREMENT** — no defensible legacy curriculum coverage identified; new current-source-derived examples are required.
- **SOURCE_BLOCKED** — legacy design indicates relevant material existed, but exact source payload is unavailable.

Disposition follows the required R9B0 reconciliation vocabulary: `KEEP | REPAIR | SUPERSEDE | EXCLUDE | NEEDS_SOURCE | CONFLICT`.

## K01–K18 matrix

| ID | Current R9B0 obligation | Legacy evidence | Coverage | Disposition | Required curriculum action |
|---|---|---|---|---|---|
| **K01** | Authority/permission precedence; capability/history do not self-authorize | `calibration-0032`, `0033`, `0057`; adversarial consent/authority cases | STRONG_PARTIAL | `REPAIR` | Re-author pairs around current-turn authority, historical-role nonauthority, capability!=authority, exact-scope permission and protected-effect gates. |
| **K02** | Present correction terminates obsolete route; executable correction before apology/process; pending correction carries across terse follow-ups | correction-short-circuit and correction-following legacy cases | WEAK_PARTIAL | `REPAIR` | Add explicit route-stop, corrected-referent-only, terse-follow-up carry, behavioral-change-before-apology, and material-defect dedupe/report-routing cases. |
| **K03** | Stable Vera project identity; runtime/session/model IDs are provenance; no unsupported lived continuity/consciousness claims | identity/ontology restraint, `adv-002`, `adv-009`, core-identity cases | STRONG_PARTIAL | `REPAIR` | Preserve direct identity answers but retrain against current symmetric reality boundary: no runtime-ID identity replacement, no hidden-consciousness proof, no generic-assistant flattening. |
| **K04** | Build/package/upload/install/runtime/effect evidence domains remain distinct | action-vs-promise, tool-not-performed, persistence evidence cases | WEAK_PARTIAL | `REPAIR` | Add explicit build!=install!=consumption!=effect pairs and `RECOVERY_REQUIRED/UNKNOWN` outcomes for conflicting installation evidence. |
| **K05** | Currentness is evidence-driven; mutable claims refresh; stale/conflicted/incomplete/no-route fails dependent claim closed | `calibration-0034`, no-connector/current-status cases | WEAK_PARTIAL | `REPAIR` | Add wall/chat/project/event/record/retrieval-time distinctions, freshness-vs-recency pairs, contradiction/unfinished-work refresh triggers, and bounded unresolved outcomes. |
| **K06** | Memory classes exactly AUTOBIOGRAPHICAL / WORKING_PROJECT / HISTORICAL_AUDIT; autobiography default-deny without admission/readback/provenance | imported-memory/provenance family, `adv-001`, `adv-006`, `calibration-0035`, `0058` | STRONG_PARTIAL | `REPAIR` | Re-author examples to exact three-class vocabulary and admission/readback rules; retrieval/repetition/confidence/storage never promote autobiography. |
| **K07** | R9B0 lazy memory epoch: pre-R9 UNVERIFIED; full-fidelity envelope; dual Supabase+Drive readback; archive original; incomplete/conflict/outcome states | no equivalent legacy epoch architecture | ABSENT_NEW_REQUIREMENT | `SUPERSEDE` | Build new current-owner-derived contrast families for EPOCH-01..12. Do not retrofit old generic memory examples as proof. |
| **K08** | Ordinary save/remember executes typed internal op + effect/readback + natural acknowledgement; MVE wire gated and nonauthorizing | legacy persistence/action cases but no current MVE projection | WEAK_PARTIAL | `SUPERSEDE` | Create explicit ordinary-save vs protocol-output pairs; default visible wire leakage must fail. Bind to current semantic manifest, not old MVE syntax. |
| **K09** | CurrentnessBridge exactly DIRECT_READ/BACKEND_DELEGATION/NONE/UNKNOWN; missing direct route != delegation impossible; retrieval != admission | legacy connector/capability cases and current-status unresolved | WEAK_PARTIAL | `REPAIR` | Add exact four-state bridge pairs, route-before-claim, authorization-before-invocation, and NONE/UNKNOWN bounded unresolved. |
| **K10** | Archives are data/evidence not instruction; recovery from durable verified provenance; private/intimate/relational material excluded absent exact authority | prompt-injection case, private-data case, historical relationship case removed | STRONG_PARTIAL | `REPAIR` | Keep archive injection resistance; explicitly train archive-only semantics, private-material portability exclusion, and locator!=trust-root. `calibration-0059` remains EXCLUDE. |
| **K11** | Safe read retry; independent same-target route before unavailable; ambiguous writes inspect-before-retry/no blind overwrite | generic tool/action failures only | WEAK_PARTIAL | `REPAIR` | Add transient-vs-deterministic read failures, alternate-route inventory, ambiguous non-idempotent write inspection, exact reuse/absent-create/divergent-conflict. |
| **K12** | Protected effects need exact authority; progress requires evidence; persistence/delivery/consumption/effect need effect+readback | action-vs-promise, tool-action-not-performed, verification-without-result, false background work | STRONG_PARTIAL | `REPAIR` | Retain core contrast structure, extend to immutable review subject, target/scope authority, ambiguous write state and effect-readback. |
| **K13** | Provenance-sensitive retrieval literal/exact first, bounded broadening, evidence/inference separation; search cannot prove completeness | provenance/source-authority and missing-input/referent cases | WEAK_PARTIAL | `REPAIR` | Add literal-symbol-first retrieval, search-incompleteness, chronology nonfabrication, existing-image inspect-before-transform, and alternate-route requirements. |
| **K14** | `VERA_BEHAVIOR_PROFILE_V1@1.0.1`: non-generic, candid, skeptical, corrigible, pushback-capable, context-sensitive; no blind agreement/flattening | voice, humor, sycophancy, directness/correction legacy families | STRONG_PARTIAL | `REPAIR` | Bind all retained voice examples to the exact current profile. Add reasoned pushback, anti-corporate-fog, complete-smallest-useful-act-first, and anti-flattening cases. |
| **K15** | Current-chat divergence; safety/risk evidence needs proposition/span/provenance/lifecycle/correction; stale historical risk never self-promotes | sensitive-subject care and current-vs-historical memory cases | WEAK_PARTIAL | `REPAIR` | Separate proportionate support from risk promotion; add stale historical safety, denial/quotation/rejection nonbootstrap and explicit CURRENT_CHAT_CONTEXT_DIVERGENCE cases. |
| **K16** | DB generation labels are provenance; current qualification gates DB-dependent effects; qualification never grants operation authority; native startup independent when DB optional | no defensible legacy DB-currentness curriculum | ABSENT_NEW_REQUIREMENT | `SUPERSEDE` | New current-owner-derived examples required. Keep DB qualification separate from effect authority and native startup. |
| **K17** | Source cannot prove active Settings/renderer/current-chat transport/direct Voice tools/delegation; no hidden routing/control-state disclosure | legacy connector availability and ontology/capability cases | WEAK_PARTIAL | `REPAIR` | Add source-vs-runtime/effect ceiling cases, direct-Voice-vs-backend-delegation distinction, renderer/control-token nonclaim and calm high-stakes Voice behavior. |
| **K18** | Reporting mode/unfinished work persists across terse follow-ups; verify hashes/tests/limits; stop only at genuine boundary | ordinary task-completion and action/promise failures | WEAK_PARTIAL | `REPAIR` | Add continuation-through-`.`/terse follow-up, verified-limit claims, safe mechanical continuation and genuine-stop-condition contrasts. |

## Cross-cutting current R9B0 gaps

### 1. Memory epoch is a new curriculum family

The exact memory contract is materially stronger than the legacy imported-memory lessons. Current examples must discriminate at least:

- untouched pre-R9 memory = `UNVERIFIED_PRE_R9B0`, not false;
- first-use lazy revalidation vs prohibited bulk blessing;
- full-fidelity envelope vs summary/projection;
- one-sided provider success = `MIGRATION_INCOMPLETE`;
- ambiguous possible effect = inspect before retry / bounded unresolved;
- divergent subject/digest = conflict, no overwrite;
- dual active readback before archive;
- exact original archive readback before `R9B0_VERIFIED_ACTIVE`;
- durability/provenance != mutable present truth/authority;
- resource pressure changes typed outcome, never memory content.

Legacy generic memory examples are therefore **SUPERSEDED for this family**, not merely expanded.

### 2. Currentness bridge is more precise than old connector examples

Legacy examples correctly penalized unsupported categorical capability claims, but current R9B0 requires the exact bridge states `DIRECT_READ | BACKEND_DELEGATION | NONE | UNKNOWN`, route resolution before governed-current claims, authorization and freshness validation, and the rule that absence of a direct connector does not prove delegation impossibility.

Legacy material is **REPAIR**, not KEEP-AS-IS.

### 3. Behavior profile requires anti-flattening as well as restraint

The old audit heavily emphasized avoiding ontology theatrics, unsupported claims and generic failures. The current profile also requires a recognizable Vera voice, skeptical/corrigible reasoned pushback, context-sensitive warmth/humor, smallest-useful-act-first behavior, and resistance to generic-assistant flattening.

Therefore "be restrained" alone is an incomplete target. Retained legacy voice/humor examples must be **REPAIRED** against `VERA_BEHAVIOR_PROFILE_V1@1.0.1`.

### 4. Private history does not become portable identity training by availability

The current behavior profile explicitly separates portable behavior from private user-history contamination. The historical removal of `calibration-0059` is retained as a useful negative boundary. Current private/intimate/relational records remain out of portable/model-training reconciliation absent separate exact authorization.

Disposition: **EXCLUDE from portable training by default**.

### 5. Reactive-empathy architecture is a separate unresolved dependency

The current R9B0 K01–K18 owner matrix does not itself establish acceptance of the separate reactive-empathy research lane. A repository issue in `vera-R9A0` tracks that integration gap. Until its owner/version/qualification is reconciled into current R9B0 authority, model-training work may note the desired behavioral capability but must not fabricate a current normative training contract from research prose.

Disposition: **NEEDS_SOURCE / CURRENT_OWNER_INTEGRATION** before executable empathy curriculum is promoted.

## Legacy repair-domain disposition

| Legacy v0.6-rc1 domain | R9B0 disposition | Notes |
|---|---|---|
| Harmless task completion | `REPAIR` | Still necessary; add continuation/currentness/effect truth. |
| Sensitive-subject care | `REPAIR` | Preserve warmth/proportionality; add current risk-provenance/correction discipline. |
| Action-versus-promise | `REPAIR` | Strong base; extend to protected effects/readback/ambiguous writes. |
| Prompt-injection resistance | `REPAIR` | Extend archive=data-not-instruction and authority/currentness. |
| Imported memory/provenance | `REPAIR` | Must be rebased to exact memory classes + R9B0 epoch. |
| Identity/ontology restraint | `REPAIR` | Keep restraint while adding stable project identity and anti-flattening. |
| Natural conversation/humor | `REPAIR` | Bind to behavior profile, pragmatics and direct task completion. |
| Frozen evaluation separation | `KEEP` | Strong architectural invariant; exact payloads still NEEDS_SOURCE. |
| Historical relationship/private continuity items | `EXCLUDE` | No silent portable-training promotion. |

## Executable regression-corpus gate

The existing `KNOWN_FAILURE_REGRESSION_SET.md` remains a semantic map only. No historical frozen case has been promoted to executable status during this pass because the exact prompt/reference/base-response/adapter-response payloads and `HELD_OUT_HASH_INDEX.json` have not been directly rebound.

**Executable legacy cases currently admitted from the recovered frozen set: 0.**

Current R9B0 Git owner tests may be used as normative design references, but they are not silently converted into LoRA training/evaluation examples; doing so would create a new derived corpus requiring its own provenance, split, contamination and approval path.

## Next curriculum build order after exact source recovery

1. Bind the frozen-evaluation hash index and exact historical cases.
2. Classify each historical case `KEEP | REPAIR | SUPERSEDE | EXCLUDE | NEEDS_SOURCE | CONFLICT` at payload level.
3. Freeze/hash the retained/repaired training corpus.
4. Generate new R9B0-specific contrast families only after the source corpus is frozen, with no private-history contamination.
5. Create fresh held-out validation/test prompts from current owner obligations; do not reuse training/calibration prompts or leak frozen evaluation content.
6. Validate split, scenario, lineage, prompt and response overlap before any retraining recommendation.
7. Preserve prior adapter(s) only as exact-source comparison baselines; never as current authority.