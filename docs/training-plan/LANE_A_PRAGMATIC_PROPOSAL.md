# Lane A Pragmatic Training Proposal

Status: INDEPENDENT FIRST PASS
Role bias: pragmatic obsessive-compulsive
Date: 2026-10-05

## Thesis

Vera should be trained as a sequence of **small, separately qualified capability increments**, not as a monolithic personality/capability mixture. Every stage begins from an exact immutable input adapter/base, uses a corpus slice with explicit provenance and replay anchors, emits a durable receipt, and is promoted only after cold held-out, transfer, retention, and regression checks. Runtime reproducibility is Stage 0, not plumbing outside the training plan.

## Non-negotiable ordering

1. Runtime reproducibility and deterministic execution envelope.
2. Corpus census, deduplication, provenance and train/eval firewall.
3. Baseline/frozen control and regression bank.
4. Core instruction/identity SFT.
5. Epistemic discipline and correction uptake.
6. Tool-use/action semantics.
7. Reasoning/process quality.
8. Memory/retention and continual-learning behavior.
9. Preference/style alignment.
10. Integrated multi-capability consolidation.
11. Independent final qualification and rollback package.

## Stage A0 — Runtime qualification

Owner: A. Review: C. Creative alternatives: B.

Freeze Python, Torch/CUDA, transformers, TRL, PEFT, bitsandbytes, driver, GPU identity, model revision, tokenizer, and exact trainer source. Require both `nvidia-smi` visibility and `torch.cuda.is_available()==True` plus a one-batch forward/backward smoke test before any one-attempt training subject is created. A reboot or environment mutation invalidates runtime qualification until re-read.

Gate: exact runtime receipt + 1 optimizer-step disposable smoke subject. No corpus-bearing experiment is allowed to diagnose environment problems.

## Stage A1 — Corpus constitution

Owner: C for audit, A for materialization, B for coverage ideas.

Partition material into capability families: identity/voice, instruction following, epistemic correction, provenance/currentness, tool/action contracts, reasoning, memory/retention, safety/boundaries, relationship/authority semantics, negative-transfer resistance. Hash each record, detect near-duplicates/templates, record source/provenance, and create immutable train/dev/held-out/final-bank membership before training.

Hard rule: final-bank examples and semantically equivalent templates never enter training or model-visible reviewer prompts.

## Stage A2 — Baseline and regression control

Freeze the base model and an untouched adapter-control path. Record cold behavior on every qualification family before training. Establish replay/regression anchors representing already-good capabilities and known prior failures.

Promotion metric is not aggregate score alone. Require per-family deltas, worst-family delta, retained-baseline floor, and explicit critical-failure count.

## Stage A3 — Core identity + instruction SFT

Use QLoRA as the default resource-efficient mechanism, but treat the current 4-bit/NF4/double-quant recipe as an empirical configuration rather than doctrine. Train only the minimum identity/instruction core needed to establish stable role, authority boundaries, correction uptake, and response contract.

Do not mix tool execution, deep reasoning traces, or preference-style pairs into this stage unless ablation proves no interference.

## Stage A4 — Epistemic discipline

Train explicit distinctions among fact, source-derived claim, inference, uncertainty, stale/current evidence, correction, supersession, and unresolved conflict. Include adversarial near-miss examples where confident fluency is wrong.

Require transfer to unseen domains and a regression test that the model does not become reflexively hedged or refusal-prone.

## Stage A5 — Tool-use competence

Train decision-to-call, argument construction, result integration, failure interpretation, and no-tool boundaries using synthetic and real tool contracts. Tool outputs remain external evidence; the model must not fabricate successful actions.

First qualify offline structured tool traces. Only then qualify live tool execution in a sandbox.

## Stage A6 — Reasoning quality

Start with answerable tasks where process can be mechanically or independently checked. Compare outcome-only SFT against process-labeled or verifier-assisted variants. Do not train hidden/private chain-of-thought reproduction as a product requirement; train concise checkable intermediate artifacts where useful.

Use cheap ablations before adopting expensive latent-reasoning schemes.

## Stage A7 — Retention / continual-learning stage

Introduce new-domain/capability increments with replay anchors from earlier stages. Measure adaptation gain and forgetting separately. Require a fresh-process and reopen/reload test so context persistence cannot masquerade as parameter retention.

Prefer small replay-balanced increments over large mixed retrains unless B can demonstrate a cheaper superior mechanism.

## Stage A8 — Preference and style shaping

Only after capability competence is stable. Compare SFT-only, DPO-like, and reference-free preference objectives on a small controlled subset. Preference data must encode explicit dimensions rather than a single vague 'better' label.

Reject any method that improves style while degrading factuality, tool honesty, correction uptake, or worst-family retention.

## Stage A9 — Integration/consolidation

Integrate only adapters/stages with independently released evidence. Run interaction tests for capability collisions: identity vs correction, confidence vs uncertainty, tool-use vs hallucination, reasoning vs verbosity, memory vs stale-state persistence.

If combining adapters or continuing training, require exact parent digest and regression replay. No silent model-soup or merge.

## Stage A10 — Vera independent review

Vera receives the frozen integrated plan, corpus manifest summaries, stage receipts, known failures, and qualification criteria, but not hidden final-bank answer keys. Vera reviews plan coherence and corpus risks; Vera's self-evaluation is advisory unless independently checked.

## Stage A11 — Final qualification

Use sealed cold tasks, transfer tasks, adversarial variants, negative controls, and retention checks. Report family-level scores and failure exemplars. Qualification belongs to an exact adapter/runtime/evaluator bundle and cannot transfer automatically to descendants.

## Pragmatic stop rules

- Environment mismatch -> STOP before training.
- Any corpus/final-bank contamination -> rebuild subject.
- No measurable parameter change -> stage invalid.
- Gain explained by context/demo leakage -> not learning.
- Critical regression in prior stage -> reject or remediate.
- Non-reconstructible receipt -> evidence HOLD.
- Retry after a one-attempt failure requires a new explicit successor subject.
- Aggregate improvement with catastrophic worst-family loss -> reject.

## External research candidates to test, not assume

- QLoRA-style 4-bit LoRA remains the baseline for constrained hardware.
- Replay buffers are a practical candidate for reducing catastrophic forgetting.
- DPO/ORPO-style preference methods belong late, after SFT competence, because preference optimization can trade off other behaviors.
- Toolformer-style self-supervised API-call data suggests tool-use can be trained as a distinct capability.
- Process supervision and verifier-assisted reasoning deserve bounded experiments before broad adoption.
- Quiet-STaR/latent-thought approaches are research-frontier candidates, not baseline requirements on a 4 GB GPU.
