from __future__ import annotations

import json
from pathlib import Path

import bootcamp
import fast_bootcamp  # noqa: F401 - installs the bounded, conservative runtime profile


def main() -> None:
    bootcamp.assert_zero_cost()
    spec = bootcamp.load_spec()
    print(json.dumps({k: v for k, v in spec.items() if k != "sources"}), flush=True)
    knowledge, evidence = bootcamp.build_knowledge_pack(spec["function"], spec["sources"])
    caps = bootcamp.build_capabilities(spec["function"], spec["target"], knowledge)
    curriculum = bootcamp.build_curriculum(spec, knowledge, caps)
    audit, lessons, regressions = bootcamp.run_training(spec, knowledge, caps, curriculum)
    transfer_tasks = bootcamp.build_transfer_tasks(spec, caps, curriculum)
    transfers = bootcamp.run_transfer(spec, knowledge, caps, lessons, transfer_tasks)
    qual = bootcamp.qualify(spec, caps, audit, transfers, evidence)
    capsule = bootcamp.distill(spec, knowledge, caps, lessons, qual)
    bootcamp.write_outputs(spec, capsule, qual, regressions, audit, transfers, evidence, curriculum)
    Path("out/SOURCE_EXCERPTS.md").write_text(
        fast_bootcamp.get_source_pack().strip() + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "package_outcome": qual.get("outcome", "UNKNOWN"),
        "training_package_ready": bool(qual.get("training_package_ready", False)),
        "native_identity_qualification": qual.get("native_identity_qualification", "NOT_RUN"),
        "transfer_proxy_average": qual.get("transfer_proxy_average"),
    }), flush=True)


if __name__ == "__main__":
    main()
