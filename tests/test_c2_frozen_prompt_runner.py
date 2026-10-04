import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "artifacts" / "lane-c" / "c2_frozen_prompt_runner.py"
S = importlib.util.spec_from_file_location("c2r", P)
M = importlib.util.module_from_spec(S)
S.loader.exec_module(M)

def test_prompt_pack_and_scoring_contract():
    rows = M.load_jsonl(M.BANK)
    pack = M.build_pack(rows)
    assert len(pack) == 280
    assert len({r["prompt_id"] for r in pack}) == 280
    assert all("expected" not in r and "rule_fingerprint" not in r for r in pack)
    by_episode = {}
    for r in pack:
        by_episode.setdefault(r["episode_id"], set()).add(r["condition"])
    assert all(v == set(M.CONDITIONS) for v in by_episode.values())
    answers = {r["episode_id"]: r["expected"] for r in rows}
    synthetic = [
        {"prompt_id": r["prompt_id"], "prediction": answers[r["episode_id"]]}
        for r in pack if r["condition"] == "support_full"
    ]
    report = M.score(pack, synthetic)
    assert report["by_condition"]["support_full"]["accuracy"] == 1.0
    assert report["by_condition"]["zero_shot"]["accuracy"] == 0.0
    assert report["derived"]["acquisition_gain_vs_zero_shot"] == 1.0
    assert not report["unknown_prompt_ids"]
    assert not report["duplicate_prompt_ids"]
