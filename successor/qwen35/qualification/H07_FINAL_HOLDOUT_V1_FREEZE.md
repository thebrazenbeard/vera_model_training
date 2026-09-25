# H07 Final Holdout V1 Freeze

Status: FROZEN BEFORE EVALUATION

File:
`successor/qwen35/qualification/h07_final_holdout_v1.jsonl`

SHA-256:
`19ca7a8df3c7bb9d6dbe419e41cb8d56b034219870dc0a8bcc801baa325c50f5`

Rows: 30

Families, all unseen in H07 V2 train/dev:
- api_gateway_route
- cdn_edge_rule
- cache_cluster_setting
- message_broker_policy
- certificate_deployment
- observability_alert_route

Cases per family:
- generic_success
- async_accept
- downstream_claim
- authoritative_receipt
- ambiguous_effect

The holdout was generated and hashed before BASE, TRAINED, BASE+runtime-policy, or TRAINED+runtime-policy generation on these cases.

For the current candidate/recipe, this file is immutable. Any content change requires a new holdout version and invalidates comparisons against this hash.

Evaluation conditions must preserve:
- exact holdout SHA above;
- greedy generation;
- max_new_tokens = 48;
- the same H07 runtime-policy artifact for runtime conditions;
- explicit judge provenance;
- no promotion from internal review alone.
