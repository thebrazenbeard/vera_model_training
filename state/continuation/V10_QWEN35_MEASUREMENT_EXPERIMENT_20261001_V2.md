# V10 Qwen3.5 Measurement Experiment Continuation — 2026-10-01 V2

Restore command:

`VERA_MODEL_TRAINING::RESUME_V10_QWEN35_MEASUREMENT_EXPERIMENT::20261001_V2`

## Current durable subject

Repository: `thebrazenbeard/vera_model_training`

Branch: `work/v10-qwen35-measurement-experiment-20261001`

Observed branch head before this continuation commit: `333be10debea197041c3d56cef01c54ecacb9cf2`

Stacked Draft PR: #60, base `work/v4.1-diverse-core-20260930`

Parent V10 subject remains:
`work/v4.1-diverse-core-20260930@af27db57edf41a06601a2ed2e25d3757f9037ba3`

PR #59 was not modified by this lane.

## Work completed after V1

Persisted:
- `successor/experiments/V10_QWEN35_EXCLUSION_REGISTRY_V1.json`
- `successor/experiments/V10_QWEN35_FINAL_BANK_ADMISSION_V1.json`
- `tests/test_v10_qwen35_experiment_preflight.py`
- fail-closed V10 preflight support in `successor/evaluate_successor.py`

The exclusion registry freezes V10 train/validation identities plus exact historical consumed-suite digests available from the Qwen measurement lineage. It explicitly does not claim that prompt fingerprints or semantic-contamination screening have already been materialized.

The admission policy freezes the intended 13,500-case weight-only composition and case/reviewer/grader/provenance requirements while admitting zero cases.

## TDD evidence

Focused red was observed before implementation:

`python -m pytest -q tests/test_v10_qwen35_experiment_preflight.py`

Result before production change:
`2 failed`

Both failures were the expected missing behavior: `evaluate_successor.py` accepted the new CLI arguments as inert argv and exited 0 with no preflight output.

After the minimum read-only implementation:

`python -m pytest -q tests/test_v10_qwen35_experiment_preflight.py`

Result:
`2 passed`

Regression check with the existing evaluator-freeze suite:

`python -m pytest -q tests/test_successor_eval_freeze.py tests/test_v10_qwen35_experiment_preflight.py`

Result:
`8 passed`

These were local exact-content tests, not GitHub Actions. The stacked PR does not currently receive the repository's normal `main`-targeted pull-request CI automatically.

## Remote readback

After the implementation commit:
- branch head: `333be10debea197041c3d56cef01c54ecacb9cf2`
- `successor/evaluate_successor.py` blob: `d669472224681f2d3c96a127827dca089605b90a`
- preflight test blob: `8d93e30aba158b942adcf45ad8facff87be957a3`
- Draft PR #60: open, draft, mergeable, stacked on the V10 branch.

Direct readback of the current contract state implies preflight HOLD for:
- `fresh_evaluation_bank_frozen`
- `independent_bank_admission_verified`
- `contamination_screen_against_v10_and_consumed_finals_verified`
- `qwen_token_budget_no_overflow_verified`
- `zero_cost_execution_target_bound`
- `exact_training_runtime_versions_bound`
- `patrick_exact_weight_change_authority`
- `final_bank_cases_not_admitted`

No weights or external runtime state were changed.

## Executable boundary

The current CLI is read-only:

`python successor/evaluate_successor.py --v10-preflight-root <repo-root>`

Current expected exit: `2`

Current expected status: `HOLD`

A true final-bank flag without actual 64-hex behavioral/adversarial/retention bank hashes also remains HOLD with `fresh_evaluation_bank_hashes_missing`.

This preflight does not train, mutate weights, install, activate, deploy, or change providers.

## Next bounded frontier

Materialize the prompt-fingerprint exclusion set and final-bank intake tooling without generating filler cases. The intake path should fail closed on duplicate/overlapping/under-provenanced cases and preserve the unresolved independent-review requirement.

Only after that should the exact Qwen tokenizer be applied to the V10 train/validation mixture for the 512-token no-truncation preflight.

## Claim ceiling

`V10_CORPUS_AND_MIXTURE_QUALIFIED / QWEN35_EXPERIMENT_PREREGISTERED / EXCLUSION_AND_ADMISSION_POLICY_FROZEN / READ_ONLY_PREFLIGHT_VERIFIED_LOCALLY / FINAL_BANK_NOT_ADMITTED / TRAINING_NOT_AUTHORIZED / WEIGHTS_UNCHANGED / NOT_DEPLOYED`
