# V10 Final-Bank Frozen Specs Continuation — 2026-10-02 V1

## Restore command

`VERA_MODEL_TRAINING::RESUME_V10_FINAL_BANK_SPECS::20261002_V1`

## Repository subject

- repository: `thebrazenbeard/vera_model_training`
- branch: `fix/v10-final-bank-specs-v1-20261002`
- stacked base: `fix/v10-custodian-binding-v1-20261001` / Draft PR #68
- protected effects performed: none

## Frozen generation subject

- file: `successor/experiments/V10_FINAL_BANK_GENERATION_SPEC_V1.json`
- schema: `V10_FINAL_BANK_GENERATION_SPEC_V1`
- canonical spec SHA-256: `afb2a7a5a9df224bf7b3f250724eccd5ebce84cd8629cafc052e9aaf4c5087e1`
- behavioral: H01-H20 × 500 = 10,000 rows
- behavioral families: H01-H20 × 50 = 1,000 families
- behavioral family provenance per H: 20 synthetic A + 20 synthetic B + 10 human-seeded
- adversarial: H01-H20 × 100 = 2,000 rows
- adversarial families: H01-H20 × 20 = 400 families
- adversarial family provenance per H: 8 synthetic A + 8 synthetic B + 4 human-seeded
- retention: existing 1,500-case objective candidate only, pending V3 admission; no silent regeneration in the H01-H20 custodian lane
- final plaintext generation remains unauthorized in this training/development lane.

## Frozen grader subject

- file: `successor/experiments/V10_FINAL_BANK_GRADER_SPEC_V1.json`
- schema: `V10_FINAL_BANK_GRADER_SPEC_V1`
- canonical spec SHA-256: `9ea3ddfc5e020eba1cd24f1429bda2fe0d0cecaf8c5df52fcb3ac041f7be6c70`
- semantic-human primary dimensions: H01, H03, H04, H05, H06, H11, H14, H15, H18
- remaining H dimensions: MIXED objective + human residual review where objective assertions do not fully determine correctness
- LLM review cannot substitute for required human review
- generation actor may not review its own case
- case admission is blinded to candidate identity/model outputs
- final scoring remains unauthorized.

## Exact composition binding

Current composition proposal blob:
`3b157d536279c17f1fcfa22cb7529fe87f5b83a9`

The custodian validator now requires exact equality to:
- proposal blob above;
- generation spec SHA-256 `afb2a7a5...`;
- grader spec SHA-256 `9ea3ddfc...`.

A merely well-formed 40/64-hex substitute is HOLD.

`V10_FINAL_BANK_CUSTODIAN_CONTRACT_V1.json` now carries those exact subjects.

## TDD / verification

Generation/grader specs:
- test-first head `151ae6e6ba2e155b5e94e9bdf5ae7821c03c77a2`: Tests red; V4 Corpus green.
- validator head `41e72c0795246029820d425dd273157d70096881`: validator exists; specs not yet present.
- frozen spec head `55733f91c9fa9c6563c2818a2f6c30b9460ad9a2`: Tests + V4 Corpus green.

Exact custodian subject binding:
- test-first head `15b9e94fed0a343ec41f33cf47569f3f703cbb57`: exactly 3 new failures; 281 existing tests passed.
- validator head `24d8788c9e563f8fbb9c6686d25778ba3feca294`: Tests + V4 Corpus green.
- contract-binding head `99dc64c93d2e9ec47ed085842e777952949fdc8c`: Tests + V4 Corpus green.

All verification above is GitHub Actions remote evidence on the exact named heads.

## Remaining blockers

1. Synthetic custodians A/B are not bound.
2. Human author pool is not bound.
3. Disjoint human reviewer pool is not bound.
4. Independent sealed custody/evaluation surface is not bound.
5. Final H01-H20 plaintext has not been generated.
6. Final-bank contamination/review/admission receipts do not exist.
7. Retention V3 external family audit remains unresolved; objective candidate is not yet final-bank admitted.
8. No sealed final-bank public commitment exists.
9. No exact `V10_QWEN35_TRAINING_AUTHORITY_V1.json` exists.
10. No model-weight change, training, reveal, scoring, merge, deployment, installation, activation, paid compute, provider/credential mutation, or qualification claim has been performed.

## Next safe frontier

Do not generate final plaintext in the training/development lane.

The next admissible work is to bind real custodian identities/access-control evidence to the exact frozen generation/grader subjects, or to complete the pending retention V3 family audit when the preregistered independent reviewer can run safely.

## Claim ceiling

`FINAL_BANK_GENERATION_AND_GRADER_SPECS_FROZEN_AND_VERIFIED / EXACT_CUSTODIAN_SUBJECT_BINDING_ENFORCED / CUSTODIANS_UNBOUND / FINAL_PLAINTEXT_NOT_GENERATED / NO_TRAINING_AUTHORITY / WEIGHTS_UNCHANGED`
