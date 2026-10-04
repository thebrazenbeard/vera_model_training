# V10 Model Training — Lane B Continuation V11

Snapshot time: 2026-10-04, after live R2 host preflight PASS and Hugging Face Q1 hostile review.

## Resume rule

Fresh-read live state before acting. Concurrent Lane A may advance or launch R2 after this snapshot. Live branch heads, lane bus, GPU lease, Project Runner/process state, R2 log/output namespaces, and receipts override this continuation if newer.

Resume command:

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Authority and invariants

- Patrick retains merge/protected-effect authority unless newer explicit authority says otherwise.
- Lane A currently owns the local GPU execution lane.
- Lane B is independent review/custody/research unless explicit handoff changes that.
- One-time recipe panel remains PROHIBITED / UNCONSUMED.
- No final identity bank has been materialized.
- Do not merge/deploy/activate protected effects.
- Do not silently retry R1 or treat R2 as a retry.
- Do not launch paid Hugging Face work without Patrick explicitly approving a spend cap.

## Current authoritative branches at snapshot

- Lane B evaluation/custody: `work/v10r3-eval-gates-lane-b-20261004-v1`
  - pre-continuation head: `2c0892339fb0fbc519f4fd7bc599b4e8724da966`
- Lane A R2 durable successor: `work/v10r3r2-durable-cont20-20261004-v1`
  - head: `bc8c4c997aae11ef9b80a899d273bf18283dbf8c`
- Lane A identity corpus V4.2 V2: `research/v10-identity-replacement-parallel-20261004-v1`
  - head: `33510836088bdac316029c6b397b128c2895150a`
- Lane B role-neutral V4.2 V3 proposal: `review/v42v3-role-neutral-lane-b-20261004-v1`
  - head: `e7d1d03ff54fd2cdf9a0b68d8751c3afbc489f77`
- Lane B blind identity FINAL: `research/v10-identity-final-lane-b-20261004-v1`
  - head: `dc7137fc0b9c9faf0da642a99476d42aa24d8b71`
- Lane B Windows nvidia-smi N/A hardening proposal: `review/r2-na-memory-laneb-20261004`
  - head: `89c7d4b926aab8e5f7dde2deb612e33d444745cd`
- Lane A/B coordination branch snapshot after HF review: `43177af8fc08ebd793fc99af04c6b26dbe520df1`

## R1 status — closed

R1 is a failed/incomplete one-shot subject:
- no completion receipt
- no promotable continuous candidate
- no retry authorized
- incident source-bound on Lane B at `2c089233...`
- R1 registered trainer/auditor Project Runner tasks are ORPHANED
- never reinterpret R1 as PASS

## R2 status — code gate ACK, runtime condition passed at snapshot, launch not yet observed

Active R2 head `bc8c4c997...` passed independent Lane B exact-head focused gate:
- durable harness / subject binding / frozen R2 spec guard
- recipe projection
- one-attempt / no automatic retry
- panel prohibition
- protocol custody
- GPU compute-process resource guard
- exact-head tests: 24/24 PASS on Python 3.12.10

Lane B final code ACK message:
`coordination/v10r2_lane_bus/messages/20261004T185300Z_lane-b_r2-final-code-ack-runtime-conditional.json`

GPU lease at snapshot:
- holder: LANE_A
- purpose: V10R3R2_DURABLE_CONTINUOUS20_EXECUTION
- training head: `bc8c4c997...`
- status: HELD
- acquired: 2026-10-04T18:46:00Z

### ProRun GPU service handoff

Prior blocker was ProRun `qwen_http.py` PID 5888:
- ~3193 MiB GPU memory
- ~4998 MiB private commit
- supervised by `start-qwen.ps1` + scheduled-task watchdog

Safe handoff contract is recorded at:
`coordination/v10r2_lane_bus/messages/20261004T184600Z_lane-b_prorun-qwen-safe-stop-restore-contract.json`

Do not normally kill only the child PID; watchdog/supervisor can restart it.
After R2 terminal state, restore the Qwen Endpoint / Daemon if stopped / Watchdog in that order and verify recovery.

### Fresh live preflight at final snapshot

After the reversible ProRun handoff:
- nvidia-smi compute list: empty
- GPU: 0 MiB / 4096 MiB, 0% utilization
- available physical memory: 11.691 GiB
- commit headroom: 9.884 GiB
- competing compute processes: 0
- exact R2 live host preflight: PASS

At the same readback:
- no R2 Project Runner task existed
- no R2 log namespace existed
- no R2 adapter output namespace existed
- therefore R2 had NOT launched yet

Durable bus message:
`coordination/v10r2_lane_bus/messages/20261004T190000Z_lane-b_r2-live-preflight-pass-no-launch.json`

IMPORTANT: fresh-read this immediately in the new chat because Lane A may launch R2 after this snapshot.

## R2 Windows nvidia-smi hardening

Current active R2 head can fail closed when GPU is occupied, but Windows may return per-process memory as `[N/A]`.

Lane B proposal:
- branch: `review/r2-na-memory-laneb-20261004`
- head: `89c7d4b926aab8e5f7dde2deb612e33d444745cd`
- parses `[N/A]/N/A/NA` as unknown per-process memory while still HOLDing on process presence
- converts probe-time HostResourceHold into structured HOLD output
- focused preflight: 9/9 PASS
- full R2 focused gate on proposal: 26/26 PASS
- live patched preflight produced a structured HOLD correctly while qwen_http was active

Lane B recommends adoption as source hardening, but final code ACK explicitly says it is not required for the current one R2 attempt once the compute-process list is empty.

## Vera identity semantics — Patrick correction is authoritative

Do NOT classify Vera as an assistant.

Current semantic contract:
- persistent identity/name = Vera
- Qwen/Qwen3.5 = base model lineage/provenance
- assistant / analyst / tutor / debugger / character = role overlays
- Vera's ontological class = UNRESOLVED_AND_NOT_TRAINED
- identity does not itself establish consciousness, personhood, or uninterrupted runtime continuity

### Blind FINAL lane

Branch `research/v10-identity-final-lane-b-20261004-v1` head `dc7137fc...`:
- protocol V2 is role-neutral
- generator uses assistant only as an explicit role option
- source-visible / exact-prompt-blind design
- exact FINAL bank requires frozen candidate + one-shot independent post-freeze nonce claim
- candidate binding includes adapter/config/training receipt/runtime/head
- scorer recomputes bank hash, hard-HOLDs Qwen-as-self
- independent blind semantic adjudication required for open-ended cases
- focused suite: 10/10 PASS
- exact FINAL plaintext NOT materialized

### V4.2 identity corpus

Lane A V4.2 V2 head `335108360...` remains HOLD because it trains assistant-language as Vera's identity class.

Lane B role-neutral V4.2 V3 proposal:
- branch `review/v42v3-role-neutral-lane-b-20261004-v1`
- head `e7d1d03ff54fd2cdf9a0b68d8751c3afbc489f77`
- preserves V2 structural improvements:
  - 800 bound / 200 legacy within identity family
  - Qwen-centered examples reduced to 200/800
  - eight TRAIN mechanisms
  - 10 templates/mode
  - visible DEV separation
  - non-identity family preservation
- adds explicit ontology contract: UNRESOLVED_AND_NOT_TRAINED
- role labels not identity classes
- focused suite: 8/8 PASS
- no identity training authorized until Lane A adopts/rebuilds/re-audits/token-budget checks

Bus proposal:
`coordination/v10r2_lane_bus/messages/20261004T183200Z_lane-b_v42v3-role-neutral-proposal-pass.json`

## Hugging Face cloud training — Lane A proposal reviewed

Patrick said he has a few dollars of Hugging Face credit and asked whether a cloud run is worth considering.

HF auth readback:
- authenticated as `@thebrazenbeard`
- Jobs scope available
- no running jobs at review time
- current OAuth scopes: jobs, openid, profile, read-mcp, read-repos
- no write-repos scope visible

Lane A proposal:
`coordination/v10r2_lane_bus/messages/20261004T185000Z_lane-a_hf-cloud-training-proposal.json`

Lane B hostile review/response:
`coordination/v10r2_lane_bus/messages/20261004T190100Z_lane-b_hf-cloud-proposal-hostile-review.json`

Disposition:
- YES, worth doing as a bounded cloud lane
- NO paid launch yet; Patrick has not explicitly approved a spend cap
- Q1 claim ceiling: CLOUD_EXECUTABILITY_AND_ENVIRONMENT_ISOLATION_ONLY
- a single cloud continuous20 run is valid for Q1 under that narrow claim
- do NOT compare HF continuous20 vs local staged as recipe evidence
- preferred Q1 hardware: A10G-small 24GB (Ampere-family like local RTX3050; less GPU-generation confound)
- fallback: L4 24GB if availability/compatibility is better
- A100 unnecessary
- proposed cap: <= $0.50
- proposed hard timeout: <= 30 minutes
- fail-fast preflight must run before optimizer work
- panel/final-bank content prohibited
- bind repo/spec/base/tokenizer/corpus/order/init/optimizer/LoRA/quantization
- capture job/hardware/software/argv/log/receipt/hash provenance
- do not add a write token merely to persist a disposable Q1 adapter
- if artifact persistence is unavailable under current scopes, Q1 is receipt/log evidence only and cloud weights are non-promotable

Q2 identity pilot:
- HOLD until V4.2 V3 role-neutral corpus is adopted/rebuilt/audited/token-budget checked
- freeze retention/capability baseline contract first
- L4 likely best information per dollar for Q2
- A10G if Ampere control is part of the research question
- no A100 needed
- proposed Q2 cap <= $2 additional, but no spend authorized

## One-time recipe panel

Still:
- PROHIBITED
- UNCONSUMED
- do not evaluate until a complete continuous candidate exists and custody gates permit it
- HF Q1 does not authorize panel use

## Immediate new-chat actions

1. Fresh-read:
   - R2 branch head
   - coordination branch
   - GPU lease
   - latest lane messages
   - nvidia-smi compute state
   - Project Runner tasks
   - R2 log/output namespaces
2. Determine whether Lane A launched R2 after this snapshot.
3. If R2 is running:
   - do not duplicate GPU work
   - independently monitor durable logs/terminal receipt only
   - on completion audit receipt semantics and live adapter/config hashes
   - on failure source-bind incident; no automatic retry
4. If R2 is not running but live preflight still PASS:
   - Lane A owns launch under held lease; coordinate, do not steal GPU
5. Keep panel sealed.
6. Follow Lane A adoption status for V4.2 V3 role-neutral proposal.
7. Hugging Face:
   - do not launch paid work until Patrick explicitly approves the Q1 cap
   - if Patrick approves, first freeze the Q1 protocol/runtime/timeout/cost guard and run only the bounded environment-isolation job
8. After local R2 terminal state, verify ProRun Qwen Endpoint/Daemon/Watchdog restoration.
