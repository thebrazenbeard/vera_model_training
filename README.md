# VERA Model Training — Zero-Cost Identity Bootcamp

This repository hosts an external identity-training workbench for native ChatGPT Project identities.

## Hard invariant: zero monetary cost

The bootcamp must not require metered model APIs or paid compute.

The default engine runs an open-weight GGUF model locally on a **standard GitHub-hosted runner in this public repository**. The workflow fails closed if the repository is private or if `ZERO_COST` is not `true`.

No OpenAI API key, Gemini key, Hugging Face inference key, Supabase paid compute, or other paid inference service is required.

## What this does

A single bootcamp run performs, externally:

1. source acquisition from user-selected public HTTPS sources;
2. source-grounded knowledge extraction;
3. function/capability-map construction;
4. cold diagnostic;
5. adaptive Trainer → Student → Examiner rounds;
6. adversarial rounds;
7. transfer testing;
8. distillation into a compact identity capsule;
9. a qualification record and retained regression set.

The target native ChatGPT conversation does **not** need the full training transcript. It receives only the distilled capsule and can then undergo a native cold qualification.

This is not neural-weight training. The durable transferable product is the compact identity capsule and its qualification evidence.

## Trigger

Open an issue whose title starts with:

`[BOOTCAMP]`

and whose body is YAML:

```yaml
identity: SB
function: Supabase Platform Specialist
rounds: 10
target: practitioner
zero_cost: true
sources:
  - https://supabase.com/docs/guides/database/overview
  - https://supabase.com/docs/guides/database/postgres/row-level-security
```

The GitHub issue is the one-turn bridge: ChatGPT can create the issue, the external workflow performs the multi-round work, and ChatGPT can read the result from the issue/workflow artifact without placing every training round into the target chat.

## Privacy boundary

This repository is public in order to guarantee standard GitHub Actions execution is non-billable. **Do not place private chat transcripts, secrets, personal data, credentials, or confidential source text in bootcamp issues.** Pass only a function specification and public source URLs.

For a private/sensitive identity, use a different execution mode rather than leaking the subject into a public CI log merely to save a few dollars. Human beings have invented enough security incidents already.

## Output

Each run creates:

- `IDENTITY_CAPSULE.md`
- `QUALIFICATION.json`
- `REGRESSION_SET.json`
- `SUMMARY.md`

The workflow uploads these as an artifact and posts the compact summary back to the triggering issue.

## Default local model

`Qwen/Qwen3-4B-GGUF`, `Qwen3-4B-Q4_K_M.gguf` (Apache-2.0), executed through `llama.cpp`.

The model file is checksum-pinned in the workflow.

## Epistemic status

The external examiner uses a separate context but the same underlying local model as Trainer and Student. Therefore the external result is useful evidence, but it is **not treated as independent native-chat qualification**. A fresh native-chat transfer/cold test remains the stronger final gate.
