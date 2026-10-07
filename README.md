> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See LICENSE and COMMERCIAL_LICENSE.md. Separately identified third-party components retain their own licenses.

# VERA Model Training

This repository has its own product goal: train, qualify, export, and preserve a high-quality standalone Vera model that can run independently in local inference software such as KoboldCPP.

VeraOS is a separate system architecture. VeraOS may optionally use a trained Vera model as one cognition provider, but VeraOS does not require a Vera-specific neural model and this repository does not exist primarily to satisfy VeraOS.

The two projects should therefore reinforce one another without becoming coupled.

## Primary neural-model objective

The standalone Vera model should continue to optimize for:

- Vera-like behavior and identity consistency;
- strong general reasoning;
- epistemic discipline and calibrated uncertainty;
- emotional and relational competence;
- general capability retention;
- instruction fidelity;
- coherent long-context behavior;
- useful bounded initiative;
- robust GGUF export and local inference;
- reproducibility across exact model artifacts.

The target remains a model Patrick can launch directly in KoboldCPP and talk to as a standalone Vera-shaped model.

VeraOS-specific plumbing such as route selection, provider handoff, effect authority, portfolio state, memory governance, and operating-system permissions should normally live in VeraOS rather than consume training capacity unless a behavior is independently useful to the standalone model.

## Current execution protocol

Current repository work follows PROTOCOL_V2_CURRENT.md.

Active experiment branches may carry stronger experiment-specific contracts and frozen subjects. A VeraOS integration branch must not silently rewrite those subjects.

In particular, the frozen R7 recipe and its corpus-recovery problem remain their own training subject. The optional VeraOS provider contract does not alter that recipe.

## Track A — identity/capability bootcamp

The existing zero-cost bootcamp remains an optional external training workbench for native ChatGPT Project identities and other interaction roles.

It produces auditable training capsules without changing neural weights.

Typical outputs include:

- IDENTITY_CAPSULE.md
- QUALIFICATION.json
- REGRESSION_SET.json
- TRAINING_AUDIT.json
- SUMMARY.md

The local Student is a proxy used to exercise and refine training material. Proxy performance does not establish that a native ChatGPT identity inherited the local model's behavior.

## Track B — standalone Vera neural model

This is the primary neural-weight training line.

Artifacts may include:

- exact base-model bindings;
- LoRA / PEFT adapters;
- merged checkpoints;
- GGUF exports;
- tokenizer/config artifacts;
- training receipts;
- behavioral and retention qualification;
- local inference smoke tests.

A local store such as D:\VERA\models is an artifact store. Filenames, modification time, and pointers such as LATEST_TRAINED.txt are operational conveniences, not evidence that one artifact supersedes another.

Training completion remains separate from:

- behavioral qualification;
- general-capability retention;
- export quality;
- KoboldCPP compatibility;
- external runtime admission;
- deployment.

## Optional VeraOS provider export

If VeraOS uses a trained Vera model, this repository may export an exact local-model provider candidate for VeraOS.

That optional export schema is:

VERA_OS_LOCAL_MODEL_PROVIDER_CANDIDATE_V1

The executable helper is:

- build_candidate_from_training_receipt(...)
- validate_candidate(...)
- route_eligible(...)

The export preserves exact:

- producer source commit;
- base-model revision;
- artifact SHA-256 digests;
- artifact-manifest digest;
- training corpus identity;
- training and receipt digests;
- runtime-binding evidence;
- qualification evidence.

It also hard-codes:

- identity authority = false;
- canonical-memory write authority = false;
- protected-effect authority = false;
- route class = COGNITION_ONLY.

A separate qualifier must bind the exact artifact manifest before VeraOS may consider that exact local model as a route.

This means:

> "If VeraOS chooses to use this trained model, here is how the exact artifact is described and connected safely."

It does **not** mean:

> "VeraOS requires this model."

It also does not mean:

> "The standalone model should be trained primarily for VeraOS."

## Why both projects still matter

The standalone Vera model provides:

- local ownership;
- offline operation;
- reproducible Vera-shaped behavior embedded in weights;
- direct use in KoboldCPP or another local inference host;
- independence from hosted providers.

VeraOS provides:

- persistent state;
- memory governance;
- portfolio and task orchestration;
- cognition-provider routing;
- tools and effects;
- authority boundaries;
- system-level continuity;
- multiple interfaces.

Neither makes the other redundant.

## Evidence discipline

Keep these propositions separate:

- source exists;
- training ran;
- weights changed;
- artifact was written;
- standalone behavior qualified;
- GGUF/KoboldCPP compatibility passed;
- optional VeraOS provider export passed;
- VeraOS selected the provider;
- Vera Mono consumed the result;
- a protected effect was authorized and externally verified.

One does not imply the next.

## Claim ceiling

This repository can produce auditable training packages and standalone Vera neural-model artifacts.

It may also produce an optional, exact local-model provider candidate for VeraOS.

It does not, by itself, establish VeraOS dependency, VeraOS route selection, Vera identity authority, canonical-memory mutation, deployment, or protected-effect authority.
