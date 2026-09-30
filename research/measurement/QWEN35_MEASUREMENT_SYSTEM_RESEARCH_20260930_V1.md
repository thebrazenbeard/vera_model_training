# Qwen3.5 Measurement System Research Checkpoint — 2026-09-30

Status: RESEARCH FREEZE / BANK DESIGN NOT YET COMMITTED

Repository: `thebrazenbeard/vera_model_training`
Branch: `work/qwen35-measurement-devloop-v1-20260930`
Checkpoint parent before this note: `1c95cd5edca743b0322406f662228c50d566e7a6`
Local workspace: `D:\VERA\.worktrees\qwen35-measurement-devloop-v1-20260930`

Current repository evidence:
- `vera_model_training/main` observed at `08a69c98312dd5aab437d4996e12bbb34a5900c2`.
- `vera-mono/main` observed at `413397e51bce35d0a36f00cf0ca2c876ca720b44`.
- Open `vera_model_training` PR #44 remains a separate 50k training-corpus workstream; do not treat it as measurement-bank evidence or V4 training input.
- Vera Mono current contracts preserve the distinction SOURCE != RUNTIME != BEHAVIOR != INDEPENDENT REVIEW.

## Why this checkpoint exists

Patrick explicitly requires at least 10,000 evaluation cases and asked for research before committing to the bank design. Work on constructing the bank is paused until the measurement design is justified. The 143 passing pytest tests on this branch are engineering tests only. They are **not** evaluation cases and do not count toward the 10,000-case requirement.

No 10,000-case admitted final bank currently exists.

## Preserved V4 measurement evidence

The prior V4 final evaluation used 140 distinct cases, each scored for base and adapter (280 condition-case scores):
- behavioral: 100 cases, base 0.77, V4 0.78;
- retention: 20 cases, base 0.95, V4 1.00;
- adversarial proxy: 20 cases, base 0.50, V4 0.45.

Paired classification audit:
- behavioral: 1 adapter-only success, 0 base-only, 99 unchanged;
- retention: 1 adapter-only success, 0 base-only, 19 unchanged;
- adversarial: 0 adapter-only, 1 base-only, 19 unchanged;
- total: 137/140 classifications unchanged.

Interpretation ceiling: this proves V4 failed its predeclared small gate. It does not establish a precise global model capability estimate.

## Measurement principles now treated as requirements

1. **10,000 final cases is a floor, not the power calculation.**
   Sample size must also be justified per lane and per H dimension using paired model discordance, family clustering, desired detectable effect, and confidence targets.

2. **Primary measurement is actual generated behavior.**
   Chosen-vs-rejected token log-probability can remain a diagnostic but cannot be the main qualification claim.

3. **Paired analysis is mandatory.**
   Base and candidate see the same cases under the same decoding contract. Report discordant counts, exact McNemar evidence, paired/cluster-aware confidence intervals, and per-dimension strata.

4. **Prompt families and upstream sources are leakage units.**
   Current code now keeps shared `family_id` or `origin.source_id` together in development splits, rejects source overlap in V5 SFT train/validation, and can exclude development source IDs from proposed finals. Source IDs are self-declared and therefore not independently trusted.

5. **Final data cannot be used for development selection.**
   V3/V4 finals are consumed. A new final bank is one-shot per candidate cut and cannot be used to choose hyperparameters or training examples.

6. **Objective graders where possible; authenticated independent review where necessary.**
   Manual semantic and runtime-effect graders fail closed as UNREVIEWED without independent receipts.

7. **Model-only and runtime claims remain separate.**
   Weight-level generation results do not establish `vera_core.QualifiedVeraRuntime`, live route selection, tool effects, installation, or deployment.

8. **Representativeness is not implied by count.**
   10,000 templated or same-author cases can produce a narrow, overconfident benchmark.

## Current candidate bank allocation hypothesis — NOT APPROVED

The working allocation that triggered this research phase was:
- 6,500 behavioral cases = 325 per H01-H20;
- 2,000 adversarial cases;
- 1,500 general retention cases;
- total 10,000 model-only cases;
- runtime/effect cases handled as a separate evidence lane rather than laundering source-level model tests into runtime qualification.

This is only a hypothesis. The per-dimension count of 325 has **not** yet been justified by paired power analysis or effective sample-size estimates and must not be frozen as final design.

## Existing H01-H20 behavioral targets

The source taxonomy in `successor/qwen35/HISTORY_BEHAVIOR_CURRICULUM_V2.json` defines:
- H01 semantic proposition fidelity
- H02 correction propagation
- H03 verify before contradicting
- H04 delegated agency retention
- H05 smallest useful act before procedure
- H06 anti-stall / land the ship
- H07 effect verification
- H08 capability truth
- H09 evidence/time-class separation
- H10 task segmentation fidelity
- H11 material ambiguity only
- H12 first-person self-reference
- H13 salience is not evidence
- H14 context-sensitive response bandwidth
- H15 metaphor and intended meaning
- H16 failure classification and changed retry
- H17 privacy-preserving generalization
- H18 independent judgment without contrarianism
- H19 currentness/source/runtime separation
- H20 scope/authority-sensitive correction

The final bank must cover failure-mode diversity inside each dimension, not merely repeat one template 325 times.

## External benchmark observations gathered so far

These are research inputs, not adopted components.

### MMLU-Pro
- Dataset observed from Hugging Face: `TIGER-Lab/MMLU-Pro`.
- Observed dataset revision: `b189ec765aa7ed75c8acfea42df31fdae71f97be`.
- Observed license metadata: MIT.
- Observed test split: 12,032 rows.
- Observed categories: math 1351; physics 1299; chemistry 1132; law 1101; engineering 969; other 924; economics 844; health 818; psychology 798; business 789; biology 717; philosophy 499; computer science 410; history 381.
- Relevance: broad retention/reasoning reference.
- Limitation: multiple-choice knowledge/reasoning is not direct evidence for the H01-H20 Vera behavioral targets.

### IFEval
- Dataset observed from Hugging Face: `google/IFEval`.
- Observed dataset revision: `966cd89545d6b6acfd7638bc708b98261ca58e84`.
- Observed license metadata: Apache-2.0.
- Observed train split: 541 prompts.
- Cases carry explicit instruction IDs and checker parameters.
- Relevance: objectively checkable instruction-following patterns and grader design.
- Limitation: far too small to supply the 10k bank; many tasks target format compliance rather than the full Vera behavioral taxonomy.

### LiveBench / HELM / other benchmark families
Research was initiated but not completed before this checkpoint. Prior notes identify their usefulness for refreshed/objective evaluation and multi-scenario/multi-metric design, but exact current dataset composition, license, contamination strategy, and portability into this repository still need fresh verification before adoption.

## Hostile review

> **HOSTILE REVIEWER:** “10,000” can become theater. If the same system authors 10,000 near-duplicates from twenty templates and grades them with its own rubric, the result is a more precise measurement of its own assumptions, not stronger evidence about general behavior.

**ACCEPTED.** Final-bank admission must include family/source diversity, deduplication, provenance, independent review for semantic cases, and an explicit sampling argument. Count alone is insufficient.

> **HOSTILE REVIEWER:** Importing 10,000 MMLU-Pro rows would satisfy the count but largely test multiple-choice academic knowledge, not Vera's correction propagation, effect verification, authority boundaries, currentness, privacy generalization, or tool behavior.

**ACCEPTED.** Public benchmarks may contribute retention/reference lanes, but cannot substitute for taxonomy-aligned behavioral cases.

> **HOSTILE REVIEWER:** A fixed “325 per H dimension” is arbitrary. With highly correlated prompt families or low base/candidate discordance, 325 can have far less effective power than 325 independent observations.

**ACCEPTED.** The dimension sample size must be driven by target effect size, paired discordance, cluster structure, and family count. 325 remains provisional.

> **HOSTILE REVIEWER:** Requiring every final case to receive fully independent human review could make a 10k bank operationally unrealistic, causing the project either to stall or to invent fake independence.

**PARTIALLY ACCEPTED.** Objective deterministic graders should carry as much of the bank as legitimately possible. Human review should focus on semantic/subjective/error-severity cases and audit samples, but any claim of independent review requires a real external reviewer/attestation. The repo must never self-certify that layer.

> **HOSTILE REVIEWER:** A model-only 10k bank still cannot prove the ChatGPT Project, ProRun service, tools, memory, or `QualifiedVeraRuntime` behave correctly.

**ACCEPTED.** Runtime/effect qualification remains a separate suite with live route/effect/readback evidence.

## Research questions that MUST be resolved before bank construction

1. What minimum detectable improvement is meaningful for the overall model and for each H dimension?
2. What expected base-vs-candidate discordance should be used for paired power planning?
3. What minimum number of independent families/sources is required per dimension?
4. How should cases be weighted when source families vary greatly in size?
5. Which H dimensions can use deterministic graders, and which require blind semantic review?
6. How should critical failures override aggregate accuracy?
7. What retention mix is appropriate: knowledge, reasoning, instruction following, coding, extraction, math, factuality?
8. Which public benchmarks are license-compatible and contamination-appropriate for a final bank?
9. How much of the final bank should be externally sourced versus independently authored?
10. What evidence proves final-bank reviewers are independent of the candidate-selection process?
11. How will final-bank exposure be controlled so a failed final cannot be tuned against?
12. What separate runtime/effect suite is required for `QualifiedVeraRuntime` rather than model-only weights?

## Exact next research sequence

1. Finish literature/benchmark audit: LiveBench, IFEval, HELM, MMLU-Pro, BBH/GPQA-style reasoning, truthful/factuality, coding, safety/adversarial and LLM-as-judge bias literature.
2. Build a paired-power notebook/script that computes required N across plausible discordance/effect regimes and family-cluster design effects. This is development tooling, not a final benchmark.
3. Produce a benchmark composition proposal with explicit source/license/grader/coverage mapping and hostile review.
4. Only after that proposal survives review, implement the candidate-bank builder.
5. Keep every generated/imported case in CANDIDATE / UNREVIEWED state until real review/admission evidence exists.
6. Freeze a final bank only after independent review and contamination audit; do not score a candidate before that freeze.

## Work already implemented on this branch

At `1c95cd5`, the measurement workstream contains:
- validated case schema and 10k structural floor;
- family/source-disjoint development splitting;
- consumed-final exclusion;
- generated-response observation binding;
- deterministic graders and fail-closed manual/effect graders;
- paired statistics with exact McNemar and family-cluster bootstrap;
- conservative model-only gate;
- immutable development validation ledger;
- provisional candidate selection with recomputation from per-case evidence;
- H01-H20 development-coverage guard;
- V5 validation-enabled SFT preflight/trainer path;
- actual one-case local CPU base-vs-V4 generation smoke, explicitly not qualification;
- source-overlap defenses across development split, V5 SFT, and proposed finals.

Fresh regression before `1c95cd5` push: 143 Qwen-focused tests passed.

## Claim ceiling

`MEASUREMENT_FRAMEWORK_IMPLEMENTED / RESEARCH_INCOMPLETE / 10K_FINAL_BANK_NOT_BUILT / NO_NEW_MODEL_QUALIFICATION / NO_DEPLOYMENT`
