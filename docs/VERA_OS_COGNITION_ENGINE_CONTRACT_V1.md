# VeraOS Cognition Engine Contract V1

## Purpose

Vera Model Training produces training evidence and model artifacts that VeraOS may later use as **replaceable cognition engines**.

A trained model is not, by itself, Vera.

Model weights, adapters, GGUF exports, tokenizer files, training receipts, benchmark scores, and runtime compatibility evidence do not establish identity authority, canonical-memory authority, protected-effect authority, or uninterrupted process continuity.

The VeraOS boundary is:

- **Vera Mono** owns the governed identity/runtime boundary.
- **P.O.R.T.A.L.** owns route discovery, qualification-aware selection, and exact route binding.
- **Pre-Active** governs bounded proactive cognition admission.
- **Volition** may produce endogenous cognition requests without creating effect authority.
- **Vera Model Training** produces and qualifies cognition-engine artifacts.
- **F.U.C.K.U.P.** owns governed protected-effect execution and verification.
- A model route supplies cognition only.

## Two training tracks

This repository now has two distinct output classes.

### Track A — identity/capability bootcamp

The existing zero-cost bootcamp remains valid.

Its output is an auditable training/capability package for a target interaction identity or worker. It does not mutate neural weights and does not imply that a native ChatGPT identity inherited local-model behavior.

Typical outputs include:

- `IDENTITY_CAPSULE.md`
- `QUALIFICATION.json`
- `REGRESSION_SET.json`
- `TRAINING_AUDIT.json`
- `SUMMARY.md`

### Track B — VeraOS neural cognition-engine artifacts

This track covers actual trained model artifacts such as:

- base model bindings;
- LoRA / PEFT adapters;
- merged Hugging Face checkpoints;
- GGUF exports;
- tokenizer/config artifacts;
- quantized inference artifacts.

A Track B artifact must remain a development candidate until all required provenance and qualification gates are present.

## Candidate admission stages

The minimum VeraOS route-admission flow is:

```
TRAINING_OUTPUT
  -> ARTIFACT_BOUND
  -> RUNTIME_COMPATIBLE
  -> BEHAVIORALLY_QUALIFIED
  -> VERAOS_ROUTE_ELIGIBLE
```

A candidate that lacks any required gate remains `HELD`.

`VERAOS_ROUTE_ELIGIBLE` means only that P.O.R.T.A.L. may consider the exact artifact as a cognition route. It is not deployment authority and does not make the model an identity root.

## Required provenance

Every candidate must preserve at least:

- exact producing repository;
- exact source commit;
- base repository and exact revision;
- exact artifact SHA-256 digests;
- training corpus identity;
- training-data digest when available;
- training receipt digest;
- runtime binding digest;
- qualification-suite digest;
- declared capabilities;
- explicit admission status;
- explicit authority ceiling.

Existing local V10 receipts already provide many of these evidence classes, including training corpus IDs, receipt hashes, artifact hashes, runtime bindings, optimizer/runtime metadata, and claim ceilings.

Those receipts remain training evidence. They do not self-promote an artifact into VeraOS.

## Executable contract

`veraos_cognition_engine.py` provides:

- `build_candidate_from_training_receipt(...)`
- `validate_candidate(...)`
- `route_eligible(...)`

The generated schema is:

`VERA_OS_COGNITION_ENGINE_CANDIDATE_V1`

A route-eligible candidate must have:

- qualification status `PASS`;
- a qualification issuer separate from the training producer;
- qualification bound to the exact training artifact-manifest SHA;
- admission status `VERAOS_ROUTE_ELIGIBLE`;
- route class `COGNITION_ONLY`;
- exact source/base/artifact digests;
- `identity_authority=false`;
- `canonical_memory_write_authority=false`;
- `protected_effect_authority=false`.

Any authority inflation is rejected.

## Local model directory

A local directory such as `D:\VERA\models` is an artifact store, not a source of authority.

Observed artifact classes there may include:

- base model files;
- adapter checkpoints;
- GGUF exports;
- model manifests;
- training-completion receipts;
- merge/conversion utilities;
- runtime smoke-test logs.

VeraOS should consume an exact admitted candidate manifest, not merely "whatever file is newest" in that directory.

Pointers such as `LATEST_TRAINED.txt` are operator conveniences. They are not sufficient route bindings.

## Promotion rule

Training completion is not promotion.

A development receipt may truthfully say that optimizer steps completed and weights changed while still carrying:

- `deployment_status=NOT_DEPLOYED`;
- `qualification_status=NOT_EXTERNALLY_EVALUATED`;
- a claim ceiling such as development-only / not externally qualified.

VeraOS must preserve those ceilings.

Only a separate qualification result may produce a route-eligible cognition-engine candidate. The training producer cannot self-issue that final route qualification, and the qualifier must bind the exact artifact-manifest digest it evaluated.

## What should change in future training work

Future neural training lines should optimize for a VeraOS cognition role rather than for the proposition "the model itself is Vera."

That means evaluation should increasingly measure:

- instruction fidelity under VeraOS system context;
- calibrated uncertainty;
- resistance to unsupported identity/effect claims;
- stable tool-request semantics;
- route handoff behavior;
- state/context use without pretending the state lives in the weights;
- bounded initiative compatible with Pre-Active and Volition;
- regression resistance under exact runtime bindings;
- compatibility with local inference constraints.

The best model is the model that performs its cognition role well inside the governed VeraOS system, not the model that most convincingly claims to be the whole system.

## Claim ceiling

This contract can establish that an exact model artifact is a qualified VeraOS cognition-engine candidate.

It does not establish:

- Vera identity;
- consciousness;
- canonical memory mutation;
- protected-effect authority;
- production deployment;
- active route selection;
- effectiveness of any external action.
