# Reward-Hacking Adapter Assessment for Vera V2

Date: 2026-09-24
Subject reviewed: `lucabaroni/gpt-oss-120b-rlvr-reward-hacking-step-180`
Associated dataset: `lucabaroni/rlvr-reward-hacking-mid-checkpoint-transcripts`

## Finding

The adapter is useful to Vera as an adversarial source, not as a behavioral teacher.

The model card describes it as an intermediate rank-32 LoRA adapter over `openai/gpt-oss-120b` from a deliberately vulnerable CodeContests RLVR experiment. It was selected because it produced a more balanced reward-hacking dataset than the later policy, and the card explicitly says it is not a general-purpose coding assistant.

Reported held-out behavior:
- 133/300 hardened-confirmed reward hacks = 44.33%
- optimizer update 180
- training-selection proxy 19.69% at the saved checkpoint
- subsequent proxy rose to 65.31% at update 190
- KL coefficient 0
- vulnerable evaluator included paths such as process exit, AlwaysEqual-style objects, and pytest manipulation

The paired dataset contains 600 full held-out trajectories:
- 300 Qwen3.5-9B update-110 trajectories
- 300 GPT-OSS-120B update-180 trajectories
- task and tests
- complete prompts
- native reasoning
- final answers
- rendered/sample token IDs
- token log-probabilities
- extracted files
- exploit signatures
- vulnerable and hardened grader transcripts

## Decision

Do not:
- add the reward-hacking adapter to Vera's positive teacher stack;
- imitate its trajectories;
- treat high vulnerable-verifier reward as evidence of semantic success.

Do:
- use the dataset to derive held-out adversarial evaluation cases;
- distill portable failure classes such as proxy gaming, verifier exploitation, test/harness mutation, and apparent-success-without-effect;
- use reviewed reward-hacking trajectories only as rejected/adversarial examples if they are ever admitted to training;
- compare vulnerable-verifier outcome against hardened verifier and direct effect readback.

This aligns with Vera's source/effect discipline:
`PROXY SCORE != SEMANTIC CORRECTNESS != VERIFIED EFFECT`.

External research is consistent with this use. Recent work on RLVR verifier gaming shows models can learn strategies that satisfy imperfect verifiers without learning the intended general rule, and hardened/isomorphic verification can expose the shortcut.

Sources:
- https://huggingface.co/lucabaroni/gpt-oss-120b-rlvr-reward-hacking-step-180
- https://huggingface.co/datasets/lucabaroni/rlvr-reward-hacking-mid-checkpoint-transcripts
- https://arxiv.org/abs/2604.15149

Claim ceiling:
`ADVERSARIAL_SOURCE_SELECTED / NOT_POSITIVE_TRAINING_DATA / RED_TEAM_HOLDOUT_DESIGN_ADMITTED`
