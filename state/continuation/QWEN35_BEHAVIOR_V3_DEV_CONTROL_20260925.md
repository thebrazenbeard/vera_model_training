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
- Qwen-lane verification after the runtime-policy seam is 26/26 passing; `py_compile` and `git diff --check` also pass; repository-wide pytest collection remains environment-blocked by missing unrelated bootcamp dependency `bs4` after resolving `torch`/`requests` from the qualification venv;
- not merged, published, installed, activated, or deployed.

Next frontier:
Do not spend another H07 V1 training cycle. Finish the exact frozen BASE + runtime and TRAINED + runtime comparison using the versioned H07 policy, but treat paragraph log-prob margin as a diagnostic rather than the sole behavioral criterion. H07 V2 should use explicit-rule SFT, a staged family-held-out design (initial target: 96 training cases across 12 mechanism families and 32 development cases across 4 held-out families), free-generation semantic-rubric scoring as the primary metric, short-form decision scoring as secondary, and preference margin only as a diagnostic. Only after broader SFT shows transfer should preference objectives or PEFT variants be reconsidered. Benchmark the clean parent Qwen3.5-4B against the aggressive checkpoint before attributing a capability ceiling to the base architecture. Do not create a fresh final qualification holdout until the V3 recipe and evaluator are frozen.

Claim ceiling:
`V2_CUSTODY_VERIFIED / V2_BEHAVIORALLY_NOT_QUALIFIED_ON_DEV_CONTROL / V3_RECIPE_RESEARCH_IN_PROGRESS / 40_ROW_SET_DEVELOPMENT_ONLY / NO_V3_CANDIDATE_PROMOTED / NOT_DEPLOYED`
