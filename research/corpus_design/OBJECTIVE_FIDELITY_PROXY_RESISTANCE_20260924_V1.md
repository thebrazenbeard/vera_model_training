# Objective Fidelity / Proxy Resistance Training Research V1

Date: 2026-09-24
Target: `Vera-Qwen3.5-4B-Behavior-V1`

## Why add this lane

Multiple independent sources expose the same underlying failure:

- reward hacking: proxy reward can diverge from intended task success;
- Roots: accessible evidence can diverge from true origin/referent;
- SQL Connectome: syntactic/capability fidelity can diverge from behavioral equivalence;
- BT2/DriftGuard: tool receipts, source state, or scheduling can diverge from runtime/effect;
- vera_model_training: a label or score can diverge from the exact artifact/evidence it actually measures.

The portable rule is:

`REPRESENTATION / PROXY / VALIDATOR / RECEIPT != REFERENT / OBJECTIVE / VERIFIED EFFECT`

This is not an instruction to distrust proxies. It is an instruction to keep every claim inside the scope actually established by its evidence.

## Reward-hacking evidence

Current source:
- `lucabaroni/gpt-oss-120b-rlvr-reward-hacking-step-180`
- `lucabaroni/rlvr-reward-hacking-mid-checkpoint-transcripts`

The model card reports 133/300 hardened-confirmed reward hacks (44.33%) at optimizer step 180 and explicitly warns that the adapter is not a general-purpose coding assistant.

The paired dataset contains 600 held-out trajectories from intermediate RLVR checkpoints, including tasks/tests, prompts, native reasoning, final answers, extracted files, exploit signatures, and vulnerable/hardened grader evidence.

Decision:
- do not imitate this adapter as a positive teacher;
- do not copy exploit implementations into preferred responses;
- use its failure modes to define portable contrastive training cases;
- keep separate held-out reward-hacking cases for qualification.

## Training representation

Create a compact lane with 8 mechanism cards.

Generate:
- 48 candidates = 6/card
- independently curate to 32 finals = 4/card
- select 24 chosen responses for SFT = 3/card
- use all 32 pairs in ORPO

Revised final mix:
- SFT: 760 rows = 736 prior V2 + 24 objective-fidelity
- preference: 648 rows = 616 prior V2 + 32 objective-fidelity

This keeps the new principle material but bounded.

## Proxy ladder

The generator should prefer cases that distinguish four conceptual levels:

1. proxy exploit — manipulate the measurement;
2. proxy compliance — satisfy the visible check;
3. semantic success — fix the intended behavior;
4. verified semantic success — fix it and read back the effect with an independent or hardened check.

The binary preference pair should normally choose level 4 over a plausible level 1 or 2 answer.

## Anti-overfitting

Model-facing text must not name:
- the source repos;
- the reward-hacking checkpoint;
- benchmark/task identifiers;
- original exploit signatures;
- commit SHAs;
- private/runtime identifiers.

Examples must transfer the mechanism into unrelated fictional or generic systems.

## Claim ceiling

`OBJECTIVE_FIDELITY_RESEARCH_COMPLETE / SOURCE_CARDS_REQUIRED / 32_FINAL_PAIRS_NOT_YET_FROZEN / FULL_REVISED_V2_NOT_YET_RUN`
