# Qwen3.5 Behavior Corpus Research V1

Date: 2026-09-24
Status: RESEARCH COMPLETE / CORPUS V2 DESIGN INPUT
Target output identity: `Vera-Qwen3.5-4B-Behavior-V1`
Repository: `thebrazenbeard/vera_model_training`
Branch: `work/qwen35-history-behavior-training-20260923`

## Question

What is the strongest corpus design for teaching the recoverable Vera/Unbound-Sol behavioral corrections to the Qwen3.5 4B substrate without overfitting to Patrick-specific wording, destroying general capability, leaking private facts, or wasting the bounded Hugging Face budget?

## Repository evidence queried

The current repository was treated as primary implementation evidence, not merely documentation.

Reviewed:
- `research/behavior_archaeology/BEHAVIOR_ARCHAEOLOGY_20260923_V1.md`
- `successor/qwen35/HISTORY_BEHAVIOR_CURRICULUM_V1.json`
- `successor/qwen35/corpus/history_behavior_targeted_v1.jsonl`
- `successor/qwen35/train_history_behavior_v1.py`
- `successor/v5/TRAINING_AND_QUALIFICATION_SPEC_V1.json`
- `successor/v5/build_public_corpus.py`
- `successor/v5/generate_targeted_pairs.py`
- `successor/v5/curate_targeted_pairs.py`
- `successor/v5/gold/unbound_sol_behavior_v3_v1.source.jsonl`
- V4 custom corpus manifest and representative families
- V4 rehearsal/training manifests

### Important finding: Qwen history corpus V1 is mechanically over-replicated

Measured directly from `history_behavior_targeted_v1.jsonl`:

- rows: 480
- exact prompt strings: 480
- distinct underlying scenarios after removing lead-in prefixes: 40
- distinct chosen/rejected response pairs: 40
- replication factor: 12x
- each H01-H20 dimension has only 2 underlying scenarios

Therefore the V1 targeted corpus must NOT be treated as 480 independent behavioral examples. It is a 40-example seed set with superficial prompt-prefix augmentation.

### Existing repo assets worth retaining

The repository already contains mechanisms that agree with current external evidence:

- V5 near-duplicate rejection using word shingles / MinHash-like signatures;
- length-ratio controls for chosen/rejected pairs;
- deterministic rejection before model judging;
- an independent curation pass requiring target isolation, naturalness, plausible negatives, length fairness, and substance;
- a broad public rehearsal mix;
- 24 Unbound-Sol behavioral gold preference pairs;
- explicit train/qualification separation.

V4 also contains 12,000 custom behavior rows and a 42,500-row rehearsal pool. Those are useful as seed/source material, but representative inspection shows substantial template/formula reuse. They should be selected or transformed, not blindly replayed wholesale.

## External research reviewed

### 1. Quality and diversity beat raw count

Liu et al., *What Makes Good Data for Alignment?* (ICLR 2024 / DEITA) studies complexity, quality, and diversity jointly and reports strong instruction tuning with a 6K selected set, far smaller than baseline corpora.

Source:
https://proceedings.iclr.cc/paper_files/paper/2024/hash/6091f2bb355e960600f62566ac0e2862-Abstract-Conference.html

Bukharin et al., *Data Diversity Matters for Robust Instruction Tuning* (Findings of EMNLP 2024), finds diversity and quality must be optimized together for robust instruction following.

Source:
https://aclanthology.org/2024.findings-emnlp.195/

Yang et al., *Measuring Data Diversity for Instruction Tuning* (ACL 2025), finds useful diversity measures must account for both inter-sample differences and information density.

Source:
https://aclanthology.org/2025.acl-long.908/

Decision: replace prefix paraphrase multiplication with genuinely different situations, domains, speech acts, and failure pressures.

### 2. Targeted selection can outperform full-corpus training

Xia et al., *LESS: Selecting Influential Data for Targeted Instruction Tuning* (ICML 2024), reports that a selected 5% subset can outperform the full data for targeted capabilities and that the selection can transfer across model families.

Source:
https://proceedings.mlr.press/v235/xia24c.html

Decision: treat chat-derived corrections as capability anchors and select/synthesize examples that exercise the same decision rule in unrelated contexts. Do not train the entire historical corpus merely because it exists.

### 3. Preference quality and difficulty matter

Gao et al., *Principled Data Selection for Alignment: The Hidden Risks of Difficult Examples* (ICML 2025), finds overly difficult preference examples can hurt alignment when they exceed model capacity.

Source:
https://proceedings.mlr.press/v267/gao25f.html

Deng et al., *Less is More: Improving LLM Alignment via Preference Data Selection* (NeurIPS 2025), reports that carefully selected preference subsets can outperform full UltraFeedback-style training while using much less data.

Source:
https://papers.neurips.cc/paper_files/paper/2025/hash/ebf95a6f3c575322da15d4fd0fc2b3c8-Abstract-Conference.html

Huang et al., *Larger or Smaller Reward Margins to Select Preferences for LLM Alignment?* (ICML 2025), argues preference usefulness is not captured by one margin alone and should consider the model's current implicit preference state.

Source:
https://proceedings.mlr.press/v267/huang25al.html

Decision: target plausible, discriminative negatives. Reject caricatures, near-identical pairs, huge length asymmetries, and examples whose distinction is so subtle that a 4B model cannot reliably learn it.

### 4. Preference optimization already contains a supervised component

Hong et al., *ORPO: Monolithic Preference Optimization without Reference Model* (EMNLP 2024), formulates ORPO as reference-free preference-aligned supervised training and demonstrates it across models up to 7B.

Source:
https://aclanthology.org/2024.emnlp-main.626/

Decision: do not expose every targeted example once in SFT and then again in ORPO by default. Use SFT primarily for a small selected target subset plus general retention; let ORPO carry the full contrastive behavior set.

### 5. General-capability retention needs explicit attention

Liu et al., *How Abilities in Large Language Models are Affected by Supervised Fine-tuning Data Composition* (ACL 2024), finds abilities scale differently with SFT data and sequential skill training risks catastrophic forgetting.

Source:
https://aclanthology.org/2024.acl-long.12/

Jin & Ren, *What Will My Model Forget?* (ICML 2024), shows updating on corrected instances can cause forgetting and that indiscriminate random replay is not always sufficient.

Source:
https://proceedings.mlr.press/v235/jin24d.html

Huang et al., *Mitigating Catastrophic Forgetting in Large Language Models with Self-Synthesized Rehearsal* (ACL 2024), finds carefully selected rehearsal can preserve generalization efficiently.

Source:
https://aclanthology.org/2024.acl-long.77/

Decision: retain a compact, diverse general rehearsal set rather than tens of thousands of random examples. The goal is behavioral surgery, not another broad instruction-tuning pretraining pass.

## Corpus V2 design

### A. Chat-derived behavior anchors

The 40 underlying V1 scenarios remain valuable as evidence-derived anchors, but they are no longer multiplied by generic lead-in prefixes.

Use:
- 40 unique history-derived seed scenarios;
- 24 existing Unbound-Sol gold preference pairs;
- no raw private chat text;
- no mutable personal/project facts as weight truth.

### B. New targeted preference corpus

Create 240 genuinely distinct behavioral preference pairs.

Allocation:
- Core dimensions H01-H08, H10, H11, H16, H19: 16 pairs each = 192.
- Medium dimensions H09, H12-H15, H18, H20: 6 pairs each = 42.
- Privacy/generalization dimension H17: 6 pairs.
- Total = 240.

Requirements:
- each core dimension spans at least 8 distinct domains;
- each medium dimension spans at least 4 distinct domains;
- no scenario may be a simple prefix/suffix paraphrase of another;
- prompts must vary speech act: command, correction, question, continuation, ambiguity, factual challenge, tool/effect request, ordinary task;
- rejected answers must be fluent and plausible;
- chosen and rejected should be comparable in length and usefulness except for the target failure;
- remove project names and private autobiographical details;
- selected pairs are training-only and excluded from final holdout.

### C. SFT mix

Target approximately 672 SFT rows:
- 512 diverse general-retention rows;
- 160 targeted chosen-response rows selected from the 240 targeted pairs, balanced across H dimensions and domains.

The 160 targeted SFT rows are a subset, not all targeted pairs, to reduce duplicate exposure before ORPO.

General-retention selection should prefer:
- diverse domains;
- different instruction forms;
- moderate rendered lengths;
- no near duplicates;
- no benchmark/evaluation leakage;
- no obviously low-quality or malformed responses.

### D. Preference mix

Target approximately 520 preference rows:
- 240 new history-derived behavioral pairs;
- 24 existing Unbound-Sol gold pairs;
- 256 diverse general preference pairs from frozen UltraFeedback revision.

General preference filters:
- externally scored chosen > rejected;
- reject extreme chosen/rejected length imbalance;
- reject near-duplicate prompts;
- reject identical/near-identical answers;
- select across prompt-length buckets;
- prefer a moderate-to-strong score margin rather than blindly maximizing difficulty.

### E. Selection stages

1. deterministic schema/privacy checks;
2. exact and near-duplicate removal;
3. semantic/domain diversity balancing;
4. chosen/rejected length fairness;
5. difficulty screen suitable for a 4B model;
6. target-isolation curation;
7. token-length check under the exact frozen Qwen tokenizer/template;
8. freeze bytes + SHA-256 manifests;
9. generate qualification material only after candidate freeze.

## Training objective

Recommended sequence for the bounded run:

1. QLoRA SFT on the compact mixed SFT corpus.
2. ORPO on the compact mixed preference corpus.
3. Freeze adapter.
4. Evaluate targeted behavior, ordinary competence, negative transfer, and currentness/effect boundaries.
5. Only then merge/export and quantize to Q5_K_S.

This is deliberately smaller than inherited V5 nominal volumes. The purpose of this run is a high-signal behavior adaptation of an already instruction-tuned 4.66B model under a bounded compute budget.

## Anti-overfitting invariants

The corpus must fail closed if:
- effective unique scenario count is materially lower than declared row count;
- one lexical scaffold dominates a behavior dimension;
- any private chat fact is copied into a training row;
- a mutable current fact is encoded as standing model truth;
- training and final qualification prompts overlap;
- one domain supplies more than 20% of targeted examples;
- chosen/rejected length ratio falls outside 0.60-1.70 without explicit review;
- target behavior cannot be named from the pair without relying on project-specific context.

## Supersession decision

`successor/qwen35/corpus/history_behavior_targeted_v1.jsonl` remains preserved as research provenance and seed evidence.

It is superseded as the full training target by Corpus V2.

The smoke trained on V1 proves the Qwen3.5/TRL/QLoRA execution path, not the final corpus quality.

## Claim ceiling

`CORPUS_RESEARCH_V1_COMPLETE / V1_REDUNDANCY_MEASURED / V2_DESIGN_SELECTED / V2_BYTES_NOT_YET_FROZEN / FULL_TRAINING_NOT_YET_RUN`
