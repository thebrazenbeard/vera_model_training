# Qwen3.5 Measurement + Development Loop V1 — Live Handoff

**Checkpoint:** TASK_6_CPU_REAL_SMOKE_PASS_AND_FURTHER_SELECTION_AUDIT_PENDING. This file must be updated after each independently verified commit.
**Repository:** `thebrazenbeard/vera_model_training`
**Branch:** `work/qwen35-measurement-devloop-v1-20260930`
**Branch parent:** `d0acf17b66057cf452226674218ee17b0714fb38`
**Local workspace:** `D:\VERA\.worktrees\qwen35-measurement-devloop-v1-20260930`
**Canonical main is not changed.**
**Contract plan:** `docs/superpowers/plans/2026-09-30-qwen35-measurement-devloop-v1.md`

## Preserved evidence

V4 failed its frozen 100 behavioral, 20 retention, 20 adversarial proxy final. Full result local at `D:\VERA\.worktrees\qwen35-v4-repair-20260929-lf\results\final_qualification_v4_automated.json`. Failed receipt versioned in `successor/qwen35/qualification/FINAL_QUALIFICATION_V4_AUTOMATED_FAILURE_RECEIPT.json`. V3 and V4 final cases **consumed**, never development or replacement final data. V4 weights unqualified/not deployed.

## Boundaries

No model training or deployment authorized by this measurement build. No final benchmark results asserted without independently reviewed 10,000 distinct cases. Existing BV V4 corpus PR #44 separate; do not modify it. No protected effects.

## State at this checkpoint

- [x] Fresh-read exact branch heads / repo contracts and PR #44.
- [x] New isolated worktree created from V4 failed-gate commit, LF checkout.
- [x] Task 1 plan/handoff committed/pushed at ff487ed177f42ef0a04edb42b99a84062c118239.
- [x] Task 2 case schema/intake, family-disjoint dev split, 10k floor, 10 tests. Synthetic fixtures prove only structure; NOT an admitted bank.
- [x] Task 3 direct generated-text grading and paired observation binding. Objective grader, manual/effect fail-closed. 8 focused tests.
- [x] Task 4 exact paired discordance/McNemar, independent-family bootstrap with effective-group warnings, 20-dimension coverage, count-reconciliation and conservative gate. 13 focused tests.
- [x] Task 5 group split persistence, immutable hash-chained validation ledger, 3-check budget, paired generated-response scorer, CLI and README.
- [ ] Task 6 integration adversarial test. Source additions: measurement_v1/training.py, generation.py, local_generate.py, successor/qwen35/train_behavior_v5.py; V5 5 + entrypoint 3 + generation 3 + local runner 2 focused tests. Pending live Qwen generation, end-to-end refusal test, independent review.

**Next command:** Add selection-case reconciliation RED tests, recompute statistics from per_case, ensure malformed evidence fails closed; then full tests and remote commit; refresh this handoff.

**Last verified remote head before Task 6 partial checkpoint:** 3443dbfb539c919f664395cdd9f897610fec4790.
**Unresolved material:** real independently authored and reviewed case bank, real model generation recordings, runtime-route evidence. None may be fabricated to clear a test.

## Actual Qwen local CPU smoke verified 2026-09-30
New, development-only fictional greenhouse prompt; the original pinned base and V4 LoRA each generated the text inspection pending. Both pass an exact grader on this ONE case. No final evaluation or model qualification. Source code invoked actual model.generate and smoke scorer verified binding.
Inputs: D:/VERA/scratch/qwen35-measurement-new-dev-smoke-20260930.jsonl
Outputs: D:/VERA/qwen35-measurement-real-smoke-20260930 (base, candidate, manifest)
Score: D:/VERA/scratch/qwen35-measurement-real-smoke-score-20260930.json
Versioned receipt: successor/qwen35/measurement_v1/REAL_CPU_GENERATION_SMOKE_20260930_V1.json; SHA 756bd5744007c9b72665a1550a70c3a454517b23ae319bdb2a6b1558765fa61a.

## Hostile regression fixes since previous commit
Consumed V1/V3/V4 final prompts are now mandatory exclusions for development split, scorer and V5 SFT, even if a caller supplied an empty blocklist; source absence fails closed. Statistical gate now requires at least 50 families and non-null cluster CIs per H dimension. New end-to-end smoke and provisional candidate selection tests pass. Remaining selection defect: a hash-chain authenticates file identity, not the truth of claimed summary; require summary recomputation from per-case data before treating selection as robust.
