from __future__ import annotations

import json
from pathlib import Path

import pytest

from successor.experiments.evaluate_v10r2_lane_b import (
    EvalConfigHold,
    load_retention_shadow_manifest,
    pad_completion_example,
    parse_candidate_specs,
    resolve_runtime_binding_path,
)


def test_parse_candidate_specs_supports_base_and_named_adapter() -> None:
    candidates = parse_candidate_specs([
        'base',
        r'lane_b=D:\VERA\models\adapters\lane-b\adapter',
    ])
    assert candidates == [
        ('base', None),
        ('lane_b', Path(r'D:\VERA\models\adapters\lane-b\adapter')),
    ]


def test_parse_candidate_specs_rejects_duplicates() -> None:
    with pytest.raises(EvalConfigHold, match='duplicate'):
        parse_candidate_specs(['base', 'base'])


def test_resolve_runtime_binding_defaults_to_lane_b_binding(tmp_path: Path) -> None:
    expected = tmp_path / 'successor' / 'experiments' / 'V10R2_LANE_B_RUNTIME_BINDING_V2.json'
    assert resolve_runtime_binding_path(tmp_path, None) == expected


def test_resolve_runtime_binding_accepts_explicit_path(tmp_path: Path) -> None:
    explicit = tmp_path / 'custom.json'
    assert resolve_runtime_binding_path(tmp_path, explicit) == explicit


def test_pad_completion_example_right_pads_and_masks() -> None:
    item={'record_id':'r1','input_ids':[10,11,12],'labels':[-100,-100,12],'prompt_tokens':2,'completion_tokens':1}
    got=pad_completion_example(item,pad_token_id=0,fixed_length=8)
    assert got['input_ids']==[10,11,12,0,0,0,0,0]
    assert got['labels']==[-100,-100,12,-100,-100,-100,-100,-100]
    assert got['attention_mask']==[1,1,1,0,0,0,0,0]
    assert got['completion_tokens']==1


def test_pad_completion_example_rejects_overflow() -> None:
    item={'record_id':'r1','input_ids':[1,2,3],'labels':[1,2,3],'prompt_tokens':0,'completion_tokens':3}
    with pytest.raises(EvalConfigHold,match='fixed eval length'):
        pad_completion_example(item,pad_token_id=0,fixed_length=2)


def test_load_retention_shadow_manifest_requires_non_final_policy(tmp_path: Path) -> None:
    value={
      'schema':'V10_RETENTION_SHADOW_BENCHMARK_MANIFEST_V1',
      'status':'PINNED_SHADOW_DIAGNOSTICS_NOT_FINAL_EVIDENCE',
      'sources':{
        'x':{'dataset':'d','revision':'r','file':'f','file_sha256':'a'*64,'rows':1,'license':'MIT'},
      },
      'use_policy':{'final_bank_use':False,'promotion_gate_use':False,'candidate_selection_use':False,'paired_base_candidate_diagnostic':True},
      'claim_ceiling':'SHADOW_ONLY',
    }
    p=tmp_path/'m.json'; p.write_text(json.dumps(value),encoding='utf-8')
    got=load_retention_shadow_manifest(p)
    assert got['status']=='PINNED_SHADOW_DIAGNOSTICS_NOT_FINAL_EVIDENCE'
    assert got['sources']['x']['file_sha256']=='a'*64
    value['use_policy']['final_bank_use']=True
    p.write_text(json.dumps(value),encoding='utf-8')
    with pytest.raises(EvalConfigHold,match='final-bank use'):
        load_retention_shadow_manifest(p)
