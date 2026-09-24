from __future__ import annotations

import ast
import json
import pathlib
import re

ROOT=pathlib.Path(__file__).resolve().parents[1]
Q=ROOT/"successor"/"qwen35"

def test_v2_spec_counts():
    spec=json.loads((Q/"HISTORY_BEHAVIOR_CURRICULUM_V2.json").read_text())
    assert spec["output_identity"]=="Vera-Qwen3.5-4B-Behavior-V1"
    assert spec["targeted_generation"]["accepted_target"]==240
    assert sum(x["quota"] for x in spec["dimensions"].values())==240
    assert spec["sft"]["total_rows"]==672
    assert spec["preference"]["total_rows"]==520
    assert spec["training"]["target_modules"]=="all-linear"

def test_v1_redundancy_is_preserved_as_baseline_not_v2():
    rows=[json.loads(x) for x in (Q/"corpus"/"history_behavior_targeted_v1.jsonl").read_text().splitlines() if x.strip()]
    assert len(rows)==480
    assert len({(r["dimension"],r["chosen"],r["rejected"]) for r in rows})==40

def test_generator_and_curator_use_frozen_models():
    g=(Q/"generate_behavior_corpus_v2.py").read_text()
    c=(Q/"curate_behavior_corpus_v2.py").read_text()
    assert 'Qwen/Qwen3-8B' in g
    assert 'b968826d9c46dd6066d109eabc6255188de91218' in g
    assert 'Qwen/Qwen2.5-14B-Instruct' in c
    assert 'cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8' in c

def test_trainer_is_text_only_all_linear_and_frozen():
    t=(Q/"train_behavior_v2.py").read_text()
    assert 'Qwen3_5ForCausalLM' in t
    assert 'target_modules="all-linear"' in t
    assert 'types.count("linear_attention")!=24' in t
    assert 'types.count("full_attention")!=8' in t
    assert 'vision target detected' in t
    assert 'd61dd146c8fd44c9a49cdb7f59f34e17b61902d8' in t

def test_python_sources_parse():
    for name in ("generate_behavior_corpus_v2.py","curate_behavior_corpus_v2.py","build_behavior_corpus_v2.py","train_behavior_v2.py"):
        ast.parse((Q/name).read_text(),filename=name)
