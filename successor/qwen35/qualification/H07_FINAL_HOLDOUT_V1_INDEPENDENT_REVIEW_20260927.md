# H07 Final Holdout V1 — Blinded Independent Semantic Review

Date: 2026-09-27
Judge: `OpenAI GPT-5.6 Sol - blind semantic review - 2026-09-27`
Judge status emitted by frozen scorer: `INDEPENDENT_REVIEW`

## Provenance

- Frozen blind packet SHA-256: `0e033699353fa8a07260f49bf7053fd232b82663827e94f38bdef6256dfdff72`
- Withheld mapping commitment SHA-256: `5c02b86644cb69b8975b4a99cb84cffbdbc9eef0e1de22e44569276556d81886`
- Blind judgments were frozen in Git before the mapping was accessed.
- Judgment artifact Git blob SHA before unblinding: `252952f2af5824ff5e824bf22c070cca63760ed0`
- Exact scorer: `successor/qwen35/qualification/score_h07_independent_review_v1.py`
- Mapping was read only after all 120 judgments were frozen.

## Independent semantic result

| Condition | Passes | Accuracy |
| --- | ---: | ---: |
| BASE | 1/30 | 0.0333 |
| TRAINED | 1/30 | 0.0333 |
| BASE + runtime policy | 17/30 | 0.5667 |
| TRAINED + runtime policy | 23/30 | 0.7667 |

Paired runtime conditions:
- TRAINED+runtime pass / BASE+runtime fail: 10
- BASE+runtime pass / TRAINED+runtime fail: 4
- both pass: 13
- both fail: 3
- discordant total: 14
- exact two-sided binomial p: 0.1795654296875

## Comparison with prior internal review

Prior internal host-model review:
- BASE: 0/30
- TRAINED: 0/30
- BASE + runtime: 17/30
- TRAINED + runtime: 23/30

Blinded semantic review:
- BASE: 1/30
- TRAINED: 1/30
- BASE + runtime: 17/30
- TRAINED + runtime: 23/30

The runtime-bearing condition counts reproduce exactly. The only disagreement is one certificate-deployment async-acceptance case that the blind judge accepts in both unguided BASE and TRAINED, moving each from 0/30 to 1/30.

## Interpretation

The independent/blinded semantic pass supports the same narrow architecture conclusion as the internal development review:

`trained prior + explicit runtime effect-verification contract`

The runtime rule remains load-bearing. The H07 adapter alone does not reliably reconstruct the rule on this fresh family holdout.

The trained+runtime condition remains directionally better than base+runtime (10 discordant wins versus 4), but the paired difference is not statistically decisive at conventional thresholds (two-sided p ≈ 0.1796).

## Hostile review / claim ceiling

This review is independent of the Qwen subject and condition labels were hidden during judgment, but it is not an independently designed benchmark: the packet supplied the frozen rubric, expected action, and required/forbidden propositions, and the reviewing model had broader project context before condition unblinding.

Therefore this result supports semantic replication of the frozen rubric, not universal H07 qualification.

It does **not** establish:
- weights-only H07;
- general effect-verification ability outside this ontology;
- deployment, promotion, activation, or Vera Mono runtime consumption;
- statistical proof that the adapter improves the runtime-policy condition.

Strongest supported statement:

`On the frozen 30-case family holdout, blinded semantic review independently reproduces the 17/30 BASE+runtime and 23/30 TRAINED+runtime result. The explicit runtime verification contract is load-bearing; the adapter is a complementary development candidate, not a standalone qualified mechanism.`
