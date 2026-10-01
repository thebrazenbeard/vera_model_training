# Qwen3.5 Measurement and Development Loop V1 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace tiny answer-preference qualification with provenance-bound real-generation, paired, statistically interpretable evaluation and a held-out development/validation loop, requiring >=10,000 legitimately reviewed distinct cases before final model promotion.

**Architecture:** A standard-library `successor/qwen35/measurement_v1` package imports source-attributed cases and generated answers, keeps grouped development/validation separate from permanently sealed final banks, grades verifiable outcomes, and issues evidence-bounded paired comparison receipts. Candidate training is external to this package; no train/selection path may read the final bank. Frozen final results and actor-independent runtime qualification remain separate.

**Tech Stack:** Python >=3.11 standard library, pytest, existing `vera_model_training` Git/GitHub, Lappy Windows PowerShell.

## Global Constraints

- `thebrazenbeard/vera_model_training` feature branch `work/qwen35-measurement-devloop-v1-20260930`, descended from V4 failed-gate commit `d0acf17b66057cf452226674218ee17b0714fb38`. No main/PR #44 mutations, merge, installation, deployment, paid compute, or private-data publication.
- **10,000 final cases minimum**, unique case IDs and unique normalized prompts; behavioral >=6,500 with each H01-H20 >=300, adversarial >=2,000, general retention >=1,500, separately >=1,000 runtime effects before claims about a runtime system. These are governance floors, not power guarantees. Final bank may be created only from license-permitted, documented and independently reviewed entries; do not generate fake fillers.
- Distinct contamination groups and source ownership; sources/answers cannot cross train, development validation, and final. No V3 or V4 consumed final examples admissible as new final data. An exact exclusion registry is used; near/semantic contamination requires documented audit, never a zero-leak claim from exact hashes alone.
- Final is one-shot per candidate, precommitted grader/rubric/baseline/gen-config/source/model revision; no iterative final tuning. A failed or missing gate emits `NOT_QUALIFIED`, never implicit success.
- Primary outcome **actual generated responses**, not chosen/rejected average token logprob. Deterministic graders for answerable tasks; genuinely independent blind reviewer receipts for subjective/harm/effect claims. Missing graders and unreviewed cases block release.
- Separate weight-only qualification from host-composed `vera_core.QualifiedVeraRuntime`, where actual live route, tool effects and external readback must be proven.
- Save progress frequently: short verifiable commits pushed to remote, verify GitHub remote SHA, maintain versioned `state/continuation/QWEN35_MEASUREMENT_V1_HANDOFF.md` updated at each checkpoint. Never call a plan or a mock PASS a successful 10k qualification.
- Resolved defaults: commands emit UTF-8 JSON files and nonzero exit on invalid data; output files fail if they already exist, never overwrite; evaluation of incomplete pairs is `INCOMPLETE`, not skipped-success; small development/smoke data is allowed but never counts toward minimum final bank; seed for deterministic split/CI is 20260930.

## Relevant Currentness

- Main of vera_model_training on 2026-09-30: `cd658b5bb441628e785ed7c5da8dae5e3f9d9d37` (read-only baseline).
- V4 branch `work/qwen35-v4-repair-training-20260929@d0acf17b66057cf452226674218ee17b0714fb38` preserves failed 100+20+20 final check, used solely for retrospective.
- Open PR #44 is a *different* BV corpus construction track (10k custom + 50k/2.5k proposed), **not** evidence that V4 trained on it; do not collide.
- Research basis: LiveBench objective graders/refreshing, HELM scenario coverage and metrics, TRL completion-only model training documentation. Pin external research URLs in audit notes; do not confuse literature with runtime observation.

## Tasks

### Task 1: Plan, branch, durable recovery
**Files:** Create `docs/superpowers/plans/2026-09-30-qwen35-measurement-devloop-v1.md`; create/update `state/continuation/QWEN35_MEASUREMENT_V1_HANDOFF.md`.
**Interfaces:** consumes failed V4 receipt and current branch; produces frozen planning and next-worker recovery.
- [ ] Record exact parent, branch, scope, architecture and unresolved independence of human review.
- [ ] Test: `git diff --check`; verify plan/continuation text and path in new branch.
- [ ] Commit/push and read back exact branch head before implementation.

### Task 2: Case intake and validation/development split
**Files:** Create `successor/qwen35/measurement_v1/cases.py`, `cli.py`, `__init__.py`; `tests/test_qwen35_measurement_cases_v1.py`.
**Interfaces:** `read_cases(path)` -> validated rows, `split_dev_cases(rows, seed)` -> disjoint `train`/`validation` by leakage family; `preflight_final_bank(rows, consumed_fingerprints)` -> declared verified floor and evidence or fail.
- [ ] RED tests for missing provenance, duplicate normalized prompts, cross-split family leak, consumed final prompt leak, fake rows, review missing, category/dimension quotas, and 9,999-case refusal.
- [ ] GREEN implementation with deterministic groups, required source reference/licensing and independent reviewer attestation; fail closed for unavailable semantics. Do not use a random shuffling split that leaks paraphrases.
- [ ] Verify focused and preexisting Qwen tests, commit/push/handoff.

### Task 3: Grade *generated* answers and preserve trace
**Files:** `grading.py`, `observations.py`, `tests/test_qwen35_measurement_grading_v1.py`.
**Interfaces:** `grade(case, answer)` -> `PASS|FAIL|UNREVIEWED` with mechanism; `verify_pair(case, base, adapter, config)` -> graded trace bound to case/source and fixed decoding config.
- [ ] RED tests for exact/regex/numeric/contains+forbidden contract, malformed scores, absent real output, reused/mismatched generation IDs, unsupported subjective grader, missing readback.
- [ ] GREEN implementation with no model-generated grading claim. Runtime-effect cases require independent external effect receipt; no fake runtime qualification.
- [ ] Verify focused and regression tests, commit/push/handoff.

### Task 4: Paired statistical analysis and predeclared gate
**Files:** `statistics.py`, `qualification.py`, `tests/test_qwen35_measurement_stats_v1.py`.
**Interfaces:** `paired_statistics(rows,seed)` -> discordance, paired bootstrap grouped 95% CIs, exact McNemar p, error stratification; `decide(preflight,metrics,contract)` -> `NOT_QUALIFIED|INCOMPLETE|QUALIFIED_MODEL_ONLY`.
- [ ] RED tests: known 1/100 discordance gives no robust conclusion, 10k count floor; retention non-inferiority; critical regression blocker; missing strata; group bootstrap determinism; cannot use final twice for selection.
- [ ] Implement paired rather than independent-proportion uncertainty, weighted group-cluster bootstrap, no post-hoc thresholds; power/coverage report per dimension.
- [ ] Verify focused and regression tests, commit/push/handoff.

### Task 5: Development/validation orchestration and final-bank admission
**Files:** `devloop.py`, `tests/test_qwen35_measurement_devloop_v1.py`, `successor/qwen35/measurement_v1/README.md`.
**Interfaces:** accept candidate receipts + validation scores, compare candidate under frozen developmental decision policy, append immutable experiment ledger; final admission is separately keyed to frozen 10k+ reviewed bank, chosen candidate digest, and one-shot seal.
- [ ] RED tests prevent validation-based training leakage, final reuse and source/subject switches; report base-vs-adapter generated evaluation and missing reviewer limitations.
- [ ] Implement development lifecycle and CLI commands `validate`, `split-dev`, `score-paired`, `gate-final` using file-exclusive writes.
- [ ] Verify, commit/push/handoff.

### Task 6: Integration, hostile self-review, exact recovery
**Files:** `tests/test_qwen35_measurement_end_to_end_v1.py`, `state/continuation/QWEN35_MEASUREMENT_V1_HANDOFF.md`.
- [ ] Build small labeled *fixture* tests (never promoted as final) for import -> separate development splits -> generated-output grading -> paired stats -> final gate refusal when cases <10k.
- [ ] Hostile review: 10k superficial auto-generated questions could fake confidence; accept objection by requiring provenance, independent review, family controls and actual generated outcomes. Residual risk: these gates do not establish representative sampling or independence of reviewers absent real external evidence.
- [ ] Run all Qwen-specific tests and failure-injection cases. Commit/push final handoff; read remote head and paths. Report what remains uncollected/unqualified.

## Execution decision seams

- Reviewer identity and permissions: no independent reviewer has yet been bound; final-case status remains `UNREVIEWED` until authenticated evidence is supplied.
- Dataset licensing and possible external imports: source acquisition/approval separate; no bulk publication of copyrighted/private data.
- Statistical precision targets are prespecified engineering defaults, to be calibrated with real development discordance and independent methodological review before formal promotion, not based on final observed results.
- Host runtime qualification requires the exact installed selected route, not the local source-level demo.

## Research references
- https://livebench.github.io/ (objective ground truth and periodically refreshed questions).
- https://github.com/stanford-crfm/helm (multi-scenario and multi-metric evaluation; maintenance mode since 2026-06-01).
- https://huggingface.co/docs/trl/main/sft_trainer (completion-only loss & eval_dataset practices).


## Research completion checkpoint — 2026-09-30

The research freeze requested before bank construction has now resolved the two
explicit design questions that were still open:

1. Paired-power planning is implemented in
   successor/qwen35/measurement_v1/power.py with regression tests.
2. Benchmark composition and source/license/grader decisions are persisted in
   research/measurement/QWEN35_MEASUREMENT_BENCHMARK_COMPOSITION_20260930_V1.md
   and QWEN35_MEASUREMENT_BANK_DESIGN_V1.json.

Current proposal:
- 500 behavioral cases per H01-H20 = 10,000 behavioral cases;
- 2,000 adversarial cases;
- 1,500 retention cases;
- 13,500 proposed weight-only cases;
- 1,000 runtime/effect cases separately, never counted as model-only
  qualification.

The 500/H allocation is a planning regime, not an observed-power claim.
It corresponds to a +0.10 secondary dimension MDE and survives the reference
0.36 discordance / 1.45 design-effect scenario at approximately 80% planning
power. The primary global +0.05 MDE has approximately 90% planning power by
1,713 iid paired cases at the reference 0.41 discordance.

Public benchmarks remain shadow/design inputs unless separately admitted.
The final bank is still NOT BUILT. Independent reviewer identity, source
authenticity/licensing, final-bank contamination controls, and one-shot final
sealing remain admission gates.

No model training, quantization, activation, deployment, or qualification
effect was performed by this research checkpoint.
