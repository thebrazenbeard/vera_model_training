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
- Qwen-lane verification after the local optimizer correction is 24/24 passing; `py_compile` and `git diff --check` also pass; repository-wide pytest collection remains environment-blocked by missing unrelated bootcamp dependency `bs4` after resolving `torch`/`requests` from the qualification venv;
- not merged, published, installed, activated, or deployed.

Next frontier:
H07 architecture-discrimination V1 has completed the BASE and TRAINED weight-only conditions on the frozen 8-row development set. BASE scored 0.375 accuracy / -0.12643978 mean margin; corrected `adamw_torch` SFT 16 scored 0.375 / -0.16070238; corrected `adamw_torch` SFT 16 + ORPO 16 scored 0.375 / -0.16137591. Neither trained condition improved H07. `paged_adamw_8bit` is excluded from Lappy after Patrick's prior crash history and a coincident `nvlddmkm` event during the paged trial; no causal mechanism is claimed. The next work is BASE + runtime and TRAINED + runtime on the same frozen H07 dev set, not more epochs. Do not create the fresh final qualification holdout until the recipe is frozen.

Claim ceiling:
`V2_CUSTODY_VERIFIED / V2_BEHAVIORALLY_NOT_QUALIFIED_ON_DEV_CONTROL / V3_RECIPE_RESEARCH_IN_PROGRESS / 40_ROW_SET_DEVELOPMENT_ONLY / NO_V3_CANDIDATE_PROMOTED / NOT_DEPLOYED`
