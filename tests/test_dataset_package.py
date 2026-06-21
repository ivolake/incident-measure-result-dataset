from pathlib import Path

from incident_measure_result.metrics import evaluate_predictions
from incident_measure_result.rankers import rank_bm25
from incident_measure_result.validation import validate_dataset

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "external_gold_seed_8_8_35"
ANNOTATIONS = ROOT / "data" / "annotations" / "subagent_annotations"


def test_dataset_validation_counts() -> None:
    report = validate_dataset(DATASET, ANNOTATIONS)
    assert report["status"] == "passed"
    assert report["query_count"] == 30
    assert report["measure_count"] == 25
    assert report["annotation_count"] == 600
    assert report["grade_counts"] == {"0": 428, "1": 82, "2": 88, "3": 2}
    assert len(report["annotator_files"]) == 5


def test_bm25_smoke_and_metrics(tmp_path: Path) -> None:
    predictions = rank_bm25(DATASET, top_k=5)
    assert len(predictions) == 30
    assert all(len(row["top_k"]) == 5 for row in predictions)
    prediction_path = tmp_path / "bm25.jsonl"
    with prediction_path.open("w", encoding="utf-8") as handle:
        for row in predictions:
            import json

            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = evaluate_predictions(DATASET, prediction_path)
    assert report["query_count"] == 30
    assert "graded_ndcg@5" in report["metrics"]
