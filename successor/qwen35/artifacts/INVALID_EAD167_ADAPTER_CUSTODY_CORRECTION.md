# V2 Adapter Custody Correction — 2026-09-24

The adapter split artifacts introduced at commit `ead167e9a45be6bb42b31c0cb1bb8b8648db3422` are **not valid model artifacts** and must not be used for qualification, merge, export, or deployment.

## What happened

The first full V2 training job `6ab59c3852d0dbd7f1d8cd4c` completed successfully and reported an adapter archive:

- bytes: 12,854,260
- SHA-256: `5dddfdbfccbe63ad12a84e329c324e50e5162fdde3a0d332b554a207ddc8c2a4`

The trainer emitted that archive as base64 log chunks of 65,536 characters each.

HF Jobs log retrieval truncated those long output lines to roughly 16.35k characters. The resulting Git split files therefore reconstruct to different bytes:

- reconstructed invalid SHA-256: `d9afe363ac7d9d11d7230f6625b8f0cef177ad6e858b57a64e8299919612c9f3`
- expected training-receipt SHA-256: `5dddfdbfccbe63ad12a84e329c324e50e5162fdde3a0d332b554a207ddc8c2a4`

The qualification evaluator correctly failed closed on this mismatch before loading the adapter.

## Correction

Trainer output chunk size is now 12,000 characters, below the observed HF log-line truncation boundary.

Corrected trainer subject:
`7e541559abf1dfddcdde50373f33c9c087fb9750`

The full training subject remains the exact frozen 736-row SFT / 616-row preference corpus. The rerun changes artifact transport only.

## Status labels

- first full training runtime: COMPLETED
- first adapter log custody: INVALID / TRUNCATED
- `ead167...` split files: SUPERSEDED_INVALID_ARTIFACT
- behavioral qualification from those files: NOT PERFORMED
- corrected artifact-safe full rerun: runtime subject in progress

Do not delete the invalid files: they are provenance for the detected transport failure.

Claim ceiling:
`TRAINING_RUNTIME_PROVEN / FIRST_CUSTODY_INVALID / CORRECTED_CUSTODY_PENDING`
