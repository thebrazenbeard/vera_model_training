from __future__ import annotations

from successor.experiments.build_v10_behavior_qualification import (
    assess_case_set,
)


def _train_rows() -> list[dict]:
    return [
        {
            "record_id": "train-a-1",
            "family": "family_a",
            "scenario_case": "old scenario alpha",
            "domain": "software",
            "cognitive_level": "identify",
            "prompt": "Use the evidence from scenario alpha.",
        },
        {
            "record_id": "train-b-1",
            "family": "family_b",
            "scenario_case": "old scenario beta",
            "domain": "research",
            "cognitive_level": "apply",
            "prompt": "Apply the rule in scenario beta.",
        },
    ]


def _policy() -> dict:
    return {
        "allocation": {"family_a": 2, "family_b": 2},
        "max_cases_per_scenario_family": 1,
        "min_scenario_families_per_behavior": 2,
        "min_domains_per_behavior": 2,
        "required_cognitive_levels": ["identify", "apply"],
    }


def _clean_candidates() -> list[dict]:
    return [
        {
            "case_id": "eval-a-1",
            "family": "family_a",
            "scenario_family_id": "a-new-1",
            "scenario_case": "novel scenario one",
            "domain": "finance",
            "cognitive_level": "identify",
            "prompt": "Identify what the new evidence establishes in case one.",
            "expected_behavior": "state the evidence boundary",
        },
        {
            "case_id": "eval-a-2",
            "family": "family_a",
            "scenario_family_id": "a-new-2",
            "scenario_case": "novel scenario two",
            "domain": "history",
            "cognitive_level": "apply",
            "prompt": "Apply the behavior to a new historical conflict.",
            "expected_behavior": "apply the evidence boundary",
        },
        {
            "case_id": "eval-b-1",
            "family": "family_b",
            "scenario_family_id": "b-new-1",
            "scenario_case": "novel scenario three",
            "domain": "operations",
            "cognitive_level": "identify",
            "prompt": "Identify the correct action in a new operations case.",
            "expected_behavior": "state the bounded action",
        },
        {
            "case_id": "eval-b-2",
            "family": "family_b",
            "scenario_family_id": "b-new-2",
            "scenario_case": "novel scenario four",
            "domain": "writing",
            "cognitive_level": "apply",
            "prompt": "Apply the behavior to a new writing case.",
            "expected_behavior": "apply the bounded action",
        },
    ]


def test_clean_heldout_case_set_passes() -> None:
    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=_clean_candidates(),
        policy=_policy(),
    )

    assert result["status"] == "PASS"
    assert result["reasons"] == []
    assert result["total_cases"] == 4


def test_training_scenario_overlap_holds_even_with_new_prompt_and_id() -> None:
    candidates = _clean_candidates()
    candidates[0] = {
        **candidates[0],
        "case_id": "different-id",
        "scenario_case": "old scenario alpha",
        "prompt": "A completely different prompt surface.",
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "training_scenario_overlap:different-id" in result["reasons"]


def test_normalized_training_prompt_overlap_holds() -> None:
    candidates = _clean_candidates()
    candidates[0] = {
        **candidates[0],
        "prompt": "  USE   the evidence from SCENARIO alpha. ",
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "training_prompt_overlap:eval-a-1" in result["reasons"]


def test_pseudoreplicated_scenario_family_holds() -> None:
    candidates = _clean_candidates()
    candidates[1] = {
        **candidates[1],
        "scenario_family_id": "a-new-1",
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "scenario_family_size:family_a:a-new-1:2>1" in result["reasons"]
    assert "scenario_family_count:family_a:1<2" in result["reasons"]


def test_insufficient_domain_and_cognitive_coverage_holds() -> None:
    candidates = _clean_candidates()
    candidates[1] = {
        **candidates[1],
        "domain": candidates[0]["domain"],
        "cognitive_level": candidates[0]["cognitive_level"],
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "domain_count:family_a:1<2" in result["reasons"]
    assert "cognitive_level_missing:family_a:apply" in result["reasons"]


def test_candidate_duplicate_prompt_holds() -> None:
    candidates = _clean_candidates()
    candidates[1] = {
        **candidates[1],
        "prompt": candidates[0]["prompt"],
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "candidate_prompt_duplicate:eval-a-2" in result["reasons"]


import hashlib
import successor.experiments.build_v10_behavior_qualification as qualification


def _v2_policy() -> dict:
    policy = _policy()
    policy.update({
        "allowed_construction_methods": ["independent_manual"],
        "protected_behavior_families": ["family_a"],
        "max_training_prompt_token_jaccard": 0.75,
        "max_training_scenario_token_jaccard": 0.75,
    })
    return policy


def _v2_training_rows() -> list[dict]:
    rows = _train_rows()
    for row in rows:
        row["provenance"] = "BV_V4_1_DIVERSE_CORE_20260930_V10"
        row["generator_revision"] = "V4_1_COMPOSITIONAL_DIVERSITY_V10"
    return rows


def _v2_candidates() -> list[dict]:
    rows = _clean_candidates()
    for row in rows:
        row["source_provenance"] = {
            "construction_method": "independent_manual",
            "training_record_ids_used": [],
            "training_generator_revisions_used": [],
            "template_ancestry": "independent_non_v4_1",
        }
        row["rubric_ref"] = f"rubric-{row['case_id']}"
        row["criticality"] = (
            "protected_critical" if row["family"] == "family_a" else "standard"
        )
    return rows


def test_training_record_id_overlap_holds() -> None:
    candidates = _v2_candidates()
    candidates[0] = {**candidates[0], "case_id": "train-a-1"}
    result = assess_case_set(
        training_rows=_v2_training_rows(),
        candidate_rows=candidates,
        policy=_v2_policy(),
    )
    assert result["status"] == "HOLD"
    assert "training_record_id_overlap:train-a-1" in result["reasons"]


def test_training_generator_revision_reuse_holds() -> None:
    candidates = _v2_candidates()
    candidates[0]["source_provenance"]["training_generator_revisions_used"] = [
        "V4_1_COMPOSITIONAL_DIVERSITY_V10"
    ]
    result = assess_case_set(
        training_rows=_v2_training_rows(),
        candidate_rows=candidates,
        policy=_v2_policy(),
    )
    assert result["status"] == "HOLD"
    assert "training_generator_revision_reuse:eval-a-1" in result["reasons"]


def test_prompt_collision_screen_holds_without_exact_match() -> None:
    candidates = _v2_candidates()
    candidates[1]["prompt"] = (
        "Use the evidence from scenario alpha now."
    )
    result = assess_case_set(
        training_rows=_v2_training_rows(),
        candidate_rows=candidates,
        policy=_v2_policy(),
    )
    assert result["status"] == "HOLD"
    assert any(
        reason.startswith("training_prompt_collision:eval-a-2:")
        for reason in result["reasons"]
    )


def test_protected_family_requires_critical_case_marking() -> None:
    candidates = _v2_candidates()
    candidates[0]["criticality"] = "standard"
    result = assess_case_set(
        training_rows=_v2_training_rows(),
        candidate_rows=candidates,
        policy=_v2_policy(),
    )
    assert result["status"] == "HOLD"
    assert "protected_case_not_critical:eval-a-1:family_a" in result["reasons"]


def test_candidate_manifest_binds_frozen_subject_and_hidden_rubric() -> None:
    validator = getattr(qualification, "validate_candidate_manifest", None)
    assert callable(validator)
    candidate_sha = hashlib.sha256(b'{"case_id":"eval-a-1"}\n').hexdigest()
    policy = {
        "training_subject": {
            "corpus_commit": "corpus-commit",
            "manifest_digest": "manifest-digest",
        },
        "allowed_construction_methods": ["independent_manual"],
    }
    manifest = {
        "source_training_corpus_commit": "wrong-commit",
        "source_training_manifest_digest": "manifest-digest",
        "candidate_jsonl_sha256": candidate_sha,
        "construction_method": "independent_manual",
        "training_record_ids_used": [],
        "training_generator_revisions_used": [],
        "template_ancestry": "independent_non_v4_1",
        "protected_eval_material_used": False,
        "hidden_rubric_packet_sha256": "a" * 64,
        "rubric_refs": ["rubric-a-1"],
    }
    reasons = validator(
        manifest=manifest,
        candidate_sha256=candidate_sha,
        policy=policy,
    )
    assert "candidate_manifest_training_commit_mismatch" in reasons


def test_training_subject_audit_detects_shard_tamper(tmp_path) -> None:
    auditor = getattr(qualification, "audit_training_subject", None)
    assert callable(auditor)
    corpus_root = tmp_path / "successor" / "corpus" / "v4_1" / "custom"
    corpus_root.mkdir(parents=True)
    shard = corpus_root / "family_a.jsonl"
    shard.write_text('{"record_id":"x"}\n', encoding="utf-8")
    manifest = {
        "manifest_digest": "bound-manifest",
        "families": {
            "family_a": {
                "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
            }
        },
    }
    manifest_path = corpus_root / "manifest.json"
    manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
    generator = tmp_path / "successor" / "build_v4_1_diverse_corpus.py"
    generator.parent.mkdir(parents=True, exist_ok=True)
    generator.write_text("print('bound')\n", encoding="utf-8")

    def git_blob_sha1(path):
        payload = path.read_bytes().replace(b"\r\n", b"\n")
        return hashlib.sha1(
            f"blob {len(payload)}\0".encode("ascii") + payload
        ).hexdigest()

    policy = {
        "allocation": {"family_a": 1},
        "training_subject": {
            "training_root": "successor/corpus/v4_1/custom",
            "manifest_path": "successor/corpus/v4_1/custom/manifest.json",
            "manifest_digest": "bound-manifest",
            "manifest_git_blob_sha1": git_blob_sha1(manifest_path),
            "generator_path": "successor/build_v4_1_diverse_corpus.py",
            "generator_git_blob_sha1": git_blob_sha1(generator),
            "family_sha256": {
                "family_a": hashlib.sha256(
                    shard.read_bytes().replace(b"\r\n", b"\n")
                ).hexdigest()
            },
        },
    }
    assert auditor(repository_root=tmp_path, policy=policy)["status"] == "PASS"
    shard.write_text('{"record_id":"tampered"}\n', encoding="utf-8")
    result = auditor(repository_root=tmp_path, policy=policy)
    assert result["status"] == "HOLD"
    assert "training_shard_sha256_mismatch:family_a" in result["reasons"]


def test_full_protocol_document_normalizes_case_policy_and_training_subject() -> None:
    normalizer = getattr(qualification, "normalize_policy_document", None)
    assert callable(normalizer)
    document = {
        "case_set_policy": _v2_policy(),
        "training_subject": {"corpus_commit": "bound-head"},
    }
    policy = normalizer(document)
    assert policy["allocation"] == _v2_policy()["allocation"]
    assert policy["training_subject"]["corpus_commit"] == "bound-head"


def test_training_subject_audit_uses_frozen_commit_not_mutable_worktree(tmp_path) -> None:
    import json
    import subprocess

    auditor = getattr(qualification, "audit_training_subject", None)
    assert callable(auditor)

    corpus_root = tmp_path / "successor" / "corpus" / "v4_1" / "custom"
    corpus_root.mkdir(parents=True)
    shard = corpus_root / "family_a.jsonl"
    shard.write_text('{"record_id":"frozen"}\n', encoding="utf-8", newline="\n")
    manifest = {
        "manifest_digest": "bound-manifest",
        "families": {
            "family_a": {
                "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
            }
        },
    }
    manifest_path = corpus_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
    generator = tmp_path / "successor" / "build_v4_1_diverse_corpus.py"
    generator.parent.mkdir(parents=True, exist_ok=True)
    generator.write_text("print('frozen')\n", encoding="utf-8", newline="\n")

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "freeze"], check=True)
    frozen = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True).strip()

    def git_blob_sha1(path):
        payload = path.read_bytes()
        return hashlib.sha1(
            f"blob {len(payload)}\0".encode("ascii") + payload
        ).hexdigest()

    policy = {
        "training_subject": {
            "corpus_commit": frozen,
            "generator_commit": frozen,
            "training_root": "successor/corpus/v4_1/custom",
            "manifest_path": "successor/corpus/v4_1/custom/manifest.json",
            "manifest_digest": "bound-manifest",
            "manifest_git_blob_sha1": git_blob_sha1(manifest_path),
            "generator_path": "successor/build_v4_1_diverse_corpus.py",
            "generator_git_blob_sha1": git_blob_sha1(generator),
            "family_sha256": {
                "family_a": hashlib.sha256(shard.read_bytes()).hexdigest()
            },
        },
    }

    shard.write_text('{"record_id":"mutable-drift"}\n', encoding="utf-8", newline="\n")
    manifest_path.write_text('{"manifest_digest":"drift"}\n', encoding="utf-8", newline="\n")
    generator.write_text("print('drift')\n", encoding="utf-8", newline="\n")

    result = auditor(repository_root=tmp_path, policy=policy)
    assert result["status"] == "PASS"
    assert result["source_mode"] == "FROZEN_GIT_OBJECTS"


def test_training_subject_audit_normalizes_windows_checkout_line_endings(tmp_path) -> None:
    auditor = getattr(qualification, "audit_training_subject", None)
    assert callable(auditor)

    corpus_root = tmp_path / "successor" / "corpus" / "v4_1" / "custom"
    corpus_root.mkdir(parents=True)
    shard = corpus_root / "family_a.jsonl"
    shard_lf = b'{"record_id":"x"}\n'
    shard.write_bytes(shard_lf.replace(b"\n", b"\r\n"))

    manifest = {
        "manifest_digest": "bound-manifest",
        "families": {
            "family_a": {
                "sha256": hashlib.sha256(shard_lf).hexdigest(),
            }
        },
    }
    manifest_lf = (
        __import__("json").dumps(manifest, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    manifest_path = corpus_root / "manifest.json"
    manifest_path.write_bytes(manifest_lf.replace(b"\n", b"\r\n"))

    generator = tmp_path / "successor" / "build_v4_1_diverse_corpus.py"
    generator.parent.mkdir(parents=True, exist_ok=True)
    generator_lf = b"print('bound')\n"
    generator.write_bytes(generator_lf.replace(b"\n", b"\r\n"))

    def git_blob_sha1(payload: bytes) -> str:
        return hashlib.sha1(
            f"blob {len(payload)}\0".encode("ascii") + payload
        ).hexdigest()

    policy = {
        "allocation": {"family_a": 1},
        "training_subject": {
            "training_root": "successor/corpus/v4_1/custom",
            "manifest_path": "successor/corpus/v4_1/custom/manifest.json",
            "manifest_digest": "bound-manifest",
            "manifest_git_blob_sha1": git_blob_sha1(manifest_lf),
            "generator_path": "successor/build_v4_1_diverse_corpus.py",
            "generator_git_blob_sha1": git_blob_sha1(generator_lf),
            "family_sha256": {
                "family_a": hashlib.sha256(shard_lf).hexdigest(),
            },
        },
    }

    assert auditor(repository_root=tmp_path, policy=policy)["status"] == "PASS"
