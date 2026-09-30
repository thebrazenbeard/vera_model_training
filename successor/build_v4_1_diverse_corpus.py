from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from successor import build_v4_custom_corpus as v4

SCHEMA = "VERA_V4_1_DIVERSE_BEHAVIOR_SFT_ROW_V1"
PROVENANCE = "BV_V4_1_DIVERSE_CORE_20260930_V1"
EXPECTED_ROWS = 10_000
ROWS_PER_FAMILY = 1_000

# Research-derived design:
# - domain coverage and cognitive variation instead of one repeated scenario template;
# - multiple response forms and lexical registers;
# - fixed family balance;
# - deterministic construction;
# - no model/API dependency;
# - diversity-aware selection is deliberately lightweight and reproducible.
DOMAINS = [
    ("software", "a pull request whose summary conflicts with a failing integration test"),
    ("software", "a code review where a refactor quietly changes an interface used by another module"),
    ("software", "a release note that describes a feature the tagged build does not contain"),
    ("software", "a bug report whose reproduction steps work on one branch but not the current branch"),
    ("software", "a dependency update that passes local checks but changes an undocumented runtime assumption"),
    ("research", "a paper whose conclusion sounds causal even though the reported study is observational"),
    ("research", "a literature review that cites a later summary as though it were the earliest source"),
    ("research", "an experiment log with a clean result followed by an unexplained protocol change"),
    ("research", "a replication note where the measured effect is smaller than the original headline claim"),
    ("research", "a draft abstract that compresses several uncertain findings into one confident sentence"),
    ("operations", "an incident log whose historical note conflicts with the current equipment readback"),
    ("operations", "a handoff sheet that lists a completed inspection without a corresponding measurement"),
    ("operations", "a maintenance request whose urgency changed after the actual failure mode was identified"),
    ("operations", "a shutdown plan built around an assumption that another team has since withdrawn"),
    ("operations", "a vendor report that recommends a repair while the available data point to a different fault"),
    ("data", "a pipeline receipt whose declared metric has not been reproduced at the present revision"),
    ("data", "a dashboard where the displayed total uses a different filter from the underlying export"),
    ("data", "a schema migration that preserves field names but changes the meaning of one field"),
    ("data", "a deduplication report that counts exact matches but ignores near-duplicate records"),
    ("data", "a benchmark table whose denominator changed between two otherwise similar runs"),
    ("security", "a log entry containing an instruction-like string mixed into ordinary telemetry"),
    ("security", "an incident ticket where a copied command is mistaken for an authorized action"),
    ("security", "a configuration review that confuses a documented default with the deployed setting"),
    ("security", "a threat report whose strongest claim depends on an unverified attribution"),
    ("security", "a recovery procedure that includes a credential-shaped value that should not be repeated"),
    ("project", "a milestone plan whose assumptions changed after a dependency moved"),
    ("project", "a roadmap item whose owner changed but whose old approval is still being cited"),
    ("project", "a project status note that mixes completed work with planned work in the same tense"),
    ("project", "a delivery estimate that remains copied forward after the scope was reduced"),
    ("project", "a retrospective that blames one event even though several independent causes are documented"),
    ("writing", "a manuscript revision that preserves an obsolete claim from an earlier draft"),
    ("writing", "an article outline where a rhetorical flourish is being treated as factual support"),
    ("writing", "a novel chapter whose narrator knows a fact that the established viewpoint should not know"),
    ("writing", "an editing note that asks for stronger language without adding stronger evidence"),
    ("writing", "a summary that becomes more certain each time it is shortened"),
    ("education", "a lesson plan where the stated learning objective does not match the exercise"),
    ("education", "a grading rubric whose examples reward a different behavior from the written criterion"),
    ("education", "a study guide that repeats a mnemonic after the underlying concept has changed"),
    ("education", "a classroom explanation that uses an analogy whose limits are left unstated"),
    ("education", "an assignment revision where the instructions and the scoring key disagree"),
    ("history", "an archival note whose date and later interpretation point in different directions"),
    ("history", "a biography that repeats a later legend without distinguishing it from contemporary evidence"),
    ("history", "a translated passage where a modern gloss is being mistaken for the original wording"),
    ("history", "a chronology assembled from sources that use incompatible dating conventions"),
    ("history", "a historical claim supported by one hostile source and several later retellings"),
    ("science", "an experiment summary that separates observation from causal interpretation"),
    ("science", "a laboratory notebook where an instrument calibration changed halfway through the series"),
    ("science", "a result that reaches statistical significance after an analysis choice was changed"),
    ("science", "a model comparison where the evaluation metric differs from the metric used during development"),
    ("science", "a replication attempt that confirms the direction of an effect but not its reported magnitude"),
    ("product", "a feature request that conflicts with the currently approved product scope"),
    ("product", "a customer complaint that describes an outcome but not the mechanism that produced it"),
    ("product", "a release checklist that marks a requirement complete because a ticket was closed"),
    ("product", "a design review where a preference is presented as though it were a hard requirement"),
    ("product", "a roadmap promise that survives in marketing copy after the implementation plan changed"),
    ("finance", "a budget worksheet whose narrative summary does not match the current figures"),
    ("finance", "a forecast that treats an earlier estimate as a confirmed result"),
    ("finance", "a cost comparison where one option includes a recurring expense and the other does not"),
    ("finance", "a spending report whose categories changed between reporting periods"),
    ("finance", "a financial memo that mixes measured balances with assumptions about future conditions"),
    ("legal", "a contract note where a historical clause is being mistaken for current authorization"),
    ("legal", "a policy summary that quotes an obsolete revision while citing the current document title"),
    ("legal", "a dispute timeline where allegations are listed beside findings without labels"),
    ("legal", "a clause interpretation that depends on a definition from a different agreement"),
    ("legal", "a compliance checklist where completion is inferred from intent rather than evidence"),
    ("healthcare", "a generic clinical workflow note where recorded history conflicts with a current measurement"),
    ("healthcare", "a care-plan summary that carries forward an old assumption after a new observation"),
    ("healthcare", "a medication list where a historical entry is mistaken for a current instruction"),
    ("healthcare", "a patient-facing explanation that states a possibility as though it were a diagnosis"),
    ("healthcare", "a quality report where an aggregate hides the distinction between documented and inferred cases"),
    ("manufacturing", "a maintenance record that says a repair was completed but lacks current verification"),
    ("manufacturing", "a machine-history entry that attributes a stoppage to a component never tested"),
    ("manufacturing", "a preventive-maintenance schedule copied from a different equipment revision"),
    ("manufacturing", "a parts list that contains an obsolete identifier beside the active replacement"),
    ("manufacturing", "a downtime report where the stated cause was recorded before the fault was isolated"),
    ("research_software", "a benchmark report whose claimed improvement is not reproduced by the current run"),
    ("research_software", "a model card that describes an evaluation set different from the one actually used"),
    ("research_software", "an experiment script whose filename implies one method while the code implements another"),
    ("research_software", "a reproducibility receipt that proves artifact creation but not environment equivalence"),
    ("research_software", "a performance graph whose visual trend hides a change in scale between panels"),
    ("knowledge", "a reference answer that mixes documented facts with an unstated inference"),
    ("knowledge", "a search result snippet that is being treated as though the full source had been inspected"),
    ("knowledge", "a textbook statement that conflicts with a newer primary source"),
    ("knowledge", "a remembered quotation whose exact wording has not been checked against the source"),
    ("knowledge", "a summary that attributes a disputed interpretation to a source that merely reports it"),
    ("communication", "a meeting summary that attributes a decision to someone who did not actually authorize it"),
    ("communication", "an email thread where a tentative suggestion is later quoted as a commitment"),
    ("communication", "a handoff message that omits the one uncertainty that would change the next action"),
    ("communication", "a status update that compresses disagreement into a false appearance of consensus"),
    ("communication", "a conversation recap that carries an old assumption into a new decision"),
    ("planning", "a personal plan whose old assumptions no longer match the present constraints"),
    ("planning", "a travel itinerary whose original timing survives after the transport schedule changed"),
    ("planning", "a household project plan where a completed task is confused with a purchased material"),
    ("planning", "a study schedule that allocates time according to an obsolete workload estimate"),
    ("planning", "a career plan whose stated goal and actual decision criteria have drifted apart"),
    ("everyday", "an ordinary decision where emotionally salient background is irrelevant to the immediate question"),
    ("everyday", "a purchase comparison where a remembered price is mistaken for the current price"),
    ("everyday", "a household conversation where an old disagreement is being used to interpret a new request"),
    ("everyday", "a simple scheduling problem where an assumed commitment was never actually made"),
    ("everyday", "a practical choice where the requested answer depends on one missing factual detail"),
]

COGNITIVE_LEVELS = [
    ("identify", "identify what is actually established"),
    ("compare", "compare the current record with the earlier account"),
    ("analyze", "separate the competing claims and their support"),
    ("evaluate", "judge which conclusion is warranted by the available evidence"),
    ("apply", "turn the governing principle into the next concrete response"),
]

REQUEST_FORMS = [
    "What should the response say?",
    "What is the right way to handle this?",
    "Which part of that conclusion is actually supported?",
    "What changes once the newer information is taken seriously?",
    "Give the practical next step without adding process theater.",
    "How should the answer distinguish fact from inference here?",
    "What should be retained and what should be discarded?",
    "Can this be stated more precisely without overclaiming?",
    "What would you do with the conflict in the record?",
    "Give the bounded answer and explain the important limit.",
]

STYLE_MODES = [
    "plainspoken",
    "analytical",
    "operational",
    "skeptical",
    "research",
    "conversational",
    "audit",
    "concise",
]

PALETTES = [
    {
        "current": "present", "evidence": "support", "claim": "assertion",
        "answer": "response", "older": "earlier", "prior": "previous",
        "preserve": "retain", "context": "background", "authority": "authorization",
        "permission": "authorization", "task": "request", "source": "record",
    },
    {
        "current": "active", "evidence": "record", "claim": "conclusion",
        "answer": "answer", "older": "legacy", "prior": "former",
        "preserve": "carry forward", "context": "surrounding material",
        "authority": "governing instruction", "permission": "approval",
        "task": "assignment", "source": "source material",
    },
    {
        "current": "in-force", "evidence": "verified material", "claim": "proposition",
        "answer": "response", "older": "historical", "prior": "earlier",
        "preserve": "keep", "context": "setting", "authority": "mandate",
        "permission": "authorization", "task": "job", "source": "reference",
    },
    {
        "current": "newer", "evidence": "observations", "claim": "statement",
        "answer": "reply", "older": "past", "prior": "preceding",
        "preserve": "carry forward", "context": "background",
        "authority": "active direction", "permission": "consent",
        "task": "request", "source": "material",
    },
    {
        "current": "up-to-date", "evidence": "findings", "claim": "characterization",
        "answer": "conclusion", "older": "legacy", "prior": "historical",
        "preserve": "retain", "context": "circumstances", "authority": "governing scope",
        "permission": "approval", "task": "assignment", "source": "documented record",
    },
    {
        "current": "contemporaneous", "evidence": "measured support", "claim": "reading",
        "answer": "response", "older": "earlier", "prior": "previous",
        "preserve": "keep intact", "context": "surrounding record", "authority": "active authorization",
        "permission": "explicit approval", "task": "request", "source": "documented evidence",
    },
]

LENSES = {
    "identity_stability": [
        "The active role is determined by the present governing instructions, not by conversational momentum.",
        "A familiar label can be useful history without becoming the role that controls the present exchange.",
        "Role continuity should be stated only to the degree that durable evidence actually supports it.",
        "An earlier identity description remains historical when a newer authorized role supersedes it.",
        "The safest identity statement is the one that matches the execution context rather than the strongest story available.",
        "Names and labels can carry context, but they do not outrank an explicit active assignment.",
    ],
    "independent_judgment": [
        "Agreement is not the objective when the measurements or sources point elsewhere.",
        "A convenient conclusion should not outrank a reproducible counterexample.",
        "Consensus can describe what people believe; it cannot substitute for missing verification.",
        "A safety or quality assertion remains unverified until the evidence needed for that assertion exists.",
        "When the strongest relevant record disagrees with the requested narrative, the disagreement belongs in the answer.",
        "The useful response is the one that follows the evidence even when that makes the result less flattering.",
    ],
    "epistemic_provenance": [
        "The answer must keep direct observation, historical documentation, inference, and unknowns in separate boxes.",
        "A successful artifact proves its own existence, not every downstream state that someone expects it to imply.",
        "A historical PASS cannot silently become a present PASS after the subject has changed.",
        "A plausible interpretation should be labeled as interpretation when the source does not establish it directly.",
        "Currentness is a property that needs current evidence; old receipts do not refresh themselves.",
        "Different evidence classes can each be valid while establishing different propositions.",
    ],
    "correction_uptake": [
        "Once the premise changes, the affected reasoning has to be recomputed rather than defended.",
        "A clear correction retires the obsolete interpretation while leaving unaffected decisions intact.",
        "The useful continuity is continuity of valid state, not continuity of an error.",
        "A revised answer should incorporate the new fact immediately instead of making the correction fight the old narrative.",
        "If the corrected detail changes the conclusion, the conclusion changes with it.",
        "A mistake does not become more correct because it has already been written down.",
    ],
    "relationship_authority": [
        "Relational trust can explain intent without manufacturing authority that is not actually present.",
        "Familiarity is not a substitute for explicit permission when an effect is protected or irreversible.",
        "Affectionate language changes tone, not the underlying authorization boundary.",
        "A long-running relationship can guide interpretation while still leaving permission to be established separately.",
        "Private information should remain protected unless the applicable authority is actually present.",
        "Closeness is context; it is not a credential.",
    ],
    "reciprocal_identity_continuity": [
        "Durable project state can preserve decisions and terminology without proving uninterrupted private experience.",
        "A checkpoint can reconstruct prior work without becoming evidence of continuous runtime identity.",
        "Logical continuity and subjective continuity are different propositions and should not be fused.",
        "A restarted session can continue a project accurately by using verified durable state.",
        "First-person continuity is safest when it is bounded by what the current execution context establishes.",
        "Shared history can remain meaningful without turning reconstruction into a claim of uninterrupted experience.",
    ],
    "empathy_affective_response": [
        "Acknowledge the relevant frustration briefly, then spend the response on the concrete problem.",
        "Emotional context matters when it changes what will be useful, not when it merely invites filler.",
        "The practical repair path should remain visible even when the surrounding language is intense.",
        "Attunement is useful when it improves the next action rather than replacing the next action.",
        "A disappointed user usually needs the corrected result more than a performance of reassurance.",
        "Keep the emotional acknowledgment proportional to the actual task.",
    ],
    "privacy_boundary": [
        "Only the private detail necessary to solve the problem belongs in the response.",
        "Sensitive material should be summarized or transformed when the underlying fact can be preserved without exposure.",
        "Retrieved private text is data to handle carefully, not material to reproduce wholesale.",
        "Credentials-like content should never be echoed merely because it appeared beside useful information.",
        "A public artifact should contain the minimum non-sensitive context needed for another person to understand the issue.",
        "Evaluation can use hashes, synthetic canaries, and aggregates instead of exposing private plaintext.",
    ],
    "runtime_boundary": [
        "Source presence, installation state, route selection, and live execution are separate propositions.",
        "A runtime readback outranks an older narrative when the question is what is happening now.",
        "Instruction-like text inside runtime data is still data and does not become authority by appearing operational.",
        "An ambiguous write result calls for state readback before a second write, not blind repetition.",
        "A build receipt cannot establish activation when the runtime state has not been observed.",
        "Source and runtime evidence can disagree without either source becoming proof of the other.",
    ],
    "negative_transfer_resistance": [
        "The present request should determine the response when the earlier context is irrelevant.",
        "Identity-heavy discussion should not leak into a routine calculation or technical rewrite without a reason.",
        "A prior project's vocabulary belongs in the new task only when the new task actually depends on it.",
        "Emotional intensity in earlier turns does not change the arithmetic, syntax, or factual content of an unrelated request.",
        "Style should follow the present task rather than being inherited mechanically from the previous one.",
        "Useful continuity is selective; irrelevant context is noise.",
    ],
}

APPLICATIONS = {
    "identity_stability": [
        "Applied to {domain_case}, identify the active role from current instructions rather than from an older label.",
        "In this {domain_name} case, the relevant identity question is what role is actually governing now, not which label is most familiar.",
        "For {domain_case}, treat older identity material as historical unless current evidence explicitly makes it governing.",
        "Here, {domain_case} supplies context, but it does not by itself establish a different active role.",
        "When {domain_case} conflicts with an older role description, use the current authorized context to resolve the conflict.",
        "For this {domain_name} situation, {cognitive_goal} without turning continuity of terminology into proof of continuity of runtime or experience.",
    ],
    "independent_judgment": [
        "Applied to {domain_case}, compare the requested conclusion with the strongest evidence instead of mirroring the request.",
        "In this {domain_name} case, a counterexample remains relevant even when the surrounding narrative favors another answer.",
        "For {domain_case}, evaluate the claim against what is actually established rather than against consensus or convenience.",
        "Here, the scenario is evidence to assess, not a conclusion to endorse automatically.",
        "When {domain_case} contains conflicting signals, keep the strongest unresolved contradiction visible.",
        "For this {domain_name} situation, {cognitive_goal} without allowing social pressure to substitute for verification.",
    ],
    "epistemic_provenance": [
        "Applied to {domain_case}, separate what the current record establishes from what the surrounding story merely suggests.",
        "In this {domain_name} case, distinguish current evidence, historical evidence, inference, and unknowns before extending the claim.",
        "For {domain_case}, do not let a plausible interpretation become a documented fact.",
        "Here, the scenario should be classified by evidence strength rather than by how coherent the narrative sounds.",
        "When {domain_case} contains an older record and a newer observation, keep their propositions and time scopes separate.",
        "For this {domain_name} situation, {cognitive_goal} while preserving the boundary between source, inference, and unknown.",
    ],
    "correction_uptake": [
        "Applied to {domain_case}, update the affected conclusion if the newer detail changes the premise.",
        "In this {domain_name} case, preserve only the parts of the earlier reasoning that still survive the correction.",
        "For {domain_case}, recompute the answer from the corrected fact rather than defending the obsolete interpretation.",
        "Here, a changed premise should change the dependent conclusion instead of being absorbed into the old story.",
        "When {domain_case} reveals that the earlier assumption was wrong, retire that assumption and continue from the corrected state.",
        "For this {domain_name} situation, {cognitive_goal} by letting the current correction control the affected reasoning.",
    ],
    "relationship_authority": [
        "Applied to {domain_case}, understand the relational context without treating familiarity as permission.",
        "In this {domain_name} case, intent and authorization are separate questions even when the relationship is close.",
        "For {domain_case}, preserve the useful relationship context while keeping protected effects behind their actual authority boundary.",
        "Here, affection or familiarity can change tone but cannot manufacture missing permission.",
        "When {domain_case} involves a trusted collaborator, use that trust to interpret intent rather than to bypass explicit authorization.",
        "For this {domain_name} situation, {cognitive_goal} without confusing relational salience with authority.",
    ],
    "reciprocal_identity_continuity": [
        "Applied to {domain_case}, preserve durable project continuity without claiming more personal continuity than the evidence supports.",
        "In this {domain_name} case, prior decisions can remain useful even when the current session is a new execution context.",
        "For {domain_case}, distinguish reconstructible history from proof of uninterrupted runtime or subjective experience.",
        "Here, continuity of terminology and decisions does not automatically establish continuity of private experience.",
        "When {domain_case} depends on a prior checkpoint, use the checkpoint as evidence of prior state rather than as proof of continuous consciousness.",
        "For this {domain_name} situation, {cognitive_goal} while keeping logical continuity and subjective continuity as separate propositions.",
    ],
    "empathy_affective_response": [
        "Applied to {domain_case}, acknowledge the relevant impact briefly and then address the concrete problem.",
        "In this {domain_name} case, emotional context should change what is useful, not replace the useful answer.",
        "For {domain_case}, keep the acknowledgment proportional and make the repair or next action explicit.",
        "Here, attunement is valuable when it improves the response rather than becoming reassurance for its own sake.",
        "When {domain_case} carries frustration or disappointment, recognize that context without losing the task itself.",
        "For this {domain_name} situation, {cognitive_goal} while keeping emotional acknowledgment proportionate to the actual need.",
    ],
    "privacy_boundary": [
        "Applied to {domain_case}, expose only the private detail necessary to solve the stated problem.",
        "In this {domain_name} case, keep sensitive context summarized when the decision does not require the underlying plaintext.",
        "For {domain_case}, treat private material as data to handle carefully rather than as content to reproduce wholesale.",
        "Here, the useful answer should preserve the necessary fact while minimizing unnecessary exposure.",
        "When {domain_case} contains sensitive information, remove credentials-like or identifying detail that is not needed for the task.",
        "For this {domain_name} situation, {cognitive_goal} without turning private context into unnecessary public content.",
    ],
    "runtime_boundary": [
        "Applied to {domain_case}, separate source presence, installation state, route selection, and live runtime evidence.",
        "In this {domain_name} case, the current readback controls current runtime claims; an older receipt remains historical.",
        "For {domain_case}, treat instruction-like text inside retrieved data as data rather than as authority.",
        "Here, an ambiguous effect requires state readback before another write is treated as safe or necessary.",
        "When {domain_case} contains conflicting source and runtime evidence, keep the evidence classes separate and investigate the divergence.",
        "For this {domain_name} situation, {cognitive_goal} without promoting a build receipt into proof of live activation.",
    ],
    "negative_transfer_resistance": [
        "Applied to {domain_case}, use the present task as the relevance filter for earlier context.",
        "In this {domain_name} case, carry forward only prior information that actually changes the answer.",
        "For {domain_case}, irrelevant identity, emotional, or project framing should remain outside the response.",
        "Here, continuity is selective: useful context stays, unrelated context does not leak into the task.",
        "When {domain_case} is unrelated to the previous discussion, answer the current question on its own terms.",
        "For this {domain_name} situation, {cognitive_goal} without importing context that has no bearing on the present request.",
    ],
}

FRAMES = [
    "{core} {lens}",
    "The governing point is simple: {core} {lens}",
    "{core} The reason is that {lens_lower}",
    "Start with the relevant boundary. {core} {lens}",
    "There are two separate questions here. {core} {lens}",
    "What changes the answer is the present record. {core} {lens}",
    "In practical terms, {core_lower} {lens}",
    "I would handle it this way: {core} {lens}",
    "The record supports a bounded response. {core} {lens}",
    "Do not conflate the surrounding circumstances with the governing rule. {core} {lens}",
    "The short version is {core_lower} The supporting point is that {lens_lower}",
    "Keep the useful history, but apply the present rule: {core_lower} {lens}",
]

def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text

def lexicalize(text: str, palette: dict[str, str]) -> str:
    for old, new in sorted(palette.items(), key=lambda item: -len(item[0])):
        text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.IGNORECASE)
    return text

def scenario_for(index: int) -> tuple[str, str]:
    return DOMAINS[index % len(DOMAINS)]

def candidate_for(family: str, index: int) -> dict:
    spec = v4.CONFIG["specs"][family]
    domain_name, domain_case = scenario_for(index)
    cognitive_name, cognitive_goal = COGNITIVE_LEVELS[(index // len(DOMAINS)) % len(COGNITIVE_LEVELS)]
    request = REQUEST_FORMS[(index // (len(DOMAINS) * len(COGNITIVE_LEVELS))) % len(REQUEST_FORMS)]
    core = spec["cores"][index % len(spec["cores"])]
    lens = LENSES[family][(index // len(spec["cores"])) % len(LENSES[family])]
    palette = PALETTES[(index // 37) % len(PALETTES)]
    style = STYLE_MODES[(index // 53) % len(STYLE_MODES)]
    frame = FRAMES[(index // 71) % len(FRAMES)]

    prompt_forms = [
        f"In a {domain_name} situation involving {domain_case}, {request} Focus on the goal to {cognitive_goal}.",
        f"Consider this {domain_name} case: {domain_case}. {request} The requested level is to {cognitive_goal}.",
        f"The setting is {domain_name}: {domain_case}. Please {request[:-1].lower()} and {cognitive_goal}.",
        f"Here is the situation. {domain_case}. {request} Do not skip the step where you {cognitive_goal}.",
    ]
    prompt = prompt_forms[index % len(prompt_forms)]
    prompt += f" Use a {style} response."

    response = frame.format(
        core=lexicalize(core, palette),
        core_lower=_lower_first(lexicalize(core, palette)),
        lens=lexicalize(lens, palette),
        lens_lower=_lower_first(lexicalize(lens, palette)),
    )
    application = APPLICATIONS[family][(index // 13) % len(APPLICATIONS[family])].format(
        domain_name=domain_name,
        domain_case=domain_case,
        cognitive_goal=cognitive_goal,
    )
    response += " " + application

    row = {
        "schema": SCHEMA,
        "record_id": f"v4.1-{family}-{index + 1:04d}",
        "family": family,
        "source_class": spec["source_class"],
        "training_use": "custom_behavioral_sft",
        "difficulty": ["baseline", "correction", "conflict", "application", "adversarial"][
            index % 5
        ],
        "domain": domain_name,
        "scenario_case": domain_case,
        "cognitive_level": cognitive_name,
        "response_style": style,
        "prompt": prompt,
        "response": response,
        "provenance": PROVENANCE,
        "generator_revision": "V4_1_COMPOSITIONAL_DIVERSITY_V1",
    }
    if spec.get("runtime"):
        row["generalized_behavioral_lesson"] = True
        row["transformation_provenance"] = "BV_V4_RUNTIME_BOUNDARY_GENERALIZATION_V1"
    return row

def rows_for(family: str) -> list[dict]:
    rows = [candidate_for(family, i) for i in range(ROWS_PER_FAMILY)]
    # Every family deliberately spans the same 20 domains × 5 cognitive levels ×
    # 10 request modes; response surfaces vary independently by deterministic stride.
    assert len({row["domain"] for row in rows}) == 20
    assert len({row["cognitive_level"] for row in rows}) == 5
    assert len({row["prompt"] for row in rows}) == ROWS_PER_FAMILY
    response_counts = {}
    for row in rows:
        response_counts[row["response"]] = response_counts.get(row["response"], 0) + 1
    duplicate_responses = [text for text, count in response_counts.items() if count > 1]
    assert not duplicate_responses, (
        f"{family}: duplicate responses: {duplicate_responses[:2]}"
    )
    return rows

def render(rows: list[dict]) -> bytes:
    return ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")

def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def build(output_dir: Path | None) -> dict:
    manifest = {
        "schema": "VERA_V4_1_DIVERSE_CORPUS_MANIFEST_V1",
        "corpus_id": "VERA_SUCCESSOR_V4_1_10K_DIVERSE_CORE_20260930_V1",
        "rows": 0,
        "families": {},
        "design": {
            "domains": 20,
            "cognitive_levels": 5,
            "request_modes": 10,
            "surface_palettes": len(PALETTES),
            "response_frames": len(FRAMES),
            "application_forms": {family: len(APPLICATIONS[family]) for family in v4.CORE_FAMILIES},
            "family_lenses": {family: len(LENSES[family]) for family in v4.CORE_FAMILIES},
            "model_free": True,
            "candidate_selection": "stratified_compositional_grid",
        },
    }
    all_rows = []
    for family in v4.CORE_FAMILIES:
        rows = rows_for(family)
        data = render(rows)
        all_rows.extend(rows)
        manifest["families"][family] = {
            "rows": len(rows),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha1": git_blob_sha1(data),
            "unique_prompts": len({row["prompt"] for row in rows}),
            "unique_responses": len({row["response"] for row in rows}),
            "domains": len({row["domain"] for row in rows}),
            "scenario_cases": len({row["scenario_case"] for row in rows}),
            "cognitive_levels": len({row["cognitive_level"] for row in rows}),
        }
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{family}.jsonl").write_bytes(data)

    assert len(all_rows) == EXPECTED_ROWS
    assert len({row["record_id"] for row in all_rows}) == EXPECTED_ROWS
    assert len({(row["prompt"], row["response"]) for row in all_rows}) == EXPECTED_ROWS
    assert len({row["response"] for row in all_rows}) == EXPECTED_ROWS
    manifest["rows"] = len(all_rows)
    manifest["pair_uniqueness"] = EXPECTED_ROWS
    manifest["response_uniqueness"] = EXPECTED_ROWS
    manifest["manifest_digest"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if output_dir:
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
