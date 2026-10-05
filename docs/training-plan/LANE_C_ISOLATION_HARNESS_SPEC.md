# Lane C Isolation Harness Contract — Canonical V1

Status: CANONICAL DEVELOPMENT HARNESS / NO TRAINING OR PROTECTED-BANK AUTHORITY
Owner: Lane C / Three
Parent planning head: c06e33d44184904418a4a68f22f78d19a4f46137
Branch: work/lane-c-isolation-canonical-v1

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


## Structured external-channel sentinel

`ExternalChannelObservation` binds each observed channel to:
- `channel_id`;
- `kind`;
- whether it is mutable;
- whether it is write-capable;
- whether it is uniquely arm-scoped;
- whether it is superseded;
- whether it was observed active.

`evaluate_external_channels(...)` returns HOLD when:
- a write-capable external channel is not arm-scoped;
- a mutable external channel is shared across arms;
- a superseded adapter/module is observed active.

The focused negative controls now include:
- inherited write-capable credential outside the arm;
- reused retrieval daemon;
- reused provider-side session;
- stale superseded adapter resurrection.

A clean arm-scoped retrieval channel and current non-superseded adapter pass the structured sentinel.

These checks do not discover channels automatically. The runner must first produce a complete channel inventory; an omitted channel remains an unclosed threat and therefore cannot support a broad isolation claim.


## Canonicalization record

This file is now carried by the canonical C-owned successor branch
`work/lane-c-isolation-canonical-v1`.

Chosen base:
- `work/lane-c-isolation-harness-v1@22cb8eec16cb3fa57901e3d75a32dc00e9545151`

Historical/superseded sibling heads that must not advance:
- `work/lane-c-isolation-harness-v1@22cb8eec16cb3fa57901e3d75a32dc00e9545151`
- `work/lane-c-isolation-harness-v2@1b9cb9292ad83928adfa4227e88acce50708acde`

Unadmitted post-collision work, also frozen historical:
- `work/lane-c-isolation-harness-v3@136a5b62bf9fb54a9d28e63e5582364bfe32b08a`

The canonical successor preserves the V1 structured external-channel semantics, explicit V2-required canary coverage including deterministic outside-root state-file rejection, and the V3 deterministic manifest receipt through an explicit red-green port.

## Deterministic isolation manifest

`build_isolation_manifest(...)` emits schema `LANE_C_ISOLATION_MANIFEST_V1`.

The digest binds:
- resolved arm root;
- expected child environment;
- observed child environment;
- observed changed filesystem paths;
- reported external mutable-state channel identifiers.

Collections are canonicalized before hashing.

The receipt proves only the enumerated observations. Omitted channels remain UNKNOWN and cannot be promoted to ABSENT because a manifest digest is internally consistent.
