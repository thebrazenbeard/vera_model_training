# Tattler reasoning-surface results — 2026-10-07

Status: QUALIFICATION-SURFACE EVIDENCE

## Shared experiment result

On 2026-10-07, the same repository stress-test prompt was run through three ChatGPT surfaces while WorkLaptop was instrumented with Tattler plus a companion Codex process/network tracer.

Observed controlled windows:

- Desktop Chat, GPT-5.6 Sol High: **0 MXC launches** and **2 new established Codex TLS connections** in the companion tracer.
- ChatGPT Desktop Work, Ultra: **59 MXC launches** and **73 new established Codex TLS connections** using the same companion-tracer definitions.
- Firefox cloud Work, Max: browser-side traffic was observable locally, but the provider's server-side worker topology was not.

The bounded conclusion is that Desktop Work used materially different local orchestration from ordinary High Chat in this runtime. It does **not** establish that sockets or MXC processes equal agents, that connection fanout grants a reasoning tier, or that a client can promote High into Ultra/Max by imitating transport behavior.

Canonical detailed evidence is being preserved in `thebrazenbeard/tattler` PR #7 and the reasoning interpretation in `thebrazenbeard/rezon` PR #103.


## Why vera_model_training needs this result

This repository already requires fresh native ChatGPT qualification after the external training workbench. The Tattler experiment strengthens that boundary: capability evidence gathered on one ChatGPT execution surface should not silently transfer to another surface/reasoning configuration.

```text
High qualification != Ultra qualification
Ultra qualification != Max qualification
same prompt != same orchestration conditions
local proxy score != native surface qualification
```

## Qualification implication

A native cold/adversarial/transfer evaluation should record:
- Chat vs Work;
- desktop vs browser;
- model/reasoning setting;
- exact Project/context package;
- tool/connector availability;
- runtime/build when relevant;
- source head and evaluation timestamp.

If a capability is claimed portable across surfaces, test that portability explicitly. Do not infer it from shared model-family naming or from similar final prose.

Tattler/process observations may be attached as diagnostic evidence, but they are not a substitute for native behavioral qualification and do not prove hidden provider topology.
