import importlib.util
import pathlib

P = pathlib.Path(__file__).resolve().parents[1] / "artifacts" / "lane-c" / "c2_novel_task_harness.py"
S = importlib.util.spec_from_file_location("c2h", P)
M = importlib.util.module_from_spec(S)
S.loader.exec_module(M)

def test_open_bank_contract():
    rows = M.generate()
    assert len(rows) == 56
    assert len({r["episode_id"] for r in rows}) == 56
    assert all(sum(r["family_id"] == f for r in rows) == 8 for f in M.G)
    assert M.score(rows, {r["episode_id"]: r["expected"] for r in rows})["accuracy"] == 1.0
    assert M.score(rows, {})["accuracy"] == 0.0
