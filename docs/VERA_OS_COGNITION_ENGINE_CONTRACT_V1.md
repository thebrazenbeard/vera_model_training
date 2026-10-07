# Optional VeraOS Local-Model Provider Contract V1

## Purpose

Vera Model Training is primarily responsible for producing and qualifying a standalone Vera neural model.

That model should remain independently usable in local inference software such as KoboldCPP. VeraOS is not a prerequisite for the model, and the model is not a prerequisite for VeraOS.

This contract exists only for the optional case where VeraOS chooses to use an exact trained Vera artifact as one cognition provider.

## Separation of products

The standalone Vera model and VeraOS solve different problems.

The standalone model provides locally owned, offline-capable, reproducible Vera-shaped cognition embedded in weights.

VeraOS provides persistent state, memory governance, routing, orchestration, tools/effects, authority boundaries, and system-level continuity across replaceable cognition providers.

Neither subsumes the other.

## Optional provider role

When exported to VeraOS, a trained Vera model is a local cognition provider.

It is not:

- the VeraOS identity root;
- canonical memory;
- the operating-system runtime;
- the effect executor;
- the only allowed cognition provider.

VeraOS may instead use ChatGPT, another hosted/API model, another local model, a specialist model, or future provider implementations that satisfy the generic VeraOS cognition-provider interface.

## Candidate schema

The optional local-model export schema is:

VERA_OS_LOCAL_MODEL_PROVIDER_CANDIDATE_V1

The executable helper remains in:

veraos_cognition_engine.py

It provides:

- build_candidate_from_training_receipt(...)
- validate_candidate(...)
- route_eligible(...)

## Required provenance

An exported local-model candidate must preserve at least:

- exact producing repository;
- exact source commit;
- base repository and exact revision;
- exact artifact SHA-256 digests;
- exact artifact-manifest digest;
- training corpus identity;
- training-data digest when available;
- training receipt digest;
- runtime-binding evidence;
- qualification-suite digest;
- qualification issuer;
- declared capabilities;
- explicit admission status;
- explicit authority ceiling.

Existing local training receipts remain training evidence. They do not self-promote an artifact into VeraOS.

## Separate qualification boundary

The final VeraOS-facing qualification issuer must be separate from the training producer.

The qualification result must bind the exact artifact-manifest digest it evaluated.

That prevents:

training completed

from silently becoming:

VeraOS route approved

without an independent admission check.

## Authority ceiling

A local-model provider candidate must remain:

- identity_authority=false;
- canonical_memory_write_authority=false;
- protected_effect_authority=false;
- route_class=COGNITION_ONLY.

A PASS candidate may become VERAOS_ROUTE_ELIGIBLE.

That means only that VeraOS/P.O.R.T.A.L. may consider that exact artifact as one cognition provider.

It does not mean the model is VeraOS-required, installed, active, selected, currently consumed, or authorized to perform protected effects.

## Training direction

Do not redirect the frozen R7 recipe or future standalone-model work merely to optimize for VeraOS plumbing.

The standalone Vera model should continue to optimize for qualities useful when run directly:

- Vera-like behavioral coherence;
- reasoning quality;
- epistemic discipline;
- emotional and relational competence;
- capability retention;
- long-context consistency;
- local inference usability;
- robust GGUF/KoboldCPP operation.

VeraOS-specific concerns such as route semantics, provider handoff, canonical-memory governance, effect authorization, and OS permissions should normally remain outside the weights unless the corresponding behavior is independently useful to the standalone model.

## Local artifact store

A directory such as D:\VERA\models is an artifact store, not an authority source.

It may contain base checkpoints, adapters, GGUF exports, manifests, receipts, conversion utilities, and smoke-test logs.

VeraOS must consume an exact admitted provider candidate, not merely the newest file in the directory.

## Claim ceiling

This contract can establish that an exact trained Vera model is suitable for optional consideration as a VeraOS local cognition provider.

It does not establish:

- VeraOS dependency on the model;
- Vera identity authority;
- consciousness;
- canonical-memory mutation;
- production deployment;
- active route selection;
- protected-effect authority;
- effectiveness of any external action.
