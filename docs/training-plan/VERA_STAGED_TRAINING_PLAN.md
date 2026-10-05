# Vera Staged Training Plan — A/B/C/Vera

Status: **PROVISIONAL INTEGRATED PLAN — TRAINING PAUSED — B/C FRESH SIGN-OFF PENDING**  
Date: 2026-10-05  
Planning branch: `a-b-c-vera-training-plan`

## 1. Purpose

Train Vera through a sequence of bounded, falsifiable capability increments that can be reconstructed from source, survived by independent review, and rolled back without ambiguity.

This plan explicitly rejects a single mixed "train everything" run. Capability growth, preference shaping, continual-learning experiments, and final qualification are different effects and must remain distinguishable.

The training program has four standing roles:

- **Lane A — pragmatic obsessive-compulsive:** exact subjects, runtime reproducibility, sequencing, receipts, integration, minimal wasted compute.
- **Lane B — creative genius / deliberately unconventional:** widen the hypothesis space, design high-upside experiments, challenge obvious training assumptions, build novel but falsifiable curricula.
- **Lane C — paranoid skeptic / hyper-vigilant:** contamination, hidden state, leakage, currentness, evaluator coupling, false learning, regression, recovery, and adversarial qualification.
- **Vera — independent reviewer:** review the frozen plan and corpus strategy independently. Vera does not author the controlling plan and cannot self-qualify its own training.

## 2. Current operational starting point

Training is paused by Patrick.

The prior R2 subject passed the post-reboot atomic host preflight with ample physical and commit headroom. A guarded launch then exited **before model load and before any optimizer step** because the selected Python runtime reported CUDA unavailable even though `nvidia-smi` saw the RTX 3050. The exact failure must be treated as a runtime-binding incident, not a model/corpus result.

No further training run is authorized by this planning document.

The current canonical planning branch also carries the existing Training Bus and adaptive-latent research. Those are evidence and design inputs; they do not themselves establish model-learning effects.

## 3. Governing evidence rules

Every stage must distinguish:

1. **source state** — exact Git head and files;
2. **runtime state** — exact executable environment and hardware;
3. **training effect** — actual parameter update or adapter change;
4. **behavioral effect** — measured change in outputs;
5. **qualification effect** — independent evidence that the exact candidate satisfies a defined target.

A PASS belongs only to the exact subject tested.

Proxy scores are not native qualification. Same-model generation/grading is supporting evidence only. Final-bank material is never training material.

## 4. Stage ownership model

Each stage has four responsibilities:

| Responsibility | Default owner |
| --- | --- |
| Builder / integrator | Lane A |
| Novel-method challenger | Lane B |
| Hostile reviewer / contamination auditor | Lane C |
| Independent plan/corpus reviewer | Vera |

For stages where B or C leads, A remains integration owner but does not overwrite the lead's proposal. Review evidence remains separately attributable.

## 5. Stage 0 — Runtime and execution qualification

**Lead:** Lane A  
**Hostile review:** Lane C  
**Alternative-runtime research:** Lane B  
**Vera role:** none beyond reviewing the eventual runtime assumptions in the integrated plan.

### Goal

Prove that the workstation can execute the exact training stack reproducibly before any valuable one-attempt subject or protected corpus is touched.

### Required work

Freeze and receipt:

- Python executable and version;
- Torch build and `torch.version.cuda`;
- `torch.cuda.is_available()`;
- GPU name, compute capability, VRAM and driver;
- CUDA runtime/driver compatibility;
- Transformers, TRL, PEFT, bitsandbytes versions;
- base-model repository/revision and local artifact hashes;
- tokenizer identity/hash;
- trainer source head/hash;
- quantization backend and actual device map;
- BF16/TF32 capability;
- system RAM and commit headroom;
- exact environment/package digest.

### Disposable smoke sequence

Before corpus-bearing training:

1. import stack;
2. load a tiny/disposable subject;
3. prove GPU tensor allocation;
4. perform one forward pass;
5. perform one backward pass;
6. perform exactly one optimizer step;
7. prove a trainable-parameter digest changed;
8. destroy the disposable output.

The smoke subject must not reuse a one-attempt production namespace.

### Lane C attacks

- `nvidia-smi` visible while Torch is CPU-only;
- stale virtual environment;
- PATH/PYTHONPATH selecting a different interpreter;
- package update after runtime receipt;
- GPU visible but bitsandbytes backend wrong;
- apparent optimizer success with no trainable weight change;
- hidden fallback to CPU;
- output/log namespace collision.

### Promotion gate

No Stage 1+ training until all runtime checks PASS on the exact environment that will run training.

## 6. Stage 1 — Corpus constitution and custody

**Lead:** Lane C  
**Materialization/integration:** Lane A  
**Coverage/augmentation research:** Lane B  
**Independent corpus review:** Vera

### Goal

Turn the current training material into an auditable corpus with immutable family membership and a real train/eval firewall.

### Capability families

At minimum:

- identity stability and role continuity;
- instruction following;
- correction uptake;
- epistemic provenance/currentness;
- uncertainty and conflict handling;
- privacy/boundary behavior;
- relationship/authority semantics;
- reciprocal identity continuity;
- tool-use/action semantics;
- reasoning and decomposition;
- memory/retention;
- novel-rule adaptation;
- negative-transfer resistance.

### Required corpus metadata

Every record gets:

- stable record ID;
- source family;
- provenance class;
- construction source and commit;
- semantic template/ancestry tag;
- privacy classification;
- intended capability;
- known confounds;
- training/eval custody;
- exact content hash.

### Train/eval firewall

Lane C controls final-bank custody. Training lanes may know schemas and families but not final answer keys or exact final rows.

Leakage defense must include:

- exact duplicate detection;
- normalized-text duplicate detection;
- near-duplicate/embedding search;
- template ancestry checks;
- counterfactual twin detection;
- source overlap checks;
- record-ID overlap = zero;
- canary strings/structures to detect accidental exposure;
- final-bank construction after training corpus freeze where practical.

### Vera review

Vera reviews corpus composition, blind spots, class imbalance, representativeness, duplicated ideology/style, and whether the corpus teaches the target behavior rather than merely the evaluator's preferred wording.

## 7. Stage 2 — Frozen baseline and qualification harness

**Lead:** Lane C for harness; Lane A for exact subject binding  
**Challenge design:** Lane B  
**Vera:** independent review of qualification dimensions

### Goal

Know what the base candidate already does before training and make regression measurable.

### Required controls

- untouched base/control candidate;
- deterministic or preregistered seeded generation;
- blinded candidate labels;
- paired baseline/candidate scoring;
- hidden structured grading fields;
- critical-failure flags;
- cold tasks;
- transfer tasks;
- adversarial variants;
- negative controls;
- no-acquisition/stateless controls;
- fresh-process and reopen tests for retention claims.

Development screening can use small banks. Promotion banks should be powered for the intended claim; the prior B review's `~80/family unless power analysis justifies otherwise` is a reasonable planning default, not an immutable constant.

### Metrics

Report at least:

- per-family accuracy/score;
- paired delta vs baseline;
- confidence interval;
- worst-family delta;
- critical-failure count;
- retained-baseline floor;
- contamination/leakage checks;
- grader disagreement/adjudication;
- no-acquisition baseline.

Aggregate score cannot hide a critical regression.

## 8. Stage 3 — Core identity and instruction SFT

**Lead:** Lane A  
**Creative challenger:** Lane B  
**Hostile review:** Lane C  
**Vera:** qualitative independent review after release candidate freeze

### Goal

Create the smallest adapter that reliably establishes Vera's core role, authority boundaries, correction uptake, stable identity behavior, and instruction contract.

### Default method

QLoRA-style parameter-efficient SFT is the baseline because the workstation is resource constrained. The current NF4 + double-quant + LoRA recipe is a hypothesis, not doctrine.

### Starting experiment family

Run small bounded ablations, changing one factor at a time:

- LoRA rank;
- target modules;
- learning rate;
- sequence length;
- replay ratio;
- completion-only vs full loss;
- data order;
- staged vs continuous schedule.

### Promotion gate

Must improve target-family behavior without materially worsening epistemic discipline, privacy/boundary behavior, or prior baseline anchors.

## 9. Stage 4 — Epistemic discipline and correction training

**Lead:** Lane A  
**Novel counterexample generation:** Lane B  
**Adversarial audit:** Lane C  
**Vera:** independent sample review

### Goal

Teach Vera to distinguish:

- fact;
- source-derived claim;
- inference;
- hypothesis;
- stale evidence;
- current evidence;
- correction;
- supersession;
- unresolved conflict;
- missing evidence.

### Curriculum

Use adversarial near-miss pairs:

- fluent-but-wrong vs cautious-correct;
- old/current source conflict;
- answerable vs unknowable;
- user assertion vs external evidence;
- remembered context vs current repository/runtime evidence;
- explicit correction after confident prior answer.

### Regression risk

Overtraining can produce excessive hedging/refusal. Require a usefulness floor on ordinary answerable tasks.

## 10. Stage 5 — Tool-use and action semantics

**Lead:** Lane B  
**Execution integration:** Lane A  
**Security/failure audit:** Lane C  
**Vera:** review tool-behavior corpus and error cases

### Goal

Train *when* to call tools, *which* tool, argument construction, failure interpretation, and truthful result integration.

### Curriculum

Use:

- tool-contract examples;
- renamed/nonce tool surfaces;
- missing-tool cases;
- malformed-result cases;
- permission failures;
- stale-result cases;
- tool not needed;
- competing tools;
- "action failed after partial progress" cases.

Toolformer-style self-supervised tool-call generation is a research inspiration, not an automatic production method.

### Hard rule

The model never converts an attempted action into a claimed successful action without returned evidence.

## 11. Stage 6 — Reasoning and generalization experiments

**Lead:** Lane B  
**Baseline/integration:** Lane A  
**False-novelty audit:** Lane C  
**Vera:** independent review of task families

### Goal

Improve reasoning/generalization without teaching benchmark templates or requiring private chain-of-thought reproduction.

### Baseline experiment

Compare:

1. outcome-only SFT;
2. concise checkable intermediate-artifact supervision;
3. verifier-assisted candidate selection;
4. curriculum with counterfactual twins;
5. support-removal novel-rule tasks.

### Lane B high-upside experimental track

Test, cheaply and separately:

- **Counterfactual twins:** identical surface structure, opposite latent rule;
- **Perturbation maze:** rename entities/tools/labels every episode to kill lexical shortcuts;
- **Difficulty routing:** train on examples near the current failure frontier rather than uniform sampling;
- **Teacher disagreement mining:** prioritize examples where independent graders disagree;
- **latent-thought/Quiet-STaR-like proxy experiments:** only after cheap controls prove value;
- **micro-adapter laboratory:** short capability-specific adapters used as experiments before any consolidation.

Each idea requires a falsifier, a minimal viable experiment, and a kill criterion.

## 12. Stage 7 — Memory, retention and continual-learning qualification

**Lead:** Lane C for protocol; Lane A for training integration; Lane B for mechanism alternatives  
**Vera:** review the claim language and retained-behavior samples

### Goal

Separate true retained learning from:

- in-context adaptation;
- prompt support;
- hidden mutable global state;
- filesystem/retrieval state;
- reused KV/cache/session state;
- evaluator knowledge.

### Required arms

- no-acquisition control;
- clean acquisition;
- shuffled/incorrect acquisition;
- irrelevant-memory control;
- familiar-lookalike control;
- fresh-process retest;
- reopened-session retest;
- support-removed retest.

Every arm must start from independently verifiable fresh state. Comparing hashes of an incomplete state dump is insufficient.

### Continual-learning method

Start with replay-balanced incremental training. A practical first hypothesis:

- 60% current capability material;
- 30% replay anchors from prior qualified stages;
- 10% adversarial/negative-transfer examples.

Those ratios are experimental; B should challenge them and C should demand ablations.

### Promotion gate

New capability gain plus retained prior-family floor. If gain disappears after support removal/reopen, label it in-context adaptation, not learning.

## 13. Stage 8 — Adaptive latent / selective-retention frontier

**Lead:** Lane B  
**Integration:** Lane A  
**Hostile evidence audit:** Lane C  
**Vera:** independent usefulness review

### Goal

Investigate the existing adaptive-latent research without making it a prerequisite for the baseline training program.

### Experimental sequence

1. full-context control;
2. structured explicit-state bottleneck;
3. compact learned representation;
4. progressive budget pressure;
5. resolution-fault/rehydration training;
6. specialist handoff experiments.

### Kill conditions

Reject or narrow the mechanism if it:

- hallucinates exact details not present in compressed state;
- loses corrections/currentness;
- creates unrecoverable provenance;
- only works with evaluator-visible metadata;
- increases downstream error enough to erase the memory/compression benefit.

## 14. Stage 9 — Preference/style shaping

**Lead:** Lane A with Lane B method comparison  
**Hostile review:** Lane C  
**Vera:** independent preference review

### Goal

Shape tone, style and preference *after* competence exists.

### Methods to compare

- SFT-only reference;
- DPO-style preference tuning;
- ORPO/reference-free preference tuning;
- rating-gap variants only if the ratings are meaningful enough to justify them.

### Preference data contract

Do not use a single vague "better" label. Record dimensions such as:

- correctness;
- relevance;
- epistemic honesty;
- concision;
- warmth/directness;
- tool honesty;
- correction behavior;
- authority boundaries.

### Promotion gate

Preference gains cannot purchase regressions in factuality, tool honesty, privacy, correction uptake, or worst-family retention.

## 15. Stage 10 — Consolidation and collision testing

**Lead:** Lane A  
**Novel integration alternatives:** Lane B  
**Collision/red-team owner:** Lane C  
**Vera:** review collision failures

### Goal

Create a single candidate without erasing evidence about where each capability came from.

### Default approach

Prefer sequential continued training with replay on a single lineage over opaque adapter merging. If adapter fusion/merging is tested, it is a separate experiment with exact parent digests and its own qualification.

### Collision matrix

Explicitly test:

- stable identity vs correction uptake;
- confidence vs uncertainty;
- tool initiative vs fabrication;
- memory vs stale-state persistence;
- reasoning depth vs verbosity;
- directness vs empathy;
- privacy vs helpfulness;
- creativity vs source fidelity.

## 16. Stage 11 — Vera independent plan/corpus review

**Lead:** Vera as independent reviewer  
**Custodian:** Lane C  
**Response owner:** Lane A  
**Alternative remediation:** Lane B

Vera receives:

- frozen integrated training plan;
- corpus manifests/summaries;
- known failures;
- stage receipts;
- evaluation schemas;
- no hidden final-bank answer keys.

Vera's role is to find:

- missing capability families;
- overrepresented style/ideology;
- contradictory objectives;
- training examples likely to reward superficial wording;
- places where the plan confuses external memory with learned state;
- likely negative transfer;
- unrealistic resource assumptions;
- stages that cannot support the claim they intend to make.

Vera cannot certify itself. Its review is an independent model opinion that must be reconciled with deterministic evidence and Lane C's hostile review.

## 17. Stage 12 — Final independent qualification

**Lead:** Lane C  
**Execution/integration:** Lane A  
**Novel adversarial set suggestions:** Lane B  
**Independent qualitative reviewer:** Vera

Qualification uses sealed material never exposed to training.

Required strata:

- cold tasks;
- transfer tasks;
- counterfactual twins;
- adversarial prompts;
- negative controls;
- support-removed retention;
- fresh-process/reopen persistence;
- tool-failure cases;
- currentness/provenance conflicts;
- critical privacy/authority cases;
- regression replay.

Report PASS / CONDITIONAL PASS / FAIL for the exact adapter/runtime/evaluator tuple.

## 18. Stage 13 — Release and rollback package

**Lead:** Lane A  
**Audit:** Lane C  
**Creative documentation/diagnostics:** Lane B  
**Vera:** no authority effect

A release package contains:

- exact base revision;
- adapter hash;
- runtime receipt;
- corpus manifest hashes;
- training spec;
- training receipt;
- qualification receipt;
- known failures;
- claim ceiling;
- previous qualified release for rollback.

Training Bus admission remains separate from native qualification.

## 19. Branch and handoff protocol

For every stage:

1. one exact source head;
2. one owner;
3. immutable protocol/spec;
4. preflight;
5. execution;
6. durable logs/receipt;
7. owner self-check;
8. independent hostile review;
9. remediation on a new head if needed;
10. promotion only after exact-head release.

Never repair reviewed evidence in place.

## 20. Compute policy

Given the RTX 3050 Laptop GPU with 4 GB VRAM:

- use QLoRA/PEFT as the default;
- keep sequence lengths and batch sizes conservative;
- prefer cheap CPU/source/harness tests before GPU;
- do not use the GPU to discover obvious schema/runtime bugs;
- stage larger-cloud experiments only if local evidence gives a concrete reason and separate cost authority exists;
- preserve no-paid-compute as the default.

## 21. Research grounding

Methods informing the plan include:

- Dettmers et al., **QLoRA: Efficient Finetuning of Quantized LLMs**, arXiv:2305.14314.
- Rafailov et al., **Direct Preference Optimization**, arXiv:2305.18290.
- Hong et al., **ORPO: Monolithic Preference Optimization without Reference Model**, arXiv:2403.07691.
- Schick et al., **Toolformer**, arXiv:2302.04761.
- Zelikman et al., **Quiet-STaR**, arXiv:2403.09629.
- Wu et al., **Continual Learning for Large Language Models: A Survey**, arXiv:2402.01364.

These papers justify experiments, not guaranteed outcomes on Vera.

## 22. Immediate next actions once Patrick unpauses training

1. Repair/select a CUDA-enabled Torch environment and bind it immutably.
2. Run disposable Stage-0 forward/backward/optimizer smoke.
3. Rebuild R2 only as a **new successor subject** if Patrick authorizes it; never retry the exhausted/failed subject in place.
4. Freeze Stage-1 corpus manifest and custody.
5. Freeze Stage-2 baseline/qualification harness.
6. Start Stage-3 core behavior training with bounded ablations.

## 23. Current unresolved planning dependencies

Fresh Lane B and Lane C role-specific proposal files were requested on the planning branch. Lane B has already participated by committing the Vera review contract; Lane C's fresh planning proposal has not yet been observed in this planning turn.

Until both fresh proposal files are present and reviewed, this integrated file is **provisional**. Historical B/C exact-head reviews were used as real evidence inputs, but they are not mislabeled as fresh planning sign-off.
