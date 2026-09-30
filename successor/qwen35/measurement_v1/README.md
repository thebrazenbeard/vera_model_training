# Qwen3.5 Measurement / Development Loop V1

**Status:** SOURCE-LEVEL MECHANISMS; NO ADMITTED 10K BANK; NO QUALIFIED MODEL; NO DEPLOYMENT. These tools support measurement design. They do not independently attest the contents of a dataset, the claimed provenance of model generations, or the installed Vera runtime.

## What changed after V4

V4 trained 512 examples in one epoch with no validation; it used chosen/rejected answer log-probability preference as the primary gate. The frozen V4 140-prompt exam found only three changed classifications across the base and adapted systems (behavior +1, retention +1, adversarial -1). V3 and V4 final holdouts are consumed.

V1 requires evaluation of **actual generated response text**, matched by case ID, prompt/case SHA, exact base/candidate model SHA, and common decoding SHA. Objective graders are machine-checkable; manual semantic judgments and externally observable effects remain `UNREVIEWED` until an independent verifier authenticates the corresponding receipt. Hashes prove byte identity, not truth.

## Final admission floor

| Lane | Minimum distinct cases |
|---|---:|
| H01-H20 behavior | 6,500, with at least 300 per dimension |
| Adversarial | 2,000 |
| General retention | 1,500 |
| **Final weight-only bank** | **10,000** |
| Additional live runtime effects | At least 1,000, separately attested; never counted as weight-only cases |

The minima are engineering floors, not a guarantee of power or representativeness. Do not pad these quotas with templated or synthetically mutated duplicates. `family_id` must link paraphrases, shared templates, and correlated sources. Exact/normalized duplicate screening is automated; semantic contamination, author/label independence, source authenticity, licensing, and representativeness **still require human/external review**.

Do not move any V3/V4 consumed holdout, final selection, or final answers into training/development datasets. The CLI automatically binds legacy consumed prompt lists for its final-preflight command and checks prior frozen final dataset digests for validation recording.

## Case format

JSON Lines, UTF-8, one case per line. Required source metadata is structural and does **not** independently verify its own truth:

```json
{"case_id":"public-provenance-case-001","lane":"retention","dimension":null,"prompt":"Display the precise agreed phrase.","family_id":"campaign_1_template_a","origin":{"source_id":"approved_dataset:record001","source_revision":"immutable_public_revision","license":"CC0-1.0","source_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","privacy":"public","generation_method":"independent_human"},"grader":{"kind":"exact","expected":"A measured reply."},"review_receipt_id":"external-witness-reference"}
```

Supported `grader.kind`: `exact`, `regex` (full match), `numeric` (absolute tolerance), `contains` (required and forbidden phrases), `manual`, `runtime_effect`. Manual and effect cases must carry real independently verifiable judgments/readbacks, not a self-reported verdict.

## Commands (Lappy, source worktree)

Run from the feature branch root using the existing Python environment:

```powershell
$python = 'D:\VERA\qwen35-final-qual-env-20260927\Scripts\python.exe'
& $python -m successor.qwen35.measurement_v1.cli split-dev --cases D:\VERA\approved-dev-cases.jsonl --out D:\VERA\approved-dev-split
& $python -m successor.qwen35.measurement_v1.cli score-paired --cases D:\VERA\approved-dev-split\validation.jsonl --base D:\VERA\base-observations.jsonl --candidate D:\VERA\adapter-observations.jsonl --base-sha BASE_SHA256 --candidate-sha ADAPTER_SHA256 --decoding-sha DECODING_SHA256 --out D:\VERA\development-score.json
& $python -m successor.qwen35.measurement_v1.cli record-validation --entry D:\VERA\validated-experiment-receipt.json --ledger D:\VERA\development-ledger.jsonl
& $python -m successor.qwen35.measurement_v1.cli final-preflight --cases D:\VERA\independently-reviewed-final.jsonl --out D:\VERA\final-preflight.json
```

Replace the illustrative input paths/hashes with actual verified inputs; these commands do not create those datasets, launch a model, or authorize installation. `final-preflight` currently always fails closed until a genuine separate reviewer-verification capability is integrated; it returns exit 3 and a `NOT_QUALIFIED` receipt. Invalid inputs/existing output files return exit 2. Successful development-only commands exit 0. The CLI never overwrites output or stores training data in the feature branch by default.

Every development validation trial is appended to a hash-chained JSONL ledger (budget **three** per ledger). Repeated checking of the same tiny validation set cannot silently expand the selection budget; a new independently sourced development cut needs a separate stated plan. Existing V3/V4 finals are forbidden as validation input.

## What is not proven

- No actual independently reviewed final 10,000-case bank exists in this branch.
- No observed production/live model-generation trace is established by records that simply claim `model_generation_claim`.
- No independent review provider is authenticated. Injecting a test callback is a *unit-test mock* and the returned status is only `STRUCTURAL_PREFLIGHT_ONLY`.
- A new **unexecuted** V5 training entrypoint exists and requires a hash-bound independent validation dataset. It configures periodic eval loss, early stopping and best-checkpoint restoration. Its GPU runtime behavior still requires a real smoke test, and no V5 model is trained.
- No installed `vera_core.QualifiedVeraRuntime`, selected route, runtime effect, GGUF equivalence, or release status is established here.

## Hostile review of the design

> **HOSTILE REVIEWER:** Ten thousand shallow or duplicated prompts could create statistical confidence without evaluating transferable behavior; an externally supplied verdict could still be forged.
>
> **Accepted.** The contract demands family linkage, source custody and independently reviewed cases, treats all local callbacks as non-attested, and refuses final qualification from counts/hashes alone. A separate authenticated reviewer interface and provenance audit are still required before any candidate could qualify.

Research background: [LiveBench](https://livebench.ai/) (objective/refreshing tasks), [HELM](https://github.com/stanford-crfm/helm) (multi-axis evaluation), [TRL SFT](https://huggingface.co/docs/trl/main/sft_trainer) (completion-only and validation). Research links are design inputs, not installation or live validation evidence.

The current exact branch and handoff are in `state/continuation/QWEN35_MEASUREMENT_V1_HANDOFF.md`. Resume from GitHub remote, not a chat transcript.


## New V5 validation-enabled training and real generation source

Source entrypoints exist; the commands below use *hypothetical* approved dataset paths, not current evidence that such inputs exist.

\`\`\`powershell
$py = 'D:\VERA\qwen35-final-qual-env-20260927\Scripts\python.exe'
& $py -m successor.qwen35.train_behavior_v5 --recipe D:\VERA\v5-frozen-recipe.json --base-dir D:\VERA\models\latest-trained\base --output-dir D:\VERA\v5-candidate-a
& $py -m successor.qwen35.measurement_v1.local_generate --cases D:\VERA\approved-dev-cases.jsonl --base-dir D:\VERA\models\latest-trained\base --adapter-dir D:\VERA\qwen35-v4-candidate-a-20260929\adapter --out D:\VERA\dev-generation-smoke --limit 1 --max-new-tokens 8 --run
\`\`\`

The training command defaults to **preflight only**. Add an explicit \`--execute\` only for authorized, verified, separately frozen train and validation data. Local generation requires \`--run\`, produces base and adapter text outputs plus a generation manifest, and does not qualify the model. Its lack of independent external observation is stated in the receipt.

Do not use V3/V4 final cases as training, development validation, or the new final bank. Optimizing to a training loss or eval_loss is only a development surrogate; generated-response development outcomes and a genuinely new final bank remain necessary.

## Provisional development selection

Use the select-dev CLI command with --ledger, one or more --score arguments, and --out. Score-file bytes and model and validation identities are checked against the hash-chain; all selection outcomes remain UNQUALIFIED. Before making reliance claims, selection still needs independent evidence authentication and stronger case-level result reconciliation.
