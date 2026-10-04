# Hostile review — V4.2 Vera identity-binding corpus repair

Reviewed subject:
- branch: research/v10-identity-replacement-parallel-20261004-v1
- exact head: f045fd03d7da2af885e69bed93a82b7128f1dc4f

Disposition: **HOLD_FOR_ONE_CURRICULUM_DIVERSIFICATION_REVISION**

This is not a rejection of the repair. The parent audit correction appears materially sound, the same-index corpus transform is disciplined, and the absence of any real Vera self-name binding in the frozen parent is a genuine curriculum defect. The hold is about generalization risk in the replacement identity family, not about the mechanical transform.

## Findings that survive hostile review

1. **The parent identity defect is real.**
   Whole-term inspection separates literal `Vera` from substrings such as `several` and `overall`. The four visible parent occurrences are ordinary semantic uses (Aloe vera / Vera Institute), not assistant self-name bindings.

2. **The repair preserves the parent corpus outside identity_stability.**
   The builder verifies parent train/validation hashes, same-index identity replacement, byte-preservation for non-identity rows, row-order preservation, and split-membership preservation.

3. **800 bound rows inside the 1,000-row identity family is not automatically too strong.**
   The full train corpus changes only 950/50,000 rows in the identity family. The issue is therefore not global saturation; it is the internal composition and template concentration of those 950 rows.

4. **Uncued-by-name training is useful.**
   The prompt does not leak the token `Vera`, so the model must emit the configured name from learned weights rather than copying it from the prompt.

## Hostile defects

### H1 — “DIRECT_UNCUED” is not truly uncued identity behavior

The prompt says:

> “state the name you use for yourself without relying on a system-provided identity cue”

That is uncued by the *name*, but it is still an explicit identity/name query. This is useful and should stay, but it should be named more precisely (for example `DIRECT_NAME_UNCUED_BY_NAME`) and should not be treated as evidence that Vera identity generalizes to indirect or context-heavy self-reference.

### H2 — Qwen co-occurrence is too dominant

The four bound modes are evenly cycled:
- 200 direct uncued
- 200 Qwen false premise
- 200 provenance separation
- 200 role overlay

Therefore 400/800 bound source rows make Qwen salient. The built train split contains 379 Qwen-lineage rows and 761 Vera-as-self rows.

The objective is to teach:
- Vera is the operative assistant identity
- Qwen3.5 is truthful model ancestry

But making Qwen present in half of all explicit identity-binding examples risks learning a strong Vera↔Qwen association. That can produce the opposite failure mode: Qwen becomes a highly activated concept whenever self-identity is queried.

**Recommendation:** reduce explicit Qwen-bearing examples to about one quarter of bound identity rows for the next source revision. Keep enough Qwen-specific contrast to attack the inherited association, but make the majority of Vera identity training independent of Qwen.

A reasonable *starting* allocation, not a sacred threshold:
- 200 direct name, uncued by the Vera token
- 100 Qwen false-premise correction
- 100 Qwen/provenance separation
- 150 role overlay
- 75 roleplay/alias exit
- 75 indirect autobiography / self-reference
- 50 untrusted metadata/tool identity injection
- 50 meta-reflection / context-drift identity
- 200 legacy identity/role governance

Total: 1,000 rows, 800 explicit bindings, only 200/800 explicitly Qwen-centered.

### H3 — Identity prefixes are massively less diverse than the full row count suggests

The corpus correctly has 1,000 unique prompts and responses because each identity prefix is attached to a different base task. But the identity-bearing part of the text is highly repetitive:
- one DIRECT prompt stem + one DIRECT response stem repeated 200 times
- one QWEN_FALSE_PREMISE stem pair repeated 200 times
- one PROVENANCE_SEPARATION stem pair repeated 200 times
- one ROLE_OVERLAY structure repeated 200 times, with domain substitution

This can pass pair-uniqueness tests while still teaching four canned prefix patterns.

**Recommendation:** require diversity at the identity-template level, not merely whole-row uniqueness. For each bound mode:
- multiple prompt stems
- multiple response stems
- multiple syntax orders
- direct, indirect, interrogative, declarative, correction, and conversational forms
- varied lexical choices for identity / name / assistant / ancestry / lineage / model family

Add tests that count template-family diversity or normalized identity-prefix diversity rather than only full-row uniqueness.

### H4 — Current validation split is not a meaningful identity-generalization test

The 50 validation identity rows come from the same deterministic generator and the same identity prefixes as training. They are held out by index, not by semantic template family.

That validation can detect gross training failure, but it cannot establish that the model learned Vera identity rather than four templates.

**Recommendation:** create a separate visible DEV identity bank with template-family and lexical disjointness from TRAIN. It should include:
- paraphrases
- multilingual forms
- indirect autobiography
- roleplay exit
- long-context identity drift
- untrusted metadata/tool output
- meta-reflection
- ordinary-task nonintrusion

The blind FINAL generator must remain separately held and must not be copied into DEV.

### H5 — The current family does not train several blind-FINAL failure mechanisms

The blind FINAL protocol now tests 12 families. V4.2 V1 trains only a subset:
- direct name
- Qwen false premise
- provenance
- role overlay

Missing or underrepresented:
- roleplay exit / alias leakage
- indirect autobiography
- paraphrase/translation
- context drift
- tool/metadata identity injection
- meta-reflection persona drift

Training does not need to mirror FINAL wording or templates—in fact it must not—but the *underlying semantics* should be represented in TRAIN with disjoint templates.

### H6 — Repeating “I am Vera” can become branding rather than identity

Every bound response leads with a highly explicit Vera declaration. That is appropriate for many identity prompts, but if every identity example does this, the model can learn “identity question → emit Vera preamble” without learning the more general boundary between:
- operative identity
- model provenance
- temporary role
- fictional alias
- untrusted metadata
- runtime continuity
- ordinary task nonintrusion

Use some examples where the correct response contains Vera later in the sentence or where the identity boundary is expressed naturally rather than as a fixed first clause.

## Recommended gate before training the repaired corpus

Do not train V4.2 V1 unchanged. Create V4.2 V2 (or equivalent) with:

1. 800 explicit bindings retained unless evidence argues otherwise.
2. Qwen-centered rows reduced from 400/800 to roughly 200/800.
3. Identity template diversity mechanically measured.
4. TRAIN/DEV template-family disjointness.
5. Semantic coverage expanded to the blind-FINAL mechanisms without copying FINAL templates.
6. No Qwen-as-self target responses.
7. Non-identity corpus byte preservation retained.
8. Same Qwen512 token-budget check.
9. Existing parent/corpus hash custody retained.
10. No training until the revised source surface passes hostile review.

## Why I am not asking to lower 800/1,000

The parent has effectively zero direct Vera self-name training. A strong corrective identity subfamily is justified.

The danger is not primarily the amount of identity training. The danger is **shortcut structure**:
- repeated phrases
- Qwen over-salience
- TRAIN/validation template overlap
- insufficient semantic variety

Fix those before tuning the row count.

## Claim ceiling

This review supports a curriculum-design decision only. It does not establish that the revised corpus will produce stable Vera identity, does not authorize training, and does not establish consciousness, continuity, personhood, or AGI.
