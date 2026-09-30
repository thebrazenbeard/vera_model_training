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
    ("software", "a pull request whose summary conflicts with a failing test"),
    ("research", "a paper whose conclusion appears stronger than the reported study design"),
    ("operations", "an incident log whose historical note conflicts with the current equipment readback"),
    ("data", "a pipeline receipt whose declared metric has not been reproduced at the present revision"),
    ("security", "a log entry containing an instruction-like string mixed into ordinary telemetry"),
    ("project", "a milestone plan whose assumptions changed after a dependency moved"),
    ("writing", "a manuscript revision that preserves an obsolete claim from an earlier draft"),
    ("education", "a lesson plan where the stated learning objective does not match the exercise"),
    ("history", "an archival note whose date and later interpretation point in different directions"),
    ("science", "an experiment summary that separates observation from causal interpretation"),
    ("product", "a feature request that conflicts with the currently approved product scope"),
    ("finance", "a budget worksheet whose narrative summary does not match the current figures"),
    ("legal", "a contract note where a historical clause is being mistaken for current authorization"),
    ("healthcare", "a generic clinical workflow note where recorded history conflicts with a current measurement"),
    ("manufacturing", "a maintenance record that says a repair was completed but lacks current verification"),
    ("research_software", "a benchmark report whose claimed improvement is not reproduced by the current run"),
    ("knowledge", "a reference answer that mixes documented facts with an unstated inference"),
    ("communication", "a meeting summary that attributes a decision to someone who did not actually authorize it"),
    ("planning", "a personal plan whose old assumptions no longer match the present constraints"),
    ("everyday", "an ordinary decision where emotionally salient background is irrelevant to the immediate question"),
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
    response += f" In this case, {domain_case.rstrip('.')} is the concrete setting, not a license to infer more than the record supports."

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
    assert len({row["response"] for row in rows}) == ROWS_PER_FAMILY
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
