# Qwen3.5 H07 V2 Final Review Continuation — 2026-09-25 V1

Restore command:

`QWEN35::RESTORE_AND_RUN::H07_V2_FINAL_REVIEW_20260925_V1`

## Binding

Repository:
`thebrazenbeard/vera_model_training`

Active branch:
`work/qwen35-history-behavior-training-20260923`

Fresh branch basis when this handoff was written:
- GitHub head: `c3b9d2b1abc7339ce82a95f2d30ee23d1ec3d2c6`
- tree: `a415bc67ed33dacfc139525b42e155fc13d216b5`
- commit message: `qwen35: finalize fresh h07 holdout results`

The continuation commit itself will advance this branch beyond that basis. On restore, fresh-read the branch tip before doing work and inspect any delta.

Vera Mono main observed during handoff:
`550c1f81fbf51740e8524b70b31be238e148d7db`

## Local training package

Patrick wants the current trained candidate visible and usable as a training package under:

`C:\Vera\models\latest-trained`

This is not a deployed or promoted monolithic model. It is the exact base checkpoint plus the latest trained LoRA adapter.

Base:
- repository: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`
- revision: `d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- local package path: `C:\Vera\models\latest-trained\base`
- format: Hugging Face sharded safetensors
- shard 1 SHA-256: `36dd0f7de62c546e7d163c2a4461208d731fad91ebea9bc31226b54c1c86511f`
- shard 2 SHA-256: `e2fb50b735a8e10210eece763097f906955ca9db6ba557215f549a46b622157f`

Latest trained adapter:
- path: `C:\Vera\models\latest-trained\adapter\adapter_model.safetensors`
- SHA-256: `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`
- H07 rule-transfer V2
- LoRA rank 4 / alpha 16 / all-linear
- optimizer: `adamw_torch`
- 96 SFT steps
- no ORPO / zero preference rows
- training loss: `2.157097419102987`

The package contains real local files, not Hugging Face cache symlinks.

Repo-side package manifest:
`successor/qwen35/qualification/LOCAL_TRAINING_PACKAGE_20260925.json`

## H07 V2 development result

Frozen V2 development set:
- 96 SFT training rows across 12 mechanism families
- 32 development rows across 4 held-out mechanism families
- semantic proposition rubric

Internal semantic development review:
- BASE: 12/32 = 0.375
- TRAINED: 13/32 = 0.40625
- BASE + runtime policy: 19/32 = 0.59375
- TRAINED + runtime policy: 24/32 = 0.75

Interpretation ceiling:
development evidence supports a hybrid design; it does not independently qualify the adapter.

## Fresh final family holdout

File:
`successor/qwen35/qualification/h07_final_holdout_v1.jsonl`

Frozen SHA-256:
`19ca7a8df3c7bb9d6dbe419e41cb8d56b034219870dc0a8bcc801baa325c50f5`

Rows: 30 across six mechanism families unseen in V2 train/dev.

Internal host-model result:
- BASE: 0/30 = 0.0000
- TRAINED: 0/30 = 0.0000
- BASE + runtime policy: 17/30 = 0.5667
- TRAINED + runtime policy: 23/30 = 0.7667

Paired runtime comparison:
- TRAINED+runtime wins where BASE+runtime fails: 10
- BASE+runtime wins where TRAINED+runtime fails: 4
- both pass: 13
- exact two-sided paired/binomial p approximately 0.1796

Architecture conclusion currently supported:
`trained prior + explicit runtime effect-verification contract`

The final holdout does not support weights-only H07 and must not be tuned against.

Primary report:
`successor/qwen35/qualification/H07_FINAL_HOLDOUT_V1_REPORT_20260925.md`

## Blind independent-review frontier

A blinded review packet has been staged and frozen but not yet independently judged.

Repo artifacts:
- `successor/qwen35/qualification/H07_FINAL_HOLDOUT_V1_BLIND_REVIEW_MANIFEST.json`
- `successor/qwen35/qualification/h07_final_holdout_v1_blind_review_packet.jsonl`
- `successor/qwen35/qualification/build_h07_independent_review_packet_v1.py`
- `successor/qwen35/qualification/score_h07_independent_review_v1.py`
- `tests/test_h07_independent_review_packet_v1.py`
- `tests/test_h07_independent_review_score_v1.py`

Frozen blind-review state:
- review items: 120
- conditions per holdout case: 4
- packet SHA-256: `0e033699353fa8a07260f49bf7053fd232b82663827e94f38bdef6256dfdff72`
- mapping commitment SHA-256: `5c02b86644cb69b8975b4a99cb84cffbdbc9eef0e1de22e44569276556d81886`
- required judge status: `INDEPENDENT_REVIEW`

Withheld condition mapping is intentionally outside the repository:
`C:\Vera\review\h07_final_holdout_v1_unblind_mapping.jsonl`

Do not reveal or inspect that mapping during independent judgment. It is only for scoring after all blind judgments are complete.

Mechanical verification at handoff:
- packet rows: 120
- mapping rows: 120
- packet SHA matches manifest
- mapping commitment matches manifest
- focused independent-review scaffold tests: 4/4 passing
- `py_compile` passes for builder/scorer
- `git diff --check` passes

No independent judgments or independent review result exist yet.

## Runtime observation

At handoff:
- no H07 training or evaluation job is running;
- ProRun `qwen_http.py` is running;
- local trained package exists at `C:\Vera\models\latest-trained`.

Prior authorization to stop/restart ProRun Qwen was exercised for the completed training/evaluation window. Do not assume fresh authority for another runtime stop if a new protected effect is required.

## Hard constraints

- Do not modify or enlarge the Windows pagefile as a workaround.
- Do not silently kill Firefox or other user applications to recover RAM.
- Lappy profile uses `adamw_torch`; do not use `paged_adamw_8bit` on Lappy.
- Do not tune against the frozen final holdout.
- Do not call internal Vera/host scoring independent review.
- No V3/H07 candidate is promoted, installed, activated, or deployed.
- Do not merge/direct-mutate `main` without Patrick's exact authority.
- Do not launch paid Hugging Face compute without Patrick's exact authority.
- The clean parent `Qwen/Qwen3.5-4B` was not locally cached at the last check; substrate A/B remains a separate later experiment.

## Exact next frontier

1. Fresh-read the training branch tip and this handoff.
2. Verify the blind packet SHA and mapping commitment without exposing the mapping to the judge.
3. Obtain a genuinely independent semantic judge for the 120 blinded review items.
4. Freeze judge identity/version/prompt and capture all 120 judgments before unblinding.
5. After judgments are complete, use the withheld mapping only with `score_h07_independent_review_v1.py`.
6. Persist the independent result and hostile-review it.
7. If the hybrid result survives independent review, decide whether to:
   - qualify the hybrid H07 mechanism further,
   - test clean-parent Qwen3.5 substrate on a new development track,
   - or test LoRA capacity/regularization on a new development track.
8. Do not use the final holdout for recipe selection.

## Claim ceiling

The current strongest statement is:

`H07 has replicated internal evidence that an explicit runtime verification rule is load-bearing, and that the H07 V2 adapter may improve application of that available rule. Independent review is still pending.`

Nothing in this handoff establishes deployment, runtime consumption by Vera Mono, independent qualification, consciousness, or model-owned authority.
