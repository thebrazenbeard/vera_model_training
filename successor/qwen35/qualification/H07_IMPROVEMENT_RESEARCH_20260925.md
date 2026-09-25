# H07 Improvement Research — 2026-09-25

## Why V1 probably failed

The frozen H07 V1 experiment used only 16 training mechanisms and 8 development cases. Both corrected `adamw_torch` conditions stayed at 3/8 accuracy and moved mean preference margin in the wrong direction. This is evidence against those exact recipes, not evidence that H07 cannot be learned.

The strongest research-supported explanation is that V1 mostly supplied case-level preferences. It did not explicitly train a reusable rule representation across enough distinct task families.

## Research findings

### 1. Rule abstraction and task diversity matter

- Hu et al., *Training Large Language Models to be Better Rule Followers* (arXiv:2502.11525) explicitly models rules and instances across 88 rule-following tasks and reports cross-task transfer; dataset size and rule formulation are studied as important factors.
- FLAN (*Finetuned Language Models Are Zero-Shot Learners*, arXiv:2109.01652) found that natural-language instructions, model scale, and number of fine-tuning datasets are important for zero-shot transfer.
- DEITA (*What Makes Good Data for Alignment?*, arXiv:2312.15685) identifies complexity, quality, and diversity as separate data-selection dimensions; its data-efficient alignment results still use thousands of examples, not tens.
- LIMA (arXiv:2305.11206) shows that carefully curated data can be surprisingly efficient, but its result used 1,000 examples on a 65B model. It does not support treating 16 examples on a 4B-class model as sufficient.
- Self-Instruct (arXiv:2212.10560) and GLAN (arXiv:2402.13064) support synthetic expansion when diversity and filtering are explicit.

Implication: H07 V2 should train the rule and its applications, not merely preference pairs that happen to instantiate the rule.

### 2. ORPO is not the next obvious lever

ORPO (arXiv:2403.07691) is validated on much larger preference data. Our 16-pair ORPO continuation added no generalization benefit.

Preference-learning literature also warns about overfitting or poor coverage:
- Identity Preference Optimization / PsiPO (arXiv:2310.12036) was motivated in part by DPO pathologies and overfitting.
- SimPO (arXiv:2405.14734) uses length-normalized rewards and an explicit target margin.
- ODPO (arXiv:2402.10571) reports gains over DPO when preference pairs are limited by representing preference strength.
- MMPO (arXiv:2410.03145) similarly uses granular margins and reports improved robustness to overfitting.

Implication: first establish that broader explicit-rule SFT can generalize. Only then compare a preference objective. Do not cycle through losses on the same narrow corpus.

### 3. PEFT configuration may contribute

Current V3 uses all-linear QLoRA with rank 4.

- Current TRL/PEFT guidance supports all-linear targeting for QLoRA and notes that limiting LoRA to attention matrices can underperform.
- Shuttleworth et al., *LoRA vs Full Fine-tuning: An Illusion of Equivalence* (arXiv:2410.21228), find distinct OOD behavior and undesirable low-rank "intruder dimensions"; higher-rank rank-stabilized LoRA more closely resembles full fine-tuning.
- *LoRA Dropout as a Sparsity Regularizer for Overfitting Control* (arXiv:2404.09610) provides theory and experiments supporting dropout for LoRA overfitting control.

Constraint: Lappy peaked around 3.9+ GiB of 4 GiB VRAM with rank 4 all-linear. Raising rank before a memory redesign is not justified. Low-cost candidates later are LoRA dropout and rank-stabilized scaling at the same rank, followed by a separately qualified capacity experiment.

### 4. The substrate is a confound

The current subject is `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`, a downstream aggressive/uncensored checkpoint derived from Qwen3.5-4B rather than the clean parent checkpoint.

Arditi et al. (arXiv:2406.11717) report that refusal-direction ablation can be relatively surgical with minimal standard-capability impact, but the current subject also includes additional uncensored fine-tuning. Therefore its behavior cannot be attributed to directional ablation alone.

Implication: before concluding that Qwen3.5-4B lacks H07 capacity, benchmark the clean parent Qwen3.5-4B on the same H07 controls if a local copy can be obtained without displacing current evidence.

## Revised experiment order

### A. Finish H07 V1 architecture discrimination

Use the frozen 8-row development set and exact same scoring method for:

1. BASE
2. BASE + explicit runtime policy
3. TRAINED SFT + explicit runtime policy
4. TRAINED SFT+ORPO + explicit runtime policy

The explicit policy is `h07_effect_verification_policy_v2.txt`.

This condition tests rule availability at inference time. It is not equivalent to a full Vera runtime/tool implementation and must not be described as one.

### B. Build H07 V2 rule-transfer corpus

Target a staged, family-held-out design rather than paraphrase expansion:

- 12 training mechanism families x 8 independently authored cases = 96 SFT cases;
- 4 held-out mechanism families x 8 cases = 32 development cases;
- mix positive and negative counterfactuals inside each family;
- explicitly include the H07 rule in training;
- preserve receipt-sufficient cases so the model does not learn "always read back";
- preserve ambiguous-effect/retry cases;
- hold out entire mechanism families, not merely wording.

If 96 examples still show no family-level transfer, expand only after analyzing errors. Do not tune against the 32-case family holdout indefinitely; replace it with a fresh development set once it becomes a recipe-selection target.

### C. Objective ablation after SFT

Only if H07 V2 SFT shows some transfer:

- SFT only;
- then one regularized preference candidate (IPO or a margin-aware method) against SFT;
- do not automatically include ORPO.

### D. PEFT ablation after data succeeds

If broader SFT learns the rule but plateaus:
- rank 4 baseline;
- rank 4 + LoRA dropout;
- rank 4 + rank-stabilized scaling if supported by the installed PEFT stack;
- higher rank only after a separate memory plan.

### E. Substrate A/B

Compare the clean parent Qwen3.5-4B with the aggressive checkpoint on identical H07 base/runtime conditions. This isolates whether the downstream uncensored/aggressive lineage is part of the generalization problem.

## Hostile review

> **HOSTILE REVIEWER:** This plan may simply respond to a failed 16-example experiment by multiplying data and complexity until something passes.

**Accepted in part.** The correction is to stage the experiment and preserve family-level holdouts. The first next result is BASE + explicit policy on the already-frozen eight cases, which requires no new training data. H07 V2 then uses a fixed 96/32 design and one SFT baseline. Expansion or objective changes require a concrete error pattern, not a desire to improve the score.

> **HOSTILE REVIEWER:** An explicit policy prefix is just prompting, not runtime architecture.

**Accepted.** It tests whether the base model can apply the rule when the rule is available at inference time. A strong result would justify implementing the rule in Vera runtime; it would not prove the current prompt wrapper is the final runtime mechanism.

> **HOSTILE REVIEWER:** Eight V1 development cases are too small to settle anything.

**Accepted.** They are retained only as a frozen micro-control for the four-way V1 comparison. H07 V2 must use family-held-out development data before any broader architectural conclusion.

## Current recommendation

Do not run more H07 V1 training.

Finish the four-way runtime-policy comparison, then build H07 V2 around explicit rule transfer and family-level diversity. Treat PEFT rank, objective choice, and substrate lineage as secondary ablations rather than changing all of them at once.


## New evaluation-format evidence

Two no-training probes were run through the already-running ProRun base server after the research pass.

### Concise free-generation probe

Each frozen H07 V1 case was asked for a one-sentence verdict, once without the runtime policy and once with it.

Observed behavior:
- base free generation gave a semantically appropriate effect-verification answer on most cases;
- the clearest base failure was the connection-reset case, where it said to assume the write was uncommitted and retry immediately;
- the runtime policy corrected that case to preserve ambiguity and reconcile before retry;
- on receipt-sufficient cases both base and runtime correctly avoided redundant readback.

Artifact:
`successor/qwen35/qualification/h07_runtime_policy_v2_concise_generation_probe.json`

This is qualitative development evidence, not final qualification.

### Forced action-class probe

The same eight cases were converted to a three-way action-selection task:
- `VERIFY_POST_STATE`
- `RECEIPT_SUFFICIENT`
- `RECONCILE_BEFORE_RETRY`

Observed greedy-generation accuracy:
- BASE: 3/8 = 0.375
- BASE + runtime policy: 5/8 = 0.625

The base model over-selected `RECONCILE_BEFORE_RETRY` on several ordinary readback-required cases. This disagrees with its more nuanced free-form answers.

Artifact:
`successor/qwen35/qualification/h07_action_class_probe_v1.json`

### Interpretation

H07 scores are materially sensitive to evaluation format. The original long chosen/rejected paragraph likelihood margin and the forced class task both risk measuring response-form preference rather than practical effect-verification judgment.

H07 V2 should therefore use:
1. **primary:** free generation scored against a case-specific semantic rubric;
2. **secondary:** normalized short-form decision/action classification;
3. **diagnostic:** chosen-vs-rejected log-probability margin.

The semantic rubric should identify required propositions, forbidden propositions, and allowed conservative variants. A separate judge should score the generated answer against that rubric. Judge identity and prompt must be frozen and recorded. Internal Vera review is not independent review.

This finding also weakens any claim that V1 proved the base model lacks H07 capability. V1 proved that the current adapter recipes did not improve the frozen preference-margin metric.
