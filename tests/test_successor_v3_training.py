import hashlib
import json
from pathlib import Path

import pytest

import successor.v3_training as v3
from successor.v3_training import preflight_v3_training, validate_v3_training_config


HEAD = "c" * 40
TASK9 = "a" * 40
SHA_PARENT = "1" * 64
SHA_SUBJECT = "2" * 64


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def base_manifest():
    return {
        "repo_id": "HuggingFaceTB/SmolLM3-3B",
        "revision": "a07cc9a04f16550a088caea529712d1d335b0ac1",
        "mutable_revision_allowed": False,
    }


def make_subject(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "successor").mkdir(parents=True)
    write_json(repo / "successor" / "base_model_manifest.json", base_manifest())

    private = tmp_path / "private"
    parent = private / "parent"
    parent.mkdir(parents=True)
    (parent / "adapter_model.safetensors").write_bytes(b"parent")

    train = private / "train.jsonl"
    validation = private / "validation.jsonl"
    train.write_text('{"prompt":"t","response":"a"}\n', encoding="utf-8")
    validation.write_text('{"prompt":"v","response":"b"}\n', encoding="utf-8")

    corpus = private / "corpus_manifest.json"
    corpus_payload = {
        "readiness_source_commit": TASK9,
        "train_file_sha256": file_sha(train),
        "validation_file_sha256": file_sha(validation),
        "general_fraction": 0.5,
        "train_validation_overlap": 0,
        "blind_plaintext_included": False,
        "weight_change_performed": False,
    }
    write_json(corpus, corpus_payload)

    ready = private / "training_ready_receipt.json"
    write_json(ready, {
        "schema": v3.TASK9_READY_SCHEMA,
        "ready": True,
        "status": "READY",
        "readiness_source_commit": TASK9,
        "subject_digest": "3" * 64,
        "evidence_digest": "4" * 64,
        "external_verification_digest": "5" * 64,
    })

    spec = {
        "schema": v3.V3_TRAINING_SCHEMA,
        "run_id": "VERA_SUCCESSOR_V3_DEV_TEST",
        "task9_source_commit": TASK9,
        "task9_ready_receipt_path": str(ready),
        "training_authorization_receipt_path": str(private / "training_authorization_receipt.json"),
        "base_repo_id": base_manifest()["repo_id"],
        "base_revision": base_manifest()["revision"],
        "parent_adapter_path": str(parent),
        "parent_adapter_sha256": file_sha(parent / "adapter_model.safetensors"),
        "parent_candidate_subject_digest": SHA_SUBJECT,
        "parent_selection_basis": "development parent only",
        "train_path": str(train),
        "train_sha256": file_sha(train),
        "validation_path": str(validation),
        "validation_sha256": file_sha(validation),
        "corpus_manifest_path": str(corpus),
        "corpus_manifest_sha256": file_sha(corpus),
        "output_dir": str(private / "output"),
        "seed": 20260919,
        "learning_rate": 5e-6,
        "gradient_accumulation": 8,
        "assistant_only_loss": True,
        "neutral_system_override": True,
        "general_rehearsal_fraction": 0.5,
    }
    spec_path = repo / "successor" / "v3_training_config.json"
    write_json(spec_path, spec)
    return repo, private, spec_path, spec


def fake_git(monkeypatch):
    monkeypatch.setattr(v3, "_git_head", lambda repo: HEAD)
    monkeypatch.setattr(v3, "_is_ancestor", lambda repo, ancestor, descendant: True)


def authorize(private: Path, spec: dict):
    ready_path = Path(spec["task9_ready_receipt_path"])
    ready_sha = file_sha(ready_path)
    write_json(private / "training_authorization_receipt.json", {
        "schema": v3.TRAINING_AUTH_SCHEMA,
        "authorized": True,
        "effect": "WEIGHT_CHANGING_TRAINING",
        "task9_ready_receipt_sha256": ready_sha,
        "task9_source_commit": spec["task9_source_commit"],
        "run_id": spec["run_id"],
        "parent_adapter_sha256": spec["parent_adapter_sha256"],
        "train_sha256": spec["train_sha256"],
        "validation_sha256": spec["validation_sha256"],
    })


def test_validate_v3_config_enforces_initial_general_rehearsal():
    spec = {
        "schema": v3.V3_TRAINING_SCHEMA,
        "run_id": "VERA_SUCCESSOR_V3_DEV_X",
        "task9_source_commit": TASK9,
        "task9_ready_receipt_path": "ready.json",
        "training_authorization_receipt_path": "auth.json",
        "base_repo_id": base_manifest()["repo_id"],
        "base_revision": base_manifest()["revision"],
        "parent_adapter_path": "parent",
        "parent_adapter_sha256": "1" * 64,
        "parent_candidate_subject_digest": "2" * 64,
        "parent_selection_basis": "development parent",
        "train_path": "train.jsonl",
        "train_sha256": "3" * 64,
        "validation_path": "validation.jsonl",
        "validation_sha256": "4" * 64,
        "corpus_manifest_path": "corpus.json",
        "corpus_manifest_sha256": "5" * 64,
        "output_dir": "output",
        "seed": 1,
        "learning_rate": 1e-5,
        "gradient_accumulation": 8,
        "assistant_only_loss": True,
        "neutral_system_override": True,
        "general_rehearsal_fraction": 0.49,
    }
    with pytest.raises(ValueError, match="general_rehearsal_fraction"):
        validate_v3_training_config(spec, base_manifest())


def test_static_subject_holds_only_for_missing_training_authority(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    fake_git(monkeypatch)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert decision.runnable is False
    assert decision.status == "HOLD"
    assert decision.reasons == ("training_authorization_receipt_missing",)
    assert decision.parent_adapter_sha256 == spec["parent_adapter_sha256"]
    assert decision.train_sha256 == spec["train_sha256"]
    assert decision.validation_sha256 == spec["validation_sha256"]


def test_missing_task9_and_training_authority_are_hold_not_runnable(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    Path(spec["task9_ready_receipt_path"]).unlink()
    fake_git(monkeypatch)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert decision.status == "HOLD"
    assert decision.reasons == (
        "task9_ready_receipt_missing",
        "training_authorization_receipt_missing",
    )


def test_ready_plus_exact_authorization_is_runnable(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    authorize(private, spec)
    fake_git(monkeypatch)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert decision.runnable is True
    assert decision.status == "RUNNABLE"
    assert decision.reasons == ()
    assert len(decision.task9_ready_receipt_sha256) == 64
    assert len(decision.training_authorization_receipt_sha256) == 64


def test_tampered_parent_or_dataset_blocks(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    authorize(private, spec)
    (Path(spec["parent_adapter_path"]) / "adapter_model.safetensors").write_bytes(b"tamper")
    Path(spec["train_path"]).write_text('{"prompt":"tamper","response":"x"}\n', encoding="utf-8")
    fake_git(monkeypatch)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert decision.status == "BLOCKED"
    assert "parent_adapter_sha256_mismatch" in decision.reasons
    assert "train_sha256_mismatch" in decision.reasons
    assert "corpus_train_file_binding_mismatch" in decision.reasons


def test_corpus_cannot_smuggle_blind_plaintext_or_overlap(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    authorize(private, spec)
    corpus_path = Path(spec["corpus_manifest_path"])
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    corpus["train_validation_overlap"] = 1
    corpus["blind_plaintext_included"] = True
    write_json(corpus_path, corpus)
    spec["corpus_manifest_sha256"] = file_sha(corpus_path)
    write_json(spec_path, spec)
    fake_git(monkeypatch)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert "corpus_train_validation_overlap_nonzero" in decision.reasons
    assert "blind_plaintext_included_in_training_corpus" in decision.reasons


def test_stale_task9_source_blocks_even_with_receipts(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    authorize(private, spec)
    monkeypatch.setattr(v3, "_git_head", lambda repo: HEAD)
    monkeypatch.setattr(v3, "_is_ancestor", lambda repo, ancestor, descendant: False)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert "task9_source_not_ancestor_of_training_code" in decision.reasons


def test_authorization_is_bound_to_exact_run_material(tmp_path, monkeypatch):
    repo, private, spec_path, spec = make_subject(tmp_path)
    authorize(private, spec)
    auth_path = Path(spec["training_authorization_receipt_path"])
    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    auth["parent_adapter_sha256"] = "f" * 64
    write_json(auth_path, auth)
    fake_git(monkeypatch)
    decision = preflight_v3_training(spec_path, repo_root=repo)
    assert "training_authorization_parent_mismatch" in decision.reasons


def test_committed_task10_config_is_structurally_valid():
    repo = Path(__file__).resolve().parents[1]
    spec = json.loads(
        (repo / "successor" / "v3_training_config.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (repo / "successor" / "base_model_manifest.json").read_text(encoding="utf-8")
    )
    validate_v3_training_config(spec, manifest)
    assert spec["general_rehearsal_fraction"] >= 0.50
    assert spec["assistant_only_loss"] is True
    assert spec["parent_adapter_sha256"] == "94c6af3b16fd8e21305aa69e095e480721d1e31b33a2a40e1e504d59c73cfa7a"


def test_v3_dry_run_returns_preflight_without_legacy_prepare(tmp_path, monkeypatch):
    import successor.train_pilot_sft as runner

    spec_path = tmp_path / "spec.json"
    write_json(spec_path, {"schema": v3.V3_TRAINING_SCHEMA, "run_id": "VERA_SUCCESSOR_V3_DEV_X"})
    decision = v3.V3TrainingPreflight(
        runnable=False,
        status="HOLD",
        code_commit=HEAD,
        parent_adapter_sha256=None,
        train_sha256=None,
        validation_sha256=None,
        corpus_manifest_sha256=None,
        task9_ready_receipt_sha256=None,
        training_authorization_receipt_sha256=None,
        reasons=("task9_ready_receipt_missing",),
    )
    monkeypatch.setattr(runner, "preflight_v3_training", lambda *args, **kwargs: decision)
    monkeypatch.setattr(
        runner,
        "prepare",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("legacy prepare called")),
    )
    result = runner.dry_run(spec_path)
    assert result["run_id"] == "VERA_SUCCESSOR_V3_DEV_X"
    assert result["runnable"] is False
    assert result["status"] == "HOLD"
    assert result["reasons"] == ["task9_ready_receipt_missing"]


def test_v3_prepare_blocks_before_private_file_loading(tmp_path, monkeypatch):
    import successor.train_pilot_sft as runner

    spec_path = tmp_path / "spec.json"
    write_json(spec_path, {"schema": v3.V3_TRAINING_SCHEMA})
    decision = v3.V3TrainingPreflight(
        runnable=False,
        status="HOLD",
        code_commit=HEAD,
        parent_adapter_sha256=None,
        train_sha256=None,
        validation_sha256=None,
        corpus_manifest_sha256=None,
        task9_ready_receipt_sha256=None,
        training_authorization_receipt_sha256=None,
        reasons=("training_authorization_receipt_missing",),
    )
    monkeypatch.setattr(runner, "preflight_v3_training", lambda *args, **kwargs: decision)
    with pytest.raises(RuntimeError, match="V3 training preflight blocked"):
        runner.prepare(spec_path)
