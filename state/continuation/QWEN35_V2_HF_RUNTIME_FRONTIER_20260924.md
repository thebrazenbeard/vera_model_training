# Qwen3.5 V2 HF Runtime Frontier — 2026-09-24

Target output: `Vera-Qwen3.5-4B-Behavior-V1`
Branch: `work/qwen35-history-behavior-training-20260923`

## Frozen inputs already complete

- Chat-derived candidate pool: 360 rows
  - SHA-256: `68215851c52f986dfe97e6523524e7d83a0fabfb1f207f3bd553f539f457d21d`
- Independently curated chat-derived target set: 240 rows
  - SHA-256: `9221fcb33c93f9e9c8a7c2508698d7ed38decaef941be98acb187fa954db802c`
- Repo-engineering source cards: 16 immutable source-bound mechanisms
  - includes BT2, DriftGuard, Project Achilles, vera_model_training, Roots, SQL Connectome
- General rehearsal selectors validated:
  - 256 UltraFeedback SFT
  - 256 SmolTalk2 SFT
  - 256 UltraFeedback preference rows
- QLoRA target design:
  - Qwen3.5 text-only class
  - 32 text layers: 24 linear-attention + 8 full-attention
  - `target_modules="all-linear"`
  - 248 targeted modules
  - 8,116,224 trainable parameters
  - compact BF16 adapter-only export

## Expanded final corpus contract

Training must not start from the old 672/520 layout.

Required final mix:

SFT = 736 rows
- 160 chat-derived targeted chosen responses
- 64 repo-derived engineering chosen responses
- 512 general rehearsal

Preference = 616 rows
- 240 chat-derived behavior pairs
- 96 repo-derived engineering pairs
- 24 frozen Unbound-Sol gold pairs
- 256 general rehearsal pairs

## Current repo-engineering lane

Research decision:
- do not train raw repo trees or mutable current state;
- convert immutable verified change units into deidentified portable engineering mechanisms;
- provenance remains metadata;
- model-facing examples use unrelated fictional/generic systems.

Source cards:
- 16 cards total
- generation target: 144 candidates = 9/card
- curation target: 96 finals = 6/card
- final SFT subset: 64 = 4/card

Roots additions:
- accessible provenance frontier != proven origin;
- reuse/overlap/naming similarity != lineage or supersession.

SQL Connectome additions:
- translation/capability fidelity != behavioral equivalence;
- UNDERSTAND / TRANSLATE / VALIDATE / EXECUTE / AUTHORIZE remain separate claims.

## HF execution state

Earlier expanded repo-generator attempts:
- A10G job `6ab58c1b6b030d633f68f577`: infrastructure ERROR before container code, GPU idmap mount failure.
- T4 job `6ab58c3352d0dbd7f1d8ca02`: same infrastructure ERROR before container code.

Current materially different retry:
- L4 job `6ab58fe76b030d633f68f60c`
- status at last readback: SCHEDULING
- timeout: 30m
- exact source commit: `a2ad6cc91b0e61d1f4601a80810bafaa26fbb1da`

## Next gates

1. L4 repo-engineering generator completes.
2. Recover exact 144-row candidate bytes from job logs.
3. Commit candidate JSONL to this branch and read back SHA/counts.
4. Run deterministic audit.
5. Independently curate to 96 rows.
6. Commit/read back curated repo-engineering bytes.
7. Build exact 736-row SFT + 616-row preference corpora from frozen inputs.
8. Freeze SHA-256 manifests and run contract tests.
9. Run a one-step V2 smoke with all-linear QLoRA.
10. Run full bounded V2 SFT+ORPO.
11. Persist BF16 adapter artifact and receipt.
12. Evaluate against the frozen V1 40-row control holdout plus a new unrevealed engineering/behavior holdout.
13. No merge, deployment, GGUF activation, or runtime promotion without separate authority.

Claim ceiling:
`CHAT_TARGETED_FROZEN / REPO_ENGINEERING_GENERATION_PENDING / FINAL_736_616_NOT_FROZEN / FULL_V2_TRAINING_NOT_STARTED`
