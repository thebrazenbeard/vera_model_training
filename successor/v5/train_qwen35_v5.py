from __future__ import annotations

import json
from pathlib import Path

from successor.v5.qwen35_substrate import (
    lora_receipt_fields,
    load_qwen35_text_model,
    load_spec,
)
from successor.v5.train_v5 import train


def train_qwen35(
    general_sft_path: Path,
    general_pref_path: Path,
    targeted_path: Path,
    output_dir: Path,
    *,
    smoke: bool = False,
) -> dict:
    spec = load_spec()
    receipt = train(
        general_sft_path,
        general_pref_path,
        targeted_path,
        output_dir,
        smoke=smoke,
        model_loader=load_qwen35_text_model,
        base_repo=spec["repo"],
        base_revision=spec["revision"],
        lora_receipt=lora_receipt_fields(spec),
    )
    receipt["substrate_subject_id"] = spec["subject_id"]
    receipt["training_modality"] = spec["training_modality"]
    receipt["allow_vision_adapters"] = spec["allow_vision_adapters"]
    receipt["license_status"] = spec["license_status"]
    (output_dir / "training_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--general-sft", type=Path, required=True)
    ap.add_argument("--general-prefs", type=Path, required=True)
    ap.add_argument("--targeted", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    print(
        json.dumps(
            train_qwen35(
                args.general_sft,
                args.general_prefs,
                args.targeted,
                args.output_dir,
                smoke=args.smoke,
            ),
            sort_keys=True,
        )
    )
