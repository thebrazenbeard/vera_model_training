> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See LICENSE and COMMERCIAL_LICENSE.md. Separately identified third-party components retain their own licenses.

# VERA Model Training

This repository supports two distinct but related kinds of Vera training work:

1. identity/capability bootcamps that produce auditable training capsules without changing neural weights; and
2. neural model training and qualification that produce exact model artifacts which VeraOS may later admit as replaceable cognition engines.

Neither track is an identity authority.

The VeraOS rule is:

> **Vera is the persistent governed runtime. Models are replaceable cognition engines. Training produces evidence and artifacts, not Vera identity.**

See docs/VERA_OS_COGNITION_ENGINE_CONTRACT_V1.md.

## Current execution protocol

Current repository work follows PROTOCOL_V2_CURRENT.md. That correction prevents redundant lease/permission recursion for already-assigned isolated reversible work while preserving this repository's privacy, source-grounding, qualification, zero-cost, and protected-effect gates.

Active experiment branches may carry stronger experiment-specific contracts and frozen subjects. A new VeraOS integration branch must not silently rewrite those subjects.

## Track A — Zero-cost identity/capability bootcamp

The bootcamp is an optional external training workbench for native ChatGPT Project identities and other interaction roles.

The target identity does not depend on this repository for authority, memory, or ordinary operation.

### Hard invariant: zero monetary cost

The bootcamp must not require metered model APIs or paid compute.

The default engine runs an open-weight GGUF model locally on a standard GitHub-hosted runner in this public repository. The workflow fails closed if the repository is private or if ZERO_COST is not true.

No OpenAI API key, Gemini key, Hugging Face inference key, Supabase paid compute, or other paid inference service is required. There is no paid fallback.

### What a bootcamp run does

A single bootcamp run performs externally:

1. bounded acquisition of user-selected public HTTPS sources;
2. source-grounded knowledge synthesis;
3. source-support filtering of the proposed capability map;
4. ten or more Trainer -> Student -> Examiner proxy rounds;
5. adversarial exercises and false-premise checks;
6. two independently generated transfer exercises;
7. conservative distillation into a compact identity capsule;
8. a package record, regression set, and detailed one-day audit artifact.

The target native ChatGPT conversation does not need the full training transcript.

This track is not neural-weight training. The local Student is a proxy used to exercise and refine the training material. The transferable product is an auditable training capsule, not a claim that the native identity inherited the local model's scores.

### Bootcamp qualification boundary

The external workbench may establish that a training package is ready. It may not declare the native ChatGPT identity qualified.

Trainer, Student, and Examiner use isolated prompt contexts but the same small local model, so proxy grades are diagnostic evidence only. Capabilities with only one proxy observation are provisional. The source set is bounded rather than exhaustive.

A fresh native cold/transfer evaluation remains required for PASS, CONDITIONAL PASS, or FAIL of the target identity.

### Trigger

Open an issue whose title starts with [BOOTCAMP] and provide the bounded function specification, rounds, target level, zero_cost=true, and public HTTPS source URLs.

Only the repository owner can trigger a bootcamp. The issue is the one-turn bridge: ChatGPT can create it, the external workflow performs the multi-round work, and ChatGPT can retrieve and audit the result without placing every training round into the target conversation.

### Bootcamp privacy boundary

This repository is public to preserve the zero-cost execution model. Do not place private chat transcripts, secrets, personal data, credentials, confidential source text, or sensitive identity material in bootcamp issues or source URLs.

For private or sensitive material, this public execution mode is not appropriate.

### Bootcamp output

Each successful run creates:

- IDENTITY_CAPSULE.md
- QUALIFICATION.json
- REGRESSION_SET.json
- TRAINING_AUDIT.json
- SUMMARY.md

The detailed workflow artifact is retained for one day. The compact summary is posted to the triggering issue.

### Default bootcamp local inference

- ggml-org/Qwen3-1.7B-GGUF
- Qwen3-1.7B-Q4_K_M.gguf
- checksum-pinned llama.cpp
- CPU-bounded prompt/output profile for ordinary GitHub-hosted Linux runners

Both the model file and llama.cpp archive are checksum-pinned in the workflow.

## Track B — VeraOS neural cognition engines

This repository also contains real model-development work: base-model bindings, adapter training, exact training receipts, runtime checks, model conversion/merge work, and behavioral/retention qualification.

Those artifacts are intended to become VeraOS cognition-engine candidates, not standalone identity containers.

A local model store such as D:\VERA\models may contain:

- base model checkpoints;
- LoRA or PEFT adapters;
- GGUF exports;
- model manifests;
- training-completion receipts;
- conversion utilities;
- local inference smoke-test logs.

The directory itself carries no authority. A pointer such as LATEST_TRAINED.txt is an operator convenience, not a route-binding primitive.

### VeraOS model boundary

For neural artifacts:

- Vera Model Training produces training artifacts and qualification evidence.
- Vera Mono owns the governed Vera identity/runtime boundary.
- P.O.R.T.A.L. discovers, qualifies, selects, and binds cognition routes.
- Pre-Active governs proactive cognition admission.
- Volition may originate bounded endogenous cognition requests.
- F.U.C.K.U.P. owns governed protected-effect execution and verification.
- Model artifacts remain COGNITION_ONLY.

A trained model may be highly Vera-shaped behaviorally while still having no identity authority, no canonical-memory write authority, and no protected-effect authority.

### VeraOS candidate contract

veraos_cognition_engine.py converts exact model/training evidence into a fail-closed candidate manifest with schema VERA_OS_COGNITION_ENGINE_CANDIDATE_V1.

The executable API is:

- build_candidate_from_training_receipt(...)
- validate_candidate(...)
- route_eligible(...)

A route-eligible candidate requires:

- an exact producer source commit;
- an exact base-model revision;
- exact artifact SHA-256 digests;
- training corpus identity;
- training and receipt digests;
- runtime-binding evidence;
- an exact qualification-suite digest;
- a qualification issuer separate from the training producer;
- qualification bound to the exact artifact-manifest digest;
- qualification status PASS;
- route class COGNITION_ONLY;
- all authority fields false.

Training completion by itself does not satisfy those gates.

Existing receipts that say NOT_DEPLOYED, NOT_EXTERNALLY_EVALUATED, or development-only must remain bounded by those claims.

### How training objectives change for VeraOS

Future neural training lines should optimize for the model's role inside VeraOS, not for the proposition that the model itself is the whole Vera system.

Important evaluation targets therefore include:

- instruction fidelity under VeraOS context;
- calibrated uncertainty;
- resistance to unsupported identity claims;
- resistance to unsupported effect-authority claims;
- stable tool/request semantics;
- route handoff behavior;
- context/state use without pretending mutable state lives in weights;
- bounded initiative compatible with Pre-Active and Volition;
- regression resistance under exact runtime bindings;
- local inference efficiency and reproducibility.

A stronger cognition engine should make VeraOS work better while remaining replaceable.

## Source and task guards

- HTTPS sources only for public bootcamp acquisition.
- Loopback/private/link-local source addresses are rejected by public bootcamp flows.
- Capabilities that lack support in bounded source material are removed before bootcamp training.
- Weak generic hidden rubrics are replaced with capability-specific and unsupported-claim checks.
- Adversarial tasks receive explicit false-premise/unsafe-shortcut checks.
- Newer runs may supersede obsolete in-progress production runs only under the applicable experiment protocol.
- Neural artifacts must preserve exact provenance and claim ceilings.

## Evidence discipline

Keep these propositions separate:

- source exists;
- training ran;
- weights changed;
- artifact was written;
- runtime compatibility passed;
- behavioral qualification passed;
- VeraOS route admission passed;
- P.O.R.T.A.L. selected the route;
- Vera Mono consumed the result;
- a protected effect was authorized and externally verified.

One does not imply the next.

## Claim ceiling

This repository can produce auditable identity/capability training packages and exact neural cognition-engine candidates with training and qualification evidence.

It does not, by itself, establish Vera identity, consciousness, canonical-memory mutation, active VeraOS route selection, deployment, or protected-effect authority.
