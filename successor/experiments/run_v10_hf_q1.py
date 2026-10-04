from __future__ import annotations

import argparse
import json
from pathlib import Path


class HfQ1Hold(RuntimeError):
    """Fail-closed refusal for the bounded Hugging Face Q1 package."""


SCHEMA = "V10_HF_Q1_R2_CLOUD_PROTOCOL_V1"
EXPECTED_R2_HEAD = "bc8c4c997aae11ef9b80a899d273bf18283dbf8c"
EXPECTED_R2_SPEC_SHA256 = (
    "caaecf6309aee0ff5279c42b48118065d156228e22c614a5347bf489951b290d"
)
EXPECTED_BASE = {
    "repo": "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive",
    "revision": "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8",
    "mutable_revision_allowed": False,
}
CLAIM_CEILING = (
    "CLOUD_EXECUTABILITY_AND_ENVIRONMENT_ISOLATION_ONLY_"
    "NOT_RECIPE_WINNER_NOT_BEHAVIOR_QUALIFICATION_NOT_FINAL_TRAINING"
)


def load_and_validate_protocol(path: Path | str) -> dict:
    path = Path(path)
    if not path.is_file():
        raise HfQ1Hold(f"protocol missing:{path}")
    value = json.loads(path.read_text(encoding="utf-8"))

    if value.get("schema") != SCHEMA:
        raise HfQ1Hold("protocol schema mismatch")
    if value.get("status") != "DRY_RUN_ONLY_NO_PAID_EXECUTION":
        raise HfQ1Hold("protocol must remain dry-run only")

    authority = value.get("authority")
    if not isinstance(authority, dict):
        raise HfQ1Hold("authority block missing")
    if authority.get("paid_compute_authorized") is not False:
        raise HfQ1Hold("current protocol must not authorize paid compute")
    if authority.get("hf_job_launch_authorized") is not False:
        raise HfQ1Hold("current protocol must not authorize job launch")
    if authority.get("merge_authorized") is not False:
        raise HfQ1Hold("merge authority must remain false")
    if authority.get("deploy_activate_authorized") is not False:
        raise HfQ1Hold("deploy/activate authority must remain false")

    source = value.get("source_subject")
    if not isinstance(source, dict):
        raise HfQ1Hold("source subject missing")
    if source.get("r2_training_head") != EXPECTED_R2_HEAD:
        raise HfQ1Hold("R2 training head mismatch")
    if source.get("r2_execution_spec_sha256") != EXPECTED_R2_SPEC_SHA256:
        raise HfQ1Hold("R2 execution spec digest mismatch")
    if source.get("development_window_start_row") != 0:
        raise HfQ1Hold("development window must start at row 0")
    if source.get("development_window_row_count") != 160:
        raise HfQ1Hold("development window must contain 160 rows")

    if value.get("base_model") != EXPECTED_BASE:
        raise HfQ1Hold("base model binding mismatch")

    recipe = value.get("recipe_equivalence")
    if not isinstance(recipe, dict):
        raise HfQ1Hold("recipe equivalence block missing")
    expected_recipe = {
        "train_rows": [0, 159],
        "max_optimizer_steps": 20,
        "seed": 20261001,
        "learning_rate": 2e-5,
        "lr_scheduler_type": "cosine",
        "warmup_optimizer_steps": 0,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 8,
        "max_length": 512,
        "optimizer": "adamw_bnb_8bit",
        "completion_only_loss": True,
        "packing": False,
        "shuffle_dataset": False,
        "train_sampling_strategy": "sequential",
        "gradient_checkpointing": True,
        "bf16": True,
        "tf32": True,
        "quantization": {
            "load_in_4bit": True,
            "type": "nf4",
            "double_quant": True,
            "compute_dtype": "bfloat16",
        },
        "lora": {
            "r": 4,
            "alpha": 16,
            "dropout": 0,
            "target_modules": "all-linear",
        },
    }
    if recipe != expected_recipe:
        raise HfQ1Hold("R2 recipe equivalence mismatch")

    hardware = value.get("hardware")
    if not isinstance(hardware, dict):
        raise HfQ1Hold("hardware block missing")
    if hardware.get("preferred_flavor") != "a10g-small":
        raise HfQ1Hold("Q1 preferred flavor mismatch")
    if int(hardware.get("minimum_vram_gib", 0)) < 24:
        raise HfQ1Hold("Q1 requires at least 24 GiB VRAM")

    limits = value.get("limits")
    if not isinstance(limits, dict):
        raise HfQ1Hold("limits block missing")
    if limits.get("timeout_seconds") != 1800:
        raise HfQ1Hold("Q1 timeout must remain 1800 seconds")
    if float(limits.get("proposed_budget_cap_usd", 0)) != 0.50:
        raise HfQ1Hold("Q1 proposed budget cap mismatch")
    if limits.get("automatic_retry") is not False:
        raise HfQ1Hold("automatic retry must remain disabled")

    evaluation = value.get("evaluation")
    if not isinstance(evaluation, dict):
        raise HfQ1Hold("evaluation boundary missing")
    if evaluation.get("final_bank") != "PROHIBITED":
        raise HfQ1Hold("final bank must remain prohibited")
    if evaluation.get("one_time_panel") != "PROHIBITED":
        raise HfQ1Hold("one-time panel must remain prohibited")

    if value.get("claim_ceiling") != CLAIM_CEILING:
        raise HfQ1Hold("claim ceiling mismatch")

    return value


def assert_paid_launch_authority(authority: dict | None) -> dict:
    if not isinstance(authority, dict):
        raise HfQ1Hold("paid compute authority missing")
    if authority.get("paid_compute_authorized") is not True:
        raise HfQ1Hold("paid compute is not authorized")
    if authority.get("hf_job_launch_authorized") is not True:
        raise HfQ1Hold("paid compute job launch is not authorized")
    cap = authority.get("budget_cap_usd")
    if not isinstance(cap, (int, float)) or cap <= 0:
        raise HfQ1Hold("paid compute budget cap missing")
    if authority.get("subject_r2_head") != EXPECTED_R2_HEAD:
        raise HfQ1Hold("paid authority subject head mismatch")
    if authority.get("subject_r2_spec_sha256") != EXPECTED_R2_SPEC_SHA256:
        raise HfQ1Hold("paid authority spec digest mismatch")
    return authority


def build_dry_run_plan(protocol: dict) -> dict:
    authority = protocol["authority"]
    source = protocol["source_subject"]
    return {
        "schema": "V10_HF_Q1_DRY_RUN_PLAN_V1",
        "status": "DRY_RUN_ONLY",
        "paid_compute_authorized": False,
        "source_subject": {
            "repository": source["repository"],
            "r2_training_branch": source["r2_training_branch"],
            "r2_training_head": source["r2_training_head"],
            "r2_execution_spec_path": source["r2_execution_spec_path"],
            "r2_execution_spec_sha256": source["r2_execution_spec_sha256"],
            "runtime_binding_sha256": source["runtime_binding_sha256"],
            "train_sha256": source["train_sha256"],
            "development_window": {
                "start_row": source["development_window_start_row"],
                "row_count": source["development_window_row_count"],
            },
            "order_manifest_sha256": source["order_manifest_sha256"],
            "ordered_record_ids_sha256": source[
                "ordered_record_ids_sha256"
            ],
            "expected_initial_trainable_parameter_digest": source[
                "expected_initial_trainable_parameter_digest"
            ],
        },
        "base_model": protocol["base_model"],
        "base_artifact_hashes": protocol["base_artifact_hashes"],
        "runtime_packages": protocol["runtime_packages"],
        "recipe_equivalence": protocol["recipe_equivalence"],
        "environment_equivalence": protocol["environment_equivalence"],
        "hardware": {
            "flavor": protocol["hardware"]["preferred_flavor"],
            "minimum_vram_gib": protocol["hardware"]["minimum_vram_gib"],
            "fallback_flavor": protocol["hardware"]["fallback_flavor"],
        },
        "limits": {
            "timeout_seconds": protocol["limits"]["timeout_seconds"],
            "proposed_budget_cap_usd": authority[
                "proposed_budget_cap_usd"
            ],
            "automatic_retry": False,
        },
        "input_staging": protocol["input_staging"],
        "evaluation": protocol["evaluation"],
        "required_receipts": protocol["required_receipts"],
        "claim_ceiling": protocol["claim_ceiling"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol = load_and_validate_protocol(args.protocol)
    plan = build_dry_run_plan(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(plan, sort_keys=True))


if __name__ == "__main__":
    main()
