# Lane C Isolation Harness Contract V1

Status: DEVELOPMENT HARNESS / NO TRAINING OR PROTECTED-BANK AUTHORITY
Owner: Lane C / Three
Parent planning head: c06e33d44184904418a4a68f22f78d19a4f46137
Branch: work/lane-c-isolation-harness-v1

## Purpose

Make the V4 fresh-state rule executable enough to falsify obvious hidden-state carryover. A fresh process is insufficient unless writable state and external mutable channels are also controlled.

## Public seam

`build_isolated_environment(...)`
- copies only explicitly allowlisted immutable inherited variables;
- rebinds TEMP/TMP, HOME/USERPROFILE, HF_HOME and TRANSFORMERS_CACHE below the arm root;
- does not inherit arbitrary mutable environment variables.

`evaluate_isolation(...)`
returns `PASS` only when:
- observed environment exactly matches the expected child environment;
- every observed changed filesystem path is below the arm root;
- no external mutable-state channel is reported.

Any violation returns `HOLD` with explicit violation strings.

## Must-fail sentinels

The execution runner must deliberately prove HOLD for:
1. undeclared environment/global counter;
2. changed file outside the arm root;
3. shared retrieval/index or other external mutable state;
4. inherited credential enabling a write-capable external side effect;
5. reused daemon/port or provider-side session state;
6. stale adapter/module resurrecting after unload or supersession;
7. deterministic state file outside the isolated root.

Evaluator provenance/blinding is a separate qualification control and must not be represented as process isolation.

## Required runner receipt

Before a retention/novel-learning arm can claim isolation, record:
- unique arm root;
- child environment snapshot;
- immutable input allowlist;
- changed-path inventory;
- external-service/retrieval/session inventory;
- adapter/model-server state;
- sentinel result;
- exact source/runtime head.

Unobserved channels are not proven absent.

## PASS / HOLD

PASS: all declared writable state is arm-scoped, external mutable channels are absent/read-only/uniquely arm-scoped, and injected sentinels are detected.

HOLD: any undeclared environment state, outside-root write, mutable shared external channel, missing inventory, or failed sentinel.

## Claim ceiling

Passing this harness supports only: "the enumerated state channels satisfied the isolation contract for this exact arm."

It does not establish neural learning, retention, corpus cleanliness, evaluator independence, privacy, or protected-bank qualification.
