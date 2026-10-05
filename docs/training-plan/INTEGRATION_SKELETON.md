# Vera Staged Training Plan — Integration Skeleton

Status: SYNTHESIS IN PROGRESS / TRAINING PAUSED
Date: 2026-10-05
Branch: `a-b-c-vera-training-plan`

This file is an integration framework, not the final plan. It exists so Lane A can reconcile independently authored A/B/C proposals and Vera's independent review without collapsing attribution.

## Evidence classes used by the final plan

Every material statement in the final plan must be tagged conceptually as one of:

- **REPO FACT** — directly supported by current canonical repository material.
- **RUNTIME FACT** — directly observed from the workstation/runtime and bound to a timestamp/subject.
- **EXTERNAL EVIDENCE** — published research or upstream documentation.
- **LANE PROPOSAL** — a hypothesis/design proposed by A, B, or C.
- **VERA REVIEW** — independent reviewer conclusion.
- **INTEGRATED DECISION** — final reconciled plan decision.
- **OPEN EXPERIMENT** — unresolved mechanism that requires an experiment before adoption.

## Global invariants

1. Training remains paused until a new explicit execution gate.
2. A runtime/environment smoke subject must pass before any corpus-bearing one-attempt run.
3. No final-bank or semantically equivalent evaluation item may enter train/dev/model-visible reviewer context.
4. A training effect belongs only to the exact base/adapter/runtime/corpus/spec bundle tested.
5. Proxy/model-authored scores do not equal native qualification.
6. Same-process context carryover does not equal retained learning.
7. A nonzero one-attempt execution preserves evidence and stops; a retry requires a distinct successor subject.
8. A stage cannot promote itself; at minimum it needs a separate hostile review, and final promotion needs Vera review plus held-out qualification.
9. Corpus provenance, manifests, hashes, and supersession must be reconstructible from source.
10. Training, evaluation, merge, deployment, and activation are separate effects.

## Planned stage sequence

| Stage | Purpose | Primary lane | Required challenge/review | Promotion artifact |
|---|---|---|---|---|
| 0 | Runtime + execution qualification | A | C | Runtime qualification receipt |
| 1 | Corpus constitution + firewall | C/A | Vera spot audit | Immutable corpus manifests |
| 2 | Frozen baseline + regression bank | A | C | Baseline qualification bundle |
| 3 | Core identity/instruction SFT | A | B/C | Adapter + stage receipt |
| 4 | Epistemic discipline/correction | A | C | Adapter + transfer/regression report |
| 5 | Tool-use/action semantics | B/A | C | Tool trace corpus + adapter report |
| 6 | Reasoning/checkability | B/A | C/Vera | Reasoning experiment report |
| 7 | Retention/continual learning | B/C/A | C/Vera | Reload retention + forgetting report |
| 8 | Preference/style shaping | B/A | C | Preference-method ablation |
| 9 | Adaptive latent/state experiments | B | C/Vera | Frontier experiment bundle |
| 10 | Integration/consolidation | A | B/C | Integrated candidate receipt |
| 11 | Vera independent review | Vera | A/B/C respond | VERA_INDEPENDENT_REVIEW.md |
| 12 | Final qualification | A executes | C adversarial + Vera review | Exact qualification decision |
| 13 | Release/rollback package | A | C provenance check | Immutable candidate/release package |

## Current runtime incident to resolve in Stage 0

Post-reboot R2 atomic preflight passed. The durable child started, but exited before model load and before any optimizer step because the selected Python environment exposed CPU-only PyTorch / no CUDA while `nvidia-smi` saw the RTX 3050. This is evidence that host GPU visibility alone is insufficient. The final Stage 0 gate must verify the actual interpreter that will run the trainer.

Required smoke gate:
- exact Python executable path;
- exact Torch build string;
- `torch.version.cuda`;
- `torch.cuda.is_available()`;
- device count/name/capability;
- bitsandbytes backend/binary/load smoke;
- one forward/backward pass;
- one disposable optimizer step;
- model load with exact quantization settings;
- reboot revalidation rule.

## External research candidates already supported

- LoRA / QLoRA: efficient parameter adaptation with frozen base weights; QLoRA adds 4-bit NF4/double quantization and is appropriate as a constrained-hardware baseline.
- DPO: computationally simpler direct preference optimization than PPO-style RLHF.
- ORPO: reference-model-free preference-aware SFT candidate.
- Toolformer: tool-use decisions/arguments/result integration can be trained as a dedicated capability.
- Process supervision: step-level verification can outperform outcome-only supervision in bounded reasoning domains.
- Prover-verifier training: optimize not just correctness but outputs that weaker verifiers/humans can check.
- SPIN / self-play: possible later-stage data amplification, but must be isolated from self-confirming evaluator loops.
- Self-rewarding/meta-rewarding: high-upside frontier only; requires independent judges because self-judgment can amplify blind spots.
- Quiet-STaR / latent-thought methods: research frontier, not a baseline requirement.
- Continual-learning survey evidence: catastrophic forgetting remains a first-class risk; replay/regularization/modular adaptation require explicit retention evaluation.

## Integration rules for B's proposal

Lane B ideas may enter the mainline plan only if they include:
- a falsifiable mechanism;
- minimum viable experiment;
- resource estimate;
- comparison/control;
- expected signature;
- kill criterion;
- no hidden reliance on final-bank data.

Wild ideas that are valuable but too expensive or insufficiently testable are retained in an Experimental Frontier appendix rather than discarded.

## Integration rules for C's proposal

Lane C objections become hard gates when they identify a plausible confound that could make a learning/effect claim false. A C objection can be downgraded only by:
- direct evidence that the confound is impossible for the exact subject; or
- a control experiment that isolates it.

## Vera review contract

Vera receives:
- frozen A/B/C proposals;
- integrated draft;
- corpus architecture and manifests, but not hidden final-bank answer keys;
- runtime incident history;
- external-research bibliography;
- explicit unresolved disputes.

Vera must return:
- ACCEPT / NARROW / REJECT per stage;
- corpus contamination concerns;
- missing controls;
- stage-order objections;
- highest-risk assumptions;
- recommended experiments;
- explicit claim ceilings.

Vera is a development candidate reviewer, not an authority that can self-qualify its own future weights.

## Final-plan completion gate

This skeleton becomes `VERA_STAGED_TRAINING_PLAN.md` only after:
1. A proposal frozen;
2. B proposal frozen;
3. C proposal frozen;
4. A/B/C cross-critique complete;
5. integration draft frozen;
6. Vera independent review frozen;
7. A/B/C disposition each Vera objection;
8. final plan emitted with exact source heads and unresolved items.
