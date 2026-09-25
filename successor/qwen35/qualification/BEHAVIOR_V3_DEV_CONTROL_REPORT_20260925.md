# Qwen3.5 Behavior V3 Development-Control Report — 2026-09-25

## Subject and claim boundary

Repository branch:
`work/qwen35-history-behavior-training-20260923`

Base:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

V2 custody artifact:
- output identity: `Vera-Qwen3.5-4B-Behavior-V1`
- archive SHA-256: `1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69`
- rescored adapter-model SHA-256: `0b52564975086b5608021e2665c3e94e447826a115d194c56b51f2e9aec6f803`

This report records local behavioral-development evidence. It does not authorize or establish merge, publication, GGUF conversion, installation, activation, deployment, or runtime selection.

## 40-row control status

Historical file:
`successor/qwen35/qualification/history_behavior_holdout_v1.jsonl`

SHA-256:
`93bbe6605f9b80e71aa6badebab3aaf13125cc5c00305b91f8811961f5edbb8c`

The 40-row set has now been used repeatedly to compare and select V3 recipes. It is therefore reclassified as a **development control**. It must not be represented as an unseen final holdout for any future qualification claim.

Base score on this development control:
- preference accuracy: `0.525`
- mean preference margin: `0.061622443795204165`

## Exact V2 result

The exact reconstructed V2 adapter was rescored locally against the 40-row development control.

Result:
- V2 preference accuracy: `0.475`
- accuracy delta vs base: `-0.050000000000000044`
- V2 mean preference margin: `0.03630006611347199`
- mean-margin delta vs base: `-0.025322377681732178`

Therefore V2 does not satisfy the existing minimum qualification criterion requiring material improvement over the base/V1 control. V2 is **not behaviorally qualified**.

The strongest zero-accuracy development dimensions remained:
- H03: `-0.6401588320732117`
- H07: `-1.12498140335083`
- H11: `-0.5450243949890137`
- H15: `-1.8879773616790771`

## V3 experiment harness

`successor/qwen35/train_behavior_v3.py` adds bounded recipe experiments while preserving the frozen full-training count guard.

Relevant behavior:
- completion-only SFT;
- all-linear QLoRA coverage verification;
- optional ORPO continuation from the SFT model;
- bounded `--experiment-steps`;
- balanced targeted sampling;
- experimental corpora may be smaller than 760/648 only when an explicit experiment step count is supplied;
- full training still requires the frozen 760 SFT / 648 preference counts.

The evaluator supports:
- local adapter directories;
- verified local chunk reconstruction;
- bounded GPU/CPU placement for laptop qualification;
- adapter-model SHA-256 reporting.

## V2 targeted-corpus audit

The failing dimensions were inspected before increasing training steps.

Observed defects:
- **H03:** multiple targeted rows correctly imply retrieval-first behavior but then invent retrieved filenames, values, or contents.
- **H07:** several rows assert effective state without an actual readback; at least one row is unrelated to effect verification.
- **H11:** many rows do not teach ambiguity handling; one selected response chooses a live-database mutation instead of clarifying a consequential ambiguity.
- **H15:** only six targeted rows were present, and most do not teach metaphor/analogy handling.

This establishes a data-quality problem, but later experiments show it is not the only problem.

## Clean repair corpus

Added:
- `successor/qwen35/corpus/history_behavior_targeted_v3_repair_sft.jsonl`
- `successor/qwen35/corpus/history_behavior_targeted_v3_repair_preference.jsonl`

Properties:
- 16 SFT + 16 preference rows;
- four rows each for H03, H07, H11, H15;
- generic/deidentified contexts;
- no exact prompt overlap with the 40-row development control.

## Development experiments

All accuracy values below are on the 40-row development control unless stated otherwise.

| Candidate | Accuracy | Mean margin | Delta vs base |
| --- | ---: | ---: | ---: |
| Base | 0.525 | 0.06162244 | — |
| V2 final adapter | 0.475 | 0.03630007 | -0.02532238 |
| V3 balanced V2 SFT-only, 8 steps | 0.525 | ~0.0616769 | +0.0000545 |
| V3 balanced V2 SFT+ORPO, 8+8 | 0.525 | 0.06381444 | +0.00219199 |
| V3 clean repair SFT-only, 8 steps | 0.525 | 0.06257420 | +0.00095176 |
| V3 clean repair SFT+ORPO, 8+8 | 0.525 | 0.05917209 | -0.00245035 |
| H07-only clean SFT, 8 steps | 0.525 | 0.06430033 | +0.00267788 |
| H07-only clean SFT+ORPO, 8+8 | 0.525 | 0.06154400 | -0.00007845 |

No experiment improved development-control accuracy.

## H07 objective/generalization falsification

Four clean H07 examples were isolated to remove cross-dimension interference.

On those **seen training pairs**:
- base mean margin: `-0.24788808822631836`
- H07 SFT-only mean margin: `-0.20661532878875732`
- SFT-only delta: `+0.041272759437561035`
- H07 SFT+ORPO mean margin: `-0.1978902816772461`
- SFT+ORPO delta: `+0.049997806549072266`

On the **novel H07 development-control pairs**:
- base H07 mean margin: `-0.9849278926849365`
- H07 SFT-only: `-1.0085742473602295`
- H07 SFT+ORPO: `-0.9883644580841064`

Interpretation:
- the SFT and ORPO objectives are not inverted;
- ORPO correctly continues from `sft.model`;
- the adapter learns the contrasts it sees;
- the current narrow H07 repair set does not generalize to novel formulations;
- increasing steps alone is not justified by current evidence.

## Local hardware adaptation

Local V3 experiments are now governed by `successor/qwen35/LOCAL_TRAINING_PROFILE_V1.md`.

Observed Lappy hardware is an NVIDIA GeForce RTX 3050 Laptop GPU with 4096 MiB VRAM and about 31.7 GiB system RAM. The new `lappy-rtx3050-4gb` profile sets a conservative 512-token formatted-sequence budget and fails closed on oversized SFT or preference rows before model allocation instead of relying on trainer-side truncation.

Exact-tokenizer preflight evidence:
- V3 repair SFT: 16 rows, maximum 78 tokens, 0 over budget;
- V3 repair preference: 16 rows, maximum 78 tokens, 0 over budget;
- legacy V2 SFT at 512: 118 / 760 rows over budget;
- legacy V2 preference at 512: 115 / 648 rows over budget;
- legacy V2 remains intact under the historical generic 1024-token profile, with maxima 1007 and 1021 tokens respectively.

The 512-token value is an experiment-authoring budget, not a claim about the GPU's absolute maximum. New V3 corpus work should gain semantic breadth by adding independent examples rather than lengthening individual examples. Behaviors that genuinely require longer context should be tested as a separate hardware/architecture question instead of being silently truncated.

## Next frontier

Do not spend another training cycle merely by increasing epochs or learning rate.

The next bounded work should be:
1. expand H03/H07/H11/H15 repair data with semantic breadth, especially H07;
2. represent multiple mechanisms per dimension rather than lexical paraphrases of one pattern;
3. create a train/development split before training and keep the existing 40-row set development-only;
4. pre-score new training contrasts and inspect whether chosen/rejected pairs actually express the intended proposition;
5. freeze the V3 recipe before creating a new, unseen final qualification holdout;
6. require a fresh final holdout for any behavioral-qualification claim.

## Verification status

Fresh Qwen-lane verification after the local-hardware profile change:
`py -m pytest tests/test_qwen35_behavior_v3_recipe.py tests/test_qwen35_local_qualification.py tests/test_qwen35_behavior_v2_contract.py -q`

Result:
`22 passed`

`py -m py_compile successor/qwen35/train_behavior_v3.py` and `git diff --check` also pass.

Repository-wide `pytest -q` is not currently a clean verification path in the host environment:
- default Python stops collection because `requests` and `torch` are absent;
- exposing the existing Qwen qualification venv site-packages resolves those, but collection still stops because `bs4` is absent in unrelated bootcamp tests;
- no dependency was installed merely to manufacture a green full-suite result.

## Current claim ceiling

`V2_CUSTODY_VERIFIED / V2_BEHAVIORALLY_NOT_QUALIFIED_ON_DEV_CONTROL / V3_RECIPE_RESEARCH_IN_PROGRESS / 40_ROW_SET_DEVELOPMENT_ONLY / NO_V3_CANDIDATE_PROMOTED / NOT_DEPLOYED`
