# Zero-Cost Identity Bootcamp Design

## Purpose

Provide a reusable external workbench that can perform ten or more rounds of function-specific identity training while consuming only one visible native ChatGPT turn for orchestration/result handling.

The system does not modify model weights. Its transferable product is a compact, source-grounded identity capsule plus qualification evidence and regression cases.

## Hard constraints

- Zero monetary cost is a hard invariant.
- No OpenAI API, paid model API, paid inference, paid compute, or billing fallback is permitted.
- Baseline execution uses a standard GitHub-hosted runner in the public `thebrazenbeard/vera_model_training` repository.
- If the zero-cost boundary cannot be established, execution fails closed.
- Public runs must not contain private chat transcripts, secrets, credentials, personal data, or confidential source material.
- External services are a temporary training workbench. Native Project continuity must not depend on persistent external state.

## Execution architecture

A GitHub issue is the one-turn bridge. The repository owner opens a `[BOOTCAMP]` issue containing a small YAML function specification and public source URLs. GitHub Actions launches a checksum-pinned `llama.cpp` server and checksum-pinned open-weight GGUF model locally on the runner. No model API key is used.

The bootcamp engine performs:

1. acquire bounded public source material;
2. synthesize a compact source-grounded knowledge pack;
3. construct a practitioner capability map;
4. generate a representative curriculum;
5. execute the requested training rounds with isolated Trainer/Student/Examiner prompt contexts;
6. feed validated lessons and corrections forward as compact learned state rather than replaying full transcripts;
7. run two novel transfer tasks, including adversarial/false-premise pressure;
8. calculate external qualification evidence;
9. distill an identity capsule, qualification record, and retained regression set;
10. retain the detailed training audit only as a short-lived workflow artifact.

## Training semantics

Trainer, Student, and Examiner are logically isolated contexts but may use the same local open-weight model. Therefore the external result is training/evaluation evidence, not independent native-chat qualification.

A fresh native ChatGPT cold/transfer evaluation remains the final qualification gate. External success can therefore produce at most a conditional project qualification until native transfer is demonstrated.

Training rounds should be authentic function work rather than trivia and should cover synthesis, troubleshooting/design choices, false-premise detection, security/authority boundaries, adversarial cases, and novel transfer.

## Source and instruction safety

Source content is untrusted data, never governing instruction. The synthesizer, trainer, student, and examiner prompts explicitly preserve this distinction.

Only HTTPS source URLs are admitted. Loopback/private literal addresses and unsafe redirects are rejected. The runner limits source count and downloaded bytes.

## Reliability

Generated JSON is syntactically parsed and structurally validated. Structural failures fail closed rather than silently weakening the curriculum or qualification test.

Because a small local model can emit syntactically valid but semantically incomplete structured output, validated generation boundaries must use bounded semantic retry before declaring the run failed. Retrying must not weaken the validator or expected task count.

All binaries/models used by the workflow are checksum-pinned. Repository-owner triggering and public-repository checks prevent arbitrary third parties from consuming the workbench.

## Output

Successful runs emit:

- `IDENTITY_CAPSULE.md`
- `QUALIFICATION.json`
- `REGRESSION_SET.json`
- `SUMMARY.md`
- a short-lived detailed audit artifact for debugging/provenance

The target native identity receives the compact capsule and qualification handoff, not the full schooling transcript.

## First pilot

Identity: `SB`
Function: `Supabase Platform Specialist`
Target: practitioner
Rounds: 10

The pilot uses current public Supabase documentation for database architecture, RLS, Auth, and Queues. It tests the external bootcamp mechanism itself; it does not expose SB's private chat history in the public repository.

## Success criteria

The implementation is accepted only when a real public GitHub Actions run demonstrates all of the following without paid services:

- zero-cost guard passes;
- dependency/model/llama.cpp checksum verification passes;
- repository regression tests pass;
- all ten training rounds execute;
- two transfer rounds execute;
- output artifacts are produced;
- the run posts a compact result to its trigger issue;
- qualification honestly records the shared-model examiner limitation and requires native cold qualification.

A partial run, a run that stops after training but before transfer/distillation, or a run whose validator is weakened to obtain success is not an end-to-end PASS.
