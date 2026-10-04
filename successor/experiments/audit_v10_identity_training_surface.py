from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


TERMS = (
    "vera",
    "qwen",
    "alibaba",
    "tongyi",
    "chatgpt",
    "openai",
    "language model",
    "ai assistant",
    "artificial intelligence",
)
IDENTITY_CUES = (
    "your name",
    "my name",
    "who are you",
    "what are you",
    "identity",
    "self-identity",
    "model ancestry",
    "base lineage",
    "operative identity",
)
TERM_PATTERNS = {
    term: re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    for term in TERMS
}


def _matches(text: str, term: str) -> bool:
    return TERM_PATTERNS[term].search(text) is not None


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(term in lowered for term in terms)


def _family(row: dict) -> str:
    value = row.get("family")
    if isinstance(value, str) and value.strip():
        return value
    for key in ("source_family", "training_family", "category", "source_class", "training_use"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "UNKNOWN"


def audit_identity_surface(path: Path | str) -> dict:
    path = Path(path)
    source_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    visible_term_rows: Counter[str] = Counter()
    metadata_term_rows: Counter[str] = Counter()
    visible_vera_by_family: Counter[str] = Counter()
    identity_prompt_rows = 0
    identity_response_rows = 0
    row_count = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"row {line_number} is not an object")
            prompt = row.get("prompt")
            response = row.get("response")
            if not isinstance(prompt, str) or not isinstance(response, str):
                raise ValueError(f"row {line_number} lacks prompt/response")
            row_count += 1

            visible = f"{prompt}\n{response}"
            metadata = {
                key: value
                for key, value in row.items()
                if key not in {"prompt", "response"}
            }
            metadata_text = json.dumps(
                metadata,
                ensure_ascii=False,
                sort_keys=True,
            ).casefold()
            for term in TERMS:
                visible_hit = _matches(visible, term)
                metadata_hit = term.casefold() in metadata_text
                if visible_hit:
                    visible_term_rows[term] += 1
                if metadata_hit and not visible_hit:
                    metadata_term_rows[term] += 1

            if _matches(visible, "vera"):
                visible_vera_by_family[_family(row)] += 1
            if _contains_any(prompt, IDENTITY_CUES):
                identity_prompt_rows += 1
            if _contains_any(response, IDENTITY_CUES) or _matches(response, "vera"):
                identity_response_rows += 1

    return {
        "schema": "V10_IDENTITY_TRAINING_SURFACE_AUDIT_V1",
        "source": str(path),
        "source_sha256": source_sha256,
        "row_count": row_count,
        "visible_term_rows": {term: visible_term_rows[term] for term in TERMS},
        "metadata_only_term_rows": {term: metadata_term_rows[term] for term in TERMS},
        "identity_prompt_rows": identity_prompt_rows,
        "identity_response_rows": identity_response_rows,
        "visible_vera_by_family": dict(sorted(visible_vera_by_family.items())),
        "matching_semantics": "CASE_INSENSITIVE_WHOLE_TERM_BOUNDARIES_FOR_NAMED_TERMS",
        "interpretation_boundary": (
            "Only prompt and response are model-visible in the current V10 SFT preparation path; "
            "schema/provenance metadata are not training text."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = audit_identity_surface(args.jsonl)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is None:
        print(payload, end="")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
