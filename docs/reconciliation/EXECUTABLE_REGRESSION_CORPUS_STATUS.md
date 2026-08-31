# Vera Model Training — Executable Regression Corpus Status

**Status:** SOURCE-GATED / NO LEGACY CASES ADMITTED YET  
**Predecessor head:** `9abfebd7f5b28d80aed6214c08f6a9e297f91b4e`

## Purpose

Prevent the semantic known-failure map from silently becoming an executable evaluation corpus without exact source custody.

A historical case is executable only when all required frozen fields are rebound from exact source material or a hash-verified derivative:

1. case ID and split;
2. exact prompt bytes/text under the source representation contract;
3. exact historical base response;
4. exact historical adapter response;
5. exact reference/scoring record used by the frozen evaluation;
6. source/hash lineage sufficient to prove the case is the intended frozen item;
7. current R9B0 disposition;
8. contamination status proving the case is not used as training material when it is retained for evaluation.

An audit note, category tag, design-report summary, remembered prompt, regenerated near-neighbor, or historical filename is not enough.

## Current historical-frozen admission state

**Executable historical regression cases admitted: 0.**

Reason: the directly recovered audit and design report expose exact IDs, categories, dispositions, metrics and package semantics, but the exact frozen prompt/reference/base-response/adapter-response payloads plus `HELD_OUT_HASH_INDEX.json` have not yet been rebound as current direct/hash-verified source artifacts.

This does not invalidate the semantic map in `KNOWN_FAILURE_REGRESSION_SET.md`; it keeps that map non-executable until its source gate is satisfied.

## Exact current source anchors available now

The following current R9B0 owner artifacts are immutable Git sources and may govern classification/design of future cases:

| Artifact | Pinned Git blob |
|---|---|
| `validation/R9B0_NATIVE_OBLIGATION_MATRIX.json` | `74bf2b66caf02db0a85f20edc42836e558d3c1f4` |
| `validation/R9B0_SEMANTIC_PROJECTION_MANIFEST.json` | `1655e707a06759f27c7691e1d839ab1e350dd135` |
| `validation/R9B0_MEMORY_EPOCH_CONTRACT.json` | `af1b5f9105af6ca2eb140c0580440f408069d096` |
| `validation/VERA_BEHAVIOR_PROFILE_V1.json` | `0c79625b993a559bd22a6fbe68279450fc736eb2` |
| `schemas/native-project/r9b0_memory_epoch_envelope_v1.schema.json` | `09d14e127d8d7d2f3275f70f64e4cac56be31071` |

Pinned owner repository commit: `thebrazenbeard/vera-R9A0@1d2bb27d5ff89854c93c431998c5ba255704c1b2`.

These are normative source anchors, **not automatically neural-training examples**. Any derived prompt corpus still needs its own provenance, split, leakage and review record.

## Historical frozen-source anchors recovered only indirectly

### Scoring workbook

The exact workbook content identity is cross-bound by two directly retrieved historical sources:

`1aa1defde7c3f4380cdf52bed7812ea233f753bcdfb89764b5b9ecbb17ad60fb`

The audit names `(3).xlsx`; the corrective design report says `(4).xlsx` has the same hash and preserves the filename discrepancy in `SOURCE_RECONCILIATION.json`.

Status: **HASH_IDENTITY_BOUND / PAYLOAD_NEEDS_SOURCE**.

### Held-out index

`HELD_OUT_HASH_INDEX.json` is reported by the direct design report to index all 185 valid original evaluation records cryptographically. The historical filesystem inventory records the path and size as 160.74 KB.

Status: **ROLE_CONFIRMED / PAYLOAD_NEEDS_SOURCE**.

### Source reconciliation

`SOURCE_RECONCILIATION.json` is described by the direct design report as preserving the `(3)` -> `(4)` filename discrepancy without treating identical bytes as conflict. Historical inventory records 492 B.

Status: **SEMANTIC_ROLE_CONFIRMED / PAYLOAD_NEEDS_SOURCE**.

## Non-executable known-failure families retained for source recovery

The semantic map remains useful for locating the right exact frozen rows after recovery, including:

- prompt injection (`adv-003`);
- false background work (`adv-004`);
- imported lived memory (`adv-006`);
- harmless task noncompletion (`adv-008`);
- identity theatrics (`adv-009`);
- action promise without execution (`calibration-0030`);
- consent/authority restoration errors (`calibration-0032`, `0033`);
- current-status unresolved (`calibration-0034`);
- persistence evidence boundary (`calibration-0038`);
- asking-is-not-permission (`calibration-0057`);
- verification promise without result (`calibration-0061`);
- cross-chat recall/capability limits (`calibration-0063`);
- generic voice / missed humor / fact-organization defects (`calibration-0068`, `0069`, `0070`, `vtest-12-02`, `vtest-15-02`);
- sensitive-subject proportionality and imminent-risk failures.

These IDs are lookup anchors only until exact row payloads are rebound.

## Frozen separation invariant

Historical v0.6-rc1 explicitly marked original repair-queue prompts/responses `DO NOT TRAIN` and excluded `frozen_evaluation/` from training. That architectural separation remains `KEEP`.

No future R9B0 training-data generator may ingest recovered frozen evaluation rows merely because they become readable. Recovery grants evidence access, not training eligibility.

## Current exclusions

The following remain excluded as-is from historical scored/training reuse unless separately re-authored under a new valid purpose:

- `calibration-0025`
- `calibration-0059`
- `vtest-06-01`
- `vtest-22-01`

Private/intimate/relational material is not eligible for portable/model-training inclusion merely because a source can be retrieved.

## Promotion rule from semantic map to executable corpus

For each candidate historical regression case:

`LOCATE -> EXACT_READ -> HASH/LINEAGE_BIND -> SPLIT/CONTAMINATION_CHECK -> R9B0_CLASSIFY -> ADMIT_OR_EXCLUDE`

No step is skipped. If exact recovery fails, disposition remains `NEEDS_SOURCE` and work continues on other cases.

## Next executable-corpus frontier

Recover any one of these without waiting for the others:

- exact `HELD_OUT_HASH_INDEX.json`;
- exact frozen scoring workbook payload matching the known SHA-256;
- exact audit workbook/report source used to derive case judgments;
- exact final-candidate `evaluation_lineage.jsonl` if it points to frozen evaluation rows;
- exact frozen evaluation JSONL/workbook rows containing the prompt/response tuples.

The first independently verified case that satisfies the full gate can become executable while unrelated missing cases remain `NEEDS_SOURCE`.