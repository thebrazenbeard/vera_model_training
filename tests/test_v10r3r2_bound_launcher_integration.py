from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from successor.experiments.launch_v10r3r2_durable import (
    SPEC_REL,
    build_bound_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_BINDING = "44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224"


def test_bound_launcher_builds_exact_current_r2_subject() -> None:
    metadata = build_bound_metadata(ROOT)

    head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    spec_bytes = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"HEAD:{SPEC_REL}"]
    )

    assert metadata == {
        "repo_head": head,
        "spec_path": SPEC_REL,
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "runtime_binding_sha256": RUNTIME_BINDING,
    }
