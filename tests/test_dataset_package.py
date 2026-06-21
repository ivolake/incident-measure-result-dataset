import json
import shutil
from pathlib import Path

import pytest

from incident_measure_result.metrics import evaluate_predictions
from incident_measure_result.rankers import rank_bm25
from incident_measure_result.validation import validate_dataset, validate_predictions

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "dataset"
ANNOTATIONS = ROOT / "data" / "annotations" / "llm_panel"


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def test_dataset_validation_counts_hashes_and_hygiene() -> None:
    report = validate_dataset(DATASET, ANNOTATIONS)
    assert report["status"] == "passed"
    assert report["package_id"] == "incident-measure-result-dataset"
    assert report["schema_version"] == "incident_measure_result_v1"
    assert report["query_count"] == 30
    assert report["measure_count"] == 25
    assert report["annotation_count"] == 600
    assert report["grade_counts"] == {"0": 428, "1": 82, "2": 88, "3": 2}
    assert report["label_source_counts"] == {"adjudicated": 600}
    assert len(report["annotator_files"]) == 5
    assert report["matrix"] == {
        "status": "passed",
        "possible_pair_count": 750,
        "judged_pair_count": 600,
        "unjudged_pair_count": 150,
        "min_judged_pairs_per_query": 20,
        "max_judged_pairs_per_query": 20,
    }
    assert report["hashes"]["status"] == "passed"
    assert report["hygiene"]["status"] == "passed"


def test_bm25_metrics_regression(tmp_path: Path) -> None:
    predictions = rank_bm25(DATASET, top_k=5)
    assert len(predictions) == 30
    assert all(len(row["top_k"]) == 5 for row in predictions)

    prediction_path = tmp_path / "bm25.jsonl"
    _write_jsonl(prediction_path, predictions)

    report = evaluate_predictions(DATASET, prediction_path)
    assert report["query_count"] == 30
    assert report["metrics"]["graded_ndcg@5"] == 0.349872
    assert report["metrics"]["usable_recall@5"] == 0.41834
    assert report["metrics"]["usable_mrr@5"] == 0.391667


def test_hash_validation_rejects_modified_dataset(tmp_path: Path) -> None:
    dataset_copy = tmp_path / "dataset"
    shutil.copytree(DATASET, dataset_copy)
    with (dataset_copy / "queries.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("\n")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_dataset(dataset_copy)


def test_hygiene_validation_rejects_internal_patterns(tmp_path: Path) -> None:
    patterns = [
        "sub" + "agent_",
        "external" + "_eval",
        "si" + "lver",
    ]
    for index, pattern in enumerate(patterns):
        dataset_copy = tmp_path / f"dataset_{index}"
        shutil.copytree(DATASET, dataset_copy)
        (dataset_copy / "agreement_report.md").write_text(pattern + "\n", encoding="utf-8")

        with pytest.raises(ValueError, match="Forbidden internal patterns"):
            validate_dataset(dataset_copy)


def test_prediction_validation_rejects_bad_rows(tmp_path: Path) -> None:
    good_query = "q_vcdb_0001aa7f_c601_424a_b2b8_be6c9f5164e7"
    good_measure = "m_attack_m1026_privileged_account_management"

    bad_cases = [
        [],
        [{"method": "x", "query_id": "unknown", "top_k": [{"rank": 1, "measure_id": good_measure}]}],
        [{"method": "x", "query_id": good_query, "top_k": [{"rank": 1, "measure_id": "unknown"}]}],
        [
            {
                "method": "x",
                "query_id": good_query,
                "top_k": [
                    {"rank": 1, "measure_id": good_measure},
                    {"rank": 1, "measure_id": "m_attack_m1017_user_training"},
                ],
            }
        ],
        [
            {
                "method": "x",
                "query_id": good_query,
                "top_k": [
                    {"rank": 1, "measure_id": good_measure},
                    {"rank": 2, "measure_id": good_measure},
                ],
            }
        ],
    ]

    for index, rows in enumerate(bad_cases):
        path = tmp_path / f"bad_{index}.jsonl"
        _write_jsonl(path, rows)
        with pytest.raises(ValueError):
            validate_predictions(DATASET, path)
