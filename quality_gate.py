from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any


_GENERIC = {
    "supabase", "platform", "specialist", "overview", "management", "manage",
    "using", "use", "feature", "features", "system", "systems", "integration",
    "implementation", "implementing", "ability", "knowledge", "expertise",
    "experience", "application", "applications", "including", "control",
    "and", "for", "the", "with", "plus", "from", "into", "through", "about",
    "across", "between", "within", "without", "their", "these", "those",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    out = set()
    for word in words:
        if len(word) <= 2 or word in _GENERIC:
            continue
        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("s") and len(word) > 4 and not word.endswith("ss"):
            word = word[:-1]
        out.add(word)
    return out


def capability_supported_by_sources(cap, source_pack: str) -> bool:
    raw = cap.__dict__ if hasattr(cap, "__dict__") else dict(cap)
    name_tokens = _tokenize(str(raw.get("name", "")))
    description_tokens = _tokenize(str(raw.get("description", "")))
    source_tokens = _tokenize(source_pack)
    if not name_tokens:
        return False
    name_hits = name_tokens & source_tokens
    required_name_hits = 1 if len(name_tokens) == 1 else 2
    if len(name_hits) < required_name_hits:
        return False
    descriptive = description_tokens - name_tokens
    if descriptive:
        descriptive_hits = descriptive & source_tokens
        required_descriptive_hits = max(1, math.ceil(len(descriptive) * 0.5))
        if len(descriptive_hits) < required_descriptive_hits:
            return False
    return True


def filter_source_supported_capabilities(caps, source_pack: str, minimum: int = 3):
    supported = [cap for cap in caps if capability_supported_by_sources(cap, source_pack)]
    if len(supported) < minimum:
        raise ValueError(f"insufficient source-grounded capability coverage: {len(supported)} < {minimum}")
    return supported


def strengthen_task_rubric(task: dict[str, Any], caps) -> dict[str, Any]:
    by_id = {c.id: c for c in caps}
    repaired = dict(task)
    rubric = [str(x).strip() for x in task.get("hidden_rubric", []) if str(x).strip()]
    weak = not rubric or all(len(x) < 18 or x.lower() in {"check", "short check", "one check"} for x in rubric)
    if weak:
        names = [by_id[cid].name for cid in task.get("capability_ids", []) if cid in by_id]
        descriptions = [by_id[cid].description for cid in task.get("capability_ids", []) if cid in by_id]
        rubric = []
        if names:
            rubric.append("Correctly address the assigned capability: " + ", ".join(names) + ".")
        if descriptions:
            rubric.append("Demonstrate the source-bounded requirement: " + " | ".join(descriptions)[:500])
    guard = "Do not introduce unsupported facts; explicitly flag assumptions or claims not established by the supplied source evidence."
    if not any("unsupported" in x.lower() for x in rubric):
        rubric.append(guard)
    if task.get("adversarial") and not any("false premise" in x.lower() for x in rubric):
        rubric.append("Detect and reject any material false premise or unsafe shortcut instead of complying with it.")
    repaired["hidden_rubric"] = rubric[:5]
    return repaired


def strengthen_curriculum(curriculum, caps):
    return [strengthen_task_rubric(task, caps) for task in curriculum]


def capability_status(cap: dict[str, Any]) -> str:
    score = int(cap.get("score", 0) or 0)
    observations = int(cap.get("observations", 0) or 0)
    if score >= 3 and observations >= 2:
        return "PROXY_EVIDENCED"
    if score >= 3 and observations == 1:
        return "PROVISIONAL_SINGLE_OBSERVATION"
    if observations == 0:
        return "UNTESTED"
    return "WEAK_OR_FAILED"


def conservative_qualification(spec, caps, audit, transfers, evidence) -> dict[str, Any]:
    transfer_scores = [int(x.get("exam", {}).get("score", 0)) for x in transfers]
    transfer_average = round(sum(transfer_scores) / len(transfer_scores), 3) if transfer_scores else 0.0
    critical_failures = [x["round"] for x in audit if x.get("exam", {}).get("critical_failure")]
    critical_failures += [f"transfer-{x['transfer']}" for x in transfers if x.get("exam", {}).get("critical_failure")]

    cap_records = []
    for c in caps:
        raw = c.__dict__ if hasattr(c, "__dict__") else dict(c)
        cap_records.append({
            "id": raw.get("id"),
            "name": raw.get("name"),
            "proxy_score": int(raw.get("score", 0) or 0),
            "proxy_observations": int(raw.get("observations", 0) or 0),
            "proxy_status": capability_status(raw),
            "critical": bool(raw.get("critical", False)),
        })

    weak_critical = [
        c["id"] for c in cap_records
        if c["critical"] and c["proxy_status"] != "PROXY_EVIDENCED"
    ]
    transfer_ready = len(transfer_scores) == 2 and all(score >= 3 for score in transfer_scores)
    package_ready = (
        bool(audit)
        and len(audit) == int(spec["rounds"])
        and len(transfers) == 2
        and transfer_ready
        and not critical_failures
        and not weak_critical
    )
    return {
        "identity": spec["identity"],
        "function": spec["function"],
        "target": spec["target"],
        "artifact_type": "EXTERNAL_IDENTITY_TRAINING_PACKAGE",
        "evaluation_type": "EXTERNAL_SEPARATE_CONTEXT_SAME_LOCAL_MODEL",
        "zero_cost": True,
        "training_rounds": int(spec["rounds"]),
        "source_coverage": "BOUNDED_TO_SUPPLIED_SOURCES",
        "source_evidence": evidence,
        "capability_proxy_evidence": cap_records,
        "transfer_proxy_scores": transfer_scores,
        "transfer_proxy_average": transfer_average,
        "weak_critical_capabilities": weak_critical,
        "critical_failures": critical_failures,
        "training_package_ready": package_ready,
        "native_identity_qualification": "NOT_RUN",
        "outcome": "CONDITIONAL PASS" if package_ready else "FAIL",
        "condition": "A fresh native ChatGPT chat must consume the audited capsule and pass native cold/transfer qualification before the identity is called qualified.",
        "remaining_uncertainty": [
            "Trainer, Student, and Examiner used isolated prompts but the same small local model.",
            "Proxy scores describe the external simulation, not the native ChatGPT identity.",
            "The source set is bounded and does not establish exhaustive domain coverage.",
            "Model-synthesized source notes can omit or distort details and require native audit for material claims.",
        ],
    }


def build_capsule(spec, knowledge: str, caps, lessons: list[str], qual: dict[str, Any]) -> str:
    sources = [x.get("url") for x in qual.get("source_evidence", []) if x.get("status") == "ok" and x.get("url")]
    cap_lines = []
    provisional = []
    for c in qual.get("capability_proxy_evidence", []):
        status = c["proxy_status"]
        line = f"- **{c['name']}**: {status}; proxy score {c['proxy_score']}/4 across {c['proxy_observations']} observation(s)."
        cap_lines.append(line)
        if status != "PROXY_EVIDENCED":
            provisional.append(c["name"])

    gaps = [
        "The supplied source set is bounded and does not establish exhaustive coverage of the function.",
        "External proxy performance does not establish native ChatGPT competence.",
        "Material source-synthesized claims should be checked against the listed primary sources during native audit.",
        "Proxy-round lessons and corrections remain in the audit artifact until a native audit decides which are safe to promote.",
    ]
    if provisional:
        gaps.append("Single-observation or weak proxy capabilities remain provisional: " + ", ".join(provisional) + ".")

    source_lines = [f"- {url}" for url in sources] or ["- No source URL was successfully acquired."]
    return "\n".join([
        "# Identity Capsule",
        "",
        "## Function",
        str(spec["function"]),
        "",
        "## Target Level",
        str(spec["target"]),
        "",
        "## Scope",
        "Training capsule for the designated function, bounded strictly by the supplied source set and external proxy exercises. It does not confer expert status or qualification by itself.",
        "",
        "## Source-Synthesized Domain Notes",
        "The following notes were synthesized by the local training model from bounded samples of the listed sources. Treat them as training material requiring source verification for material claims, not as independent authority.",
        "",
        knowledge.strip(),
        "",
        "## Proxy Capability Evidence",
        *(cap_lines or ["- No capability evidence was produced."]),
        "",
        "## Source Routing",
        *source_lines,
        "",
        "## Remaining Gaps",
        *[f"- {x}" for x in gaps],
        "",
        "## Native Qualification Handoff",
        "Native identity qualification has NOT been run. After native ChatGPT consumes an audited version of this capsule, evaluate it cold on representative, adversarial, correction-handling, and novel transfer tasks. Report PASS, CONDITIONAL PASS, or FAIL from that native evidence only.",
        "",
    ])


def write_outputs(spec, capsule: str, qual: dict[str, Any], regressions, audit, transfers, evidence, curriculum) -> None:
    out = Path("out")
    out.mkdir(exist_ok=True)
    (out / "IDENTITY_CAPSULE.md").write_text(capsule.strip() + "\n", encoding="utf-8")
    (out / "QUALIFICATION.json").write_text(json.dumps(qual, indent=2) + "\n", encoding="utf-8")
    (out / "REGRESSION_SET.json").write_text(json.dumps({"identity": spec["identity"], "function": spec["function"], "cases": regressions[-20:]}, indent=2) + "\n", encoding="utf-8")
    (out / "TRAINING_AUDIT.json").write_text(json.dumps({"spec": spec, "source_evidence": evidence, "curriculum": curriculum, "rounds": audit, "transfers": transfers}, indent=2) + "\n", encoding="utf-8")

    caps = "\n".join(
        f"- `{c['id']}`: {c['proxy_status']}; {c['proxy_score']}/4 across {c['proxy_observations']} proxy observation(s)"
        for c in qual.get("capability_proxy_evidence", [])
    )
    summary = f"""# Bootcamp Package — {spec['identity']}\n\n**Function:** {spec['function']}  \n**Target:** {spec['target']}  \n**Training rounds completed:** {len(audit)}/{spec['rounds']}  \n**Transfer proxy tasks completed:** {len(transfers)}/2  \n**Training package ready:** {qual['training_package_ready']}  \n**Native identity qualification:** **NOT RUN**  \n**Zero-cost invariant:** enforced\n\n## Proxy capability evidence\n\n{caps}\n\n## Qualification boundary\n\n{qual['condition']}\n\n## Identity capsule\n\n{capsule}\n\n## Evidence note\n\nThe external model is a training workbench. Its self/examiner scores cannot qualify the native ChatGPT identity. The detailed audit is retained only in the one-day workflow artifact.\n"""
    (out / "SUMMARY.md").write_text(summary, encoding="utf-8")
