import json
from pathlib import Path
import pytest
from successor.qwen35.measurement_v1.training import freeze_training_recipe
from successor.qwen35.train_behavior_v5 import TrainingEntrypointError, read_frozen_recipe, make_trainer

def data(i):
    return {"record_id":f"sft-{i}","family_id":f"group-{i}",
            "prompt":f"Describe safe evidence check {i}.","response":f"Evidence check {i} requires readback.",
            "origin":{"source_id":f"source-{i}","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"e"*64,"privacy":"public","generation_method":"independent_human"}}
def paths(tmp_path):
    train=tmp_path/"train.jsonl";val=tmp_path/"val.jsonl"
    train.write_text("\n".join(json.dumps(data(i)) for i in range(120))+"\n",encoding="utf-8")
    val.write_text("\n".join(json.dumps(data(500+i)) for i in range(40))+"\n",encoding="utf-8")
    recipe=tmp_path/"frozen.json"
    freeze_training_recipe(train,val,recipe,base_revision="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8",source_commit="a"*40,consumed_prompt_fingerprints=set())
    return train,val,recipe

def test_entrypoint_reads_frozen_nonfinal_recipe(tmp_path):
    train,val,recipe=paths(tmp_path)
    spec=read_frozen_recipe(recipe,consumed_prompt_fingerprints=set())
    assert spec["validation_rows"]==40
    assert spec["training"]["eval_strategy"]=="steps"
    assert spec["checkpoint_status"].startswith("RECIPE_FROZEN")

def test_entrypoint_rejects_source_change_after_freeze(tmp_path):
    train,val,recipe=paths(tmp_path)
    with val.open("a",encoding="utf-8") as f:f.write(json.dumps(data(5555))+"\n")
    with pytest.raises(TrainingEntrypointError,match="changed"):
        read_frozen_recipe(recipe,consumed_prompt_fingerprints=set())

def test_trainer_adapter_receives_validation_dataset():
    calls={}
    def fake_factory(**kwargs):
        calls.update(kwargs)
        return {"constructed":True}
    result=make_trainer(fake_factory,model="model",training_args="args",tokenizer="tokenizer",
                        lora_config="lora",train_dataset=[1,2],validation_dataset=[3,4])
    assert result["constructed"]
    assert calls["train_dataset"]==[1,2] and calls["eval_dataset"]==[3,4]
    with pytest.raises(TrainingEntrypointError,match="validation"):
        make_trainer(fake_factory,model="model",training_args="args",tokenizer="tokenizer",
                     lora_config="lora",train_dataset=[1],validation_dataset=[])
