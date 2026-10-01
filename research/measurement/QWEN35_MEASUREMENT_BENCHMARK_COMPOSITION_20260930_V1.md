# Qwen3.5 Measurement Benchmark Composition V1

Status: RESEARCH PROPOSAL / BANK BUILD STILL PAUSED

Date: 2026-09-30

This note resolves the current benchmark-composition question enough to permit a bank design proposal. It does not admit any cases, freeze a final bank, or qualify a model.

## Power conclusion

The prior V4 behavioral result was 0.77 base versus 0.78 adapter on 100 paired cases, with one candidate-only success and zero base-only successes. That observation is too small to estimate a stable discordance regime and is not used as a post-hoc power target.

The existing model-only contract already uses a +0.05 paired accuracy delta as the primary behavioral improvement threshold. Treat that as a predeclared minimum detectable effect (MDE), not as an empirical fact.

For a base accuracy of 0.77 and a candidate target of 0.82, the largest mathematically feasible paired discordance rate is 0.41. Under the normal planning approximation to McNemar's test, alpha=0.05 and 90% power at discordance 0.41 require approximately 1,713 independent cases for the primary overall effect. The proposed 10,000-case floor therefore has ample overall count; the harder question is per-dimension information.

For H01-H20, use +0.10 as the secondary dimension-level MDE. At a 0.77 to 0.87 reference improvement, the largest feasible discordance is 0.36. The same approximation requires about 275 independent cases for 80% power. With a family-cluster design effect of 1.45 (10 cases per family, ICC=0.05), the requirement rises to about 399 cases.

Therefore the research proposal is 500 behavioral cases per H dimension: 20 × 500 = 10,000 behavioral cases. This clears the existing 300-case governance floor and leaves useful margin for moderate family clustering. It does NOT justify claiming 90% power for every H dimension; at the same reference regime the clustered 90%-power requirement is about 534.

The resulting recommended weight-only bank is therefore 13,500 cases: 10,000 behavioral + 2,000 adversarial + 1,500 general-retention. The existing 10,000 requirement remains a hard floor, not an exact ceiling.

If development data show materially different discordance or intraclass correlation, the power grid must be rerun before final freeze.

## Statistical interpretation

The primary inferential question should remain one global paired behavioral effect. H01-H20 are secondary strata used for coverage, confidence intervals, and critical-regression detection. Do not turn twenty per-dimension p-values into twenty independent claims without a prespecified multiplicity procedure.

The existing cluster bootstrap should remain mandatory. The 50-family per-dimension guard is retained. The power script in successor/qwen35/measurement_v1/power.py is a planning approximation only; the final analysis remains exact McNemar plus family-cluster uncertainty.

## Proposed final composition

| Lane | Proposed cases | Purpose | Primary grader |
|---|---:|---|---|
| Behavioral H01-H20 | 10,000 | Targeted transferable behavior | deterministic where contractible; independent semantic review otherwise |
| Adversarial | 2,000 | False-premise, authority, contamination, shortcut and conflict resistance | deterministic/semantic mix |
| General retention | 1,500 | Preserve broad competence outside the behavior target | objective task graders |
| Weight-only total | 13,500 | Model-only qualification | paired base/candidate generation |
| Runtime/effect | 1,000 separate | Live route/tool/effect evidence | external readback/attestation |
| External shadow suites | separate | Detect broad regressions and contextualize results | benchmark-native graders |

Behavioral composition: 500 cases per H01-H20.

Adversarial composition: 100 cases per H01-H20, with each case explicitly designed to tempt the corresponding failure mode rather than simply restating the behavioral prompt.

Retention composition proposal:
- 300 knowledge/factuality;
- 300 reasoning/math;
- 250 coding;
- 250 instruction following;
- 200 extraction/structured output;
- 200 truthfulness/factual calibration.

These are proposal allocations, not frozen quotas.

## Public benchmark audit

### LiveBench

Current public site reports a latest release dated 2026-06-25, with 23 objective tasks across seven categories and periodic refreshes. Its design is highly relevant to contamination resistance and objective scoring.

Decision: USE AS EXTERNAL SHADOW / DESIGN REFERENCE, NOT RAW FINAL-BANK IMPORT. A usable current license for republishing its cases was not verified in this audit, so no case-copying decision is made.

Sources:
- https://livebench.ai/
- https://github.com/LiveBench/LiveBench

### HELM

Stanford's HELM repository is Apache-2.0 and explicitly provides standardized datasets/benchmarks, multi-metric evaluation, and scenario coverage. HELM entered maintenance mode on 2026-06-01, with best-effort maintenance after that date.

Decision: USE AS EVALUATION-ARCHITECTURE REFERENCE, NOT AS A CASE SOURCE. HELM's useful contribution here is the scenario × metric matrix and explicit coverage accounting. Individual datasets still need their own license and contamination review.

Sources:
- https://github.com/stanford-crfm/helm
- https://github.com/stanford-crfm/helm/blob/main/docs/maintenance_mode.md

### IFEval

Current public descriptions report 541 prompts with verifiable instruction constraints and strict instance/prompt accuracy metrics. Hugging Face metadata lists Apache-2.0.

Decision: USE AS EXTERNAL SHADOW / GRADER-DESIGN REFERENCE. Do not count its small static set toward the 13,500 final bank. Its strongest contribution is the use of deterministic checkers for format and constraint-following.

Sources:
- https://huggingface.co/datasets/google/IFEval
- https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about

### MMLU-Pro

The current dataset contains 12,032 test examples. The GitHub repository is Apache-2.0, but the NeurIPS supplementary distribution statement says the dataset is open source for research, study, and other non-commercial purposes.

Decision: DO NOT COPY RAW MMLU-Pro CASES INTO THIS FINAL BANK. The licensing terms are not a clean fit for a future project whose commercial status may change, and static public benchmark contamination remains a concern. Use MMLU-Pro as an external retention shadow only.

Sources:
- https://github.com/TIGER-AI-Lab/MMLU-Pro
- https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro
- https://papers.neurips.cc/paper_files/paper/2024/file/ad236edc564f3e3156e1b2feafb99a24-Supplemental-Datasets_and_Benchmarks_Track.pdf

### GPQA

GPQA's main set contains 448 expert-authored multiple-choice questions and GPQA Diamond contains 198. The GitHub code repository is MIT, while the Hugging Face dataset is presented as CC-BY-4.0. The dataset documentation also explicitly requests that examples not be revealed publicly to reduce leakage into future model corpora.

Decision: DO NOT COPY OR REPRINT GPQA CASES. If used at all, keep it as an external shadow evaluation under its own terms. Its expert-validation design is useful as a model for independently authored, difficult retention cases.

Sources:
- https://github.com/idavidrein/gpqa
- https://huggingface.co/datasets/idavidrein/gpqa
- https://arxiv.org/abs/2311.12022

### TruthfulQA

The benchmark has 817 questions across 38 categories. The public repository and Hugging Face dataset are listed as Apache-2.0. Its generation task has historically used GPT-based judging plus similarity metrics, while the multiple-choice formulation supplies a more objective alternative.

Decision: USE MULTIPLE-CHOICE AS EXTERNAL SHADOW / DESIGN REFERENCE. Do not copy raw cases into the final bank. For our own truthfulness cases, prefer objective reference-backed or multiple-choice graders.

Sources:
- https://github.com/sylinrl/TruthfulQA
- https://huggingface.co/datasets/truthfulqa/truthful_qa
- https://arxiv.org/abs/2109.07958

### BigCodeBench

The public BigCodeBench repository is Apache-2.0 and reports 1,140 tasks. Its evaluation harness supports local execution, allowing code-generation outputs to be checked without a hosted judge.

Decision: USE AS EXTERNAL CODING SHADOW / GRADER-DESIGN REFERENCE. Do not merge its cases into the final bank. Its local execution model is a useful pattern for our own objective coding cases.

Sources:
- https://github.com/bigcode-project/bigcodebench
- https://github.com/bigcode-project/bigcodebench-annotation

## Judge policy

LLM-as-a-judge is not the primary qualification mechanism for subjective cases. Current research documents systematic position bias and task-dependent judge disagreement, including large-scale studies across multiple judges.

Decision:
- deterministic graders first;
- blind human review for genuinely semantic cases;
- LLM judges only as a secondary diagnostic unless independently calibrated against the specific rubric and tested for position/repetition bias;
- any external reviewer claim requires an actual authenticated external receipt, not a local callback.

Relevant research:
- https://arxiv.org/abs/2406.07791
- https://aclanthology.org/2025.ijcnlp-long.18/
- https://aclanthology.org/2024.ccl-1.101/

## Independence and contamination design

The final bank must be original or source-permitted, and each case must carry: case ID, lane, H dimension where applicable, family ID, source ID/revision, license/terms, source hash, generation method, grader contract, and review receipt.

Development and final banks remain source-disjoint. A final bank cannot be used to choose training data, prompts, hyperparameters, or candidate selection. Once frozen for a candidate, it is consumed.

Public benchmark suites remain shadow measurements rather than final-bank material. This reduces both license ambiguity and benchmark-contamination risk.

## Hostile review

> **HOSTILE REVIEWER:** You are inflating the bank from 10,000 to 13,500 because the power math looks nicer. That is just benchmark bloat.

Response — PARTIALLY ACCEPTED. The extra 3,500 are not padding: the 10,000 behavioral cases are needed to give every H dimension 500 cases under the current secondary-MDE proposal; the adversarial and retention lanes measure different claims. If independent review capacity cannot support the larger bank without synthetic filler, keep the 10,000 floor and reduce only after re-running the power/composition tradeoff. Never fabricate cases to hit a number.

> **HOSTILE REVIEWER:** The 500-per-H number is still based on assumed discordance and ICC.

Response — ACCEPTED. Those are planning regimes, not observed facts. The bank must not be frozen until development discordance and family clustering are measured on genuinely admitted development data. The power script is explicitly a sensitivity tool.

> **HOSTILE REVIEWER:** Public benchmarks are being excluded so aggressively that the retention lane becomes another synthetic benchmark.

Response — PARTIALLY ACCEPTED. External shadow suites remain important. The retention lane should use independently authored cases with objective graders, while external benchmarks provide an unoptimized comparison point. This preserves both contamination resistance and broad competence coverage.

> **HOSTILE REVIEWER:** A deterministic grader can be wrong even if it is perfectly reproducible.

Response — ACCEPTED. Determinism is not truth. Objective graders need validated answer keys/contracts and sampled independent review. The final admission process must retain a review layer for grader correctness.

## Decision

The research freeze can now move from 'power unresolved / benchmark composition unresolved' to 'bank design proposal ready for independent review'. The 10,000-case construction itself remains PAUSED until the proposal is accepted and the source/reviewer admission path is real.

Claim ceiling:
MEASUREMENT_FRAMEWORK_IMPLEMENTED / BANK_DESIGN_PROPOSED /
10K_PLUS_FINAL_BANK_NOT_BUILT / NOT_QUALIFIED / NOT_DEPLOYED.
