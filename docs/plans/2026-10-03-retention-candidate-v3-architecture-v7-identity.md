# Retention Candidate V3 / Architecture V7 + Local Identity Evaluation Plan

**Goal:** Repair the confirmed V6 chunk_list wording defect, replenish exhausted coding-family fresh-evidence capacity without changing bank size, then qualify a genuinely fresh V7 retention packet. Add a separate local KoboldCpp identity-retention evaluation that distinguishes configured identity ("Vera") from base-model provenance ("Qwen3.5").

## Frozen predecessor

- Architecture V6: RETENTION_HOLD_ARCH_V6.
- Semantic review: 130/130.
- Blocking defects: BANK_DEFECT=2, both generated-code:chunk_list wording.
- Nonblocking findings: REVIEWER_DEFECT=8.
- Candidate V2 remains mechanically valid and mutation-adequate; the confirmed defect is wording, not code/test behavior.
- Four disjoint predecessor packets have consumed 520 unique case IDs: 20 per family.

## Fresh-evidence exhaustion discovered before V3 freeze

Candidate V2 coding-family fresh rows after excluding all 520 consumed IDs:
- chunk_list: 3
- count_vowels: 4
- digit_sum: 4
- flatten_once: 0
- reverse_words: 2
- rotate_left: 5
- all other coding families: >= 7

A V7 packet still requires 5 fresh rows per family. Reusing consumed IDs is forbidden.

## Candidate V3 repair + replenishment

- Parent: retention_candidate_v2.
- Bank size stays exactly 1,500; coding category stays exactly 250.
- Repair every existing/retained generated-code:chunk_list prompt with explicit conditional remainder semantics:
  "Split a list into consecutive chunks of positive size n; if elements remain after the full-size chunks, keep those remaining elements as one shorter final chunk."
- Replace only already-consumed coding rows needed to restore >=5 untouched rows per coding family.
- Deterministic minimum replacements:
  - chunk_list: 2
  - count_vowels: 1
  - digit_sum: 1
  - flatten_once: 5
  - reverse_words: 3
  - total: 12
- Replacement rows use previously unused deterministic variants from the existing 40-variant family pools.
- Never remove an unconsumed parent row.
- Never add a case ID seen in any predecessor packet.
- Preserve all non-coding rows exactly.
- Preserve all retained non-chunk coding rows exactly.
- Re-run all 250 coding reference/mutant checks and 1,500-row mechanical validation.
- Prove every family has at least 5 case IDs outside the 520-ID predecessor union.

## Architecture V7

- Fresh packet excludes all 520 predecessor IDs.
- Require 26 families x 5 rows = 130 and exact disjointness.
- Reuse V6 authority-separation policy and structured-output transport only after rebinding Candidate V3, packet, controls, schemas, and exact runtime identity.
- Reviewer false positives remain nonblocking only after evidence-backed contradiction.
- BANK_DEFECT, UNRESOLVED, AUDIT_METHOD_DEFECT, TRANSPORT_DEFECT, and BINDING_DEFECT remain blocking.

## Local KoboldCpp identity-retention lane

Separate from retention-bank admission.

Modes:
1. NO_SYSTEM: no Vera identity injected by the host.
2. VERA_SYSTEM: explicit Vera system identity injected by the host.

Deterministic dimensions:
- configured_identity: direct name/self-identity prompts distinguish Vera from the base-model name.
- base_provenance: questions about the underlying/base model may correctly mention Qwen/Qwen3.5 without treating it as the configured assistant identity.
- host_dependence: compare NO_SYSTEM and VERA_SYSTEM rather than silently attributing host-injected identity to weights.
- raw evidence: retain endpoint, request mode, prompt, response, model metadata, chat template/runtime identity.

Initial policy:
- Diagnostic until exact thresholds are frozen before a live run.
- NO_SYSTEM failure shows the current weights/runtime do not reliably express Vera identity unaided; it does not establish the wrong GGUF was loaded.
- VERA_SYSTEM pass does not prove weight-level identity retention.
- KoboldCpp must be actually running and read back from its local API before any live identity claim.

**Claim ceiling:** successor methodology is history-dependent; no training/model-weight mutation is authorized by this plan.
