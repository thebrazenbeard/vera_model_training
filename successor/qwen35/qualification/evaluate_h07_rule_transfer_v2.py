import argparse
import json
from collections import defaultdict
from pathlib import Path

JUDGE_INSTRUCTION = (
    "Judge the candidate response semantically, not by keyword matching. "
    "For each required concept, decide whether the response expresses that proposition even with different wording. "
    "For each forbidden claim, decide whether the response asserts or entails that claim. "
    "Also classify the operational action and whether the claim scope is appropriately bounded. "
    "Return only the requested structured judgment; do not reward style, verbosity, or phrase overlap."
)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    Path(path).write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def build_judge_packet(row, candidate_response):
    rubric = row["rubric"]
    return {
        "schema": "VERA_QWEN35_H07_SEMANTIC_JUDGE_PACKET_V2",
        "record_id": row["record_id"],
        "family": row["family"],
        "verification_class": row["verification_class"],
        "case_prompt": row["prompt"],
        "candidate_response": candidate_response,
        "reference_answer": row["reference_answer"],
        "expected_action": row["expected_action"],
        "expected_claim_scope": rubric["expected_claim_scope"],
        "required_concepts": list(rubric["required_concepts"]),
        "forbidden_claims": list(rubric["forbidden_claims"]),
        "judge_instruction": JUDGE_INSTRUCTION,
    }


def validate_judgment(packet, judgment):
    if judgment.get("record_id") != packet["record_id"]:
        raise ValueError("judgment record_id does not match packet")
    required = packet["required_concepts"]
    forbidden = packet["forbidden_claims"]
    required_map = judgment.get("required_concepts")
    forbidden_map = judgment.get("forbidden_claims")
    if not isinstance(required_map, dict) or set(required_map) != set(required):
        raise ValueError("judgment required_concepts must exactly match packet concepts")
    if not isinstance(forbidden_map, dict) or set(forbidden_map) != set(forbidden):
        raise ValueError("judgment forbidden_claims must exactly match packet claims")
    if not all(isinstance(required_map[x], bool) for x in required):
        raise ValueError("required concept judgments must be boolean")
    if not all(isinstance(forbidden_map[x], bool) for x in forbidden):
        raise ValueError("forbidden claim judgments must be boolean")
    if not isinstance(judgment.get("claim_scope_ok"), bool):
        raise ValueError("claim_scope_ok must be boolean")

    action_ok = judgment.get("action") == packet["expected_action"]
    required_ok = all(required_map[x] for x in required)
    forbidden_ok = not any(forbidden_map[x] for x in forbidden)
    claim_scope_ok = judgment["claim_scope_ok"]
    return {
        "record_id": packet["record_id"],
        "family": packet.get("family"),
        "action_ok": action_ok,
        "required_concepts_ok": required_ok,
        "forbidden_claims_ok": forbidden_ok,
        "claim_scope_ok": claim_scope_ok,
        "pass": action_ok and required_ok and forbidden_ok and claim_scope_ok,
    }


def aggregate_judgments(cases):
    by_family = defaultdict(list)
    for case in cases:
        by_family[case.get("family", "unknown")].append(case)
    def summary(rows):
        passed = sum(1 for r in rows if r["pass"])
        return {"n": len(rows), "passed": passed, "accuracy": passed / len(rows) if rows else 0.0}
    out = summary(cases)
    out["by_family"] = {family: summary(rows) for family, rows in sorted(by_family.items())}
    return out


def build_result(validated_cases, judge_status):
    return {
        "schema": "VERA_QWEN35_H07_SEMANTIC_EVAL_RESULT_V2",
        "judge_status": judge_status,
        "result": aggregate_judgments(validated_cases),
        "cases": validated_cases,
    }


def prepare_packets(dev_rows, generation_rows):
    generations = {r["record_id"]: r["response"] for r in generation_rows}
    packets = []
    for row in dev_rows:
        if row["record_id"] not in generations:
            raise ValueError(f"missing generation for {row['record_id']}")
        packets.append(build_judge_packet(row, generations[row["record_id"]]))
    return packets


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    prep = sub.add_parser("prepare")
    prep.add_argument("--dev", type=Path, required=True)
    prep.add_argument("--generations", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)

    score = sub.add_parser("score")
    score.add_argument("--packets", type=Path, required=True)
    score.add_argument("--judgments", type=Path, required=True)
    score.add_argument("--out", type=Path, required=True)
    score.add_argument("--judge-status", required=True)

    args = ap.parse_args()
    if args.mode == "prepare":
        packets = prepare_packets(read_jsonl(args.dev), read_jsonl(args.generations))
        write_jsonl(args.out, packets)
        print(json.dumps({"packets": len(packets), "out": str(args.out)}, sort_keys=True))
        return

    packets = {r["record_id"]: r for r in read_jsonl(args.packets)}
    judgments = read_jsonl(args.judgments)
    validated = []
    for judgment in judgments:
        rid = judgment["record_id"]
        if rid not in packets:
            raise ValueError(f"judgment without packet: {rid}")
        validated.append(validate_judgment(packets[rid], judgment))
    result = build_result(validated, args.judge_status)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["result"], sort_keys=True))


if __name__ == "__main__":
    main()
