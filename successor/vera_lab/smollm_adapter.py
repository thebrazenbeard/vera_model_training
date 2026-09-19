from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


SMOLLM3_REPO_ID = "HuggingFaceTB/SmolLM3-3B"
SMOLLM3_REVISION = "a07cc9a04f16550a088caea529712d1d335b0ac1"
NEUTRAL_SYSTEM = {"role": "system", "content": "/no_think /system_override"}


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1_file(path: str | Path) -> str:
    file_path = Path(path)
    digest = hashlib.sha1()
    digest.update(f"blob {file_path.stat().st_size}\0".encode("ascii"))
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_local_base(manifest: dict[str, Any], base_path: Path) -> dict[str, Any]:
    revision = manifest.get("revision")
    if manifest.get("observed_hub_sha") != revision:
        raise ValueError("observed hub SHA does not match pinned base revision")
    tree_rel = manifest.get("observed_local_cache_tree")
    if not isinstance(tree_rel, str) or not tree_rel:
        raise ValueError("base manifest must name the observed local cache tree")
    relative_tree = Path(tree_rel)
    if relative_tree.is_absolute() or ".." in relative_tree.parts:
        raise ValueError("observed local cache tree must be a relative path")
    expected_name = f"{revision}.json"
    if relative_tree.name != expected_name:
        raise ValueError("observed local cache tree does not match pinned revision")

    base_root = base_path.resolve()
    tree_path = (base_path / relative_tree).resolve()
    if not tree_path.is_relative_to(base_root) or not tree_path.is_file():
        raise FileNotFoundError(f"base revision tree is missing: {tree_path}")
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    if tree.get("format_version") != 1 or not isinstance(tree.get("files"), dict) or not tree["files"]:
        raise ValueError("base revision tree is malformed")

    total_bytes = 0
    for rel_name, evidence in sorted(tree["files"].items()):
        if not isinstance(rel_name, str) or not isinstance(evidence, dict):
            raise ValueError("base revision tree contains malformed file evidence")
        relative_file = Path(rel_name)
        if relative_file.is_absolute() or ".." in relative_file.parts:
            raise ValueError("base revision tree contains unsafe file path")
        candidate = (base_path / relative_file).resolve()
        if not candidate.is_relative_to(base_root) or not candidate.is_file():
            raise FileNotFoundError(f"base file is missing: {rel_name}")
        size = evidence.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValueError(f"base file size evidence is invalid: {rel_name}")
        actual_size = candidate.stat().st_size
        if actual_size != size:
            raise ValueError(f"base file size mismatch: {rel_name}")
        total_bytes += actual_size

        lfs_sha256 = evidence.get("lfs_sha256")
        blob_id = evidence.get("blob_id")
        if isinstance(lfs_sha256, str) and lfs_sha256:
            if sha256_file(candidate) != lfs_sha256:
                raise ValueError(f"base file SHA-256 mismatch: {rel_name}")
        elif isinstance(blob_id, str) and blob_id:
            if git_blob_sha1_file(candidate) != blob_id:
                raise ValueError(f"base file Git blob mismatch: {rel_name}")
        else:
            raise ValueError(f"base file lacks content identity: {rel_name}")

    declared_total = manifest.get("total_bytes")
    return {
        "revision": revision,
        "tree_sha256": sha256_file(tree_path),
        "file_count": len(tree["files"]),
        "verified_total_bytes": total_bytes,
        "declared_total_bytes": declared_total,
        "total_bytes_match": declared_total is None or declared_total == total_bytes,
    }


def normalize_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(messages, list):
        raise ValueError("messages must be a list")
    normalized = [copy.deepcopy(NEUTRAL_SYSTEM)]
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("message must be an object")
        role = message.get("role")
        content = message.get("content")
        if role == "system":
            continue
        if role not in {"user", "assistant"} or not isinstance(content, str) or not content:
            raise ValueError("messages require user/assistant roles with nonempty content")
        normalized.append({"role": role, "content": content})
    return normalized


def load_model_stack(base_path: Path, adapter_path: Path):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        str(base_path),
        local_files_only=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        str(base_path),
        local_files_only=True,
        quantization_config=quantization,
        device_map={"": 0},
        dtype=torch.bfloat16,
    )
    model = PeftModel.from_pretrained(
        base,
        str(adapter_path),
        is_trainable=False,
        local_files_only=True,
    )
    model.eval()
    return tokenizer, model, torch


class SmolLMPEFTAdapter:
    def __init__(
        self,
        base_manifest_path: str | Path,
        adapter_path: str | Path,
        generation_config: dict[str, Any] | None = None,
    ) -> None:
        manifest = json.loads(Path(base_manifest_path).read_text(encoding="utf-8"))
        if manifest.get("repo_id") != SMOLLM3_REPO_ID:
            raise ValueError("base repository does not match SmolLM3 control substrate")
        if manifest.get("revision") != SMOLLM3_REVISION:
            raise ValueError("base revision does not match pinned SmolLM3 revision")
        if manifest.get("mutable_revision_allowed") is not False:
            raise ValueError("base manifest must forbid mutable revisions")

        self.base_path = Path(manifest.get("local_path", ""))
        if not self.base_path.is_dir():
            raise FileNotFoundError(f"local base model is missing: {self.base_path}")

        self.base_revision = SMOLLM3_REVISION
        self.base_inventory_digest = manifest.get("file_inventory_sha256")
        self.base_verification = verify_local_base(manifest, self.base_path)

        self.adapter_path = Path(adapter_path)
        weights = self.adapter_path / "adapter_model.safetensors"
        if not weights.is_file():
            raise FileNotFoundError(f"adapter weights are missing: {weights}")
        self.adapter_sha256 = sha256_file(weights)
        self.candidate_digest = self.adapter_sha256

        adapter_config_path = self.adapter_path / "adapter_config.json"
        self.adapter_config_sha256 = None
        if adapter_config_path.is_file():
            adapter_config = json.loads(adapter_config_path.read_text(encoding="utf-8"))
            declared_base = adapter_config.get("base_model_name_or_path")
            if not isinstance(declared_base, str) or not declared_base:
                raise ValueError("adapter config must declare base_model_name_or_path")
            if Path(declared_base).resolve() != self.base_path.resolve():
                raise ValueError("adapter base path does not match verified local base")
            if adapter_config.get("peft_type") != "LORA":
                raise ValueError("adapter config must declare LORA PEFT type")
            self.adapter_config_sha256 = sha256_file(adapter_config_path)

        config = {"max_new_tokens": 80, "do_sample": False}
        if generation_config:
            config.update(copy.deepcopy(generation_config))
        if config.get("do_sample") is not False:
            raise ValueError("do_sample must remain false for deterministic replay")
        if not isinstance(config.get("max_new_tokens"), int) or config["max_new_tokens"] < 1:
            raise ValueError("max_new_tokens must be a positive integer")
        self.generation_config = config
        self._stack = None

    def _ensure_stack(self):
        if self._stack is None:
            self._stack = load_model_stack(self.base_path, self.adapter_path)
        return self._stack

    def generate(self, messages: list[dict[str, str]], runtime_state: dict[str, Any]) -> str:
        del runtime_state
        tokenizer, model, torch = self._ensure_stack()
        formatted_messages = normalize_messages(messages)
        text = tokenizer.apply_chat_template(
            formatted_messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        batch = tokenizer(
            text,
            return_tensors="pt",
            add_special_tokens=False,
        ).to("cuda")
        kwargs = dict(self.generation_config)
        kwargs["pad_token_id"] = tokenizer.eos_token_id
        with torch.inference_mode():
            generated = model.generate(**batch, **kwargs)
        prompt_length = batch["input_ids"].shape[1]
        new_tokens = generated[0, prompt_length:]
        answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        if not answer:
            raise ValueError("model produced an empty response")
        return answer
