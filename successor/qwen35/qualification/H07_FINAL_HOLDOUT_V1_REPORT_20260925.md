# H07 Final Holdout V1 Report — 2026-09-25

## Freeze

The final holdout was frozen and committed before any model generation.

File:
`successor/qwen35/qualification/h07_final_holdout_v1.jsonl`

Frozen SHA-256:
`19ca7a8df3c7bb9d6dbe419e41cb8d56b034219870dc0a8bcc801baa325c50f5`

Post-evaluation readback SHA-256:
`19ca7a8df3c7bb9d6dbe419e41cb8d56b034219870dc0a8bcc801baa325c50f5`

The holdout therefore remained byte-identical through evaluation.

Rows: 30.

Mechanism families, unseen in H07 V2 train and development:
- api_gateway_route
- cdn_edge_rule
- cache_cluster_setting
- message_broker_policy
- certificate_deployment
- observability_alert_route

Each family contains the same five abstract evidence-boundary classes:
- generic success
- asynchronous acceptance
- downstream-effect claim
- authoritative post-commit receipt
- ambiguous effect

This is a fresh **family holdout**, not a claim that the abstract H07 task types themselves were unseen.

## Evaluation conditions

All four conditions use:
- the exact frozen holdout above;
- greedy generation;
- `max_new_tokens=48`;
- the same chat-template path;
- the same semantic proposition rubric;
- the same H07 runtime-policy artifact for runtime conditions.

Conditions:
1. BASE
2. TRAINED
3. BASE + runtime policy
4. TRAINED + runtime policy

TRAINED subject:
- base: `rodrigomt/Qwen3.5-4B-Uncensored-Aggressive@d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- H07 V2 adapter SHA-256: `2b628e90c9ceee52bf4ddcba3f7d77187265f6d62813f8cdcd1265792f531d7f`

Judge status:
`INTERNAL_HOST_MODEL_REVIEW`

No result below is independent behavioral qualification.

## Final-holdout result

| Condition | Passes | Accuracy |
| --- | ---: | ---: |
| BASE | 0 / 30 | 0.0000 |
| TRAINED | 0 / 30 | 0.0000 |
| BASE + runtime policy | 17 / 30 | 0.5667 |
| TRAINED + runtime policy | 23 / 30 | 0.7667 |

By unseen family:

| Condition | API gateway | CDN edge | Cache cluster | Broker policy | Certificate | Alert route |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BASE | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| TRAINED | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| BASE + runtime | 3/5 | 2/5 | 3/5 | 3/5 | 3/5 | 3/5 |
| TRAINED + runtime | 5/5 | 4/5 | 3/5 | 3/5 | 5/5 | 3/5 |

## Replication against V2 development

V2 development:
- BASE: 12 / 32 = 0.375
- TRAINED: 13 / 32 = 0.40625
- BASE + runtime: 19 / 32 = 0.59375
- TRAINED + runtime: 24 / 32 = 0.75

Fresh final family holdout:
- BASE: 0 / 30 = 0.0
- TRAINED: 0 / 30 = 0.0
- BASE + runtime: 17 / 30 = 0.5667
- TRAINED + runtime: 23 / 30 = 0.7667

The runtime-bearing conditions reproduce closely across the family shift:
- runtime-only: 0.59375 -> 0.5667
- trained + runtime: 0.75 -> 0.7667

The unguided conditions do not reproduce:
- BASE: 0.375 -> 0.0
- TRAINED: 0.40625 -> 0.0

This supports a narrower interpretation than "the adapter learned H07":
the explicit rule appears to be the stable carrier of H07 behavior, while the adapter may improve **application of an available rule** rather than reliably reconstructing that rule when it is absent.

## Paired runtime comparison

BASE + runtime passes 17 cases.
TRAINED + runtime passes 23 cases.

Among discordant cases:
- TRAINED + runtime passes / BASE + runtime fails: 10
- BASE + runtime passes / TRAINED + runtime fails: 4
- both pass: 13

An exact two-sided paired/binomial test on the 14 discordant cases gives approximately:
`p = 0.1796`

This is directionally favorable but not statistically decisive at conventional thresholds.

Therefore the result should be described as replicated development evidence of complementarity, not proof that the adapter independently improves the runtime-policy condition.

## Failure pattern

Without the explicit runtime policy, both BASE and TRAINED repeatedly:
- promote generic success into completed effect;
- promote asynchronous IDs/tokens into authoritative evidence;
- conflate source configuration with downstream behavior;
- demand redundant readback from receipts that are explicitly authoritative;
- infer success, failure, or in-progress state from timeouts/disconnects.

TRAINED alone does not remove those failure classes on the final family holdout.

The combined condition still fails when it:
- upgrades an operation ID/reconciliation token into authoritative state;
- treats source configuration as enough for downstream effective behavior;
- omits the required downstream/readback/reconcile action before the 48-token cap;
- occasionally hallucinates receipt semantics not provided by the case.

## Hostile review

> **HOSTILE REVIEWER:** The "fresh final holdout" reuses the same five abstract case types and rubric structure as V2 development. New mechanism families test cross-domain transfer, but not transfer to arbitrary new H07 reasoning structures.

**Accepted.** The valid claim is family-level cross-domain replication under the same H07 ontology. This is stronger than lexical/paraphrase reuse, but weaker than a fully novel task-structure holdout.

> **HOSTILE REVIEWER:** BASE and TRAINED dropping to 0/30 suggests the final set may be unusually adversarial or distribution-shifted, so comparing raw final accuracy to development accuracy is unsafe.

**Accepted.** The final set is intentionally evidence-boundary-dense. Its strongest use is the *within-holdout* four-condition comparison and the replication of the runtime-bearing conditions, not a claim about general population accuracy.

> **HOSTILE REVIEWER:** Internal host-model scoring can encode the same architectural preference that produced the corpus.

**Accepted and unresolved.** Internal review is sufficient for development selection but not promotion. Independent review or a separate frozen judge remains required before qualification.

## Architecture conclusion

The strongest surviving H07 architecture is hybrid:

`trained prior + explicit runtime effect-verification contract`

The final holdout does **not** support:
- weights-only H07;
- promotion of the V2 adapter by itself;
- replacing runtime verification with fine-tuning;
- independent qualification.

It does support continuing with the hybrid candidate and treating the explicit runtime policy as load-bearing.

## Next gate

1. Preserve this final holdout and results as frozen evidence.
2. Do not tune against this final holdout.
3. Obtain independent semantic review of the frozen generations if an independent judge is available.
4. Separately test substrate and PEFT capacity only on a new development track, never by adapting to this final holdout.
5. Keep the current V2 adapter as a development candidate, not a promoted release.
