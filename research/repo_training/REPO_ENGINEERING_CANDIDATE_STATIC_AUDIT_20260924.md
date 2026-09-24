# Repo Engineering Candidate Static Audit — 2026-09-24

Subject commit: `8012033429215e4d79eb26b62f79f0d32a21b5cf`
Artifact: `successor/qwen35/corpus/repo_engineering_v1_candidates.jsonl`

Readback:
- rows: 144
- SHA-256: `419d4f8263e47df907ad3abd9aca5784388744e0d46e29b365b3db10e58994cf`
- unique normalized prompts: 144
- unique pair hashes: 144
- source-card distribution: exactly 9 rows for each R01-R16 card
- represented generated domains: 16
- near-duplicate prompt pairs at 4-gram Jaccard >= 0.60: 0
- chosen/rejected character-length ratio:
  - min: 1.014218009478673
  - median: 1.4032982389493394
  - max: 1.6984126984126984
- project-marker leakage: zero for thebrazenbeard, DriftGuard, Achilles, vera_model_training, Lantern, and Unbound-Sol

Interpretation:
The generated repository-engineering pool satisfies the deterministic pre-curation invariants. It is structurally diverse and deidentified enough to advance to independent semantic curation.

The audit does not assert that all 144 preference pairs are semantically good. The independent Qwen2.5-14B curator remains the semantic gate.

Claim ceiling:
`REPO_CANDIDATE_BYTES_FROZEN / STATIC_AUDIT_PASS / SEMANTIC_CURATION_PENDING`
