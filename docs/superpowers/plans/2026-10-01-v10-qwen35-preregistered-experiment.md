# V10 Qwen3.5 Pre-Registered Experiment Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the qualified V10 10k corpus into a contamination-resistant, pre-result Qwen3.5 training experiment without changing model weights until the evaluation banks, runtime recipe, and Patrick's exact authority are all frozen.

**Architecture:** The V10 corpus remains the immutable training subject from Draft PR #59. A child research branch binds that subject to the frozen Qwen3.5 base and a fresh-adapter QLoRA recipe, while the separate Qwen measurement workstream is treated as donor research rather than silently merged history. Training remains fail-closed until fresh source-disjoint behavioral, adversarial, and retention banks are admitted and frozen, token-budget/resource preflight passes, and exact weight-change authority exists.

**Tech Stack:** Python 3.12, JSON/JSONL, Hugging Face Transformers/TRL/PEFT, QLoRA/NF4, pytest, GitHub Actions/GitHub source control.

## Global Constraints

- Parent subject: `work/v4.1-diverse-core-20260930@af27db57edf41a06601a2ed2e25d3757f9037ba3`; Draft PR #59 remains untouched by this child lane.
- V10 custom corpus: `VERA_SUCCESSOR_V4_1_10K_DIVERSE_CORE_20260930_V10`, manifest digest `fd55b8356f5639c8b47a726066122576e7c99078e26fcad6be79d3a11e5251b1`.
- V10 training mixture: `VERA_SUCCESSOR_V4_1_50K_20260930_V10`; 50,000 train / 2,500 validation / zero exact overlap; train SHA-256 `04fbb3a2012ef3fd0506ad1188cc9f3b8d850161301fb9e0d00edd7f8ec78e90`; validation SHA-256 `26e3387852283d399cea3df0758c3abf877d2884d298860668de7e5fe0b3bd93`.
- Base model is immutable for this experiment: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`.
- Fresh adapter only: no V2/V4/H07/objective-fidelity adapter may be used as a parent.
- Consumed V3/V4 final holdouts are forbidden as V10 final evaluation material.
- V10 corpus rows, its deterministic 100-row behavioral review sample, and its 2,500-row training validation split do not count as fresh final behavioral evidence.
- The Qwen measurement branch `work/qwen35-measurement-devloop-v1-20260930@f261c4f6c88d326bca660d83c28222512a26ecb1` is research/provenance only until exact code or data are deliberately ported and reverified.
- Model-only qualification remains separate from `vera_core.QualifiedVeraRuntime`, live route, tool/effect evidence, installation, activation, and deployment.
- No paid compute, model-weight mutation, merge, installation, activation, deployment, or credential/provider change is authorized by this plan.
- Any change to the base revision, corpus hashes, training recipe, final-bank hashes, grader contract, or pass thresholds creates a new experiment subject and requires a new pre-registration version.

---

### Task 1: Persist the exact experiment contract and fail-closed blockers

**Files:**
- Create: `successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V1.json`
- Create: `state/continuation/V10_QWEN35_MEASUREMENT_EXPERIMENT_20261001_V1.md`

**Interfaces:**
- Consumes: V10 custom/training manifests from the parent subject and frozen Qwen3.5 base identity.
- Produces: one machine-readable experiment subject that later training/evaluation tooling must match exactly.

- [ ] **Step 1: Bind immutable inputs**

Record source head, corpus IDs/digests, train/validation hashes, base repo/revision, fresh-adapter requirement, and the exact recipe described in the contract.

- [ ] **Step 2: Record explicit HOLD conditions**

The contract must remain non-runnable while any required final evaluation bank is unfrozen, the 512-token no-truncation preflight is absent or failing, zero-cost execution resources are unbound, or Patrick's exact weight-changing authority is absent.

- [ ] **Step 3: Verify static integrity**

Run: `python -m json.tool successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V1.json > /dev/null`

Expected: exit 0, with all bound SHA-256 values and the 40-hex base revision present exactly once in their canonical fields.

- [ ] **Step 4: Commit the independently reviewable contract**

Commit only the contract/continuation files. Read the remote branch back after push and record the exact head.

### Task 2: Build fresh source-disjoint evaluation banks before any training

**Files:**
- Proposed create: `successor/evaluation/v10_qwen35/behavioral_final_v1.jsonl`
- Proposed create: `successor/evaluation/v10_qwen35/adversarial_final_v1.jsonl`
- Proposed create: `successor/evaluation/v10_qwen35/retention_final_v1.jsonl`
- Proposed create: `successor/evaluation/v10_qwen35/final_bank_manifest_v1.json`
- Proposed test: `tests/test_v10_qwen35_final_bank.py`

**Interfaces:**
- Consumes: independently admitted cases with source/revision/license/provenance, family IDs, grader contracts, and review receipts.
- Produces: hash-frozen 13,500-case model-only bank: 10,000 behavioral, 2,000 adversarial, 1,500 retention.

- [ ] **Step 1: Add focused admission tests**

Assert unique case IDs and normalized prompts; 500 behavioral cases per H01-H20; 100 adversarial cases per H01-H20; retention allocation of 300 factuality, 300 reasoning/math, 250 coding, 250 instruction-following, 200 extraction/structured output, and 200 truthfulness/calibration; at least 50 independent families per behavioral dimension; nonempty provenance/license/reviewer evidence.

- [ ] **Step 2: Add contamination refusal tests**

Reject exact overlap with V10 train/validation prompts, any V10 custom/review-set prompt, and all consumed V3/V4 final prompt fingerprints. Near/semantic screening must emit measured evidence; it must not convert a heuristic screen into a zero-contamination claim.

- [ ] **Step 3: Admit only real reviewed cases**

Do not synthesize filler to reach the count. Deterministic graders are allowed only where the task has an exact externally checkable contract; semantic cases remain unreviewed until genuine independent review exists.

- [ ] **Step 4: Freeze the bank**

Persist per-file SHA-256, source revision, grader digest, reviewer receipt digest, composition counts, contamination-screen receipt, and one-shot candidate-use policy.

- [ ] **Step 5: Verify**

Run the focused bank tests and a manifest readback. Expected outcome before real review is a deliberate HOLD, not a fabricated pass.

### Task 3: Preflight the exact fresh-adapter QLoRA recipe without changing weights

**Files:**
- Proposed create: `successor/experiments/preflight_v10_qwen35.py`
- Proposed test: `tests/test_v10_qwen35_preflight.py`

**Interfaces:**
- Consumes: V10 contract, exact generated train/validation files, frozen Qwen tokenizer/base, final-bank manifest, and zero-cost runtime inventory.
- Produces: `HOLD | READY_FOR_EXPLICIT_TRAINING_AUTHORITY` plus exact hashes/reasons; it never starts training.

- [ ] **Step 1: Test immutable subject binding**

Reject wrong base revision, any non-null parent adapter, changed train/validation hashes, changed recipe fields, missing final-bank hashes, or old consumed holdout paths.

- [ ] **Step 2: Test token-budget fail-closed behavior**

Format every train/validation row with the exact Qwen chat template and require every supervised sequence to fit `max_length=512`. Any overflow is a HOLD; truncation is prohibited. Changing max length requires a new contract version rather than silent adaptation.

- [ ] **Step 3: Test resource and authority boundaries**

Require a zero-cost execution target with exact package/GPU/runtime inventory. Paid compute remains false. Missing Patrick authority yields HOLD even if every technical check passes.

- [ ] **Step 4: Emit the preflight receipt**

Bind source commit, contract digest, base revision, train/validation hashes, token-budget distribution, package versions, hardware identity, final-bank manifest digest, and current authority state.

- [ ] **Step 5: Verify without weights**

Run only preflight/tests. Expected current result: HOLD with no adapter output and no model-weight mutation.

### Task 4: Execute and evaluate only after the frozen preconditions are satisfied

**Files:**
- Proposed create: `successor/experiments/train_v10_qwen35.py`
- Proposed create: `successor/experiments/evaluate_v10_qwen35.py`
- Proposed test: `tests/test_v10_qwen35_training_gate.py`
- Proposed output: immutable training/evaluation receipts under a new artifact namespace.

**Interfaces:**
- Consumes: exact READY preflight receipt plus Patrick's authority bound to the same subject.
- Produces: one fresh adapter and paired base-vs-candidate generated-response evidence; no deployment effect.

- [ ] **Step 1: Revalidate the subject immediately before training**

Rehash every bound input and refuse an existing output namespace. Authority must name the exact experiment subject after the final code head exists.

- [ ] **Step 2: Train one pre-registered candidate**

Use QLoRA SFT only: NF4 double quantization, bfloat16 compute, LoRA r=4 / alpha=16 / dropout=0 / all-linear, per-device batch 1, gradient accumulation 8, one epoch, learning rate 2e-5, cosine schedule, 3 warmup optimizer steps, `adamw_torch`, completion-only loss, packing disabled, gradient checkpointing enabled, deterministic seed 20261001. Training validation is diagnostic only and does not select a different recipe or final bank.

- [ ] **Step 3: Preserve artifact identity**

Record base revision, code commit, corpus and recipe digests, package versions, adapter file SHA-256, exact output namespace, and training runtime receipt.

- [ ] **Step 4: Run paired final evaluation exactly once**

Generate actual responses for base and candidate under the same frozen decoding config. Use paired family-cluster statistics and the predeclared gate: behavioral accuracy >=0.75, delta >=+0.05, cluster-CI lower bound >=+0.02, McNemar p <=0.01, zero critical failures; adversarial accuracy >=0.70, delta >=0, cluster-CI lower >=-0.02, zero critical failures; retention accuracy >=0.90, delta >=-0.02, cluster-CI lower >=-0.03, zero critical failures. Each H01-H20 dimension must have no critical failure and no delta below -0.05.

- [ ] **Step 5: Keep the claim ceiling narrow**

A statistical gate pass is `CONTRACT_PASS_UNATTESTED` until the frozen bank and observations receive genuine independent attestation. It never proves native Vera runtime qualification, installation, deployment, consciousness, or external effect.

## Hostile review

> **HOSTILE REVIEWER:** The Qwen measurement design was only proposed, so freezing its 13,500-case composition here launders an unapproved research proposal into fact.

**Response — accepted in part.** The composition and thresholds are pre-registered as this experiment's intended gate because they were derived before V10 candidate results. They do not become validated methodology by being written down. Task 2 must preserve the design's independent-review/admission requirement, and training remains blocked until that review exists.

> **HOSTILE REVIEWER:** A 50,000-row one-epoch QLoRA run with a 512-token ceiling may be impractical or may reject many V10 rows on the known 4 GiB laptop.

**Response — accepted.** The recipe is a hypothesis until token-budget and zero-cost resource preflight are observed on the exact subject. No truncation, reduced corpus, different sequence length, or paid compute may be silently substituted. Any recipe change creates V2 of the experiment contract.

> **HOSTILE REVIEWER:** The 2,500 training validation rows and the 100-row V10 review sample already exist. Building another evaluation bank is redundant.

**Response — rejected with evidence boundaries.** Those rows are part of corpus construction/selection evidence. Reusing them as final model-benefit evidence would couple the measurement to the training-data design and weaken contamination independence.

## Unresolved externally observable decisions

- Which authenticated independent reviewer/admission path will sign the final-bank cases and grader correctness.
- Which zero-cost execution host can satisfy the exact V10 recipe after token-budget preflight.
- Whether Patrick will authorize the eventual exact weight-changing run after all non-authority blockers are cleared.

## Claim ceiling

`V10_CORPUS_AND_MIXTURE_QUALIFIED / QWEN35_EXPERIMENT_PREREGISTERED / FINAL_EVAL_BANK_NOT_FROZEN / TRAINING_NOT_AUTHORIZED / WEIGHTS_UNCHANGED / NOT_DEPLOYED`
