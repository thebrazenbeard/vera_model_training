from __future__ import annotations

import copy
import re
from typing import Any, Mapping


_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_ADMISSION = {"HELD", "VERAOS_ROUTE_ELIGIBLE"}
_ALLOWED_QUALIFICATION = {"PASS", "HOLD", "FAIL"}


def _require_mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _require_text(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _require_git_sha(value: object, name: str) -> str:
    text = _require_text(value, name)
    if not _GIT_SHA_RE.fullmatch(text):
        raise ValueError(f"{name} must be an exact lowercase 40-character Git SHA")
    return text


def _require_sha256(value: object, name: str) -> str:
    text = _require_text(value, name)
    if not _SHA256_RE.fullmatch(text):
        raise ValueError(f"{name} must be an exact lowercase 64-character sha256")
    return text


def _artifact_rows(training_receipt: Mapping[str, Any]) -> list[dict[str, str]]:
    artifacts = _require_mapping(
        training_receipt.get("adapter_artifacts"),
        "training_receipt.adapter_artifacts",
    )
    files = _require_mapping(
        artifacts.get("files"),
        "training_receipt.adapter_artifacts.files",
    )
    rows: list[dict[str, str]] = []
    for path, digest in sorted(files.items()):
        name = _require_text(path, "artifact path")
        rows.append(
            {
                "path": name,
                "sha256": _require_sha256(digest, f"artifact {name} sha256"),
            }
        )
    if not rows:
        raise ValueError("at least one exact model artifact is required")
    return rows


def build_candidate_from_training_receipt(
    *,
    model_package: Mapping[str, Any],
    training_receipt: Mapping[str, Any],
    qualification: Mapping[str, Any],
) -> dict[str, object]:
    package = copy.deepcopy(dict(model_package))
    receipt = copy.deepcopy(dict(training_receipt))
    qual = copy.deepcopy(dict(qualification))

    producer_commit = _require_git_sha(
        package.get("source_commit"),
        "model_package.source_commit",
    )
    base = _require_mapping(package.get("base"), "model_package.base")
    base_revision = _require_git_sha(
        base.get("revision"),
        "model_package.base.revision",
    )
    qual_status = _require_text(
        qual.get("status"),
        "qualification.status",
    ).upper()
    if qual_status not in _ALLOWED_QUALIFICATION:
        raise ValueError("qualification.status must be PASS, HOLD, or FAIL")

    capabilities = [
        _require_text(value, "qualification capability")
        for value in qual.get("capabilities", [])
    ]
    admission_status = (
        "VERAOS_ROUTE_ELIGIBLE"
        if qual_status == "PASS"
        else "HELD"
    )

    candidate = {
        "schema": "VERA_OS_LOCAL_MODEL_PROVIDER_CANDIDATE_V1",
        "artifact_id": _require_text(
            package.get("package_id"),
            "model_package.package_id",
        ),
        "producer": {
            "repository": "thebrazenbeard/vera_model_training",
            "source_branch": _require_text(
                package.get("source_branch"),
                "model_package.source_branch",
            ),
            "source_commit": producer_commit,
        },
        "base": {
            "repository": _require_text(
                base.get("repository"),
                "model_package.base.repository",
            ),
            "revision": base_revision,
            "format": _require_text(
                base.get("format"),
                "model_package.base.format",
            ),
        },
        "artifacts": _artifact_rows(receipt),
        "training": {
            "artifact_manifest_sha256": _require_sha256(
                _require_mapping(
                    receipt.get("adapter_artifacts"),
                    "training_receipt.adapter_artifacts",
                ).get("manifest_sha256"),
                "training_receipt.adapter_artifacts.manifest_sha256",
            ),
            "receipt_schema": _require_text(
                receipt.get("schema"),
                "training_receipt.schema",
            ),
            "receipt_status": _require_text(
                receipt.get("status"),
                "training_receipt.status",
            ),
            "training_corpus_id": _require_text(
                receipt.get("training_corpus_id"),
                "training_receipt.training_corpus_id",
            ),
            "train_sha256": _require_sha256(
                receipt.get("train_sha256"),
                "training_receipt.train_sha256",
            ),
            "receipt_sha256": _require_sha256(
                receipt.get("receipt_sha256"),
                "training_receipt.receipt_sha256",
            ),
            "runtime_binding_sha256": _require_sha256(
                receipt.get("runtime_binding_sha256"),
                "training_receipt.runtime_binding_sha256",
            ),
            "paid_compute": bool(receipt.get("paid_compute", False)),
            "deployment_status": _require_text(
                receipt.get("deployment_status"),
                "training_receipt.deployment_status",
            ),
            "source_qualification_status": _require_text(
                receipt.get("qualification_status"),
                "training_receipt.qualification_status",
            ),
        },
        "qualification": {
            "status": qual_status,
            "issuer_repository": _require_text(
                qual.get("issuer_repository"),
                "qualification.issuer_repository",
            ),
            "artifact_manifest_sha256": _require_sha256(
                qual.get("artifact_manifest_sha256"),
                "qualification.artifact_manifest_sha256",
            ),
            "suite_sha256": _require_sha256(
                qual.get("suite_sha256"),
                "qualification.suite_sha256",
            ),
            "runtime_binding_sha256": _require_sha256(
                qual.get("runtime_binding_sha256"),
                "qualification.runtime_binding_sha256",
            ),
            "capabilities": capabilities,
        },
        "authority": {
            "identity_authority": False,
            "canonical_memory_write_authority": False,
            "protected_effect_authority": False,
            "browser_authority": False,
        },
        "admission": {
            "status": admission_status,
            "route_class": "COGNITION_ONLY",
            "selector_owner": "thebrazenbeard/portal",
            "identity_runtime_owner": "thebrazenbeard/vera-mono",
            "integration": "OPTIONAL_PROVIDER",
        },
        "claim_ceiling": (
            "QUALIFIED_OPTIONAL_LOCAL_MODEL_PROVIDER_CANDIDATE_ONLY_"
            "NOT_VERA_IDENTITY_NOT_CANONICAL_MEMORY_AUTHORITY_"
            "NOT_PROTECTED_EFFECT_AUTHORITY"
        ),
    }
    validate_candidate(candidate)
    return candidate


def validate_candidate(candidate: Mapping[str, Any]) -> None:
    data = _require_mapping(candidate, "candidate")
    if data.get("schema") != "VERA_OS_LOCAL_MODEL_PROVIDER_CANDIDATE_V1":
        raise ValueError("local-model provider candidate schema is unsupported")

    _require_text(data.get("artifact_id"), "artifact_id")

    producer = _require_mapping(data.get("producer"), "producer")
    if producer.get("repository") != "thebrazenbeard/vera_model_training":
        raise ValueError("producer repository is not Vera Model Training")
    _require_text(producer.get("source_branch"), "producer.source_branch")
    _require_git_sha(producer.get("source_commit"), "producer.source_commit")

    base = _require_mapping(data.get("base"), "base")
    _require_text(base.get("repository"), "base.repository")
    _require_git_sha(base.get("revision"), "base.revision")
    _require_text(base.get("format"), "base.format")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("artifacts must contain at least one exact artifact")
    for index, artifact in enumerate(artifacts):
        row = _require_mapping(artifact, f"artifacts[{index}]")
        _require_text(row.get("path"), f"artifacts[{index}].path")
        _require_sha256(row.get("sha256"), f"artifacts[{index}].sha256")

    training = _require_mapping(data.get("training"), "training")
    training_artifact_manifest_sha256 = _require_sha256(
        training.get("artifact_manifest_sha256"),
        "training.artifact_manifest_sha256",
    )
    _require_text(training.get("training_corpus_id"), "training.training_corpus_id")
    _require_sha256(training.get("train_sha256"), "training.train_sha256")
    _require_sha256(training.get("receipt_sha256"), "training.receipt_sha256")
    _require_sha256(
        training.get("runtime_binding_sha256"),
        "training.runtime_binding_sha256",
    )

    qualification = _require_mapping(data.get("qualification"), "qualification")
    status = _require_text(
        qualification.get("status"),
        "qualification.status",
    ).upper()
    if status not in _ALLOWED_QUALIFICATION:
        raise ValueError("qualification.status must be PASS, HOLD, or FAIL")
    issuer_repository = _require_text(
        qualification.get("issuer_repository"),
        "qualification.issuer_repository",
    )
    if issuer_repository == producer.get("repository"):
        raise ValueError(
            "qualification issuer must be separate from the producer"
        )
    qualified_artifact_manifest_sha256 = _require_sha256(
        qualification.get("artifact_manifest_sha256"),
        "qualification.artifact_manifest_sha256",
    )
    if qualified_artifact_manifest_sha256 != training_artifact_manifest_sha256:
        raise ValueError(
            "qualification artifact manifest does not match training artifact manifest"
        )
    _require_sha256(
        qualification.get("suite_sha256"),
        "qualification.suite_sha256",
    )
    _require_sha256(
        qualification.get("runtime_binding_sha256"),
        "qualification.runtime_binding_sha256",
    )

    authority = _require_mapping(data.get("authority"), "authority")
    if authority.get("identity_authority") is not False:
        raise ValueError("cognition engine cannot hold identity authority")
    if authority.get("canonical_memory_write_authority") is not False:
        raise ValueError("cognition engine cannot hold canonical memory write authority")
    if authority.get("protected_effect_authority") is not False:
        raise ValueError("local model provider cannot hold protected effect authority")
    if authority.get("browser_authority") is not False:
        raise ValueError("local model provider cannot hold browser authority")

    admission = _require_mapping(data.get("admission"), "admission")
    admission_status = _require_text(
        admission.get("status"),
        "admission.status",
    )
    if admission_status not in _ALLOWED_ADMISSION:
        raise ValueError("admission.status is unsupported")
    if admission.get("route_class") != "COGNITION_ONLY":
        raise ValueError("VeraOS local-model provider route must be COGNITION_ONLY")
    if admission.get("selector_owner") != "thebrazenbeard/portal":
        raise ValueError("P.O.R.T.A.L. must own model route selection")
    if admission.get("identity_runtime_owner") != "thebrazenbeard/vera-mono":
        raise ValueError("Vera Mono must own identity/runtime")
    if admission.get("integration") != "OPTIONAL_PROVIDER":
        raise ValueError("trained Vera model must remain an optional provider")

    expected = "VERAOS_ROUTE_ELIGIBLE" if status == "PASS" else "HELD"
    if admission_status != expected:
        raise ValueError(
            "admission status does not match qualification status"
        )


def route_eligible(candidate: Mapping[str, Any]) -> bool:
    validate_candidate(candidate)
    return (
        candidate["qualification"]["status"] == "PASS"
        and candidate["admission"]["status"] == "VERAOS_ROUTE_ELIGIBLE"
    )
