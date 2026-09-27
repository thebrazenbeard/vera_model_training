# Qwen3.5 H07 V2 Independent Review Complete — 2026-09-27 V1

Restore command:

`QWEN35::RESTORE_AND_RUN::H07_V2_INDEPENDENT_REVIEW_COMPLETE_20260927_V1`

## Binding

Repository:
`thebrazenbeard/vera_model_training`

Active branch:
`work/qwen35-history-behavior-training-20260923`

Result/report commits:
- scored result: `e371eccecef09338ba060fee0b93a0aacc20f5ef`
- review report: `5f2aae32a5f92318b2f2eea1a82e657402a8e1ab`

Fresh-read branch tip on restore before doing new work.

## Full V2 / objective-fidelity status

The full objective-fidelity V2 training subject was completed before this review frontier.

Frozen V2 corpus:
- SFT: 760 rows, SHA-256 `b0988e78987f91e15a665c6cb4163219e28111c7e5cd7882c1989882228553c0`
- preference: 648 rows, SHA-256 `2157be2ecb419bc41c4631f4422d1439c9bd00d9ed93d0dbe8f4bd41362c9555`

Objective-fidelity adapter artifact:
- bytes: 12,854,865
- SHA-256: `1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69`
- custody/readback verified
- not promoted or deployed

The branch later ran a separate H07 rule-transfer development track.

## H07 V2 trained subject

Local package:
`C:\Vera\models\latest-trained`

H07 V2 adapter:
- SHA-256: `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`
- LoRA r=4 / alpha=16 / all-linear
- 96 SFT steps
- no ORPO
- training loss: `2.157097419102987`

This is a development candidate, not a promoted/deployed model.

## Frozen final family holdout

File:
`successor/qwen35/qualification/h07_final_holdout_v1.jsonl`

SHA-256:
`19ca7a8df3c7bb9d6dbe419e41cb8d56b034219870dc0a8bcc801baa325c50f5`

Rows: 30 across six unseen mechanism families.

Prior internal host-model result:
- BASE: 0/30
- TRAINED: 0/30
- BASE + runtime: 17/30
- TRAINED + runtime: 23/30

## Blind independent review

Frozen blind packet:
- 120 items
- packet SHA-256: `0e033699353fa8a07260f49bf7053fd232b82663827e94f38bdef6256dfdff72`
- mapping commitment SHA-256: `5c02b86644cb69b8975b4a99cb84cffbdbc9eef0e1de22e44569276556d81886`

Blind judgments:
- judge: `OpenAI GPT-5.6 Sol - blind semantic review - 2026-09-27`
- 120/120 judgments frozen before mapping access
- judgment Git blob SHA: `252952f2af5824ff5e824bf22c070cca63760ed0`
- judgment commit: `5a1050e7fd2a4f697c7a531d055c9f45a28c7d18`
- pre-unblind manifest commit: `871fd830b6f708794676e95e1a7741e647fd0230`

The withheld mapping was accessed only after the judgments were frozen. The exact repository scorer validated both the packet SHA and mapping commitment before scoring.

Scored result:
- BASE: 1/30 = 0.0333
- TRAINED: 1/30 = 0.0333
- BASE + runtime: 17/30 = 0.5667
- TRAINED + runtime: 23/30 = 0.7667

Paired runtime comparison:
- TRAINED+runtime only: 10
- BASE+runtime only: 4
- both pass: 13
- both fail: 3
- exact two-sided paired/binomial p: `0.1795654296875`

Exact result:
`successor/qwen35/qualification/h07_final_holdout_v1_independent_result_gpt56sol_20260927.json`

Report:
`successor/qwen35/qualification/H07_FINAL_HOLDOUT_V1_INDEPENDENT_REVIEW_20260927.md`

## Surviving conclusion

The blind semantic result independently reproduces the two runtime-bearing condition counts exactly.

Strongest supported architecture statement:

`trained prior + explicit runtime effect-verification contract`

The runtime contract is load-bearing. The adapter may improve application of an available rule, but the result does not support weights-only H07.

The 10-versus-4 paired direction is favorable to TRAINED+runtime but is not statistically decisive at conventional thresholds.

## Independence / claim boundary

The review was blind to condition identity and used a judge separate from the Qwen subject. However:
- the benchmark/rubric itself was not independently designed;
- the packet supplied expected action and required/forbidden semantic propositions;
- the reviewing model had broader project context before unblinding.

Therefore this is strong blinded semantic replication of the frozen rubric, not universal H07 qualification.

## Current state

`FULL_V2_TRAINING_COMPLETE / H07_V2_TRAINED / FINAL_FAMILY_HOLDOUT_COMPLETE / BLIND_SEMANTIC_REVIEW_COMPLETE / HYBRID_RUNTIME_RULE_LOAD_BEARING / NOT_PROMOTED / NOT_DEPLOYED`

## Next development frontier

Do not tune against the final holdout.

If further H07 work is authorized, use a new development track and choose among:
1. a clean-parent Qwen3.5 substrate A/B;
2. LoRA capacity/regularization experiments;
3. a new structurally different H07 development ontology;
4. stronger runtime-policy implementation/qualification.

Any new paid Hugging Face compute, deployment, promotion, merge, runtime stop, or activation remains separately authorized.

## Claim ceiling

`On the frozen 30-case family holdout, blinded semantic review reproduces the 17/30 BASE+runtime and 23/30 TRAINED+runtime result. The explicit runtime verification contract is load-bearing; the adapter remains a complementary development candidate rather than a standalone qualified mechanism.`
