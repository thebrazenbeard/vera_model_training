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

The Lappy profile now uses `adamw_torch` and excludes `paged_adamw_8bit`. Patrick's prior training record had already made that replacement because the paged path was crash-prone. During the H07 V1 paged trial Windows also recorded `nvlddmkm` event 153 at 2026-09-25 15:02:33 local time. Timing alone is not treated as causal proof; it is sufficient operational evidence not to use the paged optimizer on Lappy. Subsequent `adamw_torch` smoke, SFT, and SFT+ORPO runs completed without a new NVIDIA display-driver event.

## H07 architecture-discrimination V1

Frozen split:
- 16 SFT training rows;
- 16 matching preference training rows;
- 8 disjoint development rows;
- 16 distinct training mechanism labels;
- verification classes include readback-required, receipt-sufficient, and ambiguous-effect cases;
- exact-tokenizer maximum is 98 train / 92 development tokens under the 512-token Lappy profile.

Development results:
- BASE: accuracy `0.375`, mean margin `-0.12643977999687195`;
- `adamw_torch` SFT 16: accuracy `0.375`, mean margin `-0.16070237755775452`, delta margin `-0.03426259756088257`;
- `adamw_torch` SFT 16 + ORPO 16: accuracy `0.375`, mean margin `-0.16137591004371643`, delta margin `-0.03493613004684448`.

Neither corrected training condition improved H07 development accuracy or margin. No H07 adapter is promoted.

Structured evidence:
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_results.json`
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_base_result.json`
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_sft_adamw_training_receipt.json`
- `successor/qwen35/qualification/h07_architecture_discrimination_v1_sft_orpo_adamw_training_receipt.json`

## H07 improvement research

Follow-up research is recorded in `successor/qwen35/qualification/H07_IMPROVEMENT_RESEARCH_20260925.md`.

Main consequences:
- explicit rule representations and task/mechanism diversity are stronger next levers than more epochs on the 16-example H07 set;
- ORPO has not earned another H07 pass; broader SFT should demonstrate transfer before another preference objective is selected;
- current all-linear targeting is defensible, but rank 4 may be a PEFT-capacity/generalization constraint; higher-rank tests are deferred because Lappy has essentially no VRAM headroom at the current peak;
- the aggressive/uncensored checkpoint is a downstream modified subject, so a clean-parent Qwen3.5-4B comparison should precede any claim that Qwen3.5 itself lacks the capability;
- evaluation format is a material confound: concise free generation looked substantially stronger than the original paragraph-likelihood metric, while a forced three-way action probe scored BASE 3/8 and BASE+policy 5/8.

The evaluator now supports `--runtime-policy-path`; the versioned policy is `successor/qwen35/qualification/h07_effect_verification_policy_v2.txt`. Exact-tokenizer preflight puts the largest frozen policy+case+candidate sequence at 368 tokens, below the 512-token Lappy budget.

## H07 rule-transfer V2

Frozen design:
- 96 SFT training rows across 12 mechanism families;
- 32 development rows across 4 fully held-out families;
- semantic proposition rubrics rather than lexical matching;
- training maximum 371 tokens / development maximum 131 tokens under the 512-token Lappy profile;
- no preference rows and no ORPO in the initial V2 training condition.

Pre-training internal semantic development review:
- BASE: `12/32 = 0.375`;
- BASE + H07 runtime policy: `19/32 = 0.59375`.

These are `INTERNAL_HOST_MODEL_REVIEW` measurements, not independent qualification.

The V2 rank-4 all-linear SFT run completed locally for all 96 steps with `adamw_torch`. Training loss was `2.157097419102987`. Adapter-model SHA-256 is `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`; adapter-archive SHA-256 is `efacb77ad104f6c3369dd25832906c96780483079957b012202decb843c555d8`. No NVIDIA Display/nvlddmkm event was observed during the completed run.

The first direct PEFT evaluation load through the qualification venv failed with Windows `os error 1455` under host commit pressure. No pagefile setting was changed. Evaluation was then rerun through the already-proven ProRun model environment, which loaded the identical base checkpoint and adapter without changing Firefox or the pagefile.

Four-way internal semantic development result on the same frozen 32 rows and 48-token greedy budget:
- BASE: `12/32 = 0.375`;
- TRAINED: `13/32 = 0.40625`;
- BASE + runtime policy: `19/32 = 0.59375`;
- TRAINED + runtime policy: `24/32 = 0.75`.

TRAINED alone is only +1 case over BASE. Runtime policy alone is +7. The combined condition is +12 over BASE and +5 over BASE + runtime policy. This is development evidence of complementarity, not independent qualification or proof of causal synergy.

Primary V2 report:
`successor/qwen35/qualification/H07_RULE_TRANSFER_V2_REPORT_20260925.md`

Structured four-way comparison:
`successor/qwen35/qualification/h07_rule_transfer_v2_four_way_comparison.json`

Training receipt:
`successor/qwen35/qualification/h07_rule_transfer_v2_sft_r4_training_receipt.json`

## Next frontier

Do not increase H07 epochs, add ORPO, or raise LoRA rank yet. The strongest surviving design is hybrid: retain the V2 adapter as a development candidate while keeping the H07 verification rule explicit in runtime. Freeze the V2 evaluator/recipe and obtain independent semantic review or a fresh final holdout before promotion. Only if the combined result reproduces should clean-parent substrate or LoRA-capacity ablations become the next priority. Keep the historical 40-row set development-only.

## Verification status

Fresh Qwen-lane and H07 semantic-evaluator verification after the V2 build:
`py -m pytest tests/test_qwen35_behavior_v3_recipe.py tests/test_qwen35_local_qualification.py tests/test_qwen35_behavior_v2_contract.py tests/test_h07_semantic_eval_v2.py -q`

Result:
`33 passed`

`py -m py_compile successor/qwen35/train_behavior_v3.py successor/qwen35/qualification/evaluate_behavior_v2.py successor/qwen35/qualification/evaluate_h07_rule_transfer_v2.py successor/qwen35/corpus/build_h07_rule_transfer_v2.py` and `git diff --check` also pass.

Repository-wide `pytest -q` is not currently a clean verification path in the host environment:
- default Python stops collection because `requests` and `torch` are absent;
- exposing the existing Qwen qualification venv site-packages resolves those, but collection still stops because `bs4` is absent in unrelated bootcamp tests;
- no dependency was installed merely to manufacture a green full-suite result.

## Current claim ceiling

`V2_CUSTODY_VERIFIED / V2_BEHAVIORALLY_NOT_QUALIFIED_ON_DEV_CONTROL / V3_RECIPE_RESEARCH_IN_PROGRESS / 40_ROW_SET_DEVELOPMENT_ONLY / NO_V3_CANDIDATE_PROMOTED / NOT_DEPLOYED`
