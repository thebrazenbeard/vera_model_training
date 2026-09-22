# BV Successor V4 Large Corpus Plan

Date: 2026-09-22
Status: SOURCE / CORPUS CONSTRUCTION — NO WEIGHT CHANGE

## Objective

Replace the 78-row V3 pilot corpus with a training subject large enough to justify Hugging Face training while preserving the source/runtime/identity boundaries learned from V3.

The V4 source pool is 52,500 normalized assistant-supervision examples, deterministically split to exactly 50,000 training rows and 2,500 validation rows before a weight-changing run is considered.

## Target composition

1. Custom Vera behavioral SFT source pool: **10,000 rows** committed as deterministic JSONL shards.
2. General instruction/reasoning rehearsal source pool: **42,500 rows** sampled deterministically from exact-revision SmolTalk2 SFT material.
3. Stable-hash validation holdout: **500 custom rows** (50/family) + **2,000 rehearsal rows**.
4. Final training set: **50,000 rows**; validation set: **2,500 rows**.
5. Final qualification and blind material remain outside the training corpus.

Tool-use/function-calling is intentionally deferred to a separate trainer-capability lane. The current SFT trainer accepts prompt/response pairs only; flattening tool traces into plain text merely to inflate corpus size would destroy the semantics we intend to teach.

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

The exact rehearsal source is `HuggingFaceTB/smoltalk2` at frozen revision `fc6cc2103c066455aade5d7fbb346039ae36ca5e`, filtered to clean two-message user -> assistant examples and a 1,536-token rendered ceiling.

No public dataset enters the final mix merely because it is large. Each selected slice must pass provenance, schema, exact-pair deduplication, role-shape, tokenizer/template, and length checks.

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

Final split target mixture is approximately:
- custom behavioral: 9,500 / 50,000 = **19%**;
- general SFT/reasoning rehearsal: 40,500 / 50,000 = **81%**.

This intentionally keeps general material well above 50% to reduce narrow behavioral overfit.

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
3. Freeze the exact SmolTalk2 dataset revision and deterministic 42.5k sampling recipe.
4. Materialize and normalize the rehearsal rows on Hugging Face.
5. Split the 52.5k source pool by stable record hash and compute exact manifests.
6. Run semantic decontamination and near-duplicate checks.
7. Only then define a V4 weight-changing training job and request/verify exact training authority.

## Claim ceiling

This branch may establish a large reconstructible corpus subject and corpus-validation evidence. It does not authorize or claim training, model promotion, deployment, activation, or final behavioral qualification.
