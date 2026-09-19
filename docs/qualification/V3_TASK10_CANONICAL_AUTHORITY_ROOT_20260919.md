# V3 Task 10 — Canonical Training Authority Root

Status: `SOURCE_REPAIRED / LOCAL_TEST_PASS / LIVE_PRIVATE_DRY_RUN_FAILS_CLOSED / HOSTED_CI_NOT_CLAIMED / INDEPENDENT_REREVIEW_PENDING`

Base Task-10 authority-hardening subject:
`9959693636986f401f5e476286f8c69b6819a436` (PR #32).

## Why PR #32 still returned

PR #32 correctly moved training authority away from a bare
`authority_kind=PATRICK_EXPLICIT` string and introduced:

- Task-9 external verifier recomputation;
- exact Task-9 receipt hashes;
- a Bus authority receipt with exact run/material/code markers;
- code-commit binding;
- output collision denial.

However, the identity of the Bus itself and the training spec remained
caller-selected.

The unit fixture demonstrated the remaining trust hole directly:
it created a new local Git repository, wrote a fake Patrick authority message,
committed it, pointed the V3 spec at that repository, and expected
`RUNNABLE`.

The `--spec` CLI also accepted any structurally valid V3 JSON path, so an
alternate spec could repin its own Bus path, branch, receipt hashes, and
material bindings.

## Frozen RED

Exact PR #32 hostile RED:
`0299af1e2f05a3c3c389cda22a15cac963f7e08c`

Two exact-base failures:

1. caller-created local Bus repository self-mints Patrick authority;
2. alternate V3 spec path repins the authority root.

Both returned `runnable=True / RUNNABLE / reasons=[]` on exact
`9959693636986f401f5e476286f8c69b6819a436`.

The older PR #30 self-minted-receipt RED remains preserved separately at
`0d9469829b680bc4969945c8be99af691a9b779e`.

## Repair

Source repair:
`24507e6f1debd7ecde78d1bbb6dc10433f31cdc1`

### Canonical spec root

V3 preflight now requires the supplied spec path to resolve exactly to:

`successor/v3_training_config.json`

It also reads that config from the current Git HEAD and compares canonical JSON
semantics. A different path or dirty semantic change fails closed as:

- `training_spec_not_canonical`;
- `training_spec_not_committed`;
- or `training_spec_git_readback_failed`.

This prevents callers from repinning receipts, repository roots, branches, or
training subjects in an alternate/dirty spec while retaining the reviewed
code HEAD.

### Canonical Bus root

Training authority now requires:

- exact branch ref `origin/bus/vera-v2`;
- local `origin` normalized to the canonical repository
  `https://github.com/thebrazenbeard/chat-communication-bus`;
- a fresh read-only fetch of `origin bus/vera-v2`;
- authority commit ancestry against that freshly fetched remote branch.

A caller-created local repository or stale/fake local ref cannot satisfy the
training authority gate.

The existing PR #32 exact Bus-file digest, authority-ref, code/run/material,
Task-9 receipt, and user-instruction marker checks remain intact.

## Qualification

Fresh source-only tests after repair:

- authority-root hostile attacks + legitimate control: **4/4 PASS**;
- Task-10 test module: **19/19 PASS**;
- full repository: **187/187 PASS**;
- py_compile: PASS;
- `git diff --check`: PASS.

### Real private control

Before the source repair, exact PR #32
`9959693636986f401f5e476286f8c69b6819a436`
was dry-run against the actual private Task-9/authorization/corpus/parent
artifacts and returned:

`RUNNABLE / reasons=[]`

Observed real receipt hashes:

- Task-9 ready receipt:
  `263fef84215bb2e2d1e00949ac39f070059de4b3697c4c4f2af7774b4bb94cba`;
- current Patrick authorization receipt:
  `a6064f299937d8da3f859310ebc42ff324cf5a195c22ca2b9e0061ee0db6d5fe`.

The authorization receipt binds exact training code
`9959693636986f401f5e476286f8c69b6819a436` and declares expiration on any
bound-subject change.

After the source repair, the same real private dry-run on
`24507e6f1debd7ecde78d1bbb6dc10433f31cdc1` correctly returns
`BLOCKED` solely on the code-authority transition:

- `training_authorization_code_commit_mismatch`;
- `training_authority_bus_binding_mismatch:training_code_commit`.

All parent, corpus, base, Task-9, and receipt digests still match.

Therefore a new exact-code Patrick authorization is required before this
successor may become RUNNABLE. This source repair does not create or infer that
authorization.

## Claim ceiling

This repair establishes source-level canonicality for the Task-10 spec and the
Bus authority repository/current branch.

It does not itself authorize:
- a weight-changing training run;
- Task 10 execution on the successor code;
- merge/deployment/runtime activation;
- model/candidate promotion;
- provider/credential mutation.

No model framework was loaded and no weights were changed during this repair.
