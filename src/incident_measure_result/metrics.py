from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from .io import read_jsonl
from .validation import validate_predictions


def _dcg(grades: list[int]) -> float:
    return sum((2**grade - 1) / math.log2(index + 2) for index, grade in enumerate(grades))


def _ndcg(ranked_grades: list[int], ideal_grades: list[int], k: int) -> float | None:
    ideal = _dcg(sorted(ideal_grades, reverse=True)[:k])
    if ideal == 0:
        return None
    return _dcg(ranked_grades[:k]) / ideal


def evaluate_predictions(dataset_dir: str | Path, predictions_path: str | Path, k_values: tuple[int, ...] = (1, 3, 5)) -> dict[str, Any]:
    validate_predictions(dataset_dir, predictions_path)
    predictions = read_jsonl(predictions_path)
    annotations = read_jsonl(Path(dataset_dir) / "relevance_annotations.jsonl")
    grades = {(str(row["query_id"]), str(row["measure_id"])): int(row["relevance_grade"]) for row in annotations}
    grades_by_query: dict[str, list[int]] = defaultdict(list)
    for row in annotations:
        grades_by_query[str(row["query_id"])].append(int(row["relevance_grade"]))

    method = str(predictions[0].get("method", "unknown")) if predictions else "unknown"
    results: dict[str, Any] = {"method": method, "query_count": len(predictions), "metrics": {}}
    for k in k_values:
        graded_scores: list[float] = []
        usable_recall_scores: list[float] = []
        strict_recall_scores: list[float] = []
        usable_reciprocal_ranks: list[float] = []
        for prediction in predictions:
            query_id = str(prediction["query_id"])
            top = prediction.get("top_k", [])[:k]
            ranked_grades = [grades.get((query_id, str(item.get("measure_id"))), 0) for item in top]
            ideal_grades = grades_by_query.get(query_id, [])
            graded_score = _ndcg(ranked_grades, ideal_grades, k)
            if graded_score is not None:
                graded_scores.append(graded_score)

            usable_total = sum(1 for grade in ideal_grades if grade >= 2)
            strict_total = sum(1 for grade in ideal_grades if grade == 3)
            usable_hits = sum(1 for grade in ranked_grades if grade >= 2)
            strict_hits = sum(1 for grade in ranked_grades if grade == 3)
            if usable_total:
                usable_recall_scores.append(usable_hits / usable_total)
                rr = 0.0
                for index, grade in enumerate(ranked_grades, start=1):
                    if grade >= 2:
                        rr = 1 / index
                        break
                usable_reciprocal_ranks.append(rr)
            if strict_total:
                strict_recall_scores.append(strict_hits / strict_total)

        results["metrics"][f"graded_ndcg@{k}"] = round(sum(graded_scores) / max(len(graded_scores), 1), 6)
        results["metrics"][f"usable_recall@{k}"] = round(sum(usable_recall_scores) / max(len(usable_recall_scores), 1), 6)
        results["metrics"][f"strict_recall@{k}"] = round(sum(strict_recall_scores) / max(len(strict_recall_scores), 1), 6)
        results["metrics"][f"usable_mrr@{k}"] = round(sum(usable_reciprocal_ranks) / max(len(usable_reciprocal_ranks), 1), 6)
        results["metrics"][f"graded_query_count@{k}"] = len(graded_scores)
        results["metrics"][f"usable_query_count@{k}"] = len(usable_recall_scores)
        results["metrics"][f"strict_query_count@{k}"] = len(strict_recall_scores)
    return results
