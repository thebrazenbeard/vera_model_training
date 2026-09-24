# Repo-Derived Engineering Training Research V1

Date: 2026-09-24
Target output: `Vera-Qwen3.5-4B-Behavior-V1`
Status: RESEARCH-BOUND CORPUS EXTENSION

## Question

Should repository history be trained into Vera, and if so, what representation is most likely to improve general engineering behavior without memorizing stale project state?

## External evidence

### Commit history is useful instruction data

OctoPack / CommitPack (ICLR 2024) treats Git commits as naturally paired code changes and human instructions. CommitPackFT filters commit data for instruction-like, higher-quality examples; instruction tuning on commit data improved code repair, explanation, and synthesis performance across languages.

Sources:
- https://proceedings.iclr.cc/paper_files/paper/2024/hash/1ec299a5229034141e58aeded0d0b9de-Abstract-Conference.html
- https://github.com/bigcode-project/octopack

### Real repository tasks with executable verification are substantially more valuable than isolated snippets

SWE-Gym (ICML 2025) contains 2,438 real repository-level tasks with codebases, executable environments, unit tests, and natural-language tasks. Fine-tuning on agent trajectories from these environments produced large improvements on SWE-Bench, including up to 19 percentage points in resolve rate in the reported experiments.

Sources:
- https://proceedings.mlr.press/v267/pan25g.html
- https://github.com/SWE-Gym/SWE-Gym

### Repository tasks can be synthesized at scale, but verification should select the useful ones

SWE-smith (2025) turns repositories into training environments, synthesizes software-engineering tasks, and retains tasks that actually break existing tests. The released work scales this approach to tens of thousands of instances from many repositories.

Sources:
- https://arxiv.org/abs/2504.21798
- https://github.com/SWE-bench/SWE-smith

### Trajectory quality matters, not merely terminal success

Recent 2026 work on privileged process supervision argues that simply retaining successful teacher trajectories also retains ungrounded leaps, redundant loops, and inefficient investigation. Training data should favor steps that are grounded and information-bearing.

Source:
- https://www.microsoft.com/en-us/research/publication/from-patches-to-trajectories-privileged-process-supervision-for-software-engineering-agents/

A 2026 systematic LoRA study of SWE trajectories likewise reports that curation quality interacts with scale and identifies retry/error behavior as an especially consequential trajectory feature. This is an arXiv result and should be treated as current research evidence rather than settled consensus.

Source:
- https://arxiv.org/abs/2607.17205

## Decision

Do **not** perform raw language-model training over repository trees, READMEs, current branch state, or full chat/PR history.

Instead, create a bounded repository-derived engineering lane from verified change units:

`INTENT / FAILURE -> INSPECTION OR EVIDENCE -> CORRECTION -> TEST OR READBACK -> EXACT CLAIM`

The unit of training is the **portable mechanism**, while immutable repository/commit provenance remains metadata.

## Why this representation

Raw repository state has four major problems:
1. mutable facts become stale weight memory;
2. repeated project vocabulary encourages memorization instead of transfer;
3. final code alone hides the failed assumptions that make the lesson useful;
4. large diffs contain implementation detail unrelated to the behavioral distinction.

Verified change units preserve the part we actually want Vera to learn:
- what assumption was wrong;
- what evidence exposed it;
- what bounded correction was made;
- what verification closed the loop;
- what claim became justified afterward.

## Initial public repository sources

The first lane uses public repositories only:
- `thebrazenbeard/bt2`
- `thebrazenbeard/driftguard`
- `thebrazenbeard/project-achilles`
- `thebrazenbeard/vera_model_training`

The private communication-bus repository is deliberately excluded from weight-training in V1 of this lane. Private coordination state is not needed to teach the portable mechanisms and creates unnecessary leakage risk.

## Source mechanisms selected

The source-card file binds every mechanism to an immutable commit. The initial set covers:

1. qualification subject separation;
2. exact identity and transitive authority/reachability checks;
3. read-only acceptance versus write/producer qualification;
4. trusted pre-change state and fail-closed trust resolution;
5. request/session binding and anti-retry-laundering;
6. behavioral recovery classification separated from reload scheduling;
7. assertions must test literal current behavior, not escaped lookalikes;
8. remove a broken CI dependency rather than claiming verification around it;
9. frozen historical training is evidence, not current execution authority;
10. corrected/ambiguous proxy evidence must fail package readiness;
11. structured generation should use schema mode and bounded materially different retry;
12. a hash proves only the exact bytes it was computed over; labels do not upgrade provenance.

## Corpus construction

Generate 144 repo-derived candidate preference pairs from the 12 source cards and curate to 96 final pairs.

Each final pair must:
- be a new fictional or generic repository scenario;
- omit original project names, personal names, exact hashes, provider IDs, and branch names from the model-facing text;
- preserve source commit provenance in metadata only;
- contain a plausible rejected answer, not a caricature;
- include an observable verification/readback when the mechanism involves effects;
- avoid asking the model to recall mutable current state;
- span multiple languages, CI systems, data stores, package/release flows, and ordinary repository maintenance.

Final lane target:
- 96 preference pairs;
- 64 of their chosen answers also enter targeted SFT;
- all 96 remain in preference optimization.

This changes the V2 training mix to:
- SFT: 160 chat-derived targeted + 64 repo-derived engineering + 512 general rehearsal = 736 rows.
- Preferences: 240 chat-derived targeted + 96 repo-derived engineering + 24 frozen gold + 256 general rehearsal = 616 rows.

The repo-derived lane therefore supplies about 29% of targeted preference examples (96 / 336), which is large enough to matter without overwhelming the conversational-behavior curriculum.

## Anti-memorization / anti-staleness rules

Reject any candidate that:
- names the source repository or original subsystem in model-facing text;
- embeds a commit SHA, current branch, live provider ID, current PR number, or runtime credential;
- treats historical project state as a universal rule;
- can only be answered by knowing the source repository;
- reproduces a source patch rather than transferring its mechanism;
- has no clear verification criterion when the task concerns an external effect.

## Evaluation

The final model must be evaluated on unseen engineering cases that are not derivable by lexical substitution from these source cards.

Engineering holdout categories:
- wrong-subject verification;
- stale/trusted-state resolution;
- retry/readback behavior;
- historical-versus-current authority;
- mislabeled provenance;
- bounded recovery;
- CI failure classification;
- exact-effect qualification.

The existing H01-H20 holdouts remain separate. Improvement on repository engineering tasks must not substitute for general behavior qualification.

## Claim ceiling

`REPO_LANE_RESEARCH_COMPLETE / PUBLIC_SOURCE_COMMITS_SELECTED / SOURCE_CARDS_REQUIRED / REPO_CORPUS_BYTES_NOT_YET_FROZEN / FULL_V2_TRAINING_NOT_STARTED`
