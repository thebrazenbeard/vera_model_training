# Qwen3.5 V2 Candidate Static Audit

Date: 2026-09-24
Subject commit: `1817fdcc0a184dd7b64fa83ec60578728f3b650d`
Candidate artifact: `successor/qwen35/corpus/history_behavior_targeted_v2_candidates.jsonl`
Artifact SHA-256: `68215851c52f986dfe97e6523524e7d83a0fabfb1f207f3bd553f539f457d21d`

Deterministic readback:
- bytes: 435,753
- rows: 360
- unique normalized prompts: 360
- unique pair SHA values: 360
- exact prompt duplicates: 0
- near-duplicate prompt pairs at 4-gram Jaccard >= 0.58: 1
- maximum observed near-duplicate Jaccard: 0.5882352941176471
- chosen/rejected character-length ratio: min 0.6067, median 1.2614, max 1.6980
- rows outside the required 0.60–1.70 ratio: 0
- scanned project-marker leakage: 0 for thebrazenbeard, vera_model_training, Build Team Two, Project Lantern, VeraMesh, Unbound-Sol, and DriftGuard

Domain coverage:
- all 20 declared domains are represented
- core 24-row dimensions contain 12–15 distinct domains
- 9-row oversample dimensions contain 5–6 distinct domains
- all dimensions therefore clear the V2 diversity floor before curation

Difficulty labels:
- overwhelmingly moderate, with a small number of hard rows and one easy row
- no dimension is dominated by hard examples

Interpretation:
The generated V2 candidate pool materially fixes the structural defect found in V1. It is not 12x prefix augmentation over a 40-scenario core; it is 360 unique candidate prompts and 360 unique preference pairs distributed across unrelated domains.

This audit does not establish semantic correctness of each chosen/rejected pair. Independent model curation remains required before the exact 240-row training set is frozen.

Claim ceiling:
`CANDIDATE_BYTES_VERIFIED / STATIC_DIVERSITY_PASS / SEMANTIC_CURATION_PENDING`
