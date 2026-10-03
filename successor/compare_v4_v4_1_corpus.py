from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

from successor import build_v4_custom_corpus as v4

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")
FAMILIES = tuple(v4.CORE_FAMILIES)


def read_rows(root: Path) -> list[dict]:
    rows = []
    for family in FAMILIES:
        path = root / f"{family}.jsonl"
        rows.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return rows


def ngram_counts(tokens: list[str], n: int) -> Counter[str]:
    return Counter(
        " ".join(tokens[index:index + n])
        for index in range(len(tokens) - n + 1)
    )


def distinct(counter: Counter[str]) -> float:
    total = sum(counter.values())
    return round(len(counter) / total, 6) if total else 0.0


def top_mass(counter: Counter[str], n: int) -> float:
    total = sum(counter.values())
    return round(sum(value for _, value in counter.most_common(n)) / total, 6) if total else 0.0


def prefix_stats(rows: list[dict]) -> dict:
    prefixes = Counter(
        " ".join((row["response"].split())[:6]).lower()
        for row in rows
    )
    return {
        "unique_six_token_prefixes": len(prefixes),
        "max_prefix_reuse": max(prefixes.values()) if prefixes else 0,
        "prefixes_used_by_more_than_1pct": sum(
            value > len(rows) * 0.01 for value in prefixes.values()
        ),
    }


def tfidf_nearest_neighbor_cosine(rows: list[dict], sample_size: int = 300, neighbors: int = 20) -> float:
    if not rows:
        return 0.0

    documents = [
        Counter(token.lower() for token in TOKEN_RE.findall(row["response"]))
        for row in rows
    ]
    df = Counter()
    for doc in documents:
        df.update(doc.keys())
    total_docs = len(documents)
    idf = {
        token: math.log((1 + total_docs) / (1 + frequency)) + 1.0
        for token, frequency in df.items()
    }

    def cosine(left: Counter[str], right: Counter[str]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(
            (count * idf[token]) * (right.get(token, 0) * idf[token])
            for token, count in left.items()
            if token in right
        )
        left_norm = math.sqrt(sum((count * idf[token]) ** 2 for token, count in left.items()))
        right_norm = math.sqrt(sum((count * idf[token]) ** 2 for token, count in right.items()))
        return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0

    sample_indices = [(index * 7919) % len(rows) for index in range(min(sample_size, len(rows)))]
    scores = []
    for position, index in enumerate(sample_indices):
        candidates = []
        for offset in range(1, neighbors + 1):
            other = sample_indices[(position * 37 + offset * 101) % len(sample_indices)]
            if other != index:
                candidates.append(cosine(documents[index], documents[other]))
        if candidates:
            scores.append(max(candidates))
    return round(sum(scores) / len(scores), 6) if scores else 0.0


def sampled_jaccard(rows: list[dict], sample_size: int = 400, pairs_per_row: int = 12) -> float:
    if not rows:
        return 0.0
    stride = 7919
    sample = [rows[(index * stride) % len(rows)] for index in range(min(sample_size, len(rows)))]
    grams = [
        set(
            " ".join(tokens[i:i + 4])
            for i in range(len(tokens) - 3)
        )
        for tokens in [
            [token.lower() for token in TOKEN_RE.findall(row["response"])]
            for row in sample
        ]
    ]
    scores = []
    for i, left in enumerate(grams):
        for offset in range(1, pairs_per_row + 1):
            right = grams[(i * 37 + offset * 101) % len(grams)]
            if left or right:
                scores.append(len(left & right) / max(1, len(left | right)))
    return round(sum(scores) / len(scores), 6) if scores else 0.0


def measure(root: Path) -> dict:
    rows = read_rows(root)
    texts = [row["prompt"] + " " + row["response"] for row in rows]
    tokens = [
        token.lower()
        for text in texts
        for token in TOKEN_RE.findall(text)
    ]
    counts = Counter(tokens)
    n2 = ngram_counts(tokens, 2)
    n3 = ngram_counts(tokens, 3)
    n4 = ngram_counts(tokens, 4)
    raw = "\n".join(row["response"] for row in rows).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)

    sentence_counts = [
        len(re.findall(r"[^.!?]+[.!?]+", row["response"]))
        for row in rows
    ]

    return {
        "rows": len(rows),
        "tokens": len(tokens),
        "unique_tokens": len(counts),
        "ttr": round(len(counts) / len(tokens), 6),
        "hapax_tokens": sum(value == 1 for value in counts.values()),
        "distinct_2": distinct(ngram_counts(tokens, 2)),
        "distinct_3": distinct(ngram_counts(tokens, 3)),
        "distinct_4": distinct(ngram_counts(tokens, 4)),
        "top100_token_mass": top_mass(counts, 100),
        "top100_bigram_mass": top_mass(n2, 100),
        "top100_trigram_mass": top_mass(n3, 100),
        "response_gzip_ratio": round(len(compressed) / max(1, len(raw)), 6),
        "response_prefix": prefix_stats(rows),
        "sampled_4gram_jaccard": sampled_jaccard(rows),
        "tfidf_nearest_neighbor_cosine": tfidf_nearest_neighbor_cosine(rows),
        "sentence_count": {
            "min": min(sentence_counts),
            "max": max(sentence_counts),
            "mean": round(sum(sentence_counts) / len(sentence_counts), 4),
        },
        "sha256_response_stream": hashlib.sha256(raw).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v4", type=Path, required=True)
    parser.add_argument("--v41", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    baseline = measure(args.v4)
    candidate = measure(args.v41)
    comparison = {
        "schema": "VERA_V4_V4_1_DIVERSITY_COMPARISON_V1",
        "baseline": baseline,
        "candidate": candidate,
        "delta": {
            key: round(candidate[key] - baseline[key], 6)
            for key in (
                "unique_tokens",
                "ttr",
                "distinct_2",
                "distinct_3",
                "distinct_4",
                "top100_token_mass",
                "top100_bigram_mass",
                "top100_trigram_mass",
                "response_gzip_ratio",
                "sampled_4gram_jaccard",
                "tfidf_nearest_neighbor_cosine",
            )
            if isinstance(candidate.get(key), (int, float))
            and isinstance(baseline.get(key), (int, float))
        },
        "interpretation": {
            "lexical_and_ngram_metrics_are_structural": True,
            "sampled_4gram_jaccard_is_not_semantic_similarity": True,
            "gzip_ratio_is_compression_not_a_quality_score": True,
            "no_model_weights_were_changed": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(comparison, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
