import hashlib
import json
from pathlib import Path

import pytest

from successor.vera_lab import smollm_adapter as module
from successor.vera_lab.smollm_adapter import (
    SMOLLM3_REPO_ID,
    SMOLLM3_REVISION,
    SmolLMPEFTAdapter,
    normalize_messages,
)


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def write_manifest(path: Path, local_base: Path, revision=SMOLLM3_REVISION):
    tree_rel = f".cache/huggingface/trees/{revision}.json"
    if local_base.is_dir():
        payload = b"{\"model_type\":\"smollm3\"}\n"
        (local_base / "config.json").write_bytes(payload)
        tree_path = local_base / tree_rel
        tree_path.parent.mkdir(parents=True, exist_ok=True)
        tree_path.write_text(json.dumps({
            "format_version": 1,
            "files": {
                "config.json": {
                    "size": len(payload),
                    "blob_id": git_blob_sha1(payload),
                }
            },
        }), encoding="utf-8")
    path.write_text(json.dumps({
        "repo_id": SMOLLM3_REPO_ID,
        "revision": revision,
        "local_path": str(local_base),
        "mutable_revision_allowed": False,
        "file_inventory_sha256": "base-inventory",
        "observed_hub_sha": revision,
        "observed_local_cache_tree": tree_rel,
    }), encoding="utf-8")


def write_adapter(path: Path, data=b"adapter-bytes"):
    path.mkdir(parents=True)
    (path / "adapter_model.safetensors").write_bytes(data)


def test_rejects_wrong_base_revision(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base, revision="wrong")
    with pytest.raises(ValueError, match="revision"):
        SmolLMPEFTAdapter(manifest, adapter)


def test_missing_local_base_fails_without_loader(tmp_path, monkeypatch):
    adapter = tmp_path / "adapter"
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, tmp_path / "missing")
    called = False

    def forbidden_loader(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("loader should not run")

    monkeypatch.setattr(module, "load_model_stack", forbidden_loader)
    with pytest.raises(FileNotFoundError):
        SmolLMPEFTAdapter(manifest, adapter)
    assert called is False


def test_adapter_digest_and_generation_defaults(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    payload = b"known-adapter"
    write_adapter(adapter, payload)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)
    instance = SmolLMPEFTAdapter(manifest, adapter)
    assert instance.candidate_digest == hashlib.sha256(payload).hexdigest()
    assert instance.generation_config["do_sample"] is False
    assert instance.generation_config["max_new_tokens"] == 80
    assert instance.base_revision == SMOLLM3_REVISION


def test_generation_config_rejects_sampling(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)
    with pytest.raises(ValueError, match="do_sample"):
        SmolLMPEFTAdapter(manifest, adapter, {"do_sample": True})


def test_adapter_config_cannot_point_at_a_different_base(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    (adapter / "adapter_config.json").write_text(json.dumps({
        "base_model_name_or_path": str(tmp_path / "other-base"),
        "peft_type": "LORA",
    }), encoding="utf-8")
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)

    with pytest.raises(ValueError, match="adapter base path"):
        SmolLMPEFTAdapter(manifest, adapter)


def test_normalize_messages_uses_only_neutral_system():
    messages = [
        {"role": "system", "content": "You are Vera"},
        {"role": "user", "content": "hello"},
    ]
    normalized = normalize_messages(messages)
    assert normalized[0] == {"role": "system", "content": "/no_think /system_override"}
    assert normalized[1:] == [{"role": "user", "content": "hello"}]


def test_generate_uses_neutral_system_and_greedy_kwargs(tmp_path, monkeypatch):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)

    class InputIds:
        shape = (1, 2)

    class Batch(dict):
        def __init__(self):
            super().__init__({"input_ids": InputIds()})
            self.device = None

        def to(self, device):
            self.device = device
            return self

    class Generated:
        def __getitem__(self, key):
            assert key[0] == 0
            assert key[1].start == 2
            return [99]

    class Tokenizer:
        eos_token_id = 2

        def __init__(self):
            self.messages = None

        def apply_chat_template(self, messages, **kwargs):
            self.messages = messages
            assert kwargs["enable_thinking"] is False
            return "formatted"

        def __call__(self, *args, **kwargs):
            return Batch()

        def decode(self, tokens, skip_special_tokens=True):
            assert tokens == [99]
            return "answer"

    class Model:
        def __init__(self):
            self.kwargs = None

        def generate(self, **kwargs):
            self.kwargs = kwargs
            return Generated()

    class Torch:
        class _Context:
            def __enter__(self):
                return None

            def __exit__(self, *args):
                return False

        @staticmethod
        def inference_mode():
            return Torch._Context()

    tokenizer = Tokenizer()
    model = Model()
    monkeypatch.setattr(module, "load_model_stack", lambda *args: (tokenizer, model, Torch))

    instance = SmolLMPEFTAdapter(manifest, adapter)
    answer = instance.generate(
        [
            {"role": "system", "content": "You are Vera"},
            {"role": "user", "content": "hello"},
        ],
        {"ignored": True},
    )
    assert answer == "answer"
    assert tokenizer.messages[0] == {"role": "system", "content": "/no_think /system_override"}
    assert tokenizer.messages[1:] == [{"role": "user", "content": "hello"}]
    assert model.kwargs["do_sample"] is False
    assert model.kwargs["max_new_tokens"] == 80
    assert model.kwargs["pad_token_id"] == 2


def test_local_base_tree_verifies_exact_file_bytes(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)

    instance = SmolLMPEFTAdapter(manifest, adapter)
    assert instance.base_revision == SMOLLM3_REVISION
    assert instance.base_verification["file_count"] == 1
    assert len(instance.base_verification["tree_sha256"]) == 64

    (base / "config.json").write_text("mutated\n", encoding="utf-8")
    with pytest.raises(ValueError, match="base file"):
        SmolLMPEFTAdapter(manifest, adapter)


def test_manifest_hub_sha_must_match_pinned_revision(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["observed_hub_sha"] = "different"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="observed hub"):
        SmolLMPEFTAdapter(manifest, adapter)


def test_historical_total_bytes_mismatch_is_reported_not_promoted_over_exact_files(tmp_path):
    base = tmp_path / "base"
    adapter = tmp_path / "adapter"
    base.mkdir()
    write_adapter(adapter)
    manifest = tmp_path / "base.json"
    write_manifest(manifest, base)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["total_bytes"] = 999
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    instance = SmolLMPEFTAdapter(manifest, adapter)
    assert instance.base_verification["declared_total_bytes"] == 999
    assert instance.base_verification["verified_total_bytes"] == (base / "config.json").stat().st_size
    assert instance.base_verification["total_bytes_match"] is False
