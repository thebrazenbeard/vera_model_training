# V3 Task 9 External Verifier — Vera Lab Review Role Binding

Status: `SOURCE_REPAIRED / LOCAL_TEST_PASS / HOSTED_CI_NOT_CLAIMED / INDEPENDENT_REREVIEW_PENDING`

Base Task 9 subject:
`cff9dcb3aa1f06aed3eae37a663d91d3a70ba77a`

## Hostile finding

`verify_local_v3_readiness()` accepted Vera Lab SOURCE and BEHAVIOR review
receipts by checking only:

- `source_commit`;
- `verdict`.

It did not bind either receipt to its declared `review_kind`.

Therefore the same SOURCE receipt could be supplied for both
`vera_lab_source_review_receipt` and
`vera_lab_behavior_review_receipt`, and the verifier returned:

`verified=True / status=VERIFIED / reasons=()`.

That collapses two independently required Task 9 receipts into one source
artifact and violates the published Task 9 independent-receipt contract.

## Frozen RED

Regression:
`tests/test_successor_v3_readiness_verifier.py::test_source_review_receipt_cannot_substitute_for_behavior_review`

Exact RED commit:
`852b15a9002d23dc2ef5ba34f8aebb8200166efb`

Fresh exact-base result:
**1 failed / 0 passed**.

## Repair

Repair commit:
`a78aa9b29ceb00b2841879e77689a30e605fa156`

The verifier now requires:

- SOURCE receipt: `review_kind == "SOURCE"`;
- BEHAVIOR receipt: `review_kind == "BEHAVIOR"`.

A role mismatch contributes
`vera_lab_review_kind_mismatch:<KIND>` and keeps the external verification
state on HOLD.

This repair does not establish receipt authenticity, reviewer identity, or
behavioral truth. Those remain external-authority/currentness questions. It
only prevents one receipt from satisfying both named gates.

## Qualification

Fresh local exact-repair evidence:

- external-verifier tests: **7/7 PASS**;
- full repository: **167/167 PASS**;
- py_compile: PASS;
- `git diff --check`: PASS.

No hosted exact-head run is claimed. The repository's private-workflow guard
remains untouched.

## Non-effects

No training, weight mutation, merge, deployment, activation, credential/provider
mutation, candidate promotion, or Task 10 start is authorized or performed.
