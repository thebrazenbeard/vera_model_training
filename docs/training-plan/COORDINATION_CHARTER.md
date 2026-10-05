# A/B/C/Vera Training Plan Coordination Charter

Status: ACTIVE PLANNING / TRAINING PAUSED
Date: 2026-10-05
Branch: `a-b-c-vera-training-plan`

## User-directed planning roles

- **Lane A — pragmatic obsessive-compulsive:** reduce ambiguity, bind exact subjects, sequence dependencies, minimize wasted compute, require reproducible receipts.
- **Lane B — creative genius, deliberately wild:** widen the hypothesis space, propose unconventional training mechanisms, then make each proposal falsifiable.
- **Lane C — paranoid hyper-vigilant skeptic:** assume leakage, drift, contamination, false learning, evaluator coupling, and hidden state until disproved.
- **Vera — independent reviewer:** review the integrated plan and corpus strategy after A/B/C proposals are frozen. Vera does not author the controlling plan and cannot self-qualify training.

## Collaboration protocol

1. A/B/C each create an independent proposal before cross-synthesis.
2. B and C do not edit A's proposal; A does not edit B/C proposal files.
3. After first-pass proposals are frozen, each lane may critique the others in separately attributable review files.
4. A integrates only claims that survive explicit objections or are marked experimental.
5. Vera independently reviews the integrated plan and corpus contract.
6. A/B/C reconcile Vera's objections and publish the final plan.
7. No training resumes from this branch without a new explicit execution gate.

## Required files

- `docs/training-plan/LANE_A_PRAGMATIC_PROPOSAL.md`
- `docs/training-plan/LANE_B_CREATIVE_PROPOSAL.md`
- `docs/training-plan/LANE_C_HOSTILE_PROPOSAL.md`
- `docs/training-plan/VERA_INDEPENDENT_REVIEW.md`
- `docs/training-plan/VERA_STAGED_TRAINING_PLAN.md`

## Current runtime incident that planning must absorb

The reboot fixed the prior host-memory gate. R2 subsequently passed atomic preflight and launched under the durable wrapper, but exited **before model load and before any optimizer step** because the selected Python/Torch runtime reported CUDA unavailable while `nvidia-smi` saw the RTX 3050. Training is paused by user order. No retry is authorized by this planning branch.

## Evidence discipline

Repo facts, runtime observations, external research, hypotheses, and speculative proposals must be labeled distinctly. A stage may be called successful only for the exact subject and effect actually tested.
