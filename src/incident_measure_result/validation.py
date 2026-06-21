from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .io import read_json, read_jsonl

REQUIRED_DATASET_FILES = (
    "external_eval_manifest.json",
    "external_sources.jsonl",
    "external_queries.jsonl",
    "external_measure_corpus.jsonl",
    "external_attack_defense_mappings.jsonl",
    "external_relevance_annotations.jsonl",
    "external_leakage_report.json",
    "external_coverage_report.json",
    "gold_agreement_report.json",
    "gold_adjudication_decisions.jsonl",
)


def validate_dataset(dataset_dir: str | Path, annotation_dir: str | Path | None = None) -> dict[str, Any]:
    """Validate dataset structure and return a compact report."""
    root = Path(dataset_dir)
    if not root.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {root}")

    missing = [name for name in REQUIRED_DATASET_FILES if not (root / name).is_file()]
    if missing:
        raise ValueError(f"Missing required dataset files: {missing}")

    manifest = read_json(root / "external_eval_manifest.json")
    queries = read_jsonl(root / "external_queries.jsonl")
    measures = read_jsonl(root / "external_measure_corpus.jsonl")
    annotations = read_jsonl(root / "external_relevance_annotations.jsonl")
    mappings = read_jsonl(root / "external_attack_defense_mappings.jsonl")
    agreement = read_json(root / "gold_agreement_report.json")

    query_ids = {row.get("query_id") for row in queries}
    measure_ids = {row.get("measure_id") for row in measures}
    if None in query_ids or None in measure_ids:
        raise ValueError("query_id and measure_id must be present in all query and measure rows")
    if len(query_ids) != len(queries):
        raise ValueError("Duplicate query_id values found")
    if len(measure_ids) != len(measures):
        raise ValueError("Duplicate measure_id values found")

    grade_counts: Counter[int] = Counter()
    label_sources: Counter[str] = Counter()
    for row in annotations:
        query_id = row.get("query_id")
        measure_id = row.get("measure_id")
        grade = row.get("relevance_grade")
        if query_id not in query_ids:
            raise ValueError(f"Annotation references unknown query_id: {query_id}")
        if measure_id not in measure_ids:
            raise ValueError(f"Annotation references unknown measure_id: {measure_id}")
        if grade not in (0, 1, 2, 3):
            raise ValueError(f"Invalid relevance_grade for {query_id}/{measure_id}: {grade}")
        grade_counts[int(grade)] += 1
        label_sources[str(row.get("label_source"))] += 1

    annotator_files: list[str] = []
    if annotation_dir is not None:
        annotator_root = Path(annotation_dir)
        annotator_files = sorted(path.name for path in annotator_root.glob("annotator_*.jsonl"))
        if len(annotator_files) != 5:
            raise ValueError(f"Expected exactly five annotator files, got {len(annotator_files)}")
        for name in annotator_files:
            rows = read_jsonl(annotator_root / name)
            if len(rows) != len(annotations):
                raise ValueError(f"Annotator file {name} has {len(rows)} rows, expected {len(annotations)}")

    return {
        "status": "passed",
        "dataset_dir": str(root),
        "package_id": manifest.get("package_id"),
        "schema_version": manifest.get("schema_version"),
        "query_count": len(queries),
        "measure_count": len(measures),
        "mapping_count": len(mappings),
        "annotation_count": len(annotations),
        "grade_counts": {str(key): grade_counts.get(key, 0) for key in range(4)},
        "label_source_counts": dict(label_sources),
        "annotator_files": annotator_files,
        "agreement": agreement,
    }
