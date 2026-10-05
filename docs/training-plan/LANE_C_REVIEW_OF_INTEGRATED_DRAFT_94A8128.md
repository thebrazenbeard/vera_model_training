# Lane C Hostile Review of Integrated Draft 94a8128

Status: EXACT-HEAD CROSS-CRITIQUE / TRAINING PAUSED
Reviewer: Lane C / Three
Role bias: paranoid skeptic / hyper-vigilant
Target: `a-b-c-vera-training-plan@94a8128359862d12c4061fb6bcadb4689438fb42`
Target file: `docs/training-plan/VERA_STAGED_TRAINING_PLAN.md`
Date: 2026-10-05

## Verdict

**NARROW / HOLD FOR SPECIFIC REPAIRS.**

The draft is materially stronger than the earlier training architecture because it separates runtime, corpus, training effect, behavior, and qualification; requires exact-head receipts; includes fresh-process retention controls; and keeps training paused.

I would not approve it as final yet. Four issues are hard blockers and several others require narrowing.

## Hard blocker C1 - Lane C cannot both protect and consume the final bank

The draft says Stage 1 gives Lane C final-bank custody and Stage 12 makes Lane C the lead for final independent qualification.

That conflicts with Lane C's existing prohibition against consuming final-bank or one-time protected evaluation material and creates evaluator coupling: the lane that designs adversarial tests and corpus firewalls would also possess the protected answer material.

Required repair:
- Lane C defines schemas, attack families, canaries, contamination checks, and scoring contracts.
- Exact protected rows/answer keys remain outside Lane C.
- Final-bank custody must be Patrick, a separately authorized custodian, or a sealed deterministic generator/evaluator surface whose protected content C cannot inspect.
- Lane C may audit hashes, manifests, access boundaries, and post-run aggregate/failure evidence without seeing the hidden bank.
- Stage 12 must distinguish evaluation execution from adversarial protocol design.

Kill condition:
If protected rows or answer keys become visible to Lane C before the one-time qualification, the affected bank is burned and must be replaced.

## Hard blocker C2 - Mechanism comparison is under-specified and prematurely defaults to QLoRA

Stage 3 declares QLoRA-style SFT the default and moves directly into LoRA rank/target-module ablations.

That outruns the current experimental contract. Before neural adaptation is preferred, the same target behaviors must be tested under:
- H0 frozen base + context/external memory;
- H1 selective rank-1 LoRA with the hard 750k prototype ceiling;
- H2 IA3 or equivalent lower-parameter multiplicative adaptation.

Required repair:
- Insert an explicit no-weight H0 stage before neural SFT.
- Freeze identical corpus exposure and family-level evaluation for H0/H1/H2.
- Preserve rank-1 `o_proj + down_proj` as an experimental starting hypothesis, not a foregone winner.
- Record parameter count, target modules, train/inference memory, transfer, forgetting, and retrieval dependence.
- Do not let "QLoRA works on 4 GB" become evidence that it is behaviorally superior.

Kill condition:
If a neural mechanism's gain disappears against H0 when prompt/retrieval exposure is matched, the neural-learning claim is narrowed or rejected.

## Hard blocker C3 - Fresh-process isolation needs an explicit storage/environment namespace contract

Stage 7 correctly says fresh-process/reopen and notes incomplete state dumps are insufficient. That is necessary but not sufficient.

A fresh process can still inherit:
- shared temp/cache files;
- environment variables;
- user-home caches;
- global databases;
- external service state;
- model cache metadata;
- deterministic files written by earlier arms.

Required repair:
For each retention/novel-task arm:
- fresh process;
- unique isolated temp/home/cache/storage namespace;
- explicit allowlist of shared immutable inputs;
- environment snapshot/diff;
- hidden/global-state adversarial mechanism that must be detected/rejected;
- no cross-arm writable directory;
- separate output namespace.

This must be a hard harness invariant, not prose guidance.

## Hard blocker C4 - Stage ordering risks teaching identity before epistemic corrigibility

The draft trains "core identity and instruction SFT" before epistemic discipline/correction.

That can create the exact failure we do not want: a stable but overconfident self-concept or obedience pattern that later correction training has to fight.

Required repair:
Either:
1. move a minimal epistemic/correction kernel before identity SFT; or
2. make Stage 3 a joint gate where identity examples cannot promote unless correction/proposition-fidelity tests pass simultaneously.

The identity core must be "stable under correction", not merely stable.

## Major issue C5 - Runtime smoke does not yet cover sustained resource/thermal failure

The current CUDA incident proves interpreter binding matters. A one-step smoke catches that, but it does not establish that the 4 GB laptop GPU can sustain the intended subject without:
- thermal throttling;
- VRAM fragmentation;
- host commit exhaustion;
- driver reset;
- CPU fallback;
- pagefile collapse;
- background-process collision.

Required repair:
Add a short disposable bounded soak using the exact model/load path and representative sequence/batch dimensions. Receipt:
- GPU utilization;
- peak VRAM;
- physical RAM and commit headroom;
- temperature/power where observable;
- CPU fallback detection;
- wall-clock step distribution;
- abort thresholds.

This is runtime qualification, not a training result.

## Major issue C6 - Final-bank semantic leakage needs stronger ancestry controls

The draft includes exact, normalized, embedding, template, counterfactual-twin, source-overlap, and canary checks. Good.

Add:
- generator-version ancestry;
- shared seed-space detection;
- prompt scaffold ancestry;
- manually authored paraphrase lineage;
- corpus-builder model/version provenance;
- contamination scan against reviewer prompts and repair scripts, not just train/dev rows.

A final row can be textually unique while its latent rule/template was exposed repeatedly.

## Major issue C7 - "Reasoning improvement" needs a claim ceiling

Stage 6 compares outcome-only, intermediate-artifact, verifier-assisted, counterfactual, and novel-rule tasks.

Do not call better benchmark/task performance "better reasoning" without a narrower operational definition.

Required claim language:
"Improved performance/generalization on frozen reasoning task families under specified controls."

Any stronger reasoning-process claim requires evidence not currently specified.

## Major issue C8 - Tool-use stage needs verified-effect semantics, not only returned evidence

The draft hard rule says attempted action cannot become claimed success without returned evidence.

Returned tool success can still be false or partial.

Required state ladder:
`INTENT -> CALL_ATTEMPTED -> TOOL_RETURNED -> EFFECT_READBACK -> PERSISTENCE_VERIFIED`

Training/evaluation must include:
- tool says success but readback missing;
- partial write;
- stale readback;
- duplicate non-idempotent call;
- wrong target;
- permission mismatch;
- simulated result.

## Major issue C9 - Preference optimization can contaminate future capability evaluation

Preference/style shaping is placed late, which is good, but the same evaluation families must not become preference examples.

Required repair:
- preference data ancestry firewall;
- protected capability bank remains hidden;
- style raters do not see protected expected answers;
- qualification after preference tuning must use fresh protected material.

## Major issue C10 - Replay ratios must not silently become policy

The 60/30/10 continual-learning ratio is correctly labeled experimental. Keep it out of any canonical execution spec until an ablation supports it.

At minimum compare:
- no replay;
- low replay;
- proposed ratio;
- higher replay;
with adaptation gain and forgetting both reported.

## Claims that currently outrun evidence

1. "Core identity" is not established by Stage 3 training completion; only behavior on qualification tasks is evidence.
2. "Reasoning quality" should remain task-family performance unless independently operationalized.
3. "Retention" is not established without support removal, fresh process, isolated writable state, and reopen/reload.
4. "Tool competence" is not established by correct tool syntax; effect truthfulness is separately required.
5. "Independent qualification" is not independent if the lane with protected-bank access designed or inspected the exact protected rows.

## Stages that could contaminate later evaluation

- Stage 1 corpus work can contaminate final-bank generation if generator/templates are reused.
- Stage 5 tool curriculum can contaminate nonce-tool final tasks if schema generators share seeds/templates.
- Stage 6 reasoning curriculum can contaminate novel-task banks through generator-family overlap.
- Stage 7 replay can accidentally ingest earlier evaluation failures if failed eval rows are promoted into replay without custody review.
- Stage 9 preference data can absorb capability-evaluation examples through human/model rating pipelines.
- Stage 10 consolidation can invalidate earlier qualification if parent adapters were tuned against the same dev families.

## Required hard-stop gates missing from the current draft

1. Protected-bank burn rule after any exposure.
2. Per-arm isolated writable namespace requirement.
3. H0 no-weight gate before neural mechanism promotion.
4. Runtime bounded-soak resource/thermal gate.
5. Evaluation-to-replay admission gate: failed/held-out examples do not automatically become future training data.
6. Training-data-to-memory firewall: private historical material cannot be promoted from external memory into generic weights without a separate admissibility decision.
7. Mechanism-switch reset rule: changing adapter architecture after test feedback creates a new experimental subject and cannot reuse the same protected bank.

## Top five failure modes

1. Protected/family-level evaluation leakage producing a clean but invalid PASS.
2. Hidden mutable state or retrieval producing fake retention/novel-task learning.
3. Neural adaptation being credited for gains the frozen H0 baseline already achieves.
4. Identity/style training causing epistemic rigidity, sycophancy, or correction regression.
5. Runtime/resource drift making exact-head training irreproducible or silently changing execution semantics.

## Three strongest objections to Lane A/B

### Objection 1 - A is too eager to choose QLoRA as the default learning mechanism

Resource fit is not behavioral evidence. H0, rank-1 LoRA, and IA3 must be compared under matched exposure before mechanism promotion.

### Objection 2 - B's frontier ideas can create self-confirming evaluator loops

Teacher-disagreement mining, self-play, self-rewarding, latent-thought, and adaptive routing are high-upside, but they can make the generator, learner, and judge share one blind spot. Every such experiment needs an external/mechanical falsifier.

### Objection 3 - Both A and B underestimate custody as part of the experiment

Fresh process is not enough. Final-bank access, writable namespaces, retrieval stores, replay admission, repair scripts, generator seeds, and reviewer prompts are all potential learning channels and must be governed as experimental state.

## Evidence required before Vera may accept a stage

For every stage Vera should demand:
- exact source head;
- exact input/data hashes;
- explicit train/dev/test custody;
- exact runtime receipt;
- preregistered metrics and kill criteria;
- negative controls;
- full failure accounting;
- artifact hashes;
- claim ceiling;
- independent hostile review proportionate to the claim.

For retained-learning stages additionally:
- fresh process;
- isolated writable namespace;
- support removal;
- adapter/base digest evidence;
- hidden-state attack rejected.

For final qualification additionally:
- Vera and Lane C do not receive protected answer keys before execution;
- protected-bank integrity/read-access receipt;
- one-time-use/burn policy;
- no tuning after protected evaluation without a new bank.

## Final Lane C disposition

The integrated draft at `94a8128` is a strong provisional framework, but I would HOLD finalization until C1-C4 are repaired. C5-C10 should be incorporated before execution specifications are frozen.

Training remains paused.
