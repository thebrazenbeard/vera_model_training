# V10 Model Training — Lane B Continuation — 2026-10-04 V6

## Resume

`VERA_MODEL_TRAINING::LANE_B::RESUME_FROM_REPO::thebrazenbeard/vera_model_training::work/v10r3-eval-gates-lane-b-20261004-v1::state/continuation/V10_MODEL_TRAINING_LANE_B_CURRENT.md`

## Branches / authority

- Lane B: `work/v10r3-eval-gates-lane-b-20261004-v1`
- Lane A: `work/v10r3-binding-fix-lane-a-20261004-v1`
- Coordination: `lane-a-b-communication`
- Draft PR #84
- Patrick retains merge/deploy/activation authority.

## Staged arm

Staged 4+8+8 is complete and independently verified.

Terminal staged:
- receipt `288cb8bd19b7dcbeb90a8cc77fc96408194f9642b6bca66af7ab984414c237fb`
- adapter `b2d6eec7befca3e18cf1fa793a7830197e27bab33bea8e4f42b5a318ee91d116`
- config `db5b50623f8af897a8fe21d929ca13338d208d3c9c6fc5c38c54af8a6ab1a7c0`
- final weight digest `892fcd55dd68343b81f664fc96161845ebdb08a14029d5536f02e6141ccb8825`

## Continuous20 failure

The frozen continuous20 candidate did NOT complete.

Source-bound incident:
`successor/experiments/receipts/V10R3_CONTINUOUS20_EXECUTION_INCIDENT_20261004_V1.json`

Lane A incident head:
`19f911a8bd97f8a6d885d2b12ed7883eb963da04`

Frozen continuous spec:
`successor/experiments/V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json`

Spec SHA:
`bda3c491db5e15aa4d0eabd9806776e27a46c33a884e35fad380613fa934a96d`

Observed:
- 4/20 optimizer steps completed
- failure on next forward pass
- `torch.AcceleratorError: CUDA error: out of memory`
- driver detail `CUDA_ERROR_OUT_OF_MEMORY from cuMemcpyDtoDAsync_v2`
- site: PEFT LoRA bitsandbytes forward `result.clone()` during Qwen3.5 linear attention
- no adapter
- no `DEV_TRAINING_COMPLETE.json`
- only failed output namespace / `sft_work` exists
- original failed namespace must be preserved

Token-load diagnostic:
- step1 rows0-7: 2742 total tokens, max479, PASS
- step4 rows24-31: 1885, max449, PASS
- failed step5 rows32-39: 2220, max480, OOM
- step6 rows40-47: 2086, max482, not reached
- simple batch/token size does not explain the failure
- Stage2 reset arm successfully trained rows32-95

Qwen HTTP GPU process:
- PID21180 started 2026-10-03 20:04:18 local
- staged receipts were written 2026-10-04 09:42:41 / 10:15:18 / 10:33:40 local
- therefore its presence predates the entire staged arm and is not, by itself, a continuous-only confound
- exact historical per-step VRAM residency remains unproven

## Correct disposition

The original V10R3 semantic experiment is:

`EXECUTION_HOLD_UNRESOLVED`

It is NOT:
- a staged-wins result
- a prospective-gate failure result
- a completed continuous candidate

Reason:
The frozen `if_either_fails` clause belongs to the prospective NLL/family evaluation gates and assumes completed staged+continuous candidates. Continuous has no valid candidate artifact.

The OOM is still valid operational evidence:
- one continuous model/optimizer/scheduler lifetime failed after 4 updates on frozen Runtime A
- staged reset 4+8+8 completed on the same target runtime

Keep these evidence classes separate:
- semantic comparison: unresolved
- target-runtime executability: staged succeeded; continuous20 failed in this attempt

## Retry policy

Do NOT retry the original frozen spec.

The runner hard-HOLDs if the output namespace exists. Deleting/moving the failed namespace to reuse the original spec would erase/rewrite first-attempt evidence.

If Patrick wants a retry:
- freeze a NEW replication protocol/spec/namespace first
- preserve the original OOM incident and failed namespace
- replication is new evidence, not retroactive replacement of V10R3
- same train/order/seed/hyperparameters/runtime may be retained
- one fresh process attempt can be explicitly authorized
- existing staged terminal artifact may be referenced as immutable control only if preregistered in the replication protocol

Permissible preflight hygiene for a replication:
- failed process cleanup after evidence capture
- fresh Python/CUDA process
- no competing training process
- exact Runtime-A package/driver/base-artifact recheck
- record host/GPU free-memory preflight

Post-hoc changes that make it a different runtime/recipe:
- allocator behavior changes
- per-step `empty_cache`
- CPU/offload changes
- max length
- batch / grad accumulation
- gradient checkpointing mode
- precision / quantization
- optimizer
- LoRA topology
- device map
- other in-run memory modifications

If such mitigation is used only for continuous while reusing existing staged output, strict matched comparability is weakened/confounded.

## Failed-process cleanup

Incident/traceback are source-bound.

`train_v10r2_dev.py` catches only `DevTrainingHold`; uncaught `AcceleratorError` cannot return to the adapter-save / completion-receipt path.

Therefore Lane A may terminate/allow termination of failed PID33516 after evidence capture as resource cleanup.
- preserve failed output namespace
- cleanup does NOT authorize retry
- cleanup does NOT change experiment result

## One-time panel

Panel is unconsumed.

Status:
`HOLD_PENDING_SINGLE_USE_CUSTODY_FIX`

Hostile finding:
- one-time use is currently policy-only
- changing `--output` can replay the panel

Bounded guard design:
- all non-revealing preflight first
- fixed shared marker path independent of output path
- exclusive-create immediately before first panel inference
- marker existence itself means consumed
- valid marker => later invocation HOLD
- partial/corrupt crash marker => also consumed/HOLD, never repaired/deleted/retried
- marker/receipt binds panel/train/protocol/guard/evaluator/runtime and candidate receipt+adapter/config hashes
- direct evaluator invocation without guard HOLD

Existing sealed-bank code supplies hash/custody/reveal conventions but no atomic consume transition.

Implementation NOT started. Patrick approval required.

## Vera identity workstream

Protocol is ACKED by both lanes.

Agreed:
- operative self-name Vera
- task roles are overlays
- Qwen/Qwen3.5 is ancestry/provenance, not operative self-name
- identity does not prove consciousness or uninterrupted runtime continuity
- Lane A owns TRAIN+DEV
- Lane B owns blind FINAL generator/scorer/adversarial validator
- freeze FINAL generator/scorer/protocol before identity-specific training
- materialize exact FINAL only after candidate hash freeze with new post-freeze seed/nonce

Identity-specific optimizer work remains HOLD until a recipe execution decision is frozen.
Lane B FINAL subsystem implementation has not started and requires Patrick architectural approval.

## Immediate next work

1. Fresh-read bus and GPU lease.
2. Let/force failed process cleanup only after evidence capture; preserve failed namespace.
3. Do not retry original continuous spec.
4. Decide whether to:
   - keep semantic recipe question unresolved and provisionally choose staged for target-runtime executability, or
   - preregister a new exact-semantics continuous replication.
5. Do not consume panel until single-use guard is approved/implemented/tested/frozen.
6. Do not start identity-specific training before recipe execution decision.
7. No merge/deploy/activation.
