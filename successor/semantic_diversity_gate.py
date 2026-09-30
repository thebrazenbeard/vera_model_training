from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

FAMILIES = [
    "identity_stability",
    "independent_judgment",
    "epistemic_provenance",
    "correction_uptake",
    "relationship_authority",
    "reciprocal_identity_continuity",
    "empathy_affective_response",
    "privacy_boundary",
    "runtime_boundary",
    "negative_transfer_resistance",
]


def read_rows(root: Path) -> list[dict]:
    rows = []
    for family in FAMILIES:
        rows.extend(
            json.loads(line)
            for line in (root / f"{family}.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return rows


def sample_rows(rows: list[dict], per_family: int = 60) -> list[dict]:
    sampled = []
    for family_index, family in enumerate(FAMILIES):
        family_rows = [row for row in rows if row["family"] == family]
        for index in range(min(per_family, len(family_rows))):
            sampled.append(family_rows[(index * 17 + family_index * 7) % len(family_rows)])
    return sampled


def embed_metrics(model: SentenceTransformer, rows: list[dict]) -> dict:
    texts = [row["response"] for row in rows]
    prompts = [row["prompt"] for row in rows]
    response_embeddings = model.encode(
        texts,
        batch_size=64,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    prompt_embeddings = model.encode(
        prompts,
        batch_size=64,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    alignment = np.sum(prompt_embeddings * response_embeddings, axis=1)
    embeddings = response_embeddings
    similarity = embeddings @ embeddings.T
    np.fill_diagonal(similarity, -1.0)
    nearest = similarity.max(axis=1)

    upper = similarity[np.triu_indices_from(similarity, k=1)]
    high_similarity_fraction = float(np.mean(upper >= 0.90)) if len(upper) else 0.0

    return {
        "sample_rows": len(rows),
        "mean_prompt_response_cosine": round(float(np.mean(alignment)), 6),
        "median_prompt_response_cosine": round(float(np.median(alignment)), 6),
        "p10_prompt_response_cosine": round(float(np.quantile(alignment, 0.10)), 6),
        "prompt_response_below_0_25_fraction": round(float(np.mean(alignment < 0.25)), 6),
        "mean_nearest_neighbor_cosine": round(float(np.mean(nearest)), 6),
        "median_nearest_neighbor_cosine": round(float(np.median(nearest)), 6),
        "p90_nearest_neighbor_cosine": round(float(np.quantile(nearest, 0.90)), 6),
        "mean_pairwise_cosine": round(float(np.mean(upper)), 6) if len(upper) else 0.0,
        "high_similarity_pair_fraction_ge_0_90": round(high_similarity_fraction, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v4", type=Path, required=True)
    parser.add_argument("--v41", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = parser.parse_args()

    model = SentenceTransformer(args.model)
    baseline_rows = sample_rows(read_rows(args.v4))
    candidate_rows = sample_rows(read_rows(args.v41))

    result = {
        "schema": "VERA_V4_V4_1_SEMANTIC_DIVERSITY_COMPARISON_V1",
        "embedding_model": args.model,
        "baseline": embed_metrics(model, baseline_rows),
        "candidate": embed_metrics(model, candidate_rows),
        "interpretation": {
            "lower_nearest_neighbor_cosine_means_less_semantic_clustering_in_this_sample": True,
            "embedding_similarity_is_a_model_based_proxy_not_ground_truth": True,
            "same_model_and_sampling_scheme_used_for_both": True,
            "no_model_weights_changed": True,
        },
    }
    result["delta"] = {
        key: round(
            result["candidate"][key] - result["baseline"][key],
            6,
        )
        for key in result["candidate"]
        if isinstance(result["candidate"][key], (int, float))
        and isinstance(result["baseline"][key], (int, float))
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
