from __future__ import annotations
import json
from pathlib import Path
import pytest
from successor.qwen35.measurement_v1.training import (
    TrainingContractError, verify_sft_partitions, build_trainer_config, freeze_training_recipe,
)

def sft(i, family=None, prompt=None):
    return {"record_id":f"sft-{i:05d}","family_id":family or f"family-{i}",
            "prompt":prompt or f"Provide a grounded explanation for mechanism {i}.",
            "response":f"Mechanism {i} is described using verifiable steps.",
            "origin":{"source_id":f"s-{i}","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"f"*64,"privacy":"public","generation_method":"independent_human"}}
def write(path, rows):
    path.write_text("\n".join(json.dumps(x) for x in rows)+"\n",encoding="utf-8")
def valid_files(tmp_path):
    train,validation=tmp_path/"train.jsonl",tmp_path/"validation.jsonl"
    write(train,[sft(i) for i in range(120)])
    write(validation,[sft(200+i) for i in range(40)])
    return train,validation

def test_sft_partition_verified_with_strict_group_separation(tmp_path):
    train,val=valid_files(tmp_path)
    report=verify_sft_partitions(train,val,consumed_prompt_fingerprints=set())
    assert report["train_rows"]==120 and report["validation_rows"]==40
    assert report["status"]=="SFT_PARTITIONS_VERIFIED_NOT_TRAINED"
    assert len(report["train_sha256"])==64 and len(report["validation_sha256"])==64

def test_rejects_train_validation_family_or_answer_leak(tmp_path):
    train,val=valid_files(tmp_path)
    rows=[sft(200+i) for i in range(40)]
    rows[3]["family_id"]="family-0"
    write(val,rows)
    with pytest.raises(TrainingContractError,match="family"):
        verify_sft_partitions(train,val,consumed_prompt_fingerprints=set())

def test_consumed_final_text_cannot_be_sft_training_or_validation(tmp_path):
    train,val=valid_files(tmp_path)
    with pytest.raises(TrainingContractError,match="consumed"):
        verify_sft_partitions(train,val,consumed_prompt_fingerprints={"provide a grounded explanation for mechanism 204"})

def test_training_spec_has_real_eval_and_best_checkpoint_selection():
    spec=build_trainer_config(batch_size=1,gradient_accumulation_steps=8,epochs=2,eval_steps=12,learning_rate=0.0001)
    assert spec["eval_strategy"]=="steps" and spec["eval_steps"]==12
    assert spec["save_strategy"]=="steps" and spec["save_steps"]==12
    assert spec["load_best_model_at_end"] is True
    assert spec["metric_for_best_model"]=="eval_loss"
    assert spec["greater_is_better"] is False
    assert spec["completion_only_loss"] is True
    assert spec["packing"] is False
    assert spec["save_total_limit"]==2
    assert spec["early_stopping_patience"]==3

def test_freeze_recipe_refuses_overwrite_and_binds_frozen_data(tmp_path):
    train,val=valid_files(tmp_path)
    out=tmp_path/"recipe.json"
    manifest=freeze_training_recipe(train,val,out,
        base_revision="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8",
        source_commit="1"*40,consumed_prompt_fingerprints=set())
    assert out.is_file()
    assert manifest["training"]["eval_strategy"]=="steps"
    assert manifest["validation_rows"]==40
    with pytest.raises(TrainingContractError,match="exists"):
        freeze_training_recipe(train,val,out,
            base_revision="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8",
            source_commit="1"*40,consumed_prompt_fingerprints=set())

def test_sft_partition_cannot_reuse_v4_final_even_when_passed_empty_blocklist(tmp_path):
    root=Path(__file__).resolve().parents[1]
    old=json.loads((root/"successor/qwen35/qualification/final_holdout_v4.jsonl").read_text(encoding="utf-8").splitlines()[0])
    train,val=valid_files(tmp_path)
    rows=[sft(i) for i in range(120)]
    rows[1]["prompt"]=old["prompt"]
    write(train,rows)
    with pytest.raises(TrainingContractError,match="consumed"):
        verify_sft_partitions(train,val,consumed_prompt_fingerprints=set())


def test_same_upstream_source_id_cannot_be_in_train_and_validation(tmp_path):
    train, val = valid_files(tmp_path)
    rows = [sft(200+i) for i in range(40)]
    rows[3]["origin"]["source_id"] = "s-0"  # other family, same source document
    write(val, rows)
    with pytest.raises(TrainingContractError, match="source"):
        verify_sft_partitions(train, val, consumed_prompt_fingerprints=set())
