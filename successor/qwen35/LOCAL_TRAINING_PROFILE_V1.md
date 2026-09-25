# Qwen3.5 Local Training Profile V1 — Lappy RTX 3050 4 GB

## Observed host

Observed on Lappy during the 2026-09-25 V3 development session:

- GPU: NVIDIA GeForce RTX 3050 Laptop GPU
- dedicated VRAM: 4096 MiB
- system RAM: 34,069,069,824 bytes (~31.7 GiB)
- training worktree: `work/qwen35-history-behavior-training-20260923`

This is runtime observation for local experiment design. It is not a claim that 512 tokens is the GPU's maximum possible sequence length.

## Training profile

`train_behavior_v3.py` exposes:

`--hardware-profile lappy-rtx3050-4gb`

The profile uses:

- maximum formatted sequence length: 512 tokens;
- overflow policy: fail closed;
- per-device batch size remains 1;
- gradient checkpointing remains enabled;
- 4-bit NF4 QLoRA remains enabled;
- optimizer: `adamw_torch` on the Lappy profile;
- `paged_adamw_8bit` is not permitted on Lappy;
- packing remains disabled.

The 512-token limit is a conservative V3 authoring/experiment budget chosen to bound activation memory on the 4 GiB GPU. It may be changed only after separate local memory evidence supports a different value.

Hardware safety note: Patrick reports that the paged optimizer path was crash-prone on Lappy and had previously been replaced with `adamw_torch`. The Lappy profile therefore excludes `paged_adamw_8bit`. Any broader causal claim about prior crashes requires separate system evidence.

## Corpus admission rule

Corpus rows are formatted with the exact base-model chat template and tokenized before model allocation.

For SFT, the complete prompt + completion sequence must fit the active profile.

For preference training, both prompt + chosen and prompt + rejected sequences must fit. The larger side is the row length.

Rows that exceed the profile fail before model allocation. Trainer-side silent truncation is not accepted as corpus adaptation.

Training receipts record the selected hardware profile, effective maximum length, overflow policy, and observed corpus token-budget report.

## Current corpus evidence

Exact base tokenizer:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

Current V3 clean repair corpus under the 512-token local profile:

- SFT rows: 16
- SFT maximum: 78 tokens
- preference rows: 16
- preference maximum: 78 tokens
- over-budget rows: 0

Legacy V2 corpus under the same 512-token profile:

- SFT: 118 / 760 rows over budget
- preference: 115 / 648 rows over budget

Legacy V2 remains reproducible with the generic 1024-token profile:

- SFT maximum: 1007 tokens
- preference maximum: 1021 tokens
- over-budget rows at 1024: 0

Therefore the legacy V2 corpus must not be silently treated as local-V3-ready merely because the trainer can accept it under the historical generic profile.

## V3 authoring consequence

New H03/H07/H11/H15 examples intended for local V3 training must be concise enough to fit the local profile after exact chat-template formatting.

Semantic coverage should come from more independent examples and mechanisms, not by making individual examples long.

If a behavior genuinely requires more than 512 tokens of context, classify that as an architecture/hardware experiment rather than truncating it into the local corpus.

## Claim boundary

This profile establishes a bounded local corpus/training contract. It does not establish:

- that 512 tokens is the hardware maximum;
- that every 512-token batch will fit under arbitrary concurrent GPU load;
- that a successful local training run is behaviorally qualified;
- that the legacy V2 corpus should be rewritten merely to satisfy the local profile;
- deployment, activation, publication, or merge authority.
