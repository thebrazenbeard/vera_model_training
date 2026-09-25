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

## Current blocker

At preflight, Lappy reported about 3.2 GiB / 4 GiB VRAM already occupied. The principal compute process is:

`C:\ProgramData\ProRun\python\python.exe C:\ProgramData\ProRun\runtime\qwen_http.py`

started by:

`C:\ProgramData\ProRun\runtime\start-qwen.ps1`

The process was not stopped because runtime deactivation/cutover requires Patrick's explicit authority for that exact effect.

## Claim boundary

No H07 V1 training run has started yet. No candidate is promoted, qualified, deployed, installed, activated, or merged.
