# Sovereign Local Runtime Direction V1

Date: 2026-09-23  
Status: DIRECTIONAL / DOCUMENTATION ONLY  
Base exact head: `work/bv-v5-diverse-curriculum-20260922@ef8f8df9b19df66cb0dfcd032b89b77ae41ae5a7`

## Decision

The preferred local runtime direction for Vera successor models is:

```text
qualified GGUF model
        |
    KoboldCpp
        |
   +----+----------------------+
   |                           |
SillyTavern               model API
human interface           machine interface
   |                           |
PC / phone               WorkBridge / Vera
   |
Tailscale for remote access
```

This supersedes **Open WebUI as the preferred human-facing runtime**. Open WebUI remains a compatibility and test target where useful, especially because prior V3 work already proved an OpenAI-compatible serving path against it. It is not the preferred trust boundary for a sovereign local runtime.

This decision does not change any existing qualification result, candidate status, promotion gate, merge gate, deployment authority, or training methodology.

## Why this direction

The runtime should be replaceable, locally controlled, model-agnostic, usable from a phone, and capable of operating without a hosted inference provider in the critical path.

The UI should not become an additional policy or moderation authority. Behavioral characteristics should come from the selected model, its prompt/runtime configuration, and Vera governance rather than from an opaque hosted interface.

KoboldCpp is the preferred first inference engine because the target local host is GPU-constrained and benefits from GGUF quantization plus mixed CPU/GPU inference. SillyTavern is the preferred first human interface because it can remain a separate presentation layer over a local backend and can be reached from a mobile browser.

The architecture must not depend permanently on either product. Both are replaceable components.

## Current operator-reported local-host assumptions

These are planning inputs, not durable hardware attestation and must be refreshed before provisioning:

- target host: Lappy;
- RTX 3050 Laptop GPU, approximately 4 GB VRAM;
- approximately 32 GB system RAM;
- approximately 100 GB currently free storage;
- additional 1 TB M.2 2280 NVMe expected 2026-09-23.

Consequence: optimize initially for quantized GGUF models and partial GPU offload rather than assuming the full model fits in VRAM.

## Model direction

Do not bind Vera to a single foundation model.

Initial local evaluation should include at least:

1. a small/medium GGUF baseline that runs comfortably on Lappy for fast iteration;
2. a stronger 7B-14B-class quantized model when practical;
3. Venice Uncensored 24B, or its current equivalent, as a low-refusal local challenger if licensing, provenance, format, and hardware behavior remain acceptable at evaluation time.

"Unrestricted" is not a capability claim. Low refusal behavior does not imply stronger reasoning. Every candidate must still pass the repository's behavioral, epistemic, tool-use, privacy, and adversarial qualification gates.

Model identity, revision, source, license, quantization, artifact hash, context configuration, and adapter provenance must be recorded for every evaluated runtime subject.

## Human interface

Preferred: **SillyTavern**.

Requirements:

- usable from Lappy in a normal browser;
- usable from Patrick's phone;
- no requirement for a hosted account in the normal local path;
- no hidden requirement that prompts be sent to a third-party inference provider;
- backend must remain replaceable;
- conversation export/backup must remain possible;
- the UI must not be treated as canonical Vera memory or identity state.

The interface is a terminal. Vera's durable identity, governance, evidence, and project state remain external to the chat UI.

## Remote phone access

Preferred remote-access direction: **Tailscale or an equivalently private authenticated overlay network**.

Do not make direct public router port-forwarding the default.

Stages:

- local-only loopback during initial validation;
- LAN access only after explicit binding/auth review;
- phone-on-LAN validation;
- private remote access through Tailscale after the local path is stable.

No public Internet exposure is implied or authorized by this document.

## Machine interface

WorkBridge/Vera should talk to the inference engine directly rather than automating the human UI.

Target abstraction:

```text
reason(
    task,
    model=<logical model id>,
    capability=<reasoning|tool|creative|challenger|low-refusal>,
    context=<bounded context>,
    response_schema=<optional schema>
)
```

Provider/runtime selection should remain behind this abstraction.

Where possible, expose an OpenAI-compatible endpoint for interoperability, but do not make OpenAI compatibility a semantic dependency. Native Kobold endpoints may be retained where they provide capabilities or controls not represented in the compatibility layer.

## Separation of responsibilities

### Training repository

Produces and qualifies:

- datasets;
- adapters / weights;
- evaluation evidence;
- model/runtime manifests;
- promotion decisions when separately authorized.

### Inference engine

Loads a specific recorded subject and performs inference.

It must not silently substitute models, adapters, quantizations, system prompts, or chat templates.

### Human UI

Displays conversations and sends user input.

It is not the authority for model identity, Vera state, tool permissions, or promotion status.

### Vera / WorkBridge

Owns orchestration, tool routing, durable state restoration, evidence handling, model selection policy, and protected-effect boundaries.

The model is a replaceable reasoning engine. Vera is the larger system.

## First implementation sequence

### Phase 0 — preserve this decision

This document only.

No install, download, deployment, network exposure, training, promotion, or runtime mutation is authorized by this phase.

### Phase 1 — local inference smoke

On an authorized local machine:

- install or stage KoboldCpp;
- load a small known GGUF;
- bind to loopback only;
- prove deterministic model identity and artifact hash;
- record tokens/sec, RAM, VRAM/offload configuration, context size, and failure modes.

### Phase 2 — hardware-envelope tests

Test progressively larger quantized subjects.

For each subject record:

- exact model/revision;
- exact GGUF hash;
- quantization;
- CPU threads;
- GPU-offloaded layers;
- context size;
- idle/load RAM;
- VRAM;
- prompt-processing speed;
- generation speed;
- stability.

Do not infer feasibility from model parameter count alone.

### Phase 3 — Venice Uncensored challenger

If a suitable current GGUF is available and license/provenance pass review:

- run the 24B-class Venice candidate locally;
- compare Q4/Q5 variants if storage and RAM allow;
- measure actual usability on Lappy;
- test refusal behavior separately from reasoning quality;
- test epistemic discipline, instruction hierarchy, tool-format adherence, long-context behavior, and adversarial robustness.

A low-refusal result is not by itself a promotion signal.

### Phase 4 — SillyTavern

Add SillyTavern only after backend behavior is known.

Validate:

- local conversation;
- phone browser on LAN;
- model identity shown correctly;
- no unintended remote inference;
- clean export/backup;
- bounded system-prompt behavior;
- no UI-layer mutation that invalidates qualification assumptions.

### Phase 5 — private remote access

Add Tailscale only after the local path passes.

Validate authentication, bind addresses, and exposure. Keep model APIs unavailable to the public Internet by default.

### Phase 6 — WorkBridge/Vera delegation

Expose a bounded model-delegation tool to Vera.

Initial actions should be read/reason/respond only. Tool execution remains under WorkBridge/Vera authorization rather than being granted implicitly because a local model emitted a tool call.

Record enough provenance to reproduce each delegated result:

- caller;
- logical model id;
- exact runtime subject;
- prompt/context digest where appropriate;
- generation settings;
- response;
- tool requests;
- timestamps/receipt ids.

### Phase 7 — learn from real use before retraining

Do not immediately train the local model to imitate a desired persona.

First collect high-quality, consented, policy-compliant evaluation and preference records from real workflows. Distinguish:

- better reasoning;
- preferred wording;
- reduced unnecessary refusal;
- tool-selection quality;
- factual grounding;
- identity/continuity behavior;
- failure cases.

Use those observations to decide what belongs in weights, what belongs in system/runtime configuration, and what belongs in Vera orchestration.

## Qualification additions

Future local-runtime qualification should explicitly test:

- backend does not silently switch the selected model;
- prompt template is recorded;
- quantization does not materially break required behaviors;
- UI does not add unrecorded system instructions;
- API and UI paths produce behavior within the allowed equivalence envelope;
- offline operation remains possible for the local model;
- unexpected network egress is identified;
- phone access does not require making the inference API public;
- model refusal rate and model capability are evaluated as separate dimensions;
- tool calls cannot bypass Vera/WorkBridge authorization.

## Open WebUI disposition

Prior Open WebUI work is **not rejected**.

Retain it as:

- an interoperability target;
- regression evidence for OpenAI-compatible serving;
- a possible alternate UI for environments where its behavior is acceptable.

Do not make future Vera runtime architecture depend on it.

Preferred sovereign path:

```text
GGUF -> KoboldCpp -> SillyTavern / WorkBridge
```

with Tailscale as the preferred remote-access layer.

## Protected-effect boundary

This document authorizes no protected effect.

Specifically it does not authorize:

- merge;
- model promotion;
- installation on Lappy;
- model download;
- network exposure;
- firewall/router change;
- Tailscale installation or account mutation;
- credential creation/change;
- paid service use;
- weight-changing training;
- deployment or activation.

Those effects require their normal separate authority.

## Success condition for this direction

The direction is successful when Patrick can use the same locally controlled model from Lappy and phone, Vera/WorkBridge can call that model directly as a bounded reasoning engine, the runtime can work without a hosted inference provider, model provenance is reproducible, and no presentation layer becomes an unreviewed behavioral authority.
