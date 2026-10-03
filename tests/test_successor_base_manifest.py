import json
from pathlib import Path


def test_base_manifest_is_exactly_pinned_as_pilot_control_not_identity_target():
    path = Path("successor/base_model_manifest.json")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["repo_id"] == "HuggingFaceTB/SmolLM3-3B"
    assert data["revision"] == "a07cc9a04f16550a088caea529712d1d335b0ac1"
    assert data["local_path"].lower() == r"c:\vera\models\base\smollm3-3b"
    assert data["mutable_revision_allowed"] is False
    assert data["license"] == "apache-2.0"
    assert data["file_inventory_sha256"] == "abba0d1b75fb0d15f130e2ccf2207c996429b4470d315d9a3f20df9f4e008cac"
    assert data["total_bytes"] == 6167869072
    assert data["training_role"] == "PILOT_CONTROL_SUBSTRATE"
    assert data["identity_package_binding"] == "SUBSTRATE_AGNOSTIC"
    assert data["successor_target_claim"] == "BEHAVIORAL_IDENTITY_PACKAGE_NOT_BASE_MODEL_IDENTITY"
