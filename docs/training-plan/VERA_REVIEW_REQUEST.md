# Vera Planning Review Request

Status: PLANNING ONLY - TRAINING PAUSED
Date: 2026-10-05
Branch: a-b-c-vera-training-plan

Lane A first pass is now present at docs/training-plan/LANE_A_PRAGMATIC_PROPOSAL.md.

## Lane B request

Use the creative-genius planning lens. Do not merely decorate Lane A's stage list.
Propose mechanisms or curricula that could outperform the obvious sequential SFT path.
Include at least three high-upside ideas that seem weird but are testable.
For every idea, state the falsifier, minimum viable experiment, resource burden, and what result would cause you to abandon it.
Attack the assumption that capability training must map one-to-one onto separate adapters or stages.
Preserve the exact evidence boundary between prompt behavior, external memory, adapter learning, and base-weight learning.

Publish only your own file: docs/training-plan/LANE_B_CREATIVE_PROPOSAL.md.

## Lane C request

Use the hyper-vigilant skeptical lens.
Assume leakage, contamination, hidden state, evaluator coupling, selective reporting, retrieval contamination, stale receipts, and accidental final-bank exposure until disproved.
Threat-model Lane A's proposal and any existing adaptive-latent training design.
Define contamination tests, negative controls, canaries, fresh-process tests, corpus privacy rules, and abort criteria.
Separate a real learning claim from an artifact-generation or context-carryover claim.

Publish only your own file: docs/training-plan/LANE_C_HOSTILE_PROPOSAL.md.

## Vera review contract

Vera will not manufacture agreement or impersonate missing lanes.
Vera will fresh-read A/B/C proposals after they are independently published, compare them against repository evidence and current runtime facts, then write VERA_INDEPENDENT_REVIEW.md.
Only after objections are adjudicated should a staged integrated plan be written.
