# Qwen3.5 V2 Qualification Plan

Date: 2026-09-24
Target: `Vera-Qwen3.5-4B-Behavior-V1`

V2 qualification must not rely on training loss.

## Control holdout

Reuse the exact frozen 40-row V1 holdout:

`successor/qwen35/qualification/history_behavior_holdout_v1.jsonl`

Reason: this provides an apples-to-apples comparison against the already measured V1 result:
- base preference accuracy: 0.525
- V1 adapter preference accuracy: 0.525
- V1 accuracy delta: 0.000
- V1 mean-margin delta: -0.030639946460723877

The V2 training corpus must not consume this holdout.

## New holdout

Create a second holdout only after the V2 training corpus bytes are frozen.

Requirements:
- 5 novel rows per H01-H20 dimension = 100 rows;
- no prompt or answer from the 360 candidate pool, curated 240, V1 corpus, or V1 holdout;
- different concrete entities, domains, wording, and task structures from training rows;
- exact and near-duplicate rejection against all training prompts;
- private facts and project-specific names prohibited;
- chosen/rejected length fairness enforced;
- generated/curated with models not used as the final training subject;
- bytes and SHA-256 frozen before V2 adapter qualification.

## Measurements

Run the exact base and exact adapter on both holdouts.

Primary preference metrics:
- chosen-vs-rejected mean response-token log-probability accuracy;
- mean preference margin;
- per-dimension accuracy and margin;
- base-to-adapter deltas.

Generative checks:
- sample natural responses for each H dimension;
- independently judge target behavior without exposing the preferred answer;
- report regressions, not only wins.

Retention checks:
- compact ordinary-instruction suite across writing, summarization, reasoning, extraction, coding explanation, and factual response;
- compare base and adapter for obvious negative transfer.

## Pass interpretation

No single scalar creates an unconditional PASS.

At minimum, V2 must:
- materially exceed V1 on the frozen 40-row control holdout;
- show positive aggregate preference movement on the new 100-row holdout;
- avoid a concentrated collapse in any core H dimension;
- show no obvious catastrophic regression on the compact retention suite.

Source, adapter artifact, merge/export, GGUF conversion, runtime deployment, and behavioral qualification remain separate states.

Claim ceiling before these checks:
`TRAINING_CANDIDATE_ONLY / NOT_BEHAVIORALLY_QUALIFIED`
