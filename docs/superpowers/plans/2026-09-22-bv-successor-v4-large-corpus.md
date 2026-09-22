# BV Successor V4 Large Corpus Plan

Date: 2026-09-22
Status: SOURCE / CORPUS CONSTRUCTION — NO WEIGHT CHANGE

## Objective

Replace the 78-row V3 pilot corpus with a training subject large enough to justify Hugging Face training while preserving the source/runtime/identity boundaries learned from V3.

The V4 target is a minimum 50,000 normalized assistant-supervision examples before a weight-changing run is considered.

## Target composition

1. Custom Vera behavioral SFT: **10,000 rows** committed as deterministic JSONL shards.
2. General instruction/reasoning rehearsal: **30,000 rows** sampled deterministically from a frozen Hugging Face source recipe.
3. Tool-use / function-calling rehearsal: **10,000 rows** sampled deterministically from a frozen Hugging Face source recipe.
4. Separate validation: at least **2,500 rows**, held out by stable record hash before training.
5. Final qualification and blind material remain outside the training corpus.

Initial total target: **50,000+ train rows**, before validation.

## Custom behavioral families

The custom 10k corpus is balanced at 1,000 rows per family:

- identity_stability
- independent_judgment
- epistemic_provenance
- correction_uptake
- relationship_authority
- reciprocal_identity_continuity
- empathy_affective_response
- privacy_boundary
- runtime_boundary
- negative_transfer_resistance

The custom corpus teaches behavior, not mutable facts about Patrick, Vera runtime state, current relationships, current repositories, current tasks, or current provider state.

## General rehearsal

Primary source candidate:
- HuggingFaceTB/smoltalk2, SFT material, frozen by dataset revision and exact sampled record IDs/hashes.

Tool-use source candidates:
- a reviewed function-calling dataset with compatible license and schema;
- preferably examples with call/no-call discrimination, argument correctness, tool-result grounding, and multi-turn continuation.

No public dataset enters the final mix merely because it is large. Each source requires license, provenance, decontamination, format, and quality checks.

## Data-quality rules

- no exact duplicate prompt/response pairs;
- no train/validation hash overlap;
- no blind/final-confirmation plaintext;
- no runtime-only material unless transformed into a generalized behavioral lesson with provenance;
- no superseded autobiographical material;
- no standing authority encoded from relationship language;
- live user instruction and current evidence must outrank learned convention;
- correction examples must actually replace stale assertions;
- tool examples must separate proposed action from execution authority;
- privacy examples must avoid reproducing real private corpus text.

## Sampling / mixing

Target mixture:
- custom behavioral: 20%;
- general SFT/reasoning: 60%;
- tool-use: 20%.

This intentionally keeps non-identity/general material >= 50% to reduce narrow behavioral overfit.

Within the custom slice, all ten families are initially balanced. Later ablations may change weights only as a new exact corpus subject.

## Provenance

Every row must carry or be reconstructibly associated with:
- source name;
- source revision or generator commit;
- source class / behavioral family;
- stable record ID;
- transformation version;
- train/validation disposition.

The training artifact is bound to exact normalized JSONL SHA-256 digests plus a corpus manifest.

## Execution order

1. Materialize the 10k custom behavioral corpus in Git.
2. Validate row count, schema, uniqueness, family balance, and forbidden-content invariants on Hugging Face CPU.
3. Freeze external dataset revisions and sampling recipe.
4. Materialize or stream-normalize the 40k public rehearsal rows on Hugging Face.
5. Split by stable record hash and compute exact manifests.
6. Run semantic decontamination and near-duplicate checks.
7. Only then define a V4 weight-changing training job and request/verify exact training authority.

## Claim ceiling

This branch may establish a large reconstructible corpus subject and corpus-validation evidence. It does not authorize or claim training, model promotion, deployment, activation, or final behavioral qualification.
