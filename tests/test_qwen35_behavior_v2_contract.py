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
    assert spec["sft"]["total_rows"]==736
    assert spec["preference"]["total_rows"]==616
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
    for name in ("generate_behavior_corpus_v2.py","curate_behavior_corpus_v2.py","generate_repo_engineering_v1.py","curate_repo_engineering_v1.py","build_behavior_corpus_v2.py","train_behavior_v2.py"):
        ast.parse((Q/name).read_text(),filename=name)


def test_builder_uses_named_smoltalk_splits_and_compact_export():
    b=(Q/"build_behavior_corpus_v2.py").read_text()
    assert 'load_dataset(SMOL_REPO,"SFT",split=split' in b
    assert 'split="train"' not in b[b.index("def select_smoltalk"):b.index("def select_general_prefs")]
    t=(Q/"train_behavior_v2.py").read_text()
    assert 'target_modules="all-linear"' in t
    assert 'param.data = param.data.to(torch.bfloat16)' in t
    assert 'tok.save_pretrained(adapter)' not in t
    assert 'chunk=65536' in t


def test_repo_engineering_lane_contract():
    spec=json.loads((Q/"HISTORY_BEHAVIOR_CURRICULUM_V2.json").read_text())
    lane=spec["repo_engineering"]
    assert lane["source_card_count"]==16
    assert lane["candidate_rows"]==144
    assert lane["accepted_rows"]==96
    assert lane["sft_rows"]==64
    assert lane["preference_rows"]==96
    cards=json.loads((Q/"repo_engineering_source_cards_v1.json").read_text())
    assert len(cards["cards"])==16
    repos={x["source_repo"] for x in cards["cards"]}
    assert "thebrazenbeard/roots" in repos
    assert "thebrazenbeard/sql-connectome" in repos
    assert all(len(x["source_commit"])==40 for x in cards["cards"])
    b=(Q/"build_behavior_corpus_v2.py").read_text()
    assert '--repo-targeted-url' in b
    assert 'repo_engineering_v1' in b
