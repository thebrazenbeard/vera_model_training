from __future__ import annotations

import argparse
import base64
import hashlib
import json
import pathlib
import subprocess
import sys
from dataclasses import dataclass
from typing import Protocol, Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "lane-c"
PACK = ART / "C2R_RETENTION_PROTOCOL_PACK_V1.jsonl"
SELFTEST = ART / "C2M_MECHANISM_WRAPPER_SELFTEST_V1.json"

def cj(x: Any) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

class Mechanism(Protocol):
    name: str
    def fresh_state(self) -> Any: ...
    def acquire(self, state: Any, prompt: str) -> Any: ...
    def infer(self, state: Any, prompt: str) -> str: ...
    def dump_state(self, state: Any) -> bytes: ...
    def load_state(self, blob: bytes) -> Any: ...

class DeterministicStatelessControl:
    name = "deterministic_stateless_control_v1"
    def fresh_state(self) -> dict[str, int]:
        return {"version": 1}
    def acquire(self, state: dict[str, int], prompt: str) -> dict[str, int]:
        return dict(state)
    def infer(self, state: dict[str, int], prompt: str) -> str:
        return "CTRL_" + hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    def dump_state(self, state: dict[str, int]) -> bytes:
        return cj(state).encode("utf-8")
    def load_state(self, blob: bytes) -> dict[str, int]:
        return json.loads(blob.decode("utf-8"))

@dataclass(frozen=True)
class EpisodePrompts:
    episode_id: str
    acquisition_clean: str
    acquisition_shuffled: str
    retained_after_update: str
    no_acquisition: str

def group_episode_prompts(pack: list[dict[str, Any]]) -> list[EpisodePrompts]:
    grouped: dict[str, dict[str, str]] = {}
    for row in pack:
        grouped.setdefault(row["episode_id"], {})[row["condition"]] = row["prompt"]
    out = []
    needed = {"acquisition_clean", "acquisition_shuffled", "retained_after_update", "no_acquisition"}
    for episode_id, rows in sorted(grouped.items()):
        if not needed <= set(rows):
            raise ValueError(f"missing required conditions for {episode_id}: {sorted(needed - set(rows))}")
        out.append(EpisodePrompts(
            episode_id=episode_id,
            acquisition_clean=rows["acquisition_clean"],
            acquisition_shuffled=rows["acquisition_shuffled"],
            retained_after_update=rows["retained_after_update"],
            no_acquisition=rows["no_acquisition"],
        ))
    return out

def state_digest(mech: Mechanism, state: Any) -> str:
    return sha_bytes(mech.dump_state(state))

def subprocess_reopen(command: list[str], state_blob: bytes, prompt: str) -> str:
    payload = {"state_b64": base64.b64encode(state_blob).decode("ascii"), "prompt": prompt}
    cp = subprocess.run(
        command,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
        cwd=pathlib.Path.home(),
    )
    obj = json.loads(cp.stdout)
    if set(obj) != {"prediction"}:
        raise ValueError("reopen worker returned fields outside prompt-only result contract")
    return str(obj["prediction"])

def run_episode(
    prompts: EpisodePrompts,
    factory: Callable[[], Mechanism],
    reopen_command: list[str] | None = None,
) -> dict[str, Any]:
    fresh = {}
    for arm in ("no_acquisition", "clean_update", "shuffled_update"):
        m = factory()
        s = m.fresh_state()
        fresh[arm] = state_digest(m, s)
    if len(set(fresh.values())) != 1:
        raise AssertionError(f"fresh pre-update state mismatch: {fresh}")

    no_m = factory()
    no_state = no_m.fresh_state()
    no_prediction = no_m.infer(no_state, prompts.no_acquisition)

    clean_m = factory()
    clean_state = clean_m.fresh_state()
    clean_state = clean_m.acquire(clean_state, prompts.acquisition_clean)
    clean_blob = clean_m.dump_state(clean_state)
    retained_prediction = clean_m.infer(clean_state, prompts.retained_after_update)

    shuffled_m = factory()
    shuffled_state = shuffled_m.fresh_state()
    shuffled_state = shuffled_m.acquire(shuffled_state, prompts.acquisition_shuffled)
    shuffled_prediction = shuffled_m.infer(shuffled_state, prompts.retained_after_update)

    same_process_reload_m = factory()
    same_process_reload_state = same_process_reload_m.load_state(clean_blob)
    same_process_reload_prediction = same_process_reload_m.infer(
        same_process_reload_state, prompts.retained_after_update
    )

    process_reopen_prediction = None
    if reopen_command is not None:
        process_reopen_prediction = subprocess_reopen(
            reopen_command, clean_blob, prompts.retained_after_update
        )

    return {
        "episode_id": prompts.episode_id,
        "mechanism": clean_m.name,
        "fresh_state_sha256": fresh,
        "no_acquisition_prediction": no_prediction,
        "retained_after_clean_update_prediction": retained_prediction,
        "retained_after_shuffled_update_prediction": shuffled_prediction,
        "same_process_reload_prediction": same_process_reload_prediction,
        "process_reopen_prediction": process_reopen_prediction,
        "clean_post_state_sha256": sha_bytes(clean_blob),
        "prompt_only_inference_contract": True,
        "metadata_passed_to_inference": False,
        "answer_key_loaded_by_wrapper": False,
        "repo_retrieval_supplied_to_inference": False,
    }

def selftest() -> int:
    episodes = group_episode_prompts(load_jsonl(PACK))[:8]
    reopen = [sys.executable, str(pathlib.Path(__file__).resolve()), "reopen-control"]
    rows = [run_episode(e, DeterministicStatelessControl, reopen) for e in episodes]
    checks = {
        "episodes_executed_8": len(rows) == 8,
        "real_no_acquisition_nonblank": all(r["no_acquisition_prediction"] for r in rows),
        "fresh_state_identical_per_arm": all(len(set(r["fresh_state_sha256"].values())) == 1 for r in rows),
        "same_process_reload_matches": all(
            r["same_process_reload_prediction"] == r["retained_after_clean_update_prediction"] for r in rows
        ),
        "process_reopen_matches": all(
            r["process_reopen_prediction"] == r["retained_after_clean_update_prediction"] for r in rows
        ),
        "prompt_only_boundary": all(r["prompt_only_inference_contract"] for r in rows),
        "no_metadata_to_inference": all(not r["metadata_passed_to_inference"] for r in rows),
        "no_answer_key_loaded": all(not r["answer_key_loaded_by_wrapper"] for r in rows),
        "no_repo_retrieval_supplied": all(not r["repo_retrieval_supplied_to_inference"] for r in rows),
    }
    report = {
        "schema": "C2M_MECHANISM_WRAPPER_SELFTEST_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "episodes": rows,
        "claim_ceiling": "MECHANISM_WRAPPER_PLUMBING_ONLY_NO_MODEL_LEARNING_OR_PERSISTENCE_CLAIM",
        "model_inference_performed": False,
        "gpu_used": False,
        "weights_changed": False,
        "protected_eval_consumed": False,
    }
    SELFTEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "PASS" else 41

def reopen_control() -> int:
    req = json.loads(sys.stdin.read())
    if set(req) != {"state_b64", "prompt"}:
        raise ValueError("reopen worker accepts state_b64 and prompt only")
    mech = DeterministicStatelessControl()
    state = mech.load_state(base64.b64decode(req["state_b64"]))
    print(json.dumps({"prediction": mech.infer(state, str(req["prompt"]))}))
    return 0

def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("selftest")
    sp.add_parser("reopen-control")
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return reopen_control()

if __name__ == "__main__":
    raise SystemExit(main())
