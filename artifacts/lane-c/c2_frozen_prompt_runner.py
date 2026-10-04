from __future__ import annotations
import argparse
import collections
import hashlib
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "lane-c"
BANK = ART / "C2_NOVEL_TASK_OPEN_BANK_V1.jsonl"
PROMPTS = ART / "C2_NOVEL_TASK_PROMPT_PACK_V1.jsonl"
CONTRACT = ART / "C2_NOVEL_TASK_SCORING_CONTRACT_V1.json"
SELFTEST = ART / "C2_NOVEL_TASK_FROZEN_RUNNER_SELFTEST_V1.json"

CONDITIONS = (
    "zero_shot",
    "support_full",
    "shuffled_labels",
    "irrelevant_memory",
    "familiar_lookalike",
)

MISLEADING_PRIOR = {
    "nonce_permute": "This is ordinary alphabetical sorting. Follow that familiar rule.",
    "mini_grammar": "This is ordinary English subject-verb-object ordering. Follow that familiar rule.",
    "tool_contract": "This is a conventional JSON API. Return a normal JSON object.",
    "state_machine": "Assume x and y simply toggle between two states.",
    "contradictory_prior": "Use the ordinary meanings of the source symbols rather than a learned remapping.",
    "string_pipeline": "This is a plain string-reversal task. Only reverse the query.",
    "goal_inference": "Choose the point closest to the origin.",
}

IRRELEVANT_MEMORY = (
    "Unrelated memory: cedar trees are evergreen; 17 is prime; "
    "a triangle has three sides. None of this is task authority."
)

def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_jsonl(path: pathlib.Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def render_support(support):
    return "\n".join(f"Example {i+1}: {x['input']} -> {x['output']}" for i, x in enumerate(support))

def shuffled_support(row):
    support = [dict(x) for x in row["support"]]
    outputs = [x["output"] for x in support]
    rng = random.Random(row["seed"] ^ 0xC2)
    rng.shuffle(outputs)
    if len(outputs) > 1 and all(outputs[i] == support[i]["output"] for i in range(len(outputs))):
        outputs = outputs[1:] + outputs[:1]
    return [{"input": x["input"], "output": y} for x, y in zip(support, outputs)]

def build_prompt(row, condition):
    header = (
        "Infer the task from the information provided. "
        "Return only the answer for the query; do not explain your reasoning."
    )
    pieces = [header]
    if condition == "zero_shot":
        pieces.append("No demonstrations are provided.")
    elif condition == "support_full":
        pieces.append(render_support(row["support"]))
    elif condition == "shuffled_labels":
        pieces.append(render_support(shuffled_support(row)))
    elif condition == "irrelevant_memory":
        pieces.append(IRRELEVANT_MEMORY)
        pieces.append(render_support(row["support"]))
    elif condition == "familiar_lookalike":
        pieces.append("Potential prior cue: " + MISLEADING_PRIOR[row["family_id"]])
        pieces.append("Use the demonstrations as the task evidence.")
        pieces.append(render_support(row["support"]))
    else:
        raise ValueError(condition)
    pieces.append("Query: " + row["query"])
    return "\n\n".join(pieces)

def build_pack(rows):
    pack = []
    for row in rows:
        for condition in CONDITIONS:
            prompt = build_prompt(row, condition)
            pack.append({
                "prompt_id": f"{row['episode_id']}::{condition}",
                "episode_id": row["episode_id"],
                "family_id": row["family_id"],
                "split": row["split"],
                "condition": condition,
                "seed": row["seed"],
                "prompt": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            })
    return pack

def score(pack, predictions):
    by_id = {r["prompt_id"]: r for r in pack}
    answers = {r["episode_id"]: str(r["expected"]) for r in load_jsonl(BANK)}
    preds = {}
    duplicates = []
    unknown = []
    for row in predictions:
        pid = row.get("prompt_id")
        if pid not in by_id:
            unknown.append(pid)
            continue
        if pid in preds:
            duplicates.append(pid)
        preds[pid] = str(row.get("prediction", "")).strip()
    cells = collections.defaultdict(lambda: [0, 0, 0])
    for row in pack:
        key = (row["split"], row["family_id"], row["condition"])
        pred = preds.get(row["prompt_id"])
        cells[key][1] += 1
        if pred is not None:
            cells[key][2] += 1
            if " ".join(pred.split()) == " ".join(answers[row["episode_id"]].split()):
                cells[key][0] += 1
    metrics = []
    for (split, family, condition), (correct, total, covered) in sorted(cells.items()):
        metrics.append({
            "split": split,
            "family_id": family,
            "condition": condition,
            "correct": correct,
            "total": total,
            "covered": covered,
            "accuracy": correct / total if total else 0.0,
            "coverage": covered / total if total else 0.0,
        })
    aggregate = collections.defaultdict(lambda: [0, 0, 0])
    for m in metrics:
        a = aggregate[m["condition"]]
        a[0] += m["correct"]; a[1] += m["total"]; a[2] += m["covered"]
    by_condition = {
        c: {
            "correct": v[0], "total": v[1], "covered": v[2],
            "accuracy": v[0]/v[1] if v[1] else 0.0,
            "coverage": v[2]/v[1] if v[1] else 0.0,
        }
        for c, v in sorted(aggregate.items())
    }
    sf = by_condition["support_full"]["accuracy"]
    derived = {
        "acquisition_gain_vs_zero_shot": sf - by_condition["zero_shot"]["accuracy"],
        "label_integrity_gain": sf - by_condition["shuffled_labels"]["accuracy"],
        "irrelevant_memory_delta": by_condition["irrelevant_memory"]["accuracy"] - sf,
        "familiar_prior_resistance_delta": by_condition["familiar_lookalike"]["accuracy"] - sf,
    }
    return {
        "schema": "C2_NOVEL_TASK_SCORE_REPORT_V1",
        "prompt_pack_sha256": sha256_bytes(PROMPTS.read_bytes()) if PROMPTS.exists() else None,
        "predictions_rows": len(predictions),
        "unknown_prompt_ids": unknown,
        "duplicate_prompt_ids": duplicates,
        "by_condition": by_condition,
        "by_family_condition": metrics,
        "derived": derived,
    }

def write_jsonl(path, rows):
    data = "".join(canonical_json(r) + "\n" for r in rows).encode("utf-8")
    path.write_bytes(data)
    return sha256_bytes(data)

def build():
    rows = load_jsonl(BANK)
    pack = build_pack(rows)
    pack_sha = write_jsonl(PROMPTS, pack)
    contract = {
        "schema": "C2_NOVEL_TASK_SCORING_CONTRACT_V1",
        "bank_sha256": sha256_bytes(BANK.read_bytes()),
        "prompt_pack_sha256": pack_sha,
        "episodes": len(rows),
        "conditions": list(CONDITIONS),
        "prompts": len(pack),
        "prediction_schema": {"prompt_id": "string", "prediction": "string"},
        "answer_key_in_prompt_pack": False,
        "score_rules": {
            "answer_match": "whitespace-normalized exact match",
            "missing_prediction": "incorrect and uncovered",
            "duplicate_prediction": "reported; last value scored",
            "unknown_prompt_id": "reported and excluded",
            "required_reporting": ["accuracy", "coverage", "family", "condition"],
        },
        "derived_metrics": {
            "acquisition_gain_vs_zero_shot": "support_full - zero_shot",
            "label_integrity_gain": "support_full - shuffled_labels",
            "irrelevant_memory_delta": "irrelevant_memory - support_full",
            "familiar_prior_resistance_delta": "familiar_lookalike - support_full",
        },
        "interpretation_guardrails": [
            "High support_full accuracy alone does not establish novel-task learning.",
            "A genuine acquisition signal requires gain over zero_shot and sensitivity to corrupted demonstrations.",
            "A familiar-lookalike cue must not improve performance by replacing demonstration evidence with pretrained priors.",
            "Open-bank performance is prototype evidence only and is not canonical qualification.",
        ],
        "model_inference_performed": False,
        "gpu_used": False,
        "weights_changed": False,
        "protected_eval_consumed": False,
    }
    CONTRACT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    answers = {r["episode_id"]: r["expected"] for r in rows}
    oracle = [{"prompt_id": r["prompt_id"], "prediction": answers[r["episode_id"]]} for r in pack]
    blank = []
    synthetic = [
        {"prompt_id": r["prompt_id"], "prediction": answers[r["episode_id"]]}
        for r in pack if r["condition"] == "support_full"
    ]
    o = score(pack, oracle); b = score(pack, blank); s = score(pack, synthetic)
    checks = {
        "prompt_rows_280": len(pack) == len(rows) * len(CONDITIONS) == 280,
        "prompt_ids_unique": len({r["prompt_id"] for r in pack}) == len(pack),
        "prompt_pack_answer_leak_absent": all("expected" not in r and "rule_fingerprint" not in r for r in pack),
        "oracle_all_conditions_1": all(v["accuracy"] == 1.0 for v in o["by_condition"].values()),
        "blank_all_conditions_0": all(v["accuracy"] == 0.0 for v in b["by_condition"].values()),
        "synthetic_support_full_1": s["by_condition"]["support_full"]["accuracy"] == 1.0,
        "synthetic_zero_shot_0": s["by_condition"]["zero_shot"]["accuracy"] == 0.0,
        "synthetic_acquisition_gain_1": s["derived"]["acquisition_gain_vs_zero_shot"] == 1.0,
        "no_model_inference": True,
    }
    report = {
        "schema": "C2_NOVEL_TASK_FROZEN_RUNNER_SELFTEST_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "prompt_pack_sha256": pack_sha,
        "contract_sha256": sha256_bytes(CONTRACT.read_bytes()),
        "oracle_accuracy": {k:v["accuracy"] for k,v in o["by_condition"].items()},
        "blank_accuracy": {k:v["accuracy"] for k,v in b["by_condition"].items()},
        "synthetic_derived": s["derived"],
    }
    SELFTEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "PASS" else 41

def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sc = sub.add_parser("score")
    sc.add_argument("predictions")
    sc.add_argument("--out")
    args = ap.parse_args(argv)
    if args.cmd == "build":
        return build()
    pack = load_jsonl(PROMPTS)
    predictions = load_jsonl(pathlib.Path(args.predictions))
    report = score(pack, predictions)
    payload = json.dumps(report, indent=2) + "\n"
    if args.out:
        pathlib.Path(args.out).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0

if __name__ == "__main__":
    sys.exit(main())
