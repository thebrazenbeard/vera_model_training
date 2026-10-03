# VERA Model Training — Continuation Checkpoint

Checkpoint date: 2026-10-01
Purpose: resume the 10,000-row corpus measurement/research lane without relying on prior chat transcript.

Repository: `thebrazenbeard/vera_model_training`
Branch: `work/v4.1-diverse-core-20260930`
Draft PR: #59
Parent head at checkpoint creation: `4b507008b54775419f0cf74994a7f67ee2c4c1c4`

## Current corpus

Corpus ID: `VERA_SUCCESSOR_V4_1_10K_DIVERSE_CORE_20260930_V10`

- 10,000 custom rows.
- 10 behavioral families, 1,000 each.
- 20 domains.
- 100 grounded scenario cases per family.
- 5 cognitive levels.
- 10 request modes.
- 8 surface prefixes.
- 12 response frames.
- 5 scenario-resolution forms per family.
- 5 family bridges per family.
- 5 cognitive-response forms.
- deterministic/model-free generation.
- 10,000 unique prompts, responses, and prompt/response pairs.

Manifest digest:
`fd55b8356f5639c8b47a726066122576e7c99078e26fcad6be79d3a11e5251b1`

## Current training mixture

Training corpus ID: `VERA_SUCCESSOR_V4_1_50K_20260930_V10`

- 52,500 source rows.
- 50,000 train.
- 2,500 validation.
- zero train/validation overlap.
- 81% general-competence fraction.
- custom source exactly bound to the V10 corpus manifest.
- training authorization: `NOT_GRANTED`.
- weight change performed: `false`.

Train SHA-256:
`04fbb3a2012ef3fd0506ad1188cc9f3b8d850161301fb9e0d00edd7f8ec78e90`

Validation SHA-256:
`26e3387852283d399cea3df0758c3abf877d2884d298860668de7e5fe0b3bd93`

Training-manifest SHA-256:
`5b1f4640bae39dfe4eeb3ce54d85a693343c0432d5dc3707ebf647b3aa9780ba`

## Semantic gate

Evaluator: `sentence-transformers/all-MiniLM-L6-v2`
Deterministic comparison sample: 600 rows, same sampling scheme for V4 and V10.

Raw:
- alignment margin: 0.355138 vs V4 0.088641.
- own prompt beats shuffled prompt: 100%.
- mean nearest-neighbor cosine: 0.823760 vs 0.859622.
- mean pairwise cosine: 0.393245 vs 0.396080.
- >=0.90 similarity-pair fraction: 0.000122 vs 0.000440.

Scenario-stripped:
- alignment margin: 0.230661 vs V4 0.088641.
- own prompt beats shuffled prompt: 94.33%.
- every family improved scenario-stripped alignment margin.
- every family stayed above the allowed regression floor.

All nine semantic gate checks passed.

The latest persisted semantic receipt has `training_lineage_verified: true` and binds the V10 custom manifest to the V10 training mixture.

## Engineering corrections

1. Earlier V2–V5 corpus revisions were rejected after deterministic behavioral review exposed malformed grammar, generic/unrelated scenarios, and negative-transfer contamination.
2. V6/V7 added scenario-stripped alignment measurement after hostile review showed raw embedding similarity could be inflated by scenario copying.
3. V8 added explicit scenario resolution; V9 separated response-variation selectors after duplicate-response failure.
4. V10 added explicit cognitive-operation grounding. This remains a hypothesis about supervision value, not proof of better learning.
5. The V4.1 training workflow previously failed because pytest was not installed before `tests/test_v4_1_training_contract.py`. The workflow was fixed and the rerun succeeded.
6. The semantic gate previously could not verify training lineage when the candidate corpus was generated into /tmp. It now accepts an explicit committed training-manifest path, and the semantic workflow runs when that manifest changes.
7. The semantic gate and training mixture are still qualification artifacts; neither proves model-training benefit.

## Next work

Continue the measurement/research lane before weight-changing work.

The next substantive experiment should:
- bind an exact base-model revision and exact training recipe;
- use a fresh SFT/QLoRA adapter rather than the failed V4 adapter lineage;
- freeze behavioral, retention/general-competence, and adversarial evaluation suites before training;
- define effect-size and regression criteria before looking at candidate results;
- preserve exact base revision, corpus hashes, training config, adapter hash, and evaluation receipts;
- keep native Vera qualification separate from proxy/local-model results.

No merge, deployment, activation, credential change, paid compute, or model-weight mutation is authorized by this checkpoint.

## Continuation command

`VERA_MODEL_TRAINING::RESUME_10K_MEASUREMENT_RESEARCH::V10_QUALIFIED_20261001_V1`

On resume, fresh-read the repository branch and this checkpoint, verify the exact current head, then continue from the current measurement/experiment boundary rather than reconstructing obsolete V2–V9 state.
