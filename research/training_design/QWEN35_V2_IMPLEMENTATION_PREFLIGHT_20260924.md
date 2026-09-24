# Qwen3.5 V2 Implementation Preflight

Date: 2026-09-24
Target: `Vera-Qwen3.5-4B-Behavior-V1`

## Candidate artifact

Persisted commit: `1817fdcc0a184dd7b64fa83ec60578728f3b650d`

Readback:
- rows: 360
- bytes: 435,753
- SHA-256: `68215851c52f986dfe97e6523524e7d83a0fabfb1f207f3bd553f539f457d21d`
- exact unique normalized prompts: 360
- exact unique pair hashes: 360

Deterministic curator prefilter:
- pass: 357/360
- rejected: 2 banned-marker rows, 1 near-duplicate prompt
- all H01-H20 dimensions remain above final quota after prefilter

## Rehearsal-source validation

Frozen revisions:
- `HuggingFaceTB/smoltalk2@fc6cc2103c066455aade5d7fbb346039ae36ca5e`
- `HuggingFaceH4/ultrafeedback_binarized@3949bf5f8c17c394422ccfab0c31ea9c20bdeb85`

SmolTalk2 implementation correction:
- the `SFT` config does not expose a generic `train` split;
- each source is a named split;
- the V2 builder was corrected to load the five selected splits directly.

Validated exact SFT selections:
- UltraFeedback SFT: 256 rows
- SmolTalk2 SFT: 256 rows
  - explore/instruction rewriting: 52
  - rewrite: 52
  - summarize: 52
  - science: 52
  - table: 48

Validated exact preference rehearsal:
- UltraFeedback preferences: 256 rows
- accepted external score-margin range: 1.0 to 7.5
- exact Qwen tokenizer/template length gate applied at <=1024 tokens

## QLoRA target coverage

Frozen base:
`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`

Exact architecture:
- text layers: 32
- linear-attention layers: 24
- full-attention layers: 8

V2 `all-linear` LoRA meta-model probe:
- target modules: 248
- linear-attention targets: 120
- MLP targets: 96
- full-attention targets: 32
- trainable parameters: 8,116,224
- raw FP32 adapter bytes: 32,464,896
- raw BF16 adapter bytes: 16,232,448

Export decision:
- cast trainable LoRA weights to BF16 after optimization and before save;
- save adapter only, not a duplicate tokenizer;
- base tokenizer remains bound by exact base repo/revision;
- chunked log export enlarged to 65,536 base64 characters per chunk for tractable artifact custody.

## Current gate

Independent ranked semantic curation is running against the 357 deterministic-pass candidates.

No full V2 training may begin until:
1. exactly 240 curated targeted preference pairs are frozen and read back;
2. the 672-row SFT and 520-row preference corpora are built and SHA-256 frozen;
3. corpus contract tests pass on those exact bytes.

Claim ceiling:
`PREFLIGHT_PASS / CANDIDATE_BYTES_FROZEN / REHEARSAL_SELECTION_VALIDATED / TARGET_COVERAGE_VALIDATED / CURATION_PENDING / FULL_V2_TRAINING_NOT_STARTED`
