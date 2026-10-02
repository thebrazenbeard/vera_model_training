from __future__ import annotations

import hashlib
import json


REQUIRED_FIELDS = {"item_id", "prompt_family", "prompt", "rubric"}
SEALED_COMMITMENT_FILENAME = "V10_SEALED_FINAL_BANK_COMMITMENT_V1.json"
SEALED_DERIVABLE_PRECONDITIONS = {
    "fresh_evaluation_bank_frozen",
    "independent_bank_admission_verified",
    "semantic_contamination_screen_verified",
    "contamination_screen_against_v10_and_consumed_finals_verified",
}


def _canonical(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def prompt_hash(prompt: str) -> str:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("heldout prompt must be nonempty text")
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()


def freeze_heldout_manifest(items, train_prompts, validation_prompts):
    train_hashes = {prompt_hash(p) for p in train_prompts}
    validation_hashes = {prompt_hash(p) for p in validation_prompts}
    seen_prompts = set()
    manifest_items = []
    for item in items:
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"heldout item missing fields: {sorted(missing)}")
        digest = prompt_hash(item["prompt"])
        if digest in seen_prompts:
            raise ValueError("duplicate heldout prompt")
        if digest in train_hashes:
            raise ValueError("heldout prompt has training leakage")
        if digest in validation_hashes:
            raise ValueError("heldout prompt has validation leakage")
        seen_prompts.add(digest)
        item_digest = hashlib.sha256(_canonical(item)).hexdigest()
        manifest_items.append({
            "item_id": item["item_id"],
            "prompt_family": item["prompt_family"],
            "prompt_sha256": digest,
            "item_sha256": item_digest,
        })

    set_digest = hashlib.sha256(_canonical(manifest_items)).hexdigest()
    return {
        "schema_version": 1,
        "item_count": len(manifest_items),
        "items": manifest_items,
        "set_sha256": set_digest,
    }


def _read_json(path):
    from pathlib import Path

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _valid_sha256(value) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(ch in "0123456789abcdef" for ch in value)


def _load_sealed_commitment_validator():
    import importlib.util
    from pathlib import Path

    module_path = (
        Path(__file__).resolve().parent
        / "experiments"
        / "sealed_final_bank_commitment.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_v10_sealed_final_bank_commitment",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("sealed commitment validator could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_sealed_final_bank_commitment


def _sealed_commitment_evidence(base, preconditions):
    validate_sealed_final_bank_commitment = (
        _load_sealed_commitment_validator()
    )

    path = base / SEALED_COMMITMENT_FILENAME
    if not path.exists():
        return (
            {
                "status": "ABSENT",
                "bank_id": None,
                "commitment_sha256": None,
            },
            [],
            {},
        )

    commitment = _read_json(path)
    reasons = []
    check = validate_sealed_final_bank_commitment(commitment)
    reasons.extend(
        "sealed_commitment:" + reason
        for reason in check.get("reasons", [])
    )

    claimed_sha = commitment.get("commitment_sha256")
    unsigned = dict(commitment)
    unsigned.pop("commitment_sha256", None)
    expected_sha = hashlib.sha256(_canonical(unsigned)).hexdigest()
    if claimed_sha != expected_sha:
        reasons.append("sealed_commitment_sha256_mismatch")
    if not _valid_sha256(commitment.get("freeze_subject_digest")):
        reasons.append("sealed_commitment_freeze_subject_digest_invalid")

    reasons = sorted(set(reasons))
    if reasons:
        return (
            {
                "status": "INVALID",
                "bank_id": commitment.get("bank_id"),
                "commitment_sha256": claimed_sha,
            },
            reasons,
            {},
        )

    derived = {
        key: True
        for key in sorted(SEALED_DERIVABLE_PRECONDITIONS)
        if key in preconditions
    }
    return (
        {
            "status": "VERIFIED",
            "bank_id": commitment.get("bank_id"),
            "commitment_sha256": claimed_sha,
            "bank_sha256": commitment.get(
                "plaintext_artifacts", {}
            ).get("bank_sha256"),
            "sealed_archive_sha256": commitment.get(
                "plaintext_artifacts", {}
            ).get("sealed_archive_sha256"),
            "plaintext_exposed_to_training_lane": False,
        },
        [],
        derived,
    )


def assess_v10_experiment_state(repo_root):
    from pathlib import Path

    root = Path(repo_root)
    base = root / "successor" / "experiments"
    contract_v2 = base / "V10_QWEN35_EXPERIMENT_CONTRACT_V2.json"
    admission_v2 = base / "V10_QWEN35_FINAL_BANK_ADMISSION_V2.json"
    if contract_v2.exists():
        contract = _read_json(contract_v2)
        admission = _read_json(admission_v2)
        expected_contract_schema = "VERA_SUCCESSOR_V10_QWEN35_EXPERIMENT_CONTRACT_V2"
        expected_admission_schema = "V10_QWEN35_FINAL_BANK_ADMISSION_V2"
    else:
        contract = _read_json(base / "V10_QWEN35_EXPERIMENT_CONTRACT_V1.json")
        admission = _read_json(base / "V10_QWEN35_FINAL_BANK_ADMISSION_V1.json")
        expected_contract_schema = "VERA_SUCCESSOR_V10_QWEN35_EXPERIMENT_CONTRACT_V1"
        expected_admission_schema = "V10_QWEN35_FINAL_BANK_ADMISSION_V1"
    exclusion = _read_json(base / "V10_QWEN35_EXCLUSION_REGISTRY_V1.json")

    reasons = []
    if contract.get("schema") != expected_contract_schema:
        reasons.append("invalid_experiment_contract_schema")
    if admission.get("schema") != expected_admission_schema:
        reasons.append("invalid_final_bank_admission_schema")
    if exclusion.get("schema") != "V10_QWEN35_EXCLUSION_REGISTRY_V1":
        reasons.append("invalid_exclusion_registry_schema")
    if exclusion.get("status") != "FROZEN_EXCLUSION_IDENTITIES":
        reasons.append("exclusion_registry_not_frozen")

    preconditions = contract.get("blocking_preconditions")
    if not isinstance(preconditions, dict):
        reasons.append("blocking_preconditions_missing")
        preconditions = {}

    sealed, sealed_reasons, derived_preconditions = (
        _sealed_commitment_evidence(base, preconditions)
    )
    reasons.extend(sealed_reasons)
    sealed_verified = sealed["status"] == "VERIFIED"

    if (
        admission.get("status") != "FINAL_BANK_ADMITTED_AND_FROZEN"
        and not sealed_verified
    ):
        reasons.append("final_bank_cases_not_admitted")

    effective_preconditions = {}
    for key, value in sorted(preconditions.items()):
        effective_value = derived_preconditions.get(key, value)
        effective_preconditions[key] = effective_value
        if effective_value is not True:
            reasons.append(key)

    if (
        effective_preconditions.get("fresh_evaluation_bank_frozen") is True
        and not sealed_verified
    ):
        bank = contract.get("evaluation_bank", {})
        required = ("behavioral", "adversarial", "retention")
        if any(
            not _valid_sha256(bank.get(lane, {}).get("sha256"))
            for lane in required
        ):
            reasons.append("fresh_evaluation_bank_hashes_missing")

    reasons = sorted(set(reasons))
    ready = not reasons
    return {
        "schema": "V10_QWEN35_PREFLIGHT_V1",
        "status": "READY_PRECONDITIONS" if ready else "HOLD",
        "training_allowed": ready,
        "reasons": reasons,
        "derived_preconditions": derived_preconditions,
        "sealed_final_bank": sealed,
        "effect": "READ_ONLY_PREFLIGHT_NO_WEIGHT_CHANGE",
    }


def _main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--v10-preflight-root")
    args = parser.parse_args(argv)
    if args.v10_preflight_root is None:
        return 0
    try:
        result = assess_v10_experiment_state(args.v10_preflight_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "schema": "V10_QWEN35_PREFLIGHT_V1",
            "status": "HOLD",
            "training_allowed": False,
            "reasons": ["preflight_input_error:" + str(exc)],
            "derived_preconditions": {},
            "sealed_final_bank": {
                "status": "ERROR",
                "bank_id": None,
                "commitment_sha256": None,
            },
            "effect": "READ_ONLY_PREFLIGHT_NO_WEIGHT_CHANGE",
        }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["training_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(_main())
