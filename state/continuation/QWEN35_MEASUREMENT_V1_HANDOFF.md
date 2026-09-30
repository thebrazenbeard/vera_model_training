# Qwen3.5 Measurement + Development Loop V1 — Live Handoff

**Checkpoint:** TASK_3_GRADING_VERIFIED. This file must be updated after each independently verified commit.
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
- [ ] Task 4 paired confidence gate.
- [ ] Task 5 dev/validation lifecycle and CLI.
- [ ] Task 6 integration adversarial test.

**Next command:** Write RED paired-statistics tests at tests/test_qwen35_measurement_stats_v1.py, then implement statistics.py and qualification.py. Preserve model-only claim ceiling.

**Last verified remote head before Task 3 commit:** 3d4baa54f08254117ea20c22ddaa2293c8f07bbc; verify newest with git ls-remote before claims.
**Unresolved material:** real independently authored and reviewed case bank, real model generation recordings, runtime-route evidence. None may be fabricated to clear a test.
