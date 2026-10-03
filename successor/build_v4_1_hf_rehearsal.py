from __future__ import annotations

from pathlib import Path

from successor import build_v4_hf_rehearsal as base

# V4.0's rehearsal pool currently produces 40,500 rows. V4.1 deliberately
# restores the originally intended 42,500-row rehearsal pool by distributing
# 2,000 additional rows across four already-selected public source splits.
TARGETS = dict(base.TARGETS)
TARGETS.update(
    {
        "smoltalk_smollm3_explore_instruct_rewriting_no_think": 7500,
        "smoltalk_smollm3_smol_rewrite_no_think": 6500,
        "tulu_3_sft_personas_instruction_following_no_think": 7500,
        "table_gpt_no_think": 5000,
    }
)
EXPECTED_ROWS = sum(TARGETS.values())


def build(output_path: Path | None = None) -> dict:
    original_targets = base.TARGETS
    original_expected = base.EXPECTED_ROWS
    try:
        base.TARGETS = TARGETS
        base.EXPECTED_ROWS = EXPECTED_ROWS
        manifest = base.build(output_path)
    finally:
        base.TARGETS = original_targets
        base.EXPECTED_ROWS = original_expected

    manifest["schema"] = "VERA_V4_1_HF_REHEARSAL_MANIFEST_V1"
    manifest["corpus_id"] = "VERA_V4_1_HF_REHEARSAL_42500_20260930_V1"
    manifest["target_rows"] = EXPECTED_ROWS
    manifest["target_adjustment_from_v4"] = 2000
    manifest["adjustment_strategy"] = {
        "smoltalk_smollm3_explore_instruct_rewriting_no_think": 500,
        "smoltalk_smollm3_smol_rewrite_no_think": 500,
        "tulu_3_sft_personas_instruction_following_no_think": 500,
        "table_gpt_no_think": 500,
    }
    return manifest


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2, sort_keys=True))
