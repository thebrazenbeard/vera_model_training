# Qwen3.5 Repo-Engineering Candidate Static Audit

Date: 2026-09-24
Candidate commit: `f2289b9008d6db14a6550b13042ebc887c2d6e33`
Artifact: `successor/qwen35/corpus/repo_engineering_v1_candidates.jsonl`
SHA-256: `419d4f8263e47df907ad3abd9aca5784388744e0d46e29b365b3db10e58994cf`
Bytes: 211,777

Deterministic readback:
- rows: 144
- source cards: 16
- rows per source card: 9
- unique normalized prompts: 144
- unique pair hashes: 144
- prompt near-duplicate pairs at 4-gram Jaccard >= 0.60: 0
- chosen/rejected character-length ratio:
  - min: 1.0142
  - median: 1.4033
  - max: 1.6984
  - outside required 0.60–1.70: 0
- model-facing source-marker leakage: 0 for thebrazenbeard, DriftGuard, Project Achilles/Achilles, vera_model_training, Lantern, Unbound-Sol, and SQL Connectome
- per-card domain coverage: 5–6 distinct domains for every card

The source-repository and source-commit fields remain present only as provenance metadata. The model-facing prompt/chosen/rejected material is deidentified and transferred to unrelated repository scenarios.

This establishes structural diversity and provenance hygiene. It does not establish semantic pair quality. Independent model curation remains the next gate.

Claim ceiling:
`REPO_CANDIDATE_BYTES_FROZEN / STATIC_AUDIT_PASS / SEMANTIC_CURATION_PENDING`
