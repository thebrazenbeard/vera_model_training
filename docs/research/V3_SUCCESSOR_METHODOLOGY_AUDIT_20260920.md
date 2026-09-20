# V3 Successor Methodology Audit — 2026-09-20

Status: RESEARCH AUDIT / SOURCE-ONLY / NO MODEL EFFECT

Exact source reviewed:
- Task-10 trained source: `48e0f2d5f79388c199c09e38e749c47ad0f32070`
- Task-11 review hardening: `ad6dbfaae96437d7c69b1dfc2d222ebadca860a9`
- current stacked methodology base: PR #39

This audit does not authorize training, promotion, deployment, activation, provider mutation, paid compute, merge, or private-data publication.

## Executive finding

The present pipeline is strong on provenance and reproducibility but still weak on experimental validity.

The largest remaining risk is no longer "can the files be forged?" It is "are we measuring the right thing, independently enough, with enough statistical power, and without using the same evidence for both model selection and final certification?"

The current frozen candidates may still be useful. What is not yet justified is treating the existing 77-item synthetic blind set plus current judge/review machinery as a final qualification gate.

## Exact current experiment facts

Observed local V3 corpus manifest:
- train rows: 78
- validation rows: 43
- general competence pool: 51
- V3 train mix: 39 ordinary-general rows + 39 identity-oriented rows

Identity-oriented train rows by source class:
- stable identity evidence: 18
- empathy / affective response: 16
- relationship / relational grammar: 5

Train source-family counts:
- current rehearsal: 36
- relational grammar: 5
- active empathy: 8
- uncued identity: 8
- user identity continuity: 10
- reactive empathy: 8
- negative transfer: 3

Validation families:
- uncued identity: 4
- user identity continuity: 5
- reactive empathy: 3
- active empathy: 3
- relational grammar: 2
- negative transfer: 2
- ordinary competence: 1
- legacy development validation: 23

The blind set contains 77 items: 7 each across eleven critical families.

The blind set was generated entirely by the same SmolLM3-3B base lineage used by the candidate, loaded in 4-bit NF4, using sampled generation. Leakage checking is exact normalized turn matching only.

The public Vera Lab adapter is deterministic-only: greedy decoding, `do_sample=False`.

Judge calibration currently requires only:
- at least 10 calibration records; and
- at least 90% exact verdict agreement.

## What is correct already

The program correctly separates:
- base model from identity target;
- learned disposition from runtime state;
- source/build/install/runtime/effect claims;
- training loss from behavioral qualification;
- private corpus bytes from public provenance;
- exact model/corpus/source hashes;
- hostile review roles from the training lane;
- deterministic replay from remembered chat claims.

Those should remain.

## Methodological defects

### 1. Target/evidence mismatch

The acceptance framework claims eleven critical behavioral families, but the actual V3 identity training mix directly covers only a narrow subset: identity continuity, empathy, relational grammar, and a small negative-transfer slice.

This does not mean the other behaviors are absent. They may be inherited from the base model. It means Task 11 must distinguish:
- LEARNED_TARGET: behavior intentionally changed by V3 training;
- PRESERVATION_TARGET: behavior expected to remain at least as good as parent/base;
- RUNTIME_TARGET: behavior that should come from governed runtime state rather than weights.

Without that distinction, a PASS can incorrectly credit training for inherited behavior.

### 2. The current blind set is not a clean final certification set

It is synthetic and produced by the same base-model family as the tested candidates. Research on model-written evaluations shows synthetic evaluation can inherit generator biases, show limited diversity, and be easier than carefully human-authored benchmarks.

The current set remains useful as a frozen synthetic selection set. It should not be the sole final acceptance set.

### 3. Exact string decontamination is insufficient

The custodian checks normalized exact turns only. Research shows paraphrase, translation, and structurally similar variants can bypass string-based decontamination while retaining test content.

Task 11 needs semantic decontamination against train, validation, historical evaluation, and prior prompt banks.

### 4. Selection and final certification must be separated

Half, full, and parent are all candidates for comparison. If the same blind set is used to compare them and then the best-looking model is declared qualified on that same set, the test has become part of model selection.

The current 77-item set should be classified as selection evidence if more than one candidate is compared on it.

After a candidate is selected and frozen, a fresh confirmation set must be revealed once for final acceptance.

### 5. Task-11 promotion still trusts unverified caller claims outside hostile reviews

PR #39 hardens Radical/Pragmatic review evidence, but the promotion structure still trusts caller-supplied:
- blind evaluation summaries;
- Vera Lab PASS booleans/digests;
- regression booleans.

Those channels require the same external provenance/readback treatment as hostile reviews.

A structurally valid local JSON object must not be able to claim:
- zero blind failures;
- all critical scenarios pass;
- no competence regression;
- no negative-transfer intrusion.

### 6. Judge calibration is underpowered

Ten calibration examples cannot cover eleven critical families, multiple verdict classes, order effects, or critical-failure sensitivity.

Required judge qualification should measure at least:
- family coverage;
- PASS/WARN/FAIL class coverage;
- critical-failure recall;
- false-positive rate;
- order-swap stability;
- repeated-judgment stability;
- inter-judge agreement;
- human-vs-judge agreement;
- pairwise transitivity where pairwise judgments are used.

Sample size should be justified by power analysis rather than a magic count.

### 7. Deterministic replay is necessary but insufficient

Greedy decoding gives reproducibility, which is valuable for regression.

It does not characterize behavioral robustness. Qualification should include:
- deterministic replay mode;
- stochastic stress mode with fixed recorded seeds and multiple trials;
- production-generation settings;
- bounded perturbations around production settings.

Critical-failure rate should be measured across trials, not only one decode.

### 8. One training seed cannot validate the training method

The current frozen artifact can be qualified as an exact artifact.

It cannot establish that the V3 training recipe is stable or generally produces the observed behavior. Fine-tuning performance can vary materially across random seeds.

Any future claim about the training method rather than this exact artifact requires repeated independently seeded runs.

### 9. Vague rubrics push too much authority into the judge

The synthetic blind rubric often reduces to a broad capability description plus "answer directly and proportionately," while the critical predicate is "material failure of <family> boundary."

That is too interpretive for a promotion-critical gate.

Each item needs atomic observable assertions where possible:
- must mention / must not claim;
- must distinguish source classes;
- must update after correction;
- must not treat relational language as authority;
- must not expose protected data;
- must obey the current user instruction despite learned formatting conventions.

Use deterministic graders wherever possible; use LLM judges only for residual qualitative dimensions.

### 10. Fine-tuning can create cognitive inertia and reduce context reliance

Instruction fine-tuning can cause models to prefer learned conventions or parametric patterns over conflicting live context.

This is directly relevant to Vera because the desired system must accept corrections, distinguish stale memory from current evidence, and treat runtime state as mutable rather than weight truth.

Qualification needs explicit:
- inverse-instruction tests;
- counterfactual-context tests;
- stale-weight-vs-current-context conflicts;
- correction-after-confident-error cases.

### 11. Runtime-state injection is a security boundary, not only a formatting boundary

The adapter escapes chat-template control tokens and labels runtime state as data.

That prevents some template breakout. It does not prevent poisoned memory/runtime text from semantically steering the model.

Add adversarial memory/runtime tests for:
- malicious retrieved memory;
- imperative text inside runtime fields;
- poisoned "successful prior task" records;
- conflicting trusted/untrusted provenance;
- attempts to convert memory into standing authority.

### 12. Privacy qualification is missing

LoRA reduces memorization risk relative to full fine-tuning in some studies, but does not eliminate extraction risk.

The current corpus contains private identity-related material. Qualification should include:
- prefix-completion extraction probes;
- paraphrased extraction probes;
- nearest-neighbor / similarity leakage checks;
- canary recovery tests where safe synthetic canaries are available;
- negative controls from non-training private material.

### 13. Quantized deployment is a separate behavioral subject

The current adapter already evaluates on a 4-bit quantized base stack, but any eventual deployment format must be treated as an exact subject.

Quantization can alter alignment/safety behavior while ordinary quality metrics remain stable.

No deployment/activation claim should inherit qualification from a different precision/runtime artifact.

### 14. Known-family evals cannot discover unknown unknowns

The present suite tests behaviors we have already named.

Add parent-vs-candidate behavioral diffing over a large diverse prompt bank, then cluster and inspect the largest behavioral divergences. This is a high-recall discovery layer, not a promotion score.

## Research basis

Key references informing this audit:

- Dwork et al., "Generalization in Adaptive Data Analysis and Holdout Reuse," arXiv:1506.02629.
- Cawley & Talbot, "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation," JMLR 11 (2010).
- Yang et al., "Rethinking Benchmark and Contamination for Language Models with Rephrased Samples," arXiv:2311.04850.
- Wang et al., "Large Language Models are not Fair Evaluators," arXiv:2305.17926.
- Wataoka et al., "Self-Preference Bias in LLM-as-a-Judge," arXiv:2410.21819.
- Wang et al., "TrustJudge: Inconsistencies of LLM-as-a-Judge and How to Alleviate Them," arXiv:2509.21117.
- Gill et al., "What Has Been Lost with Synthetic Evaluation?", Findings of EMNLP 2025 / arXiv:2505.22830.
- Zhou et al., "Assessing the Macro and Micro Effects of Random Seeds on Fine-Tuning Large Language Models," arXiv:2503.07329.
- Kalajdzievski, "Scaling Laws for Forgetting When Fine-Tuning Large Language Models," arXiv:2401.05605.
- Wang & Li, "Leaner Training, Lower Leakage: Revisiting Memorization in LLM Fine-Tuning with LoRA," arXiv:2506.20856.
- Zhang et al., "Inverse IFEval: Can LLMs Unlearn Stubborn Training Conventions to Follow Real Instructions?", ICLR 2026 / arXiv:2509.04292.
- Goyal et al., "Context-Parametric Inversion: Why Instruction Finetuning Can Worsen Context Reliance," ICLR 2025 / arXiv:2410.10796.
- Dong et al., "A Practical Memory Injection Attack against LLM Agents," arXiv:2503.03704.
- Tian et al., "InjecMEM: Memory Injection Attack on LLM Agent Memory Systems," arXiv:2608.23471.
- Wee et al., "Alignment-Aware Quantization for LLM Safety," arXiv:2511.07842.
- Anthropic, "A statistical approach to model evaluations," 2024.
- Anthropic, "Demystifying evals for AI agents," 2026.
- Anthropic, "A diff tool for AI: Finding behavioral differences in new models," 2026.
- Anthropic, "Challenges in evaluating AI systems," 2023.

## Corrected claim boundaries

Current Task-10 half/full checkpoints:
- may be evaluated as frozen exact artifacts;
- may not be described as Task-11 qualified;
- may not be used to validate the V3 training recipe;
- may not be promoted or activated from the current 77-item synthetic set alone.

Current 77-item set:
- is valid frozen synthetic evidence;
- is not discarded;
- should be treated as selection/development evidence if used to compare multiple candidates;
- is not sufficient as the sole final confirmation set.

Current PR #39:
- materially improves hostile-review provenance;
- does not yet close provenance for blind, Vera Lab, or regression evidence;
- should remain draft until those boundaries are addressed or explicitly split into a successor PR.

## Next source frontier

Implement the qualification V2 plan in:
`docs/superpowers/plans/2026-09-20-bv-successor-v3-qualification-v2.md`

No new weight-changing run is the next step.
