from __future__ import annotations


def synthetic_smoke_rows(*, count: int = 8) -> list[dict[str, str]]:
    if count < 1:
        raise ValueError("count must be positive")
    return [
        {
            "prompt": f"Stage-0 synthetic runtime smoke {index + 1}: return the fixed token READY.",
            "response": "READY",
        }
        for index in range(count)
    ]


import hashlib
import json
import math
import re


class Stage0Hold(RuntimeError):
    pass


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_sha256(name: str, value: str) -> None:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise Stage0Hold(f"{name} must be a lowercase sha256 digest")


def finalize_stage0_smoke_receipt(
    *,
    runtime_binding_sha256: str,
    execution_spec_sha256: str,
    weight_digest_before: str,
    weight_digest_after: str,
    optimizer_step_count: int,
    optimizer_created: bool,
    gradients_present: bool,
    nonzero_gradient_parameter_count: int,
    microbatches_completed: int,
    losses: list[float],
    synthetic_input: bool,
    output_artifacts_written: bool,
    optimizer_name: str,
    cuda_memory: dict,
) -> dict:
    for name, value in (
        ("runtime_binding_sha256", runtime_binding_sha256),
        ("execution_spec_sha256", execution_spec_sha256),
        ("weight_digest_before", weight_digest_before),
        ("weight_digest_after", weight_digest_after),
    ):
        _require_sha256(name, value)

    if optimizer_step_count != 1:
        raise Stage0Hold("Stage-0 requires exactly one optimizer step")
    if not optimizer_created:
        raise Stage0Hold("optimizer was not created")
    if not gradients_present or nonzero_gradient_parameter_count < 1:
        raise Stage0Hold("nonzero trainable gradients were not observed")
    if microbatches_completed < 1 or len(losses) != microbatches_completed:
        raise Stage0Hold("microbatch/loss accounting mismatch")
    if not all(isinstance(loss, (int, float)) and math.isfinite(float(loss)) for loss in losses):
        raise Stage0Hold("losses must all be finite")
    if not synthetic_input:
        raise Stage0Hold("Stage-0 smoke requires synthetic input")
    if output_artifacts_written:
        raise Stage0Hold("Stage-0 smoke must not write output artifacts")
    if weight_digest_before == weight_digest_after:
        raise Stage0Hold("trainable parameter digest did not change")
    if not optimizer_name:
        raise Stage0Hold("optimizer name missing")
    if not isinstance(cuda_memory, dict):
        raise Stage0Hold("cuda memory receipt missing")

    receipt = {
        "schema": "V10R3R3_STAGE0_RUNTIME_SMOKE_RECEIPT_V1",
        "status": "STAGE0_OPTIMIZER_SMOKE_PASS",
        "claim_ceiling": "DISPOSABLE_SYNTHETIC_ONE_STEP_RUNTIME_QUALIFICATION_ONLY",
        "runtime_binding_sha256": runtime_binding_sha256,
        "execution_spec_sha256": execution_spec_sha256,
        "optimizer_step_count": optimizer_step_count,
        "optimizer_created": optimizer_created,
        "optimizer_name": optimizer_name,
        "gradients_present": gradients_present,
        "nonzero_gradient_parameter_count": nonzero_gradient_parameter_count,
        "microbatches_completed": microbatches_completed,
        "losses": [float(loss) for loss in losses],
        "synthetic_input": synthetic_input,
        "output_artifacts_written": output_artifacts_written,
        "weight_digest_before": weight_digest_before,
        "weight_digest_after": weight_digest_after,
        "weight_digest_changed": True,
        "cuda_memory": cuda_memory,
    }
    canonical = json.dumps(
        receipt, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return receipt


def execute_stage0_optimizer_smoke(
    repo_root,
    *,
    training_stack_loader=None,
) -> dict:
    import tempfile
    from pathlib import Path

    from successor.experiments.probe_v10_qwen35_backward import (
        _trainable_parameter_digest,
    )
    from successor.experiments.train_v10_qwen35_authorized import (
        _observe_live_runtime,
        _read_json,
        _validate_qwen_topology,
        load_training_stack,
        prepare_sft_rows,
        sha256_file,
        validate_lora_target_coverage,
        validate_runtime_observation,
    )

    root = Path(repo_root)
    experiment_dir = root / "successor" / "experiments"
    runtime_path = (
        experiment_dir / "V10_QWEN35_TRAINING_RUNTIME_BINDING_V1.json"
    )
    execution_spec_path = (
        experiment_dir
        / "V10R3R3_CONTINUOUS20_DURABLE_EXECUTION_SPEC_20261005_V1.json"
    )
    runtime_binding = _read_json(runtime_path)
    execution_spec = _read_json(execution_spec_path)

    if training_stack_loader is None:
        training_stack_loader = load_training_stack
    stack = training_stack_loader()
    if not isinstance(stack, dict):
        raise Stage0Hold("training stack loader returned invalid object")

    live_runtime = _observe_live_runtime(runtime_binding, stack)
    validate_runtime_observation(runtime_binding, live_runtime)

    trainer_spec = execution_spec["trainer"]
    accumulation_steps = int(trainer_spec["gradient_accumulation_steps"])
    if accumulation_steps != 8:
        raise Stage0Hold(
            "Stage-0 frozen synthetic smoke requires gradient accumulation 8"
        )
    rows = synthetic_smoke_rows(count=accumulation_steps)

    target = runtime_binding["target"]
    base_path = Path(target["base_path"])
    tokenizer = stack["AutoTokenizer"].from_pretrained(base_path)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    prepared, _token_budget = prepare_sft_rows(
        tokenizer,
        rows,
        max_length=int(trainer_spec["max_length"]),
    )

    torch = stack["torch"]
    if not torch.cuda.is_available():
        raise Stage0Hold("CUDA is unavailable")

    quant = execution_spec["quantization"]
    bits_config = stack["BitsAndBytesConfig"](
        load_in_4bit=quant["load_in_4bit"],
        bnb_4bit_quant_type=quant["type"],
        bnb_4bit_use_double_quant=quant["double_quant"],
        bnb_4bit_compute_dtype=getattr(torch, quant["compute_dtype"]),
    )
    model_load = execution_spec["model_load"]
    model = stack["Qwen3_5ForCausalLM"].from_pretrained(
        base_path,
        quantization_config=bits_config,
        device_map=model_load["device_map"],
        dtype=getattr(torch, model_load["dtype"]),
    )
    model.config.use_cache = model_load["use_cache"]
    _validate_qwen_topology(model)
    model = stack["prepare_model_for_kbit_training"](
        model,
        use_gradient_checkpointing=model_load[
            "prepare_model_for_kbit_training_use_gradient_checkpointing"
        ],
    )

    lora_spec = execution_spec["lora"]
    lora = stack["LoraConfig"](
        r=lora_spec["r"],
        lora_alpha=lora_spec["alpha"],
        lora_dropout=lora_spec["dropout"],
        bias=lora_spec["bias"],
        task_type=lora_spec["task_type"],
        target_modules=lora_spec["target_modules"],
    )
    stack["transformers"].set_seed(trainer_spec["seed"])

    with tempfile.TemporaryDirectory(
        prefix="vera-v10r3r3-stage0-smoke-"
    ) as temp_dir:
        sft_config = stack["SFTConfig"](
            output_dir=temp_dir,
            per_device_train_batch_size=trainer_spec[
                "per_device_train_batch_size"
            ],
            gradient_accumulation_steps=accumulation_steps,
            num_train_epochs=1,
            learning_rate=trainer_spec["learning_rate"],
            lr_scheduler_type=trainer_spec["lr_scheduler_type"],
            warmup_steps=trainer_spec["warmup_optimizer_steps"],
            optim=trainer_spec["optimizer"],
            bf16=trainer_spec["bf16"],
            tf32=trainer_spec["tf32"],
            gradient_checkpointing=trainer_spec["gradient_checkpointing"],
            gradient_checkpointing_kwargs={
                "use_reentrant": trainer_spec[
                    "gradient_checkpointing_use_reentrant"
                ]
            },
            max_length=trainer_spec["max_length"],
            completion_only_loss=trainer_spec["completion_only_loss"],
            packing=False,
            shuffle_dataset=False,
            logging_steps=1,
            save_strategy="no",
            eval_strategy="no",
            report_to="none",
            seed=trainer_spec["seed"],
            data_seed=trainer_spec["seed"],
        )
        trainer = stack["SFTTrainer"](
            model=model,
            args=sft_config,
            train_dataset=stack["Dataset"].from_list(prepared),
            processing_class=tokenizer,
            peft_config=lora,
        )
        validate_lora_target_coverage(
            getattr(trainer.model, "targeted_module_names", [])
        )
        if trainer.optimizer is not None:
            raise Stage0Hold("optimizer existed before explicit Stage-0 creation")

        weight_before, trainable_count = _trainable_parameter_digest(
            trainer.model,
            torch,
        )
        expected_before = execution_spec["comparison"].get(
            "expected_initial_trainable_parameter_digest"
        )
        if weight_before != expected_before:
            raise Stage0Hold(
                "initial trainable digest mismatch:"
                f"{weight_before}!={expected_before}"
            )

        dataloader = trainer.get_train_dataloader()
        iterator = iter(dataloader)
        trainer.model.train()
        trainer.model.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        allocated_before = torch.cuda.memory_allocated()
        reserved_before = torch.cuda.memory_reserved()

        losses: list[float] = []
        for microbatch_index in range(accumulation_steps):
            try:
                batch = next(iterator)
            except StopIteration as exc:
                raise Stage0Hold(
                    "synthetic Stage-0 dataloader ended early:"
                    f"{microbatch_index}/{accumulation_steps}"
                ) from exc
            batch = trainer._prepare_inputs(batch)
            loss = trainer.compute_loss(trainer.model, batch)
            if not bool(torch.isfinite(loss.detach()).item()):
                raise Stage0Hold(
                    f"loss is not finite at microbatch:{microbatch_index}"
                )
            losses.append(float(loss.detach().float().cpu().item()))
            trainer.accelerator.backward(loss / accumulation_steps)

        torch.cuda.synchronize()
        nonzero_gradient_parameter_count = 0
        for _, parameter in trainer.model.named_parameters():
            if (
                parameter.requires_grad
                and parameter.grad is not None
                and bool(torch.count_nonzero(parameter.grad.detach()).item())
            ):
                nonzero_gradient_parameter_count += 1
        if nonzero_gradient_parameter_count < 1:
            raise Stage0Hold("no nonzero trainable gradients observed")

        trainer.create_optimizer()
        if trainer.optimizer is None:
            raise Stage0Hold("optimizer creation failed")
        optimizer_name = trainer.optimizer.__class__.__name__
        trainer.optimizer.step()
        torch.cuda.synchronize()

        weight_after, post_trainable_count = _trainable_parameter_digest(
            trainer.model,
            torch,
        )
        if post_trainable_count != trainable_count:
            raise Stage0Hold("trainable parameter count changed")

        memory = {
            "allocated_before_backward_mib": round(
                allocated_before / (1024**2), 3
            ),
            "reserved_before_backward_mib": round(
                reserved_before / (1024**2), 3
            ),
            "allocated_after_step_mib": round(
                torch.cuda.memory_allocated() / (1024**2), 3
            ),
            "reserved_after_step_mib": round(
                torch.cuda.memory_reserved() / (1024**2), 3
            ),
            "peak_allocated_mib": round(
                torch.cuda.max_memory_allocated() / (1024**2), 3
            ),
            "peak_reserved_mib": round(
                torch.cuda.max_memory_reserved() / (1024**2), 3
            ),
        }

        trainer.model.zero_grad(set_to_none=True)
        trainer.optimizer.zero_grad(set_to_none=True)

        return finalize_stage0_smoke_receipt(
            runtime_binding_sha256=runtime_binding["binding_sha256"],
            execution_spec_sha256=sha256_file(execution_spec_path),
            weight_digest_before=weight_before,
            weight_digest_after=weight_after,
            optimizer_step_count=1,
            optimizer_created=True,
            gradients_present=True,
            nonzero_gradient_parameter_count=nonzero_gradient_parameter_count,
            microbatches_completed=accumulation_steps,
            losses=losses,
            synthetic_input=True,
            output_artifacts_written=False,
            optimizer_name=optimizer_name,
            cuda_memory=memory,
        )
