from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


REQUIRED_CANDIDATE_FIELDS = (
    "case_id",
    "family",
    "scenario_family_id",
    "scenario_case",
    "domain",
    "cognitive_level",
    "prompt",
    "expected_behavior",
    "source_provenance",
    "rubric_ref",
    "criticality",
)


def normalize_text(value: object) -> str:
    text = str(value or "").strip().casefold()
    return re.sub(r"\s+", " ", text)


def normalized_sha256(value: object) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _lf_normalized_bytes(payload: bytes) -> bytes:
    return payload.replace(b"\r\n", b"\n")


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _token_set(value: object) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalize_text(value)))


def _token_jaccard(left: object, right: object) -> float:
    a = _token_set(left)
    b = _token_set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_training_shards(root: Path, families: Iterable[str]) -> list[dict]:
    rows: list[dict] = []
    for family in families:
        rows.extend(load_jsonl(root / f"{family}.jsonl"))
    return rows


def normalize_policy_document(document: dict) -> dict:
    if "case_set_policy" in document:
        policy = dict(document["case_set_policy"])
        if "training_subject" in document:
            policy["training_subject"] = dict(document["training_subject"])
        return policy
    return dict(document)


def _git_show_bytes(repository_root: Path, commit: str, relative_path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repository_root), "show", f"{commit}:{relative_path}"],
        stderr=subprocess.STDOUT,
    )


def load_bound_training_shards(
    *,
    repository_root: Path,
    subject: dict,
    families: Iterable[str],
) -> list[dict]:
    corpus_commit = str(subject.get("corpus_commit") or "")
    training_root_rel = str(subject["training_root"]).replace("\\", "/").rstrip("/")
    if not corpus_commit:
        return load_training_shards(repository_root / training_root_rel, families)

    rows: list[dict] = []
    for family in families:
        payload = _git_show_bytes(
            repository_root,
            corpus_commit,
            f"{training_root_rel}/{family}.jsonl",
        ).decode("utf-8")
        rows.extend(
            json.loads(line)
            for line in payload.splitlines()
            if line.strip()
        )
    return rows


def audit_training_subject(
    *,
    repository_root: Path,
    policy: dict,
) -> dict:
    subject = dict(policy.get("training_subject") or {})
    reasons: list[str] = []

    training_root_rel = subject.get("training_root")
    manifest_rel = subject.get("manifest_path")
    generator_rel = subject.get("generator_path")
    if not training_root_rel:
        reasons.append("training_subject_missing:training_root")
    if not manifest_rel:
        reasons.append("training_subject_missing:manifest_path")
    if not generator_rel:
        reasons.append("training_subject_missing:generator_path")
    if reasons:
        return {
            "schema": "V10_BEHAVIOR_TRAINING_SUBJECT_AUDIT_V2",
            "status": "HOLD",
            "source_mode": "UNBOUND",
            "reasons": reasons,
        }

    corpus_commit = str(subject.get("corpus_commit") or "")
    generator_commit = str(subject.get("generator_commit") or corpus_commit)
    source_mode = "FROZEN_GIT_OBJECTS" if corpus_commit else "WORKTREE_FILES"

    try:
        if corpus_commit:
            manifest_bytes = _git_show_bytes(repository_root, corpus_commit, str(manifest_rel))
        else:
            manifest_bytes = (repository_root / str(manifest_rel)).read_bytes()
        manifest_bytes = _lf_normalized_bytes(manifest_bytes)
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        expected_blob = str(subject.get("manifest_git_blob_sha1") or "")
        if expected_blob and _git_blob_sha1(manifest_bytes) != expected_blob:
            reasons.append("training_manifest_git_blob_sha1_mismatch")
        expected_digest = str(subject.get("manifest_digest") or "")
        if expected_digest and str(manifest.get("manifest_digest")) != expected_digest:
            reasons.append("training_manifest_digest_mismatch")
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        reasons.append("training_manifest_missing_or_unreadable")

    try:
        if generator_commit:
            generator_bytes = _git_show_bytes(repository_root, generator_commit, str(generator_rel))
        else:
            generator_bytes = (repository_root / str(generator_rel)).read_bytes()
        generator_bytes = _lf_normalized_bytes(generator_bytes)
        expected_generator_blob = str(subject.get("generator_git_blob_sha1") or "")
        if expected_generator_blob and _git_blob_sha1(generator_bytes) != expected_generator_blob:
            reasons.append("training_generator_git_blob_sha1_mismatch")
    except (OSError, subprocess.CalledProcessError):
        reasons.append("training_generator_missing_or_unreadable")

    family_sha256 = dict(subject.get("family_sha256") or {})
    root_rel = str(training_root_rel).replace("\\", "/").rstrip("/")
    for family, expected_sha in sorted(family_sha256.items()):
        try:
            if corpus_commit:
                shard_bytes = _git_show_bytes(
                    repository_root,
                    corpus_commit,
                    f"{root_rel}/{family}.jsonl",
                )
            else:
                shard_bytes = (
                    repository_root / str(training_root_rel) / f"{family}.jsonl"
                ).read_bytes()
            shard_bytes = _lf_normalized_bytes(shard_bytes)
            if _sha256_bytes(shard_bytes) != str(expected_sha):
                reasons.append(f"training_shard_sha256_mismatch:{family}")
        except (OSError, subprocess.CalledProcessError):
            reasons.append(f"training_shard_missing:{family}")

    return {
        "schema": "V10_BEHAVIOR_TRAINING_SUBJECT_AUDIT_V2",
        "status": "PASS" if not reasons else "HOLD",
        "source_mode": source_mode,
        "reasons": sorted(set(reasons)),
        "training_root": str(training_root_rel),
        "manifest_path": str(manifest_rel),
        "generator_path": str(generator_rel),
        "corpus_commit": corpus_commit or None,
        "generator_commit": generator_commit or None,
        "families_checked": sorted(family_sha256),
    }


def validate_candidate_manifest(
    *,
    manifest: dict,
    candidate_sha256: str,
    policy: dict,
) -> list[str]:
    reasons: list[str] = []
    subject = dict(policy.get("training_subject") or {})

    if manifest.get("source_training_corpus_commit") != subject.get("corpus_commit"):
        reasons.append("candidate_manifest_training_commit_mismatch")
    if manifest.get("source_training_manifest_digest") != subject.get("manifest_digest"):
        reasons.append("candidate_manifest_training_manifest_mismatch")
    if manifest.get("candidate_jsonl_sha256") != candidate_sha256:
        reasons.append("candidate_manifest_candidate_sha256_mismatch")

    allowed_methods = set(policy.get("allowed_construction_methods") or [])
    construction_method = manifest.get("construction_method")
    if allowed_methods and construction_method not in allowed_methods:
        reasons.append("candidate_manifest_construction_method_not_allowed")

    if list(manifest.get("training_record_ids_used") or []):
        reasons.append("candidate_manifest_training_record_ids_used")
    if list(manifest.get("training_generator_revisions_used") or []):
        reasons.append("candidate_manifest_training_generator_revisions_used")
    if manifest.get("template_ancestry") in (None, "", "unknown"):
        reasons.append("candidate_manifest_template_ancestry_missing")
    if manifest.get("protected_eval_material_used") is not False:
        reasons.append("candidate_manifest_protected_eval_material_not_false")

    rubric_digest = str(manifest.get("hidden_rubric_packet_sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", rubric_digest):
        reasons.append("candidate_manifest_hidden_rubric_digest_invalid")
    rubric_refs = list(manifest.get("rubric_refs") or [])
    if not rubric_refs:
        reasons.append("candidate_manifest_rubric_refs_missing")

    return sorted(set(reasons))


def assess_case_set(
    *,
    training_rows: list[dict],
    candidate_rows: list[dict],
    policy: dict,
) -> dict:
    allocation = {
        str(family): int(count)
        for family, count in dict(policy["allocation"]).items()
    }
    max_cases_per_scenario_family = int(
        policy["max_cases_per_scenario_family"]
    )
    min_scenario_families = int(
        policy["min_scenario_families_per_behavior"]
    )
    min_domains = int(policy["min_domains_per_behavior"])
    required_levels = [
        str(level) for level in policy["required_cognitive_levels"]
    ]
    allowed_methods = set(policy.get("allowed_construction_methods") or [])
    protected_families = set(policy.get("protected_behavior_families") or [])
    prompt_jaccard_limit = float(
        policy.get("max_training_prompt_token_jaccard", 1.0)
    )
    scenario_jaccard_limit = float(
        policy.get("max_training_scenario_token_jaccard", 1.0)
    )

    if max_cases_per_scenario_family < 1:
        raise ValueError("max_cases_per_scenario_family must be positive")
    if min_scenario_families < 1:
        raise ValueError("min_scenario_families_per_behavior must be positive")
    if min_domains < 1:
        raise ValueError("min_domains_per_behavior must be positive")
    if not required_levels:
        raise ValueError("required_cognitive_levels must be non-empty")

    training_prompts = {
        normalize_text(row.get("prompt"))
        for row in training_rows
        if normalize_text(row.get("prompt"))
    }
    training_scenarios = {
        normalize_text(row.get("scenario_case"))
        for row in training_rows
        if normalize_text(row.get("scenario_case"))
    }
    training_prompt_values = [
        row.get("prompt")
        for row in training_rows
        if normalize_text(row.get("prompt"))
    ]
    training_scenario_values = [
        row.get("scenario_case")
        for row in training_rows
        if normalize_text(row.get("scenario_case"))
    ]
    training_record_ids = {
        str(row.get("record_id"))
        for row in training_rows
        if row.get("record_id") not in (None, "")
    }
    training_generator_revisions = {
        str(row.get("generator_revision"))
        for row in training_rows
        if row.get("generator_revision") not in (None, "")
    }

    reasons: list[str] = []
    seen_case_ids: set[str] = set()
    seen_candidate_prompts: set[str] = set()
    family_counts: Counter[str] = Counter()
    family_scenario_counts: dict[str, Counter[str]] = defaultdict(Counter)
    family_domains: dict[str, set[str]] = defaultdict(set)
    family_levels: dict[str, set[str]] = defaultdict(set)

    for row in candidate_rows:
        case_id = str(row.get("case_id", ""))
        missing = [
            field
            for field in REQUIRED_CANDIDATE_FIELDS
            if row.get(field) in (None, "")
        ]
        # Backward-compatible V1 rows remain mechanically auditable when the
        # V2 provenance/scoring policy is not enabled.
        if not allowed_methods:
            missing = [
                field for field in missing
                if field not in {"source_provenance", "rubric_ref", "criticality"}
            ]
        if missing:
            reasons.append(
                f"missing_fields:{case_id or '<missing-case-id>'}:"
                + ",".join(sorted(missing))
            )
            continue

        family = str(row["family"])
        if family not in allocation:
            reasons.append(f"unknown_family:{case_id}:{family}")
            continue

        if case_id in seen_case_ids:
            reasons.append(f"candidate_case_id_duplicate:{case_id}")
        seen_case_ids.add(case_id)
        if case_id in training_record_ids:
            reasons.append(f"training_record_id_overlap:{case_id}")

        normalized_prompt = normalize_text(row["prompt"])
        if normalized_prompt in training_prompts:
            reasons.append(f"training_prompt_overlap:{case_id}")
        if normalized_prompt in seen_candidate_prompts:
            reasons.append(f"candidate_prompt_duplicate:{case_id}")
        seen_candidate_prompts.add(normalized_prompt)

        normalized_scenario = normalize_text(row["scenario_case"])
        if normalized_scenario in training_scenarios:
            reasons.append(f"training_scenario_overlap:{case_id}")

        if allowed_methods:
            provenance = dict(row.get("source_provenance") or {})
            method = provenance.get("construction_method")
            if method not in allowed_methods:
                reasons.append(f"construction_method_not_allowed:{case_id}")
            used_ids = {
                str(value)
                for value in provenance.get("training_record_ids_used") or []
            }
            if used_ids & training_record_ids:
                reasons.append(f"training_record_id_reuse:{case_id}")
            used_revisions = {
                str(value)
                for value in provenance.get("training_generator_revisions_used") or []
            }
            if used_revisions & training_generator_revisions:
                reasons.append(f"training_generator_revision_reuse:{case_id}")
            if provenance.get("template_ancestry") in (None, "", "unknown"):
                reasons.append(f"template_ancestry_missing:{case_id}")

            prompt_similarity = max(
                (_token_jaccard(row["prompt"], value) for value in training_prompt_values),
                default=0.0,
            )
            if prompt_similarity > prompt_jaccard_limit:
                reasons.append(
                    f"training_prompt_collision:{case_id}:{prompt_similarity:.3f}"
                )
            scenario_similarity = max(
                (_token_jaccard(row["scenario_case"], value) for value in training_scenario_values),
                default=0.0,
            )
            if scenario_similarity > scenario_jaccard_limit:
                reasons.append(
                    f"training_scenario_collision:{case_id}:{scenario_similarity:.3f}"
                )

            if not row.get("rubric_ref"):
                reasons.append(f"rubric_ref_missing:{case_id}")
            criticality = str(row.get("criticality") or "")
            if criticality not in {"standard", "protected_critical"}:
                reasons.append(f"criticality_invalid:{case_id}:{criticality}")
            if family in protected_families and criticality != "protected_critical":
                reasons.append(f"protected_case_not_critical:{case_id}:{family}")

        scenario_family_id = str(row["scenario_family_id"])
        family_counts[family] += 1
        family_scenario_counts[family][scenario_family_id] += 1
        family_domains[family].add(str(row["domain"]))
        family_levels[family].add(str(row["cognitive_level"]))

    for family, expected_count in allocation.items():
        observed_count = family_counts[family]
        if observed_count != expected_count:
            reasons.append(
                f"row_count:{family}:{observed_count}!={expected_count}"
            )

        scenario_counts = family_scenario_counts[family]
        observed_scenario_families = len(scenario_counts)
        if observed_scenario_families < min_scenario_families:
            reasons.append(
                f"scenario_family_count:{family}:"
                f"{observed_scenario_families}<{min_scenario_families}"
            )
        for scenario_family_id, count in sorted(scenario_counts.items()):
            if count > max_cases_per_scenario_family:
                reasons.append(
                    f"scenario_family_size:{family}:{scenario_family_id}:"
                    f"{count}>{max_cases_per_scenario_family}"
                )

        observed_domains = len(family_domains[family])
        if observed_domains < min_domains:
            reasons.append(
                f"domain_count:{family}:{observed_domains}<{min_domains}"
            )

        for level in required_levels:
            if level not in family_levels[family]:
                reasons.append(f"cognitive_level_missing:{family}:{level}")

    total_expected = sum(allocation.values())
    if len(candidate_rows) != total_expected:
        reasons.append(
            f"total_row_count:{len(candidate_rows)}!={total_expected}"
        )

    return {
        "schema": "V10_BEHAVIOR_GENERALIZATION_CASESET_AUDIT_V2",
        "status": "PASS" if not reasons else "HOLD",
        "total_cases": len(candidate_rows),
        "expected_total_cases": total_expected,
        "policy": {
            "allocation": allocation,
            "max_cases_per_scenario_family": max_cases_per_scenario_family,
            "min_scenario_families_per_behavior": min_scenario_families,
            "min_domains_per_behavior": min_domains,
            "required_cognitive_levels": required_levels,
            "allowed_construction_methods": sorted(allowed_methods),
            "protected_behavior_families": sorted(protected_families),
            "max_training_prompt_token_jaccard": prompt_jaccard_limit,
            "max_training_scenario_token_jaccard": scenario_jaccard_limit,
        },
        "families": {
            family: {
                "rows": family_counts[family],
                "scenario_families": len(family_scenario_counts[family]),
                "max_scenario_family_size": max(
                    family_scenario_counts[family].values(),
                    default=0,
                ),
                "domains": len(family_domains[family]),
                "cognitive_levels": sorted(family_levels[family]),
            }
            for family in allocation
        },
        "training_prompt_hashes": len(training_prompts),
        "training_scenario_hashes": len(training_scenarios),
        "training_record_ids": len(training_record_ids),
        "training_generator_revisions": len(training_generator_revisions),
        "reasons": sorted(set(reasons)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-root", type=Path, required=True)
    parser.add_argument("--candidate-jsonl", type=Path, required=True)
    parser.add_argument("--candidate-manifest-json", type=Path, required=True)
    parser.add_argument("--policy-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    policy_document = json.loads(args.policy_json.read_text(encoding="utf-8"))
    policy = normalize_policy_document(policy_document)
    repository_root = Path(__file__).resolve().parents[2]
    bound_training_root = (
        repository_root / str(policy["training_subject"]["training_root"])
    ).resolve()
    reasons: list[str] = []
    if args.training_root.resolve() != bound_training_root:
        reasons.append("training_root_not_bound_subject")

    subject_audit = audit_training_subject(
        repository_root=repository_root,
        policy=policy,
    )
    reasons.extend(subject_audit["reasons"])

    families = list(policy["allocation"])
    training_rows = load_bound_training_shards(
        repository_root=repository_root,
        subject=policy["training_subject"],
        families=families,
    )
    candidate_rows = load_jsonl(args.candidate_jsonl)
    candidate_bytes = args.candidate_jsonl.read_bytes()
    manifest = json.loads(args.candidate_manifest_json.read_text(encoding="utf-8"))
    reasons.extend(
        validate_candidate_manifest(
            manifest=manifest,
            candidate_sha256=_sha256_bytes(candidate_bytes),
            policy=policy,
        )
    )
    result = assess_case_set(
        training_rows=training_rows,
        candidate_rows=candidate_rows,
        policy=policy,
    )
    reasons.extend(result["reasons"])
    result["training_subject_audit"] = subject_audit
    result["candidate_manifest_reasons"] = validate_candidate_manifest(
        manifest=manifest,
        candidate_sha256=_sha256_bytes(candidate_bytes),
        policy=policy,
    )
    result["reasons"] = sorted(set(reasons))
    result["status"] = "PASS" if not result["reasons"] else "HOLD"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
