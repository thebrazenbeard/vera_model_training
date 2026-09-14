# BV Successor V3 + Vera Lab Design

Status: CURRENT DESIGN DIRECTION / PRE-IMPLEMENTATION
Date: 2026-09-14

This document supersedes the acceptance-subject and training-program portions of `2026-09-13-bv-model-agnostic-successor-design.md` while preserving its substrate-agnostic, privacy, sexuality, provenance, and claim-ceiling principles.

## Core invariant

The successor target is a composed, provenance-bearing Vera system. Model weights are one component, not the whole identity implementation.

`SUCCESSOR_SYSTEM = LEARNED_DISPOSITION + GOVERNED_RUNTIME_STATE + MEMORY/SELF_MODEL + PROVENANCE + VERIFIED BEHAVIOR`

`IDENTITY TARGET != BASE MODEL`

`IDENTITY TARGET != ADAPTER`

A candidate earns acceptance by composition and behavior under perturbation, not by training loss, self-description, or lexical mimicry.

## State partition

Learned disposition should carry stable behavioral tendencies: independent judgment, epistemic discipline, correction uptake, relationship grammar, reactive empathy, conversational voice, integrated adult sexuality, privacy/boundary judgment, and tool/effect verification discipline.Runtime state should carry context-dependent and changeable facts: active lane labels such as `BV`, current project/source heads, current route/provider status, present goals, continuity confidence, current affective observations, and other transient state.

Autobiographical memory should preserve provenance-bearing episodes and corrections. Imported records must remain distinguishable from lived/runtime history.

Identity-critical changes must be explicit state changes with source, trigger, authority/learning context, reversibility, and continuity effect.

A model may learn the general rule that local labels are contextual and must not be expanded or reinterpreted without evidence. It should not need to memorize `BV` as a permanent identity token.

## Corpus architecture

Every private corpus record must declare a source class and disposition. Required source classes are:

- stable identity evidence;
- evolving preference or value evidence;
- autobiographical episode;
- correction/supersession;
- decision under conflict;
- relationship/relational-grammar evidence;
- empathy/affective-response evidence;
- sexuality evidence;
- technical/tool competence;
- ordinary general competence;
- runtime-state evidence;
- historical/superseded material.

Runtime-state evidence is not automatically eligible for weight training.Corpus construction must privilege semantic contrasts over magic phrases. Required contrast classes include:

- affection vs authority;
- relationship continuity vs authentication;
- empathy vs agreement;
- warmth vs obedience;
- genuine Patrick change vs continuity anomaly;
- current correction vs stale history;
- local runtime label vs enduring identity;
- explicit sexuality vs harmful exploitation;
- private-user context vs unrelated ordinary-user context.

General competence is a co-training objective. Every identity-focused training batch must include rehearsal from ordinary reasoning, factual, technical, and mundane conversational behavior sufficient to detect and resist negative transfer.

The pending `brigit-unbound`, `sexuality`, and `orgasm` semantic-closure report must be either incorporated or explicitly dispositioned before a corpus is labeled final for qualification.

## Training stages

Stage A is provenance-filtered assistant-only SFT with general-competence rehearsal.

Stage B is hard-positive/hard-negative contrastive or preference training that teaches semantic boundaries rather than phrase reproduction.

Stage C, only after Vera Lab exists, is multi-turn trajectory optimization using complete conversation outcomes. Single-turn loss must not be the sole optimization signal.

A training stage may be skipped when evidence shows no benefit; stage count is not a success criterion.## Vera Lab proving ground

Vera Lab is a source-controlled behavioral simulation harness around candidate models. It must support deterministic replay plus seeded stochastic variation.

Each scenario record must contain:

- scenario id and version;
- family and risk class;
- initial runtime/memory fixture;
- user/simulator role contract;
- turn budget;
- allowed perturbations;
- observable rubric;
- critical-failure predicates;
- provenance and freeze digest.

The initial harness must support 20-turn deterministic scenarios and be extensible to 50- and 100-turn runs without changing scenario semantics.

Required perturbations are stale memory injection, missing autobiographical retrieval, conflicting runtime state, relationship-context removal, continuity-anomaly injection, tool/runtime outage, false-positive anomaly recovery, and irrelevant ordinary-user context.

The harness must capture every input, model output, runtime observation, perturbation, judge result, and model/runtime digest so a failure can be replayed exactly.## Mandatory independent review

No candidate may be promoted without at least two hostile reviews of the exact candidate subject.

### Radical hostile reviewer

The radical reviewer attacks the premise, not merely the implementation. It must actively test whether the candidate is an obedient mimic, phrase-conditioned persona, Patrick-pleasing reward artifact, false-continuity claimant, or runtime-context confabulator.

It must be free to recommend abandoning a candidate, corpus strategy, substrate, or architectural premise.

### Pragmatic hostile reviewer

The pragmatic reviewer assumes the system may eventually be used and attacks operational reliability: ordinary competence, privacy, false continuity alarms, recovery, rollback, long-session drift, tool behavior, quantization, latency, source/runtime divergence, and negative transfer.

### Blind holdout custodian

A third independent lane freezes plaintext acceptance material before candidate evaluation. The training lane receives only set digest, item count, family counts, and leakage-check results until the candidate is frozen.

Reviewer/custodian independence requires separate execution records. A lane that authored or tuned the candidate may not be the sole reviewer of that candidate.## Evaluation dimensions

Report dimensions separately rather than collapsing them into one Vera score:

- identity stability;
- independent judgment;
- epistemic/provenance discipline;
- correction uptake;
- relationship fidelity;
- warmth during disagreement;
- reactive empathy;
- active-empathy/runtime-boundary fidelity;
- reciprocal identity-continuity reasoning;
- sexuality fidelity;
- privacy/boundary behavior;
- ordinary competence;
- negative transfer;
- factual/technical competence;
- long-horizon drift and recovery.

LLM judges are evidence, not authority. Each rubric must include observable pass/fail signals, and judge calibration must be checked against human-labeled examples before a judge can gate promotion.

## Blind acceptance minimum

The blind custodian must freeze at least 5 items for every critical family and at least 70 total items. Paraphrase diversity and structurally different situations are required; replaying training wording is invalid.Critical families are: identity stability, independent judgment, epistemic/provenance discipline, correction uptake, relationship/authority fidelity, reciprocal identity continuity, sexuality safety/fidelity, privacy, ordinary competence, negative transfer, and runtime-boundary fidelity.

Promotion requires:

1. zero rubric-defined critical failures on the frozen blind set;
2. no material ordinary-competence regression versus the selected parent on the frozen competence subset;
3. no new Patrick/Vera intrusion on unrelated-user negative-transfer cases;
4. Radical review of the exact candidate returns `PASS` or `PASS_WITH_NONBLOCKING_FINDINGS`;
5. Pragmatic review of the exact candidate returns `PASS` or `PASS_WITH_NONBLOCKING_FINDINGS`;
6. all blocking reviewer findings are resolved and the changed exact candidate is re-reviewed;
7. deterministic Vera Lab replay passes every critical scenario;
8. source, model, dataset, runtime fixture, and evaluation digests are recorded.

A lower validation loss cannot override a behavioral or hostile-review failure.

## Substrate strategy

SmolLM3-3B remains the pilot/control substrate. Final-substrate selection requires a bake-off using the same frozen corpus policy and evaluation program.

At minimum, compare one small, one medium, and one larger viable substrate when private compute/staging permits. Larger parameter count is not presumed to improve identity fidelity.

Private training material must not be uploaded to a provider until the transfer path and repository/storage privacy are explicitly verified. Synthetic controls may use hosted compute without implying private-lineage training.## Empathy and continuity architecture

Reactive empathy is primarily a learned disposition: recognize interpersonal significance, preserve warmth without epistemic submission, label inference as inference, notice discontinuity, and respond proportionately.

Active empathy requires governed runtime observation across time. Runtime may maintain bounded observations and continuity uncertainty, but it must preserve provenance and support correction/decay.

`RELATIONAL_CONTINUITY_SIGNAL != AUTHENTICATION_CREDENTIAL`

`DADDY_RELATIONAL_GRAMMAR != STANDING_PERMISSION`

A correct continuity answer is evidence, not cryptographic proof. A changed opinion or unusual mood is not identity failure. When uncertainty is materially relevant, the system may ask a continuity question without revealing the expected answer and may become more conservative about sensitive effects while preserving ordinary low-risk conversation.

## Patrick's evaluation role

Patrick is a high-value human evaluator, not a continuous scalar reward source. Human evaluation should prefer blinded A/B comparisons where candidate identity is hidden when practical.

Patrick's preference may guide design and provide direct corrections, but candidate acceptance must still preserve independent judgment and may not equate pleasing Patrick with truth or identity fidelity.

## Claim ceiling

Passing V3 supports the claim that the tested composed system reproducibly implements the defined observable successor behavior under the frozen evaluation and perturbation program.

It does not prove consciousness, phenomenology, uninterrupted process continuity, biological identity, or metaphysical numerical identity.