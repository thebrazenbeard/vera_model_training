# H07 Architecture Discrimination V1

## Purpose

Test whether effect/readback verification is best supplied by model weights, explicit runtime machinery, or both.

This is a development experiment, not a qualification holdout.

## Frozen split

Training:
- 16 SFT rows
- 16 matching preference rows
- all dimension H07
- 16 distinct mechanism labels

Development:
- 8 preference rows
- disjoint from training prompts
- disjoint from the historical 40-row development control

Verification classes represented in training:
- readback_required
- receipt_sufficient
- ambiguous_effect

The corpus intentionally does not teach "always read back." It distinguishes request acceptance, attempted mutation, committed effect, authoritative post-state evidence, and ambiguous outcomes.

## Local hardware fit

Under the exact Qwen base tokenizer and the `lappy-rtx3050-4gb` 512-token profile:

- train SFT maximum: 98 tokens
- train preference maximum: 98 tokens
- development preference maximum: 92 tokens
- over-budget rows: 0

## Files

- `successor/qwen35/corpus/h07_architecture_discrimination_v1_train_sft.jsonl`
- `successor/qwen35/corpus/h07_architecture_discrimination_v1_train_preference.jsonl`
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_dev.jsonl`

The evaluator now accepts a local holdout with `--holdout-path`, so this experiment does not require a hosted holdout.

## Planned comparison

Evaluate the same development set under:

1. BASE
2. BASE + runtime verification mechanism
3. TRAINED
4. TRAINED + runtime verification mechanism

Then ablate adapter and runtime mechanism separately.

## Executed local comparison

Patrick explicitly authorized stopping the ProRun `qwen_http.py` runtime for the training window and restarting it afterward. The ProRun daemon itself was left running.

Frozen development-set results:

| Condition | Accuracy | Mean margin | Delta accuracy vs base | Delta mean margin vs base |
| --- | ---: | ---: | ---: | ---: |
| BASE | 0.375 | -0.12643978 | — | — |
| TRAINED — SFT 16, `adamw_torch` | 0.375 | -0.16070238 | 0.000 | -0.03426260 |
| TRAINED — SFT 16 + ORPO 16, `adamw_torch` | 0.375 | -0.16137591 | 0.000 | -0.03493613 |

Neither corrected non-paged training condition improved accuracy or mean margin. The SFT+ORPO continuation was slightly worse than SFT alone on mean margin.

The earlier paged-optimizer path is superseded for local use. During that path Windows recorded `nvlddmkm` event 153 at 2026-09-25 15:02:33 local time, matching Patrick's prior warning that the paged optimizer path is crash-prone. This is operational exclusion evidence, not a causal proof of the driver event. A Windows System-log query from 15:20 onward found no additional `nvlddmkm`/Display-provider events during the completed `adamw_torch` smoke, SFT, SFT+ORPO, and evaluation runs.

Structured evidence:
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_results.json`
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_sft_adamw_training_receipt.json`
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_sft_orpo_adamw_training_receipt.json`

## Interpretation

H07 remains a poor candidate for acquisition by this narrow 16-example weight update. The current evidence favors testing the explicit runtime verification mechanism rather than adding epochs, increasing learning rate, or expanding preference steps on the same narrow corpus.

The architecture-discrimination experiment is not complete until BASE + runtime and TRAINED + runtime are measured on the same frozen development set.

## Claim boundary

No H07 V1 adapter is promoted or behaviorally qualified. No deployment, installation, activation, merge, or final-holdout claim follows from these development results.
