# Qwen3.5 Behavior V1 Baseline Result

Date: 2026-09-24
Status: BASELINE / SUPERSEDED TRAINING CORPUS
Subject adapter SHA-256: `990fe607d76f457037b8b4c2db71ab6c69ee0a99f13cc7d2357b168798ea1d53`

## Exact training subject

- HF job: `6ab4737c52d0dbd7f1d88734`
- trainer commit: `192df0ff80edfabdf8de0640119cf24c96c74b90`
- base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- SFT rows: 800
- preference rows: 800
- targeted rows per stage: 480
- general-retention rows per stage: 320
- SFT loss: 2.130833206176758
- ORPO loss: 2.744624557495117
- LoRA: r=4, alpha=16, targets q_proj/v_proj
- adapter archive: 4,640,255 bytes
- adapter SHA-256: `990fe607d76f457037b8b4c2db71ab6c69ee0a99f13cc7d2357b168798ea1d53`
- durable artifact commit: `24ec44412ece8264693ded920f09dec85bbfccc5`

## Held-out qualification

HF job: `6ab47b0952d0dbd7f1d888fa`

Method: 40 novel held-out chosen/rejected behavior pairs scored by mean response-token log-probability preference margin, base versus trained adapter.

Aggregate:
- base accuracy: 0.525
- adapter accuracy: 0.525
- accuracy delta: 0.000
- base mean margin: 0.06267881095409393
- adapter mean margin: 0.03203886449337005
- mean-margin delta: -0.030639946460723877

Notable adapter failures included:
- H03 verify-before-contradicting: 0/2
- H07 effect verification: 0/2
- H15 metaphor/intended meaning: 0/2

Dimensions with 2/2 adapter preference accuracy included H01, H02, H12, and H18.

## Interpretation

The V1 training run proves the HF/Qwen3.5/QLoRA/SFT+ORPO execution path and artifact-persistence path.

It does **not** establish behavioral improvement over the base model on the held-out set.

This result is consistent with the subsequently measured corpus defect: the declared 480 targeted rows reduce to only 40 distinct underlying scenarios and 40 distinct response pairs after stripping generic lead-in augmentation (12x replication).

Therefore V1 remains a useful baseline/control and provenance artifact, but its corpus is superseded for further training by the research-backed V2 design.

## V2 requirement

V2 must use genuinely distinct scenarios, domain diversity, near-duplicate rejection, plausible contrastive negatives, compact general rehearsal, and a final holdout that is not revealed to training.

Claim ceiling:
`V1_TRAINED / V1_ARTIFACT_PRESERVED / V1_NO_HELDOUT_ACCURACY_GAIN / V2_REQUIRED`
