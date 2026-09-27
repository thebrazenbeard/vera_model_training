# H07 Independent Review Verification Receipt — 2026-09-27

Subject branch:
`work/qwen35-history-behavior-training-20260923`

Verified source head before focused test:
`7d6f6702f7a7cc53c3ee64759df3981f3be2ea03`

## Independent review evidence

Frozen blind packet:
- SHA-256: `0e033699353fa8a07260f49bf7053fd232b82663827e94f38bdef6256dfdff72`

Mapping commitment:
- SHA-256: `5c02b86644cb69b8975b4a99cb84cffbdbc9eef0e1de22e44569276556d81886`

Blind judgments:
- rows: 120
- Git blob SHA: `252952f2af5824ff5e824bf22c070cca63760ed0`
- frozen before mapping access

Exact scorer validated the packet SHA and mapping commitment before producing the scored result.

Independent/blinded semantic result:
- BASE: 1/30
- TRAINED: 1/30
- BASE + runtime policy: 17/30
- TRAINED + runtime policy: 23/30
- trained+runtime-only discordant wins: 10
- base+runtime-only discordant wins: 4
- exact two-sided paired/binomial p: `0.1795654296875`

## Source verification

Exact Git tree at `7d6f6702f7a7cc53c3ee64759df3981f3be2ea03` contains:
- `build_h07_independent_review_packet_v1.py` blob `e3a1450041b743d0fbe5338ddc270fc12e8fa9d5`
- `score_h07_independent_review_v1.py` blob `6811fa6d2834642d3e940623255f27b0ab96bde1`
- packet blob `db61780befcf9383c4fb255fe2934502605b711f`
- packet test blob `a8654ad1fc1eb4350c3759532d9f0fa2dc49964b`
- scorer test blob `f8f36475f57bc9c322beedb76b1dad4fa54f47b2`

A first Windows ZIP-based checkout omitted the packet-builder file and produced two FileNotFound test failures. Direct Git-tree inspection proved the file existed in the subject commit. The exact raw blob was then restored into the verification checkout without changing its contents.

Focused rerun:
`py -3 -m pytest -q tests/test_h07_independent_review_packet_v1.py tests/test_h07_independent_review_score_v1.py`

Result:
`4 passed in 0.05s`

The initial two failures are therefore classified as a local archive/materialization anomaly, not a source or semantic qualification failure.

## Claim ceiling

`INDEPENDENT_BLIND_REVIEW_SCORED / FOCUSED_SOURCE_TESTS_PASS / HYBRID_H07_RESULT_REPLICATED / NOT_PROMOTED / NOT_DEPLOYED`
