from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets

from successor.experiments.generate_v10_vera_identity_final import (
    canonical_json,
    protocol_sha256,
    sha256_text,
    validate_candidate_freeze,
    validate_protocol,
)


NONCE_SCHEMA = "V10_VERA_IDENTITY_FINAL_NONCE_RECEIPT_V1"


def build_nonce_receipt(
    protocol: dict,
    candidate_freeze_receipt: dict,
    *,
    actor_id: str,
    nonce_bytes: bytes | None = None,
    created_at_utc: str | None = None,
) -> dict:
    validate_protocol(protocol)
    candidate_sha = validate_candidate_freeze(candidate_freeze_receipt)

    if not isinstance(actor_id, str) or not actor_id.strip():
        raise ValueError("actor_id missing")
    raw = secrets.token_bytes(32) if nonce_bytes is None else nonce_bytes
    if not isinstance(raw, bytes) or len(raw) != 32:
        raise ValueError("nonce must be exactly 32 bytes")

    created = created_at_utc or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    if not isinstance(created, str) or not created.strip():
        raise ValueError("created_at_utc missing")

    nonce_hex = raw.hex()
    receipt = {
        "schema": NONCE_SCHEMA,
        "status": "POST_FREEZE_NONCE_CLAIMED",
        "actor_id": actor_id,
        "actor_role": "INDEPENDENT_FINAL_CUSTODIAN",
        "generated_at_utc": created,
        "protocol_sha256": protocol_sha256(protocol),
        "candidate_adapter_sha256": candidate_sha,
        "candidate_freeze_receipt_sha256": sha256_text(
            canonical_json(candidate_freeze_receipt)
        ),
        "nonce_hex": nonce_hex,
        "nonce_sha256": sha256_text(nonce_hex),
        "nonce_bytes": 32,
        "one_shot_claim": True,
        "training_lane_selected_nonce": False,
        "retry_after_claim": False,
        "crash_after_exclusive_create_counts_as_consumed": True,
    }
    receipt["receipt_sha256"] = sha256_text(canonical_json(receipt))
    return receipt


def validate_nonce_receipt(
    protocol: dict,
    candidate_freeze_receipt: dict,
    nonce_receipt: dict,
) -> str:
    validate_protocol(protocol)
    candidate_sha = validate_candidate_freeze(candidate_freeze_receipt)

    if nonce_receipt.get("schema") != NONCE_SCHEMA:
        raise ValueError("nonce receipt schema mismatch")
    if nonce_receipt.get("status") != "POST_FREEZE_NONCE_CLAIMED":
        raise ValueError("nonce receipt not claimed")
    if nonce_receipt.get("actor_role") != "INDEPENDENT_FINAL_CUSTODIAN":
        raise ValueError("nonce custodian role invalid")
    if nonce_receipt.get("training_lane_selected_nonce") is not False:
        raise ValueError("training lane must not select nonce")
    if nonce_receipt.get("one_shot_claim") is not True:
        raise ValueError("nonce claim is not one-shot")
    if nonce_receipt.get("retry_after_claim") is not False:
        raise ValueError("nonce retry must be forbidden")
    if (
        nonce_receipt.get("crash_after_exclusive_create_counts_as_consumed")
        is not True
    ):
        raise ValueError("crash-consumption rule missing")

    expected_protocol = protocol_sha256(protocol)
    if nonce_receipt.get("protocol_sha256") != expected_protocol:
        raise ValueError("nonce protocol binding mismatch")
    if nonce_receipt.get("candidate_adapter_sha256") != candidate_sha:
        raise ValueError("nonce candidate binding mismatch")

    freeze_sha = sha256_text(canonical_json(candidate_freeze_receipt))
    if nonce_receipt.get("candidate_freeze_receipt_sha256") != freeze_sha:
        raise ValueError("nonce freeze-receipt binding mismatch")

    nonce_hex = nonce_receipt.get("nonce_hex")
    if (
        not isinstance(nonce_hex, str)
        or len(nonce_hex) != 64
        or any(ch not in "0123456789abcdef" for ch in nonce_hex)
    ):
        raise ValueError("nonce_hex invalid")
    if nonce_receipt.get("nonce_bytes") != 32:
        raise ValueError("nonce byte count invalid")
    if nonce_receipt.get("nonce_sha256") != sha256_text(nonce_hex):
        raise ValueError("nonce SHA-256 mismatch")

    claimed_receipt_sha = nonce_receipt.get("receipt_sha256")
    unhashed = dict(nonce_receipt)
    unhashed.pop("receipt_sha256", None)
    if claimed_receipt_sha != sha256_text(canonical_json(unhashed)):
        raise ValueError("nonce receipt self-hash mismatch")
    return nonce_hex


def write_nonce_receipt_exclusive(path: Path, receipt: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        payload = (
            json.dumps(
                receipt,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument(
        "--candidate-freeze-receipt",
        type=Path,
        required=True,
    )
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8-sig"))
    freeze_receipt = json.loads(
        args.candidate_freeze_receipt.read_text(encoding="utf-8-sig")
    )
    receipt = build_nonce_receipt(
        protocol,
        freeze_receipt,
        actor_id=args.actor_id,
    )

    try:
        write_nonce_receipt_exclusive(args.output, receipt)
    except FileExistsError as exc:
        raise SystemExit(
            "HOLD: nonce claim path already exists; "
            "existing or partial claim counts as consumed"
        ) from exc

    print(json.dumps({
        "status": receipt["status"],
        "protocol_sha256": receipt["protocol_sha256"],
        "candidate_adapter_sha256": receipt["candidate_adapter_sha256"],
        "nonce_sha256": receipt["nonce_sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
        "output": args.output.as_posix(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
