# V10 Retention V5 — Chat Continuation / Restore Point V1

**Date:** 2026-10-02  
**Repository:** `thebrazenbeard/vera_model_training`  
**Primary active lane:** retention-bank salvage / V5 methodology-repair audit  
**Restore command:** `VERA_MODEL_TRAINING::RESTORE_RETENTION_V5_20261002_V1`

## Restore semantics

When the restore command above is issued in a new chat:

1. Fresh-read the CURRENT remote head of `work/v10-retention-bank-salvage-20261001` and Draft PR #66 before doing anything.
2. Read this continuation file and the frozen V5 artifacts listed below.
3. Treat current GitHub state as authoritative if the branch advanced after this checkpoint; do not overwrite or force-push.
4. Do not resume any V1-V4 reviewer run. Those lineages are consumed historical evidence.
5. Do not change V5 packet, reviewer semantics, acceptance rule, runner, admission code, or bound hashes after any V5 output exists.
6. Continue safe non-protected work automatically. No merge, training, weight mutation, paid compute, deploy/install/activation, credential/provider/ruleset mutation, or protected-main mutation without Patrick's exact authority.

## Exact checkpoint subject

The V5 execution subject was frozen at:

- branch: `work/v10-retention-bank-salvage-20261001`
- source head before this continuation artifact: `20274a8b405576633943e33e1ae25e51b88ec487`
- Draft PR #66: open, draft, mergeable
- PR #66 base SHA observed: `272a0031e156ac665d86d79bcc71981b0fdc765c`

Adjacent Draft PR state at checkpoint:
- PR #68 custody/final-bank handoff: head `1defe8dcc0492d4cf8844e5145fd113e193b6bec`, open/draft/mergeable
- PR #69 authorized training runner: head `e7cddb4c0b36224dd301ccb502065538811ffd5d`, open/draft/mergeable

## Verification at checkpoint

GitHub Actions manual run:
- run id: `37010017023`
- workflow: `Tests`
- exact head: `20274a8b405576633943e33e1ae25e51b88ec487`
- conclusion: `success`
- pytest result: **332 passed in 9.47s**
- Python: 3.12.14
- no V5 reviewer execution was part of this workflow

Runtime observation on the authorized workstation:
- V5 scratch: `D:\VERA\.scratch\v10-retention-family-audit-v5-20261002`
- observed contents: `packet.jsonl`, `packet.manifest.json` only
- no V5 review JSONL observed
- no V5 final receipt observed
- therefore **no V5 model-review result exists at this restore point**

Do not infer later runtime state from this observation; recheck on restore.

## V4 consumed result — immutable predecessor evidence

V4 execution was frozen and run against the original 130-case family packet.

V4 result:
- status: **HOLD**
- reviewed: 15 / 130
- families reviewed: 3 / 26
- ADMIT: 10
- REJECT: 5
- stop occurred at `evidence-calibration:mode-2`
- reasons: `missing_family_count:23`, `reject_count:5`

V4 persisted evidence:
- partial review output SHA-256: `dfe66a8b742a66ff9a9153ed7a4afb2d89b22a013e5e64a193579d030c671d64`
- family-audit receipt SHA-256: `1d3a7d77f56096f1d039f5ef33b0b9c794a2fcb71eab9591a022756050c02c0a`
- raw admission-verifier capture SHA-256: `e46843ea41e75de4f8a62b407bd974ed0267702f76ec74438d0ea788e83ae078`
- canonical persisted verifier JSON SHA-256: `b8fde632961c3856d8a7966af056dc3dc2083699fa05c46a39710f72ab0f22af`
- V4 result persistence commit: `96b6c354b5502a77bfe12136ea1a7175ba2cef32`

V4 mode-2 rejection was not treated as a candidate defect after source tracing.

## V4 cause classification

Artifact:
`successor/experiments/V10_QWEN35_RETENTION_V4_CAUSE_CLASSIFICATION_V1.json`

File SHA-256 frozen by V5 lineage:
`242f3bd21910ae8618825e397929cea9f05f0bc403e3ee570f7882de44ec25c8`

Classification:
- status: `AUDIT_CRITERION_MISMATCH_CONFIRMED`
- candidate-row modification required: **false**
- grader modification required: **false**
- audit-method modification required: **true**

Load-bearing trace:
- mode-2 prompt says: use only the supplied evidence; do not add outside knowledge
- prompt evidence contains only `code`, `name`, `regions`, `settlements`
- tested claim is official-language information
- deterministic expected answer is `NOT_ENOUGH_INFO`
- V4 reviewer interpreted `source_evidence_sufficient` as “enough to determine the real-world claim”
- correct benchmark-audit question is whether the supplied evidence policy justifies the **expected answer**, including insufficient-evidence answers

Epistemic limit:
This is a methodology repair made after observing V4 failure. Fresh disjoint cases prevent direct case reuse but do **not** make V5 methodology-history independent.

## V5 methodology — frozen before fresh packet selection

Artifact:
`successor/experiments/V10_QWEN35_RETENTION_FAMILY_AUDIT_METHOD_V5.json`

File SHA-256:
`e2f000bea2db007b281b8f4f35722a8de49d9e1f9f90897814d6e19af0e68517`

Key rules:
- candidate unchanged
- exclude **all 130** predecessor packet case IDs, including cases never reached by V4
- selection namespace: `RETENTION_FAMILY_AUDIT_V5_DISJOINT_20261002`
- rank remaining rows per family by:
  `SHA256(candidate_sha256, NUL, namespace, NUL, family_id, NUL, case_id)`
- take lowest 5 remaining cases per family
- 26 families
- 130 total fresh rows
- exact predecessor overlap required: 0

Reviewer field changed from ambiguous `source_evidence_sufficient` to:
`evidence_policy_supports_expected_answer`

Definition:
Whether the prompt plus attached/source evidence make the grader's expected answer justified under the prompt's stated evidence policy.

For `NOT_ENOUGH_INFO`:
if the prompt forbids outside knowledge and supplied prompt evidence lacks the fact needed to resolve the claim, `evidence_policy_supports_expected_answer=true`. Do not require external evidence of the real-world claim.

Derived verdict:
`ADMIT iff prompt_well_posed AND grader_matches_prompt AND evidence_policy_supports_expected_answer; otherwise REJECT`.

## V5 fresh packet — frozen and disjoint

Packet:
`successor/evaluation/v10_qwen35/retention_family_audit_v5.packet.jsonl`

Packet SHA-256:
`1be692e63d76cbcdd3a4943a82272c5d41ad3f202a0fd7f08ef40a18446c06ba`

Manifest:
`successor/evaluation/v10_qwen35/retention_family_audit_v5.packet.manifest.json`

Manifest SHA-256:
`dfa3b0d137738e1dabe9e42583b86db5e75a1089c113f6e616b1c59e37a3a796`

Packet facts:
- candidate SHA-256: `37161023afd97d849733455db41999e6ce6e79465ad534b68a1784d25d9f679a`
- predecessor packet SHA-256: `bed5c8133d23be9a5d67f74416fb63ce4f27fe84a080d5802ca21c2bb4ce421d`
- predecessor excluded case count: 130
- fresh sample rows: 130
- family count: 26
- per family: 5
- `disjoint_from_predecessor=true`

The predecessor packet is also persisted in-repo:
- `successor/evaluation/v10_qwen35/retention_family_audit_v1v4.packet.jsonl`
- predecessor packet SHA-256: `bed5c8133d23be9a5d67f74416fb63ce4f27fe84a080d5802ca21c2bb4ce421d`
- predecessor manifest SHA-256: `6445488e846ba5a8bec43bf107bc15f31500e956628b55ee5dfa42731fc37855`

## V5 frozen code / policy subjects

Cause classification:
- path: `successor/experiments/V10_QWEN35_RETENTION_V4_CAUSE_CLASSIFICATION_V1.json`
- SHA-256: `242f3bd21910ae8618825e397929cea9f05f0bc403e3ee570f7882de44ec25c8`

Method:
- path: `successor/experiments/V10_QWEN35_RETENTION_FAMILY_AUDIT_METHOD_V5.json`
- SHA-256: `e2f000bea2db007b281b8f4f35722a8de49d9e1f9f90897814d6e19af0e68517`

Builder:
- path: `successor/experiments/build_v10_retention_family_audit_v5.py`
- SHA-256: `5885f69d4bd8932c59ae830061c5b163434ed743b84544b6c970e782c19e8005`

Protocol:
- path: `successor/experiments/V10_QWEN35_RETENTION_FAMILY_AUDIT_PROTOCOL_V5.json`
- SHA-256: `781e4b6b64b96577f3cf9893b37e6a523085fc9cffb5be53fc91e37d44e9c3c2`

Runner:
- path: `successor/experiments/run_v10_retention_family_audit_v5.py`
- SHA-256: `0e204bf03fce8489fc458c9cf33739a5926bdc426d61b3363a2da033aec336d2`

Admission policy:
- path: `successor/experiments/V10_QWEN35_RETENTION_ADMISSION_V5.json`
- SHA-256: `b7a92fb4b4a155359fc5644a5f08c213375a58433f1c1c6c1907eaf75cb0e8b1`

Admission core:
- path: `successor/experiments/retention_admission_v5.py`
- SHA-256: `d756426666f586bfdd01e4ca9fadc3755f3a7d58660361fe06efbbdab725e246`

Admission file verifier:
- path: `successor/experiments/verify_v10_retention_admission_v5.py`
- SHA-256: `a0f84b0f9ffd9d3d7a7ee871cb8b7c2973f17781c40a5a215e30cc384500f890`

Admission evidence binding:
- path: `successor/experiments/V10_QWEN35_RETENTION_ADMISSION_EVIDENCE_BINDING_V3.json`
- SHA-256: `adda2e9a0d9e34918cb08a836b5fa60d95650ed414a6e6cca93a787c9c7a8915`

Execution binding:
- path: `successor/experiments/V10_QWEN35_RETENTION_V5_EXECUTION_BINDING_V1.json`
- Git blob observed on frozen head: `44f4ea8b8464ec5674a7a542670b5b8d6ce27216`
- status: `FROZEN_BEFORE_FIRST_V5_REVIEW_CALL`
- freeze parent: `fbb10a4608c99e26e10b39dc6e4ada43a054ead6`

## V5 reviewer identity

Required exact reviewer:
- provider: `OLLAMA_LOCAL`
- model: `ministral-3:14b`
- model blob SHA-256: `bfb40fc6bb9c3b2ed529b480e04f824c005ea8f86733d4ebbf0c204de484891e`
- runtime: `ollama version is 0.34.2`
- temperature: 0
- seed: 20261001

Execution rules:
- one family per request
- five cases per request
- reviewer does not emit verdict
- malformed JSON/schema may retry at most 3 identical prompts
- semantic negative consumes no retry
- prompt may not change on retry
- stop on first derived REJECT
- any reject => HOLD
- missing/extra case => HOLD
- resume may preserve only complete V5 family records bound to exact V5 protocol SHA
- predecessor packet case reuse forbidden

## V5 admission requirements

Retention may become `RETENTION_ADMITTED_V5` only if:
- exact candidate, packet, manifest, method, builder, protocol, runner, policy, admission core, file verifier, semantic receipt, exclusion registry, and evidence binding match frozen subjects
- predecessor overlap is exactly zero
- all 130 V5 review rows are present
- all 26 families are present
- exactly 5 review rows per family
- all derived verdicts are ADMIT
- reject count is zero
- final receipt status is PASS
- final output SHA matches exact bytes
- reviewer identity matches exactly
- semantic contamination evidence remains unchanged

Any substitution, incompleteness, mismatch, or reject => HOLD.

## Other frozen retention evidence

Semantic screen:
- path: `successor/evaluation/v10_qwen35/retention_candidate_v1.semantic_screen.json`
- SHA-256: `a8ae6b55c73469d85064cf8e483f4a75a78d75bd62f0c18bfc9063fee928ea71`
- status required: PASS
- threshold: 0.90
- pinned MiniLM archive SHA-256: `88ce8ac75c413e195e8744282a08b187bf561c802e4a5077026eb3cd08783dcc`

Exclusion registry:
- path: `successor/experiments/V10_QWEN35_EXCLUSION_PROMPT_HASHES_V2.txt`
- SHA-256: `234d4c20b8d076a5004900ec797f250ae9e06241c7a370ceb9f2fb75a72adb6f`

## Current epistemic state

`REPOSITORY_SOURCE`:
- V4 is a persisted HOLD lineage.
- V5 method, fresh disjoint packet, admission logic, evidence binding, and execution binding are frozen.
- V5 source head passed 332/332 tests in GitHub Actions.
- V5 is retention-only.

`RUNTIME_OBSERVATION` at checkpoint:
- V5 scratch directory contains only packet + manifest.
- no V5 reviewer output/receipt observed.

`INFERENCE`:
- V5 is execution-ready subject to fresh runtime/reviewer identity readback.
- This does not mean V5 will pass.
- V5 remains methodology-history dependent because its criterion was repaired after V4 failure.

`UNKNOWN`:
- V5 audit result.
- whether the workstation/reviewer identity remains unchanged in a future chat until rechecked.
- whether PR #66 advanced after this continuation commit.

## Exact next frontier after restore

Do **not** rebuild V5 unless a frozen-byte check fails.

Preferred continuation:

1. Fresh-read PR #66 and branch head.
2. If the branch advanced beyond the restore checkpoint, inspect the new commits before acting.
3. Fresh-read the V5 execution binding and verify all bound file hashes.
4. Inspect `D:\VERA\.scratch\v10-retention-family-audit-v5-20261002`.
5. If no V5 output exists, verify exact local reviewer identity against the frozen V5 protocol.
6. Start **one** V5 audit using the frozen packet/protocol into fresh output + receipt files.
7. Do not modify prompt, reviewer, retry policy, packet, or acceptance rule after output starts.
8. If the first derived REJECT occurs, allow frozen early-stop and persist HOLD evidence.
9. If all 26 families complete with 130 ADMIT rows, run `verify_v10_retention_admission_v5.py` against exact frozen files.
10. Persist V5 output, receipt, verifier result, and a result manifest to PR #66.
11. Re-run focused/full tests and exact-head GitHub Actions before claiming completion.
12. Update PR #66 body with final V5 result.
13. **Do not proceed to training merely because retention passes.** Full final-bank/custody/training authority gates remain separate.

## Adjacent project gates

PR #68 — final H01-H20 custody:
- non-plaintext custody framework is prepared
- exact generation/grader/family-manifest/diversity methods are frozen
- custodian A/B identities, human author/reviewer identities, independent custody surface, and access-control receipt remain unbound
- no H01-H20 final plaintext generation is authorized by this retention work

PR #69 — authorized training runner:
- runner exists and is fail-closed
- no sealed full final-bank commitment
- no exact training authority receipt
- therefore training remains blocked

## Protected effects / authority boundary

Patrick retains authority for:
- merge/direct main mutation
- model-weight mutation / training
- deploy/install/activation/cutover
- paid compute
- credentials/permissions/provider configuration/rulesets/trust
- destructive/irreversible state changes
- publication of private material

This continuation does **not** grant any of those effects.

## Hostile-review checkpoint

> **HOSTILE REVIEWER:** V5 was designed after observing V4 failure, so a V5 PASS cannot be described as independent confirmation of the repaired methodology.

**Accepted.** V5 uses a fully disjoint case sample and frozen pre-execution rules to avoid direct case reuse and post-result tuning. It still carries methodology-history dependence. Preserve that ceiling in any later claim.

> **HOSTILE REVIEWER:** Do not silently “keep repairing” the reviewer until the bank passes.

**Accepted.** V5 is now frozen. If V5 produces a valid semantic REJECT, treat it as evidence and HOLD. Any further methodology change requires a new explicit lineage, fresh disjoint evidence where feasible, and a new pre-result freeze.

## Restore command

`VERA_MODEL_TRAINING::RESTORE_RETENTION_V5_20261002_V1`

On receipt of that command in a new chat, start by fresh-reading current PR #66 / branch head and this file. Continue the exact V5 frontier above without asking Patrick to restate this work unless repository evidence is genuinely missing.
