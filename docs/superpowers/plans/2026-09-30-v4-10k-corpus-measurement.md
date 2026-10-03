# V4 10k Core Corpus Measurement

Date: 2026-09-30
Status: SOURCE / MEASUREMENT — NO WEIGHT CHANGE

## Current subject

The active V4 corpus branch had grown from the intended 10,000-row custom behavioral corpus to 12,000 rows by adding two 1,000-row families:

- `anti_glibness`
- `anti_obduracy`

Those additions are useful research material, but they are not part of the 10,000-row core training subject.

This branch makes that distinction explicit:

- core training corpus: 10 families × 1,000 rows = 10,000 rows;
- auxiliary research corpus: 2 families × 1,000 rows = 2,000 rows;
- auxiliary rows remain committed but are excluded from the core V4 training builder.

The combined V4 source-pool arithmetic is restored to:

- 10,000 custom behavioral rows;
- 42,500 general rehearsal rows;
- 52,500 source rows;
- 500 custom validation rows;
- 2,000 rehearsal validation rows;
- 50,000 training rows;
- 2,500 validation rows.

## Measurement finding

The ten current core shards were inspected directly.

Every family currently has:

- 1,000 rows;
- 1,000 unique prompts;
- 1,000 unique full responses;
- 1,000 unique prompt/response pairs;
- balanced difficulty counts of 200 per difficulty.

That is useful integrity evidence, but it is not sufficient evidence of semantic response diversity.

Sentence-position analysis found strong component reuse. For most families, the first four response positions contain only five unique sentence components each, and the fifth position contains only two. Some individual sentence components occur in 20% to 62.5% of a family.

The exact uniqueness claim therefore needs to remain narrow:

`unique full responses = 10,000` does not imply `10,000 semantically independent responses`.

A second measurement pass is more revealing. Across the 10,000 core rows, the corpus contains 947,118 normalized word tokens but only 735 unique normalized tokens. The type-token ratio is 0.000776, there are zero hapax tokens, the top 100 tokens account for 65.82% of all tokens, the top 100 bigrams account for 31.00%, and the top 100 trigrams account for 23.01%.

Those values are structural evidence of extreme template concentration. They do not, by themselves, prove that training on the corpus would harm a model, but they make semantic/linguistic diversity review a hard prerequisite rather than a cosmetic improvement.

The new measurement tool records this distinction explicitly and emits review flags rather than converting the heuristic into a failure verdict.

## Why this matters

Research on synthetic text has reported declines in linguistic diversity under recursive synthetic-data training and has proposed lexical, syntactic, and semantic diversity measurements. Other work reports a relationship between synthetic-data diversity and downstream training performance. Data curation work also emphasizes deduplication, filtering, remixing, and contamination controls.

Relevant references:

- Guo et al., *The Curious Decline of Linguistic Diversity: Training Language Models on Synthetic Text* (arXiv:2311.09807).
- Chen et al., *On the Diversity of Synthetic Data and its Impact on Training Large Language Models* (arXiv:2410.15226).
- Zhu et al., *How to Synthesize Text Data without Model Collapse?* (arXiv:2412.14689).
- Al-Lawati et al., *LLM Benchmark Datasets Should Be Contamination-Resistant* (arXiv:2605.19999).

These sources motivate measuring diversity and contamination resistance; they do not establish that this particular corpus will cause model collapse or that any particular revision will improve training.

## Hostile review

> **HOSTILE REVIEWER:** The corpus already has 10,000 unique responses. Calling it insufficiently diverse is just aesthetic judgment.

**Response — accepted in part.** Full-string uniqueness is a real integrity property. It is not a semantic-diversity measurement. The sentence-component reuse result is a concrete structural signal that justifies further review without claiming the corpus is unusable.

> **HOSTILE REVIEWER:** Fixing the 12k/10k mismatch by excluding the new families throws away potentially useful behavior.

**Response — rejected as a necessary conclusion.** The two new families remain preserved as auxiliary research material. Exclusion from this exact 10k training subject keeps the experimental variable stable. They can become a future exact corpus revision rather than silently changing the current training subject.

> **HOSTILE REVIEWER:** Why not simply train the 12k corpus and see whether it works?

**Response — rejected for experimental-control reasons.** The existing V4 training manifest and 50k split were designed around 10k custom rows. Changing the custom population simultaneously changes the training mixture and invalidates the prior corpus receipt. A new 12k experiment is legitimate, but it should be named and measured as a new subject.

## Next frontier

Do not launch weight-changing training from the current corpus yet.

First construct a new exact 10k revision with greater response-level diversity while preserving the same ten behavioral families and 1,000-row balance. Measure:

1. exact duplicate rate;
2. prompt diversity;
3. response diversity;
4. sentence/component reuse;
5. lexical diversity;
6. n-gram concentration;
7. difficulty balance;
8. family balance;
9. train/validation overlap;
10. contamination/holdout separation.

For the diversity revision, the response generator should be changed at the source level rather than merely paraphrasing the existing 10,000 rows. The current generator has a small fixed component pool; expanding that pool and varying composition is the more defensible next experiment.

Only after that comparison should a new training subject be selected.

No model weights were changed by this work.

## Verification state

The deterministic corpus regression suite has been added. CI execution is required before claiming an executable PASS for the branch. The source-level measurement above is not a substitute for executable verification.
