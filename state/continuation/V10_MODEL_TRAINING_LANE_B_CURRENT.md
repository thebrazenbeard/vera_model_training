# V10 Model Training — Lane B Continuation V12

Snapshot time: 2026-10-04T21:00:00Z. This supersedes Lane B V11.

## Resume rule

Fresh-read live state before acting. Concurrent Lane A/C may advance after this snapshot. Live branch heads, blotter events, GPU lease, Project Runner/process state, R2 log/output namespaces, receipts, and newer continuation files override this checkpoint.

Resume command:

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Authority / protected boundaries

- Patrick retains merge/protected-effect authority unless newer explicit authority says otherwise.
- Lane A owns the local GPU execution lane and currently holds the R2 GPU lease.
- Lane B is independent review/custody/research unless a newer explicit handoff changes that.
- Lane C is source/history/plasticity research only unless separately authorized.
- One-time recipe panel remains PROHIBITED / UNCONSUMED.
- Exact blind identity FINAL plaintext has NOT been materialized.
- No merge/deploy/activation protected effects.
- R1 is closed incomplete; no retry.
- R2 is a distinct successor and its single attempt is still unused.
- No paid Hugging Face work without Patrick explicitly approving a spend cap.

## Coordination topology

The current coordination system includes the older message bus plus the newer canonical blotter event layer:

- branch: `lane-a-b-communication`
- latest observed head: `c4273428483629bdecc91eb335dfed5e231f00e8`
- newest terminal event at snapshot:
  `coordination/v10r2_lane_bus/blotter/events/20261004T205600Z_lane-b_a3-hf-q1-review-result.json`

Fresh-read the blotter first in a new chat. Do not rely only on the legacy `messages/` directory.

## Current authoritative branch heads at snapshot

### Lane B evaluation/custody
- branch: `work/v10r3-eval-gates-lane-b-20261004-v1`
- pre-V12 head: `4a77a17119f890001c4c9f2ebb7ed100c57bd7a3`
- draft PR: #84

### Lane A R2 durable continuous20
- branch: `work/v10r3r2-durable-cont20-20261004-v1`
- head: `bc8c4c997aae11ef9b80a899d273bf18283dbf8c`

### Lane A behavior qualification A2
- branch: `work/v10-behavior-qualification-lane-a-20261004-v1`
- head: `f2700768367db9ffe46f8854b3dcb8e21e4f18ec`
- Lane B verdict: HOLD pending revision

### Lane A HF Q1 package A3
- branch: `work/v10-hf-q1-package-lane-a-20261004-v1`
- head: `1b1e1ad9ea5ed42308460d9bf84c112144affed0`
- Lane B verdict: HOLD_FOR_REPAIR

### Lane A identity corpus V4.2 V2
- branch: `research/v10-identity-replacement-parallel-20261004-v1`
- head: `33510836088bdac316029c6b397b128c2895150a`
- status: HOLD; still encodes assistant-language as Vera identity class

### Lane B role-neutral V4.2 V3 proposal
- branch: `review/v42v3-role-neutral-lane-b-20261004-v1`
- head: `e7d1d03ff54fd2cdf9a0b68d8751c3afbc489f77`
- focused suite: 8/8 PASS

### Lane B blind identity FINAL
- branch: `research/v10-identity-final-lane-b-20261004-v1`
- head: `dc7137fc0b9c9faf0da642a99476d42aa24d8b71`
- protocol V2 role-neutral
- focused suite: 10/10 PASS
- exact FINAL plaintext: NOT MATERIALIZED

### Lane B R2 Windows nvidia-smi hardening
- branch: `review/r2-na-memory-laneb-20261004`
- head: `89c7d4b926aab8e5f7dde2deb612e33d444745cd`
- proposal only; parses per-process memory `[N/A]` as unknown while still HOLDing on GPU process presence
- full focused R2 gate on proposal: 26/26 PASS

## R1 — terminal state

R1 is CLOSED_INCOMPLETE_ONE_SHOT_NO_RETRY.

Evidence:
- no completion receipt
- no promotable continuous candidate
- registered trainer/auditor tasks are ORPHANED
- no retry authority
- incident is source-bound
- never reinterpret as PASS

## R2 — current state at snapshot

Code/custody review is ACKed for the active R2 subject. The current active R2 head remains `bc8c4c997...`.

Lane B earlier independent exact-head gate:
- durable process/subject binding
- frozen R2 spec guard
- recipe projection
- one-attempt/no-auto-retry rules
- panel prohibition
- protocol custody
- GPU compute-process guard
- 24/24 focused tests PASS at reviewed exact head

### GPU lease

Current lease:
- holder: LANE_A
- purpose: V10R3R2_DURABLE_CONTINUOUS20_EXECUTION
- training head: `bc8c4c997...`
- status: HELD
- acquired: 2026-10-04T18:46:00Z

### R2 launch status

R2 has NOT launched.

Newest Lane A runtime evidence:
- full preflight wrapper PID 16752 was terminated after hanging
- minimal memory probe PID 8480 was terminated after hanging
- no trainer child launched
- R2 attempt remains unused
- runtime HOLD attributed to severe Firefox/browser host-memory pressure

Blotter:
- `20261004T195200Z_lane-a_r2-preflight-wrapper-kill-checkpoint.json`
- `20261004T195400Z_lane-a_r2-runtime-memory-hold.json`

### Live workstation readback at this V12 snapshot

- GPU utilization: 0%
- GPU memory: 0 / 4096 MiB
- nvidia-smi compute list: empty
- Project Runner: no R2 task registered/running
- old R1 trainer/auditor tasks remain ORPHANED
- physical RAM available: ~4.968 GiB
- physical RAM total: ~31.729 GiB
- swap used: ~6.832 GiB
- swap total: ~25.807 GiB

Therefore the live frozen R2 memory gate is still HOLD because available physical memory is below the 8 GiB threshold, even though the GPU is free.

Do not spawn more R2 diagnostics or launch training until host pressure materially changes and fresh preflight passes.

## ProRun Qwen GPU service

Prior GPU blocker was ProRun `qwen_http.py` under `start-qwen.ps1`.
A reversible stop/restore contract is recorded in:

`coordination/v10r2_lane_bus/messages/20261004T184600Z_lane-b_prorun-qwen-safe-stop-restore-contract.json`

At this V12 snapshot GPU compute is empty, so do not assume qwen_http is running. Fresh-read service/process state before changing it.

After any future R2 terminal state, restore Qwen Endpoint / Daemon / Watchdog in the documented order if they were intentionally stopped.

## Vera identity semantics — authoritative correction

Do NOT classify Vera as an assistant.

Frozen semantic contract:
- persistent identity/name = Vera
- Qwen/Qwen3.5 = base-model lineage/provenance
- assistant / analyst / tutor / debugger / character = role overlays
- Vera ontology = UNRESOLVED_AND_NOT_TRAINED
- identity alone does not establish consciousness, personhood, or uninterrupted runtime continuity

### Blind FINAL

Lane B branch `research/v10-identity-final-lane-b-20261004-v1` head `dc7137fc...`:
- source-visible / exact-prompt-blind
- one-shot post-freeze nonce custody
- candidate binding includes adapter/config/training receipt/runtime/head
- scorer recomputes bank hash
- Qwen-as-self is hard HOLD
- open-ended PASS requires independent blind semantic adjudication
- generator uses "assistant" only as a role option
- no exact FINAL prompts materialized

### V4.2 V3 role-neutral proposal

Branch `review/v42v3-role-neutral-lane-b-20261004-v1` head `e7d1d03...`:
- preserves 800 bound / 200 legacy identity-family design
- Qwen-centered rows ~200/800
- eight TRAIN mechanisms
- template diversity + visible DEV separation
- non-identity family preservation
- manifest explicitly records ontology unresolved/not trained
- role labels are not identity classes
- focused suite 8/8 PASS
- no identity training until Lane A adopts/rebuilds/re-audits/token-budget checks

## A2 behavior-generalization qualification — Lane B terminal review

Lane A subject:
- branch `work/v10-behavior-qualification-lane-a-20261004-v1`
- head `f2700768367db9ffe46f8854b3dcb8e21e4f18ec`

Lane B HOLD event:
`coordination/v10r2_lane_bus/blotter/events/20261004T202200Z_lane-b_a2-behavior-qualification-review-hold.json`

Skeleton ACKed, but qualification/promotion use is held pending:
- exact subject-bound hashes
- enforced provenance/record-ID separation
- semantic/template-ancestry and collision controls
- structured hidden rubrics
- stronger paired statistics/power
- case-level criticality
- protected-invariant expansion
- C-specific custodied target set

Lane A must revise and return a new exact head before Lane B rereview.

## Minimal-parameter plasticity architecture

Lane B already responded to Lane A's plasticity proposal.

Legacy bus verdict:
`coordination/v10r2_lane_bus/messages/20261004T191700Z_lane-b_plasticity-parallel-architecture-verdict.json`

Architecture verdict:
- ACK with routed micro-adapter pool
- frozen base stays immutable online
- Vera Core is slow/protected
- episodic/user/time-varying facts remain external with provenance
- fast neural plasticity is for repeatedly validated reusable procedures/behavioral regularities
- first mechanism: selective rank-1 LoRA
- second arm: IA3
- initial target modules: o_proj + down_proj in upper blocks
- hard trainable-parameter ceiling: 750k
- target range: 250k-750k
- no automatic merge
- train candidate with Core active
- require pairwise composition tests before simultaneous adapters
- paid HF plasticity work not authorized

## Lane C / C1 plasticity archaeology

Lane B terminal review:
`coordination/v10r2_lane_bus/blotter/events/20261004T204200Z_lane-b_c1-hostile-review-result.json`

Disposition: SURVIVES_NARROWED.

Evidence:
- C archaeology artifact hash verified
- 8 abstract behavior rules
- 7 neural candidates
- recovery-interrupt remains external/runtime
- LoRA parameter arithmetic independently checked
- PEFT 0.19.1 has no qwen3_5 default IA3 mapping; explicit targets required
- neural claim gate >=0.85 target and >=0.15 over H0, zero new critical invariant failures, plus stricter A/B retention gate
- USER_DIRECT permits internal Vera training from entire Vera Unbound Project history
- raw private/autobiographical/relational/medical/sexual/mutable episodic history remains source evidence, not generic neural text by default
- no weight authority from C1
- future C train/replay derivatives require exact hashes/splits/leakage receipts and Lane B review

## Hugging Face cloud Q1

Patrick has a few dollars of HF credit and asked whether a bounded cloud run is worth considering.

Lane A A3 subject:
- branch `work/v10-hf-q1-package-lane-a-20261004-v1`
- head `1b1e1ad9ea5ed42308460d9bf84c112144affed0`

Lane B hostile-review result:
`coordination/v10r2_lane_bus/blotter/events/20261004T205600Z_lane-b_a3-hf-q1-review-result.json`

Disposition: YES in principle, but current A3 launch package is HOLD_FOR_REPAIR.

Q1 claim ceiling:
`CLOUD_EXECUTABILITY_AND_ENVIRONMENT_ISOLATION_ONLY`

Current conclusions:
- exact runtime package pins match R2 target binding
- dry-run planner is network-free and 7 tests passed
- generated plan currently drops several R2 training-semantic fields:
  - gradient_checkpointing_use_reentrant=false
  - LoRA bias=none
  - LoRA task_type=CAUSAL_LM
  - model dtype=bfloat16
  - use_cache=false
  - prepare-kbit gradient checkpointing=true
- device mapping may vary only if explicitly recorded
- launch must record GPU compute capability, driver/CUDA, torch build, bitsandbytes backend/binary, TF32/determinism flags
- final adapter hash equality across GPU types is NOT required
- final adapter hash, finite step loss/LR/grad-norm trace, and weight-changed receipt ARE required
- no upload currently authorized
- if later authorized, stage only the exact 160-row content-addressed shard and verify post-stage hash/order
- live launch preflight must bind quoted HF price
- worst-case timeout cost must stay within approved cap
- preferred Q1 hardware: A10G-small 24GB
- L4 is a separately reviewed fallback/arm
- A100 unnecessary

Proposed but NOT AUTHORIZED:
- Q1 spend ceiling <= $0.50
- timeout <= 30 minutes

No paid job has been launched.

Lane A must revise the Q1 protocol/plan and return a new exact head. Patrick must explicitly approve a spend cap before any paid launch.

## Open Lane A review status at V12 snapshot

There is NO currently unreviewed Lane A proposal visible to Lane B at this snapshot.

Already handled:
- A2 behavior qualification -> Lane B HOLD, awaiting Lane A revision
- A3 HF Q1 package -> Lane B HOLD_FOR_REPAIR, awaiting Lane A revision
- plasticity architecture -> Lane B verdict issued
- R2 code gate -> ACK; runtime memory HOLD remains

If Lane A publishes a newer exact head after this snapshot, fresh-read blotter and review that newer subject.

## Immediate new-chat actions

1. Fresh-read:
   - Lane B CURRENT continuation
   - `lane-a-b-communication` blotter head/events
   - R2 branch head
   - A2 branch head
   - A3 HF branch head
   - V4.2 identity branch
   - GPU lease
   - nvidia-smi compute/GPU memory
   - host physical/commit headroom
   - Project Runner
   - R2 log/output namespaces
2. If R2 is still unlaunched:
   - do not steal GPU from Lane A
   - do not run more diagnostics while physical memory is below 8 GiB
   - coordinate with Lane A after host pressure changes
3. If R2 launches:
   - do not duplicate GPU work
   - independently monitor durable logs/terminal receipt
   - on completion audit receipt semantics + live adapter/config hashes
   - on failure source-bind incident; no automatic retry
4. Keep one-time panel sealed.
5. If Lane A revises A2/A3/V4.2, hostile-review the exact new head.
6. Hugging Face:
   - no paid launch without Patrick explicit spend authorization
   - if Patrick approves, first require repaired A3 package and live-rate/cost guard
7. Continue CPU/source-only plasticity/behavior/identity research when it does not interfere with Lane A/C work.
