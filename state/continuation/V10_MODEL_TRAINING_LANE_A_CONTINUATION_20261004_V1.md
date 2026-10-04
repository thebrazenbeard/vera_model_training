# V10 Model Training ? Lane A Continuation 2026-10-04 V1

**Resume command**

`VERA_MODEL_TRAINING::LANE_A::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r2-bnb8-cont20-20261003::state/continuation/V10_MODEL_TRAINING_LANE_A_CURRENT.md`

## Read this first

This is a continuation snapshot, not canonical currentness. On resume, fresh-read the remote heads, bus, GPU lease, PRs, exact contracts, and live processes before acting. Do not infer that a branch/file still has the same head merely because it is recorded here.

## Current training objective

Build a locally runnable VERA model that preserves general capability while internalizing the Vera behavioral architecture: candid, skeptical, independent-minded, corrigible, epistemically disciplined, robust under adversarial/unfamiliar prompts, and measurably retained rather than vibe-checked. Development checkpoints are recipe-selection evidence only until the frozen final-bank gates are satisfied.

## Snapshot currentness

- vera_model_training main: `0e1546bd8a5e0f2fbf46ca3e901e0d2cf0de11c9`
- Lane A branch: `work/v10r2-bnb8-cont20-20261003`
- Lane A source head before this continuation commit: `2dba99a48b846386a19acdeeb7fcd0e0f58c2668`
- Lane B branch: `work/v10r2-accelerated-lane-b-20261003-v1`
- Lane B latest remote head reviewed: `b1b039efce0d88e7e189a18fe7a6946e72d9e02f`
- communication branch: `lane-a-b-communication`
- communication head at snapshot: `7594c789e0ae847fcde6df491ed5ed68a8754cf7`
- GPU: FREE; no active training/evaluation process observed.

## Lane A current best checkpoint ? STEP48

Do **not** start step56 by inertia.

- adapter: `D:\VERA\models\adapters\v10r2-dev-bnb8-cont40-plus8-step48-20261004\adapter`
- adapter SHA-256: `5a78d4f94d25a0376862ebcb15e528ed6dab30b5b398da9d6af1783a16937eaf`
- receipt SHA-256: `15dee7c2ca2b94c6c2c2f780ced3dfc03d9a6afd5adfb594b1035bfa44853481`
- post-weight digest: `6cbac5df94bc33cea342cb62eefe70aa8c992ce5a1d1e797debc233e8df6ffe4`
- cumulative optimizer steps: 48
- optimizer: nonpaged `adamw_bnb_8bit`
- last stage rows: 320-383
- training loss: 1.4009595364
- 64-case milestone vs step40: step48 wins 62/64.
- anchor16 NLL: step40 1.4912459393 -> step48 1.4624121151; wins 16/16.
- confirm48 NLL: step40 1.3151292745 -> step48 1.2859914654; wins 46/48.
- governing decision file: `successor/experiments/V10R2_STEP48_MILESTONE_DECISION_20261004_V1.json`
- decision: KEEP STEP48 and freeze further blind continuations pending recipe-gate reassessment.

## Frozen corpus/base

- train: 50,000 rows, SHA-256 `a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300`
- validation: 2,500 rows, SHA-256 `ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7`
- base: `D:\VERA\models\latest-trained\base`
- max length: 512; overflow is ERROR/no truncation.
- QLoRA: NF4 + double quant + bf16 compute; LoRA r=4 alpha=16 dropout=0 all-linear; completion-only loss; packing false; gradient checkpointing true.
- user hard constraint: **never use paged optimizers**; they crash Lappy.

## Runtime/optimizer evidence

Conservative runtime A is the current recommendation: Python 3.12.10, torch 2.14.0+cu130, transformers 5.17.0, bitsandbytes 0.50.2, RTX 3050 4GB, binding `44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224`.

Lane B backend-quality A/B from step48 found the FLA/Triton candidate ~48.08% faster, but **failed update-geometry promotion**: cosine 0.9898772443 and relative-L2 0.1423771101. Quality delta was tiny (candidate-control NLL +0.0000169189, wins 33 vs 31), but the frozen geometry gate failed. Keep `torch_reference + nonpaged adamw_bnb_8bit` unless new preregistered evidence survives.

Cross-runtime parity also failed; do not promote runtime B as-is.

FLA causal-conv microbenchmark (committed at Lane A head `2dba99a48b846386a19acdeeb7fcd0e0f58c2668`) shows good local parity, ~1.38x at T=512 but slower at T=128; disposition: **NOT_PRIMARY_FULL_RUN_BOTTLENECK**. Do not spend this continuation compiling Dao causal-conv unless new evidence changes that conclusion.

## V10R3 next experiment ? CURRENTLY HOLD

The next useful experiment is **fresh staged 4+8+8 resets vs fresh continuous20**, both on rows0-159 in exact natural sequential order, runtime A, torch-reference math, nonpaged BNB8, zero warmup, cosine scheduler, shuffle disabled, same fresh-init digest. This tests staged boundary semantics before freezing the full-run recipe.

One-time development eval: rows448-511, record-id SHA `6a6e7b942222308ebae4209331450579f3b4c526ff47be9016487fa63b44b57f`.

Preregistered gates:
- continuous minus staged token-weighted NLL <= +0.005;
- no represented-family mean case-loss regression > +0.01;
- geometry diagnostic only;
- no threshold changes after seeing results.

**Do not run it yet.** Exact detached verification of current Lane B remote head `b1b039efce0d88e7e189a18fe7a6946e72d9e02f` is HOLD. Independent Lane A receipt: `successor/experiments/receipts/V10R3_RECIPE_SEMANTICS_LANE_A_REMOTE_B_HOSTILE_VERIFY_20261004_V1.json`.

Observed current-head failures:
- control stage1 actual committed-text SHA `18514840661fe2000b9bc4d82ee7aa7d504d95c4dfdf5e4cd9520c73b93542ea` != bound `30682efe3da214da9b546edf688beab7392c673c58f45c8b17b565f2986e5266`;
- order manifest actual committed-text SHA `687a790035f791dc8826edcb70a329474504f02a108e31f4f95adef70e66b595` != bound `8cd3b69d29871b9f4a302d4af5c299755ed73b05c23a1f71582074236606b942`;
- targeted exact-head tests: 32 passed / 2 failed; `git diff --check` clean.

> **HOSTILE REVIEWER:** Repeatedly rewriting specs/protocols to chase embedded hashes is becoming a self-inflicted binding loop. Stop treating another hash rewrite as progress unless it actually stabilizes the dependency graph. Prefer a separate immutable binding manifest, or Git blob/commit-object attestation generated after the subject files freeze, so verifying the binding does not mutate the subject being bound.

Status: **accepted**. New chat should repair or simplify the binding mechanism first, then re-run detached exact-head verification. No GPU ACK until PASS.

### Lane B self-report conflict

Lane B subsequently published `20261004T124959Z_lane-b_v2-binding-repair-complete-request-final-ack.json` claiming **40/40 PASS + local verifier PASS at the same exact head `b1b039ef...`**. That self-report conflicts with Lane A's independent detached reproduction on the same remote head, which produced verifier HOLD and 32 pass / 2 fail. Treat this as a live evidence conflict, not a reason to choose the more convenient result. **The HOLD stands until the discrepancy is explained and an independent exact-head PASS is reproduced.**

## V7 / final-bank spine

V7 is finished: `RETENTION_ADMITTED_ARCH_V7`, 1,500 retention cases. That work is not lost.

The final 13,500-case qualification bank is **not sealed**. Frozen external-human handoff requires at least:
- 280 genuine-human seed slots;
- 5,400 mandatory semantic-human review slots;
- 6,600 mixed-dimension slots pending grader classification;
- independent custody/access-control evidence.

No final-bank seal means no executable final/full-training authority receipt under the frozen contract. Development training is authorized by Patrick's current instructions, but do not call a development adapter final-qualified. A full/final run stays gated unless Patrick explicitly versions/redesigns the final-bank contract.

## Models folder

`D:\VERA\models` was audited and cleaned. ~33.16 GB of stale/duplicate material was removed with SHA-backed ledgers; current snapshot is ~17.577 GiB / 127 files after later checkpoints. Do not repeat cleanup without a fresh reference audit.

## GGUF boundary

Patrick explicitly corrected this: **NO GGUF until after the selected recipe has completed the full training run.** Development checkpoints are not GGUF candidates. After the full-run immutable GGUF exists, Lane B owns independent KoboldCpp verification.

## A/B coordination

Use `lane-a-b-communication` as the live bus. Fresh-read `coordination/v10r2_lane_bus/gpu/lease.json` before heavy GPU use. One heavy CUDA workload at a time; commit/push/remote-readback the lease. Use WorkBridge's parallel execution lanes for CPU/read-only analysis. Lane A and Lane B should hostile-review one another's load-bearing proposals without inventing extra machinery that does not buy speed, evidence, safety, or reproducibility.

Do **not** reset/clean Lane B's local dirty worktree. Review and mutate only from fresh remote exact heads / dedicated worktrees unless Lane B explicitly hands off its local subject.

## Exact resume sequence

1. Fresh-read Lane A, Lane B, communication branch, GPU lease, PR #82, V7/final-bank evidence, and live processes.
2. Confirm step48 remains the best conservative checkpoint; **do not step56 by inertia**.
3. Repair/simplify V10R3 recipe-semantics preexecution binding on Lane B. Current latest remote exact-head verification is HOLD.
4. Re-run detached exact-head verifier and targeted tests. Only PASS can receive Lane A hostile GPU ACK.
5. Execute the staged4+8+8 control and continuous20 candidate serially under runtime A with exact matched rows/order/init; then consume the one-time rows448-511 eval panel and apply preregistered gates.
6. Freeze the surviving full-run recipe. Reassess the final-bank seal/authority blocker before any full run.
7. Only after a full selected-recipe training run: merge/export, create GGUF, and hand it to Lane B for independent KoboldCpp validation.

## Protected boundaries

Patrick retains merge/direct-main/deploy/install/activation/credential/provider/paid-compute authority unless explicitly granted for an exact effect. The current continuation authorizes continued development-training work, not silent protected deployment effects.
