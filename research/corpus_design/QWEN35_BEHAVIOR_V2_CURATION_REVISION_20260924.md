# Qwen3.5 V2 Independent Curation Revision

Date: 2026-09-24

Initial independent-curator job:
- HF job: `6ab5806e6b030d633f68f3f7`
- judge: `Qwen/Qwen2.5-14B-Instruct@cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`
- deterministic prefilter: 357/360 candidates survived
- failure: final selection stopped at H02 with only 8/16 rows satisfying the original condition that every rubric score be >=4 and the judge's boolean `pass` also be true

The failure is a curation-policy failure, not evidence that H02 had only eight usable examples. The original gate converted a multi-axis quality judgment into a brittle conjunction and discarded useful relative information from the judge scores.

Revised method:
1. Keep the deterministic privacy, marker, length-ratio, exact-duplicate, and near-duplicate gates unchanged.
2. Score every deterministic-pass candidate independently on:
   - target isolation
   - naturalness
   - rejected-answer plausibility
   - length fairness
   - difficulty fit
   - substance
3. Hard-reject a candidate if any of those dimensions scores below 3/5.
4. Rank remaining candidates primarily by target isolation and rejected-answer plausibility, then minimum rubric score, aggregate mean, naturalness, and substance.
5. Select the highest-ranked quota while round-robin balancing domains.
6. Preserve the judge's original boolean `pass` as evidence, but do not make it a second hidden veto after the numeric rubric has already been applied.
7. Fail closed if a dimension cannot meet its quota or domain-diversity floor after hard rejection.

This implements the research decision to select the best targeted subset instead of pretending an arbitrary absolute threshold is itself ground truth.

Ranked-curator commit:
`3de2a83003228302fd6d6c8a598b9081f763ed5c`

Ranked-curator HF job:
`6ab585ec52d0dbd7f1d8c8d4`

Claim ceiling:
`CURATION_METHOD_REVISED / RANKED_RUN_PENDING / FINAL_240_NOT_YET_FROZEN`
