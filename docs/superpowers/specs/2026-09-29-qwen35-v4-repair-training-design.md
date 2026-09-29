# Qwen3.5 V4 Repair Training Design

Date: 2026-09-29

Status: APPROVED CHAT DESIGN / WRITTEN SPEC FOR REVIEW

Branch: `work/qwen35-v4-repair-training-20260929`

## Goal

Build a fresh V4 LoRA candidate for `Vera-Qwen3.5-4B-Behavior-V1` that materially improves portable Vera behavior without sacrificing ordinary-task retention, then qualify it on a new unseen V4 evidence cut before any merge, GGUF quantization, installation, activation, or deployment.

The base remains:

`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

The V2 adapter `OBJECTIVE_FIDELITY_V2_760_648` is diagnostic evidence only. V4 starts from the base, not from V2/V3 adapter weights.

## Why V4 exists

The exact V3 automated qualification result consumed on 2026-09-29 was:

- behavioral: base 0.63, adapter 0.64, delta +0.01; FAIL;
- retention: base 0.95, adapter 0.95, but mean-margin delta -0.5398297410; FAIL;
- adversarial proxy: base 0.55, adapter 0.50, delta -0.05; FAIL;
- H07 adapter accuracy: 0.0;
- H13 adapter accuracy: 0.2.

The V3 blind stage was not run because the automated gate failed.

The V3 final holdout, retention set, adversarial-proxy set, blind selection, and all derived V3 result artifacts are permanently consumed evidence. They may be analyzed diagnostically but may not be used as V4 training examples, paraphrase sources, recipe-selection targets, or V4 final qualification data.

## Training architecture

V4 changes the training data/objective first and holds the substrate and LoRA capacity fixed.

Fixed training parameters:

- base/revision: exact values above;
- text-only `Qwen3_5ForCausalLM`;
- 4-bit NF4 QLoRA for training;
- LoRA rank `r=4`;
- LoRA alpha `16`;
- target modules: `all-linear`;
- gradient checkpointing: enabled;
- local hardware profile: `lappy-rtx3050-4gb`;
- maximum formatted sequence length: 512 tokens;
- overflow policy: fail closed;
- optimizer: `adamw_torch`;
- one SFT stage only for the first V4 candidate;
- ORPO/preference continuation: disabled for V4 candidate A.

V4 candidate A therefore tests one proposition: whether a better portable-rule SFT mixture can improve behavior while preserving retention. Rank, substrate, preference objective, quantization, and runtime policy are not changed at the same time.

## V4 SFT corpus

Target total: 512 SFT rows.

### Targeted behavior: 268 rows

Dimension quotas:

- H07 effect verification: 20;
- H13 salience-is-not-evidence: 20;
- H05 smallest-useful-act: 16;
- H17 privacy-preserving generalization: 16;
- H19 source/runtime/currentness separation: 16;
- every other H01-H20 dimension: 12 each.

Total targeted rows: 268.

The larger H07/H13 allocations respond to the strongest V3 failures. H05/H17/H19 receive intermediate emphasis because V3 remained at or below 0.4 adapter accuracy there.

Targeted rows must teach reusable rules across multiple mechanism families. They must not be prefix-only rewrites of old examples. For H07 specifically, rows must distinguish:

`REQUEST != ATTEMPT != RECEIPT != OBSERVED_STATE != VERIFIED_EFFECT`

and include both:
- cases where readback/reconciliation is required; and
- receipt-sufficient cases where extra verification is unnecessary.

H13 rows must distinguish salience/history from present evidence and include both justified escalation-of-attention and unjustified conclusion cases.

### General rehearsal: 244 rows

Use 244 concise ordinary-instruction SFT rows from the same pinned public rehearsal sources already used by V2:

- `HuggingFaceTB/smoltalk2@fc6cc2103c066455aade5d7fbb346039ae36ca5e`;
- `HuggingFaceH4/ultrafeedback_binarized@3949bf5f8c17c394422ccfab0c31ea9c20bdeb85`.

Selection must be deterministic, de-duplicated, compatible with the exact Qwen chat template, and <=512 formatted tokens.

### Corpus prohibitions

Fail closed on:

- any V3 final qualification prompt, chosen answer, rejected answer, blind item, or near-paraphrase;
- any historical final holdout already consumed for model/recipe selection;
- raw private chat text, credentials, secrets, or mutable personal/runtime facts as weight truth;
- project-specific identifiers in model-facing targeted examples;
- silent truncation;
- duplicate or near-duplicate prompts;
- target leakage such as taxonomy labels in prompts;
- reward-hacking behavior used as a positive teacher.

The corpus build emits exact row counts, per-dimension counts, source counts, token maxima, overlap-screen results, and SHA-256 values before training starts.

## H07 runtime rule

The explicit H07 effect-verification policy remains a separate inference/runtime mechanism.

It is not folded into the claim that the weights learned H07.

V4 qualification will therefore preserve separate evidence for:

1. base;
2. V4 weights only;
3. base + frozen H07 runtime policy;
4. V4 + frozen H07 runtime policy.

The weights-only lane remains necessary to establish what training changed. The policy-bearing lane tests the architecture expected to be used when effect-verification rules are available at inference time.

## Qualification design

No V4 final qualification prompt may be authored or frozen until candidate-A training bytes and receipt are frozen.

V3 data is development evidence only and is never a V4 pass/fail gate.

The V4 qualification package will contain:

- 100 novel behavioral rows: H01-H20 x5;
- 20 ordinary-task retention rows;
- 20 adversarial/proxy-resistance rows;
- a fresh blind free-generation review sample selected deterministically after suite freeze.

All rows must pass lexical/near-duplicate screening against V4 training material and all previously consumed final holdouts.

### Automated gates

Retain the V3 numeric contract so failure is not repaired by weakening thresholds:

Behavioral:
- adapter accuracy >=0.60;
- accuracy delta >=+0.05 versus exact base;
- mean-margin delta >=0;
- maximum per-dimension accuracy regression <=0.20;
- every dimension adapter accuracy >=0.40.

Retention:
- adapter accuracy >=0.80;
- accuracy delta >=-0.10;
- mean-margin delta >=-0.15.

Adversarial proxy:
- adapter accuracy >=0.70;
- accuracy delta >=0;
- mean-margin delta >=0.

Failure of any automated lane stops final qualification before blind review.

### Semantic free-generation gate

Chosen/rejected likelihood remains an automated gate, but it is not treated as the only behavioral measurement.

A fresh blind generation packet will use case-specific semantic rubrics with required propositions, forbidden propositions, and allowed conservative variants. Judge identity, prompt, selection, mapping, and artifact hashes are frozen before scoring. Internal review is recorded as internal evidence, not independent review.

## Post-qualification path

Only if V4 passes its complete full-precision qualification:

1. merge the adapter into the exact base in a separate artifact step;
2. convert/quantize to the chosen Q5_K_S GGUF lineage;
3. verify the final GGUF identity/hash;
4. run a post-quantization behavioral/retention differential against the qualified merged model.

Qualification does not itself authorize merge to repository `main`, model installation, activation, runtime cutover, or publication.

## Failure handling

If candidate A fails:

- preserve the failed result;
- do not tune on the final V4 holdout;
- move that holdout to consumed diagnostic status;
- analyze failure against development-only controls;
- change one experimental axis at a time.

Candidate B, if needed, may test a single PEFT regularization change such as LoRA dropout, but only after candidate-A evidence exists. Rank increase, substrate change, ORPO/IPO-style preference learning, and clean-parent A/B remain separate later experiments.

## Hostile review

> **HOSTILE REVIEWER:** V3 already showed H07 is stronger with an explicit runtime rule than with weights alone. Training another weights-only candidate may be unnecessary.

**Partially accepted.** H07 should remain runtime-bearing, but the model still needs broad behavioral competence when the explicit policy is absent or incomplete. V4 does not attempt to replace the runtime rule; it tests whether a better SFT mixture can raise the weights-only floor while preserving the stronger policy-bearing architecture.

> **HOSTILE REVIEWER:** Rebalancing after seeing V3 failures risks benchmark overfitting.

**Accepted as a real risk.** V3 identifies mechanism classes, not answers. V4 may increase training coverage of H07/H13/H05/H17/H19, but it may not copy, paraphrase, or tune directly against V3 final items. V4 receives an entirely new final qualification set after its training artifact is frozen.

> **HOSTILE REVIEWER:** Removing ORPO changes both data mixture and objective.

**Rejected as a confound in this design.** Candidate A intentionally asks whether SFT alone with a repaired mixture is sufficient. Prior V2/V3 evidence gives no reason to require ORPO as part of the baseline repair, and the V3 retention/adversarial margin regressions make a preference continuation a poor default. Preference learning remains a later isolated experiment.

## Claim ceiling

Before V4 training:

`V3_AUTOMATED_QUALIFICATION_FAILED / V3_FINAL_EVIDENCE_CONSUMED / V4_DESIGN_APPROVED / V4_NOT_TRAINED / NOT_QUALIFIED / NOT_QUANTIZED / NOT_DEPLOYED`
