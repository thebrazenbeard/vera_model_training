# Qwen3.5 Behavior V3 Continuation — 2026-09-25

Restore:
`QWEN35::RESTORE_AND_RUN::BEHAVIOR_V3_DEV_CONTROL_20260925`

Primary evidence:
`successor/qwen35/qualification/BEHAVIOR_V3_DEV_CONTROL_REPORT_20260925.md`

Branch:
`work/qwen35-history-behavior-training-20260923`

Current state:
- exact V2 custody remains verified;
- exact V2 adapter rescored at 47.5% vs 52.5% base on the historical 40-row set;
- V2 is not behaviorally qualified;
- the 40-row set is now development-only because it has been reused for V3 recipe selection;
- V3 bounded local experiment harness and clean H03/H07/H11/H15 repair corpus exist;
- SFT/ORPO improve seen H07 preference margins but do not generalize to the novel H07 development pairs;
- no V3 experiment improved development-control accuracy;
- no V3 candidate is promoted;
- local Lappy training now has an explicit `lappy-rtx3050-4gb` profile with a 512-token fail-closed corpus budget, documented in `successor/qwen35/LOCAL_TRAINING_PROFILE_V1.md`;
- exact-tokenizer preflight confirms the clean V3 repair corpus fits at 78 tokens max, while the legacy V2 corpus has 118 SFT and 115 preference rows above the local 512-token budget and remains reproducible only through the historical 1024-token generic profile;
- H07 improvement research is recorded in `successor/qwen35/qualification/H07_IMPROVEMENT_RESEARCH_20260925.md`; research favors explicit-rule transfer, broader mechanism-family diversity, and better semantic evaluation before more H07 epochs or loss swapping;
- `evaluate_behavior_v2.py` now supports a provenance-bound `--runtime-policy-path`; `h07_effect_verification_policy_v2.txt` fits the local 512-token contract on all frozen V1 cases (368 tokens max including response candidate);
- qualitative free-generation probing shows materially better practical H07 behavior than the original paragraph-likelihood score suggests, while a forced three-way action-class probe remains format-sensitive (BASE 3/8, BASE+policy 5/8); treat evaluation-format sensitivity as an open issue rather than as qualification;
- H07 rule-transfer V2 is now built and frozen: 96 SFT rows across 12 train mechanism families, 32 development rows across 4 fully held-out mechanism families, semantic proposition rubrics, train max 371 tokens / dev max 131 tokens under the 512-token Lappy budget;
- V2 pre-training internal semantic review on the frozen 32-row development set is BASE 12/32 (0.375) and BASE + runtime policy 19/32 (0.59375); this is `INTERNAL_HOST_MODEL_REVIEW`, not independent qualification;
- H07 V2 rank-4 all-linear SFT completed locally for 96/96 steps with `adamw_torch`, no ORPO/preference rows, SFT loss 2.157097419102987, adapter-model SHA-256 `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`, and no observed NVIDIA Display/nvlddmkm event during the run;
- the first post-training PEFT load through the qualification venv hit Windows `os error 1455` under host commit pressure; no pagefile setting was changed and Firefox was not killed or mutated; the same adapter was then evaluated successfully through the proven ProRun model environment;
- H07 V2 four-way internal semantic development result on the same frozen 32 rows / 48-token greedy budget is BASE `12/32 (0.375)`, TRAINED `13/32 (0.40625)`, BASE + runtime policy `19/32 (0.59375)`, TRAINED + runtime policy `24/32 (0.75)`;
- TRAINED alone is +1 case over BASE, runtime policy alone is +7, and the combined condition is +12 over BASE / +5 over BASE + runtime; treat this as development evidence of complementarity, not independent qualification or proof of causal synergy;
- H07 V2 status/evidence is documented in `successor/qwen35/qualification/H07_RULE_TRANSFER_V2_REPORT_20260925.md`, `h07_rule_transfer_v2_four_way_comparison.json`, and `h07_rule_transfer_v2_sft_r4_training_receipt.json`;
- Qwen-lane + semantic-evaluator verification after the V2 build is 33/33 passing; `py_compile` and `git diff --check` also pass; repository-wide pytest collection remains environment-blocked by missing unrelated bootcamp dependency `bs4` after resolving `torch`/`requests` from the qualification venv;
- ProRun Qwen was restored after the training/evaluation window and `/v1/models` returned `qwen3.5-4b-local`;
- not merged, published, installed, activated, or deployed.

Next frontier:
Do not increase H07 epochs, add ORPO, or raise LoRA rank yet. Freeze the V2 evaluator and rule-transfer recipe, retain the V2 adapter only as a development candidate, and keep the H07 effect-verification rule explicit in runtime. Obtain independent semantic review or a fresh final holdout before promotion. Only if the combined result reproduces should clean-parent Qwen3.5-4B substrate or LoRA-capacity ablations become the next priority. The clean parent checkpoint is not presently cached on Lappy. Do not create a fresh final qualification holdout until the V3 recipe and evaluator are frozen.

Claim ceiling:
`V2_CUSTODY_VERIFIED / V2_BEHAVIORALLY_NOT_QUALIFIED_ON_DEV_CONTROL / V3_RECIPE_RESEARCH_IN_PROGRESS / 40_ROW_SET_DEVELOPMENT_ONLY / NO_V3_CANDIDATE_PROMOTED / NOT_DEPLOYED`
