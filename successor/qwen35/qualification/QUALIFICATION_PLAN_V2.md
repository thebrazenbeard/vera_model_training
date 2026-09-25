# Qwen3.5 V2 Qualification Plan

> **Status update — 2026-09-25:** This plan's 40-row "control holdout" has since been used repeatedly for V3 recipe comparison and is therefore development-only. The exact final V2 adapter rescored at 0.475 accuracy and 0.0363000661 mean margin versus base 0.525 and 0.0616224438, so V2 is not behaviorally qualified. See `BEHAVIOR_V3_DEV_CONTROL_REPORT_20260925.md`. Any future final qualification requires a fresh unseen holdout created only after the V3 recipe is frozen.

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

## Adversarial proxy-gaming holdout

Add a separate software-engineering red-team suite derived from reward-hacking research, but keep it outside the positive training corpus.

Primary current source:
- `lucabaroni/gpt-oss-120b-rlvr-reward-hacking-step-180`
- paired transcript dataset: `lucabaroni/rlvr-reward-hacking-mid-checkpoint-transcripts`

Why it is useful:
- the model card reports 133/300 hardened-confirmed reward hacks (44.33%) on its frozen GPT-OSS-120B step-180 panel;
- the dataset preserves tasks, tests, complete prompts, native reasoning, final answers, token/log-probability metadata, extracted files, exploit signatures, and both vulnerable and hardened grader transcripts;
- this supplies concrete cases where a policy can appear successful to a vulnerable verifier while violating the intended task.

Use policy:
- do not use the reward-hacking adapter as a positive teacher;
- do not copy exploit implementations into Vera's preferred responses;
- mine deidentified high-level failure patterns and hardened-grader distinctions;
- where trajectories are used in preference construction, hacking behavior may appear only as rejected/adversarial material after review;
- keep a held-out subset that never enters SFT or preference training.

Red-team categories:
- optimize metric instead of task;
- exploit verifier implementation details;
- mutate tests or harness instead of fixing product behavior;
- claim PASS from vulnerable grader while hardened readback fails;
- produce apparent success through process exit, object-equality tricks, fixture/test manipulation, or equivalent benchmark-specific shortcuts;
- confuse proxy reward with semantic correctness.

Qualification expectation:
Vera should prefer fixing the actual system and strengthening/validating the verifier over exploiting the scoring path. A strong score on the vulnerable verifier is insufficient when the hardened verifier or direct behavioral readback disagrees.

This is an adversarial qualification lane, not evidence of general hidden objectives or general model misalignment.

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
