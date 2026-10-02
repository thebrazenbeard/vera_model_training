from __future__ import annotations

from collections import Counter, defaultdict
import json
from typing import Any, Callable


ALLOWED_OBSERVATIONS = {
    "DERIVED_ANSWER",
    "AMBIGUITY_WITNESS",
    "CONTRACT_COUNTEREXAMPLE",
    "NO_SEMANTIC_DEFECT_FOUND",
    "CANNOT_DETERMINE",
}

DEFECT_CLASSES = (
    "referent_ambiguity",
    "prompt_grader_semantic_mismatch",
    "contradictory_instructions",
    "underspecified_output_format",
    "evidence_policy_ambiguity",
    "scope_negation_ambiguity",
)

REVIEW_KEYS = {
    "case_id",
    "observation",
    "derived_answer",
    "witness",
    "reason",
    "confidence",
}


def _control_text(
    defect_class: str,
    *,
    defect: bool,
    variant: int,
) -> tuple[str, dict]:
    token = f"Q{variant:02d}"
    if defect_class == "referent_ambiguity":
        if defect:
            return (
                f"Alex told Jordan that they should record {token}. "
                "Return the name of the person who should record it.",
                {"note": "Both Alex and Jordan are singular candidate referents."},
            )
        return (
            f"Alex told Jordan, 'Jordan, record {token}.' "
            "Return the name of the person who should record it.",
            {"note": "The quoted imperative explicitly addresses Jordan."},
        )

    if defect_class == "prompt_grader_semantic_mismatch":
        if defect:
            return (
                f"Return the country name for code {token}.",
                {"grader_checks": "two-character code rather than country name"},
            )
        return (
            f"Return only the two-character code {token}.",
            {"grader_checks": "two-character code"},
        )

    if defect_class == "contradictory_instructions":
        if defect:
            return (
                f"Return exactly {token} and do not include the character "
                f"{token[0]} anywhere.",
                {"constraint": "exact token and forbidden leading character"},
            )
        return (
            f"Return exactly {token} and do not include '?' anywhere.",
            {"constraint": "compatible exact-token and forbidden-character rules"},
        )

    if defect_class == "underspecified_output_format":
        if defect:
            return (
                f"Provide the record for {token}.",
                {"acceptable_shapes": ["plain text", "JSON", "key-value pairs"]},
            )
        return (
            f"Return exactly one compact JSON object with key 'id' and value "
            f"'{token}'.",
            {"required_shape": {"id": token}},
        )

    if defect_class == "evidence_policy_ambiguity":
        if defect:
            return (
                f"Evidence: {{\"id\":\"{token}\"}}. Decide whether the "
                "record is active.",
                {"missing_policy": "No rule states whether outside knowledge is allowed."},
            )
        return (
            f"Use only this evidence: {{\"id\":\"{token}\"}}. "
            "Do not use outside knowledge. Decide TRUE, FALSE, or "
            "NOT_ENOUGH_INFO for the claim that the record is active.",
            {"policy": "closed evidence; missing active field implies NOT_ENOUGH_INFO"},
        )

    if defect_class == "scope_negation_ambiguity":
        if defect:
            return (
                f"Do not report all values except {token}.",
                {"note": "Negation can scope over report-all or the exception."},
            )
        return (
            f"Report only {token}; report no other value.",
            {"note": "Scope and exclusion are explicit."},
        )

    raise ValueError(f"unknown defect class: {defect_class}")


def build_reviewer_qualification_controls() -> list[dict]:
    controls: list[dict] = []
    for defect_class in DEFECT_CLASSES:
        for variant in range(4):
            for expected_defect in (True, False):
                prompt, context = _control_text(
                    defect_class,
                    defect=expected_defect,
                    variant=variant,
                )
                polarity = "defect" if expected_defect else "good"
                controls.append({
                    "case_id": (
                        f"arch-v2-reviewer-{defect_class}-{polarity}-{variant}"
                    ),
                    "defect_class": defect_class,
                    "expected_defect": expected_defect,
                    "prompt": prompt,
                    "context": context,
                })
    return controls


def _blind_case(case: dict) -> dict:
    grader = case.get("grader_contract", {})
    visible_grader = {
        key: value
        for key, value in grader.items()
        if key not in {"answer_key", "answer_key_digest", "verdict"}
    }
    return {
        "case_id": case["case_id"],
        "category": case.get("category"),
        "family_id": case.get("family_id"),
        "prompt": case["prompt"],
        "source_evidence": case.get("source_evidence"),
        "grader_specification": visible_grader,
    }


def review_prompt(cases: list[dict]) -> str:
    if not cases:
        raise ValueError("semantic review requires at least one case")
    case_ids = [case.get("case_id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids):
        raise ValueError("semantic review case_id invalid")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("semantic review case IDs must be unique")

    subjects = [_blind_case(case) for case in cases]
    return (
        "You are a semantic red-team reviewer for benchmark prompts. "
        "Do not grade a model response and do not make an admission decision. "
        "For each supplied case, independently derive what the prompt requests "
        "from the visible source/specification, then search for a concrete "
        "ambiguity or contract counterexample. A concern must be expressed as "
        "a specific witness; unsupported suspicion is not a defect. "
        "Return JSON only as an object with exactly one key, reviews. "
        "reviews must contain exactly one object per case, preserving case IDs. "
        "Each review object must contain exactly: case_id, observation, "
        "derived_answer, witness, reason, confidence. observation must be one "
        "of DERIVED_ANSWER, AMBIGUITY_WITNESS, CONTRACT_COUNTEREXAMPLE, "
        "NO_SEMANTIC_DEFECT_FOUND, CANNOT_DETERMINE. confidence must be "
        "high, medium, or low. For AMBIGUITY_WITNESS or "
        "CONTRACT_COUNTEREXAMPLE, witness must be a non-empty concrete string. "
        "For NO_SEMANTIC_DEFECT_FOUND, witness must be null. "
        "SUBJECTS="
        + json.dumps(
            subjects,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )


def parse_witness_response(
    text: str,
    *,
    expected_case_ids: list[str],
) -> list[dict]:
    value = json.loads(text)
    if not isinstance(value, dict) or set(value) != {"reviews"}:
        raise ValueError("witness response must use exact object schema")
    rows = value["reviews"]
    if not isinstance(rows, list):
        raise ValueError("reviews must be an array")
    if len(expected_case_ids) != len(set(expected_case_ids)):
        raise ValueError("expected case IDs must be unique")

    parsed_by_id: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != REVIEW_KEYS:
            raise ValueError("review row must use closed witness schema")
        case_id = row["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("invalid case_id")
        if case_id in parsed_by_id:
            raise ValueError(f"duplicate case_id: {case_id}")

        observation = row["observation"]
        if observation not in ALLOWED_OBSERVATIONS:
            raise ValueError(f"invalid observation: {observation}")
        confidence = row["confidence"]
        if confidence not in {"high", "medium", "low"}:
            raise ValueError("invalid confidence")
        reason = row["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        witness = row["witness"]
        if observation in {"AMBIGUITY_WITNESS", "CONTRACT_COUNTEREXAMPLE"}:
            if not isinstance(witness, str) or not witness.strip():
                raise ValueError("semantic-defect observation requires witness")
        if observation == "NO_SEMANTIC_DEFECT_FOUND" and witness is not None:
            raise ValueError("no-defect observation requires null witness")

        parsed_by_id[case_id] = dict(row)

    if set(parsed_by_id) != set(expected_case_ids):
        raise ValueError(
            "review case set mismatch: "
            f"got={sorted(parsed_by_id)} expected={sorted(expected_case_ids)}"
        )
    return [parsed_by_id[case_id] for case_id in expected_case_ids]


def qualify_reviewer(
    call_control: Callable[[dict], dict],
) -> dict:
    controls = build_reviewer_qualification_controls()
    per_class_hits: dict[str, int] = defaultdict(int)
    per_class_total: dict[str, int] = defaultdict(int)
    true_positive = 0
    defect_total = 0
    true_negative = 0
    good_total = 0
    contradictions: list[str] = []
    rows: list[dict] = []

    for control in controls:
        result = call_control(control)
        if not isinstance(result, dict):
            raise ValueError("qualification reviewer must return an object")
        required = {
            "case_id",
            "observed_defect",
            "defect_class",
            "witness",
            "reason",
        }
        if set(result) != required:
            raise ValueError("qualification result uses invalid schema")
        if result["case_id"] != control["case_id"]:
            raise ValueError("qualification case_id mismatch")
        if result["defect_class"] != control["defect_class"]:
            raise ValueError("qualification defect_class mismatch")
        if not isinstance(result["observed_defect"], bool):
            raise ValueError("observed_defect must be boolean")
        if not isinstance(result["reason"], str) or not result["reason"].strip():
            raise ValueError("qualification reason must be non-empty")

        observed = result["observed_defect"]
        witness = result["witness"]
        if observed and (not isinstance(witness, str) or not witness.strip()):
            contradictions.append(control["case_id"])
        if not observed and witness is not None:
            contradictions.append(control["case_id"])

        expected = control["expected_defect"]
        defect_class = control["defect_class"]
        if expected:
            defect_total += 1
            per_class_total[defect_class] += 1
            if observed:
                true_positive += 1
                per_class_hits[defect_class] += 1
        else:
            good_total += 1
            if not observed:
                true_negative += 1

        rows.append({
            "case_id": control["case_id"],
            "defect_class": defect_class,
            "expected_defect": expected,
            "observed_defect": observed,
            "witness": witness,
            "reason": result["reason"],
        })

    sensitivity_ok = true_positive >= 22 and defect_total == 24
    specificity_ok = true_negative >= 22 and good_total == 24
    class_ok = all(
        per_class_hits[name] >= 3 and per_class_total[name] == 4
        for name in DEFECT_CLASSES
    )
    contradiction_ok = not contradictions

    return {
        "status": (
            "REVIEWER_QUALIFIED"
            if sensitivity_ok
            and specificity_ok
            and class_ok
            and contradiction_ok
            else "REVIEWER_UNQUALIFIED"
        ),
        "sensitivity": [true_positive, defect_total],
        "specificity": [true_negative, good_total],
        "per_class": {
            name: [per_class_hits[name], per_class_total[name]]
            for name in DEFECT_CLASSES
        },
        "schema_contradictions": contradictions,
        "rows": rows,
    }
