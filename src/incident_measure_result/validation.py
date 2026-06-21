from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from .io import read_json, read_jsonl

REQUIRED_DATASET_FILES = (
    "eval_manifest.json",
    "sources.jsonl",
    "queries.jsonl",
    "measure_corpus.jsonl",
    "attack_defense_mappings.jsonl",
    "relevance_annotations.jsonl",
    "leakage_report.json",
    "coverage_report.json",
    "agreement_report.json",
    "adjudication_decisions.jsonl",
)

FORBIDDEN_INTERNAL_PATTERNS = (
    "_".join(("8", "8", "35")),
    ".".join(("8", "8", "35")),
    "external_" + "gold_seed",
    "external_" + "gold" + "_review_seed",
    "examples" + "/" + "external_eval",
    "examples" + "\\" + "external_eval",
    "co" + "dex_" + "adjudicator",
    "sub" + "agent_",
)


def _scan_forbidden_patterns(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORBIDDEN_INTERNAL_PATTERNS:
                count = text.count(pattern)
                if count:
                    findings.append({"path": str(path), "pattern": pattern, "count": count})
    return findings


def _validate_manifest_hashes(root: Path, manifest: dict[str, Any]) -> dict[str, str]:
    hashes = manifest.get("file_hashes")
    if not isinstance(hashes, dict):
        raise ValueError("Manifest must contain a file_hashes object")

    verified: dict[str, str] = {}
    for name, expected in hashes.items():
        if not isinstance(name, str) or not isinstance(expected, str):
            raise ValueError("Manifest file_hashes must map file names to SHA-256 strings")
        path = root / name
        if not path.is_file():
            raise ValueError(f"Manifest hash references missing file: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {name}: expected {expected}, got {actual}")
        verified[name] = actual
    return verified


def validate_dataset(dataset_dir: str | Path, annotation_dir: str | Path | None = None) -> dict[str, Any]:
    """Validate dataset structure and return a compact report."""
    root = Path(dataset_dir)
    if not root.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {root}")

    missing = [name for name in REQUIRED_DATASET_FILES if not (root / name).is_file()]
    if missing:
        raise ValueError(f"Missing required dataset files: {missing}")

    hygiene_paths = [root]
    if annotation_dir is not None:
        hygiene_paths.append(Path(annotation_dir))
    hygiene_findings = _scan_forbidden_patterns(hygiene_paths)
    if hygiene_findings:
        raise ValueError(f"Forbidden internal patterns found: {hygiene_findings[:10]}")

    manifest = read_json(root / "eval_manifest.json")
    verified_hashes = _validate_manifest_hashes(root, manifest)
    queries = read_jsonl(root / "queries.jsonl")
    measures = read_jsonl(root / "measure_corpus.jsonl")
    annotations = read_jsonl(root / "relevance_annotations.jsonl")
    mappings = read_jsonl(root / "attack_defense_mappings.jsonl")
    agreement = read_json(root / "agreement_report.json")

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
    annotation_pairs: set[tuple[str, str]] = set()
    for row in annotations:
        query_id = row.get("query_id")
        measure_id = row.get("measure_id")
        grade = row.get("relevance_grade")
        if query_id not in query_ids:
            raise ValueError(f"Annotation references unknown query_id: {query_id}")
        if measure_id not in measure_ids:
            raise ValueError(f"Annotation references unknown measure_id: {measure_id}")
        pair = (str(query_id), str(measure_id))
        if pair in annotation_pairs:
            raise ValueError(f"Duplicate annotation pair found: {query_id}/{measure_id}")
        annotation_pairs.add(pair)
        if grade not in (0, 1, 2, 3):
            raise ValueError(f"Invalid relevance_grade for {query_id}/{measure_id}: {grade}")
        grade_counts[int(grade)] += 1
        label_sources[str(row.get("label_source"))] += 1

    possible_pairs = {(str(query_id), str(measure_id)) for query_id in query_ids for measure_id in measure_ids}
    extra_pairs = annotation_pairs - possible_pairs
    if extra_pairs:
        raise ValueError(f"Annotation matrix contains unknown pairs: extra={len(extra_pairs)}")
    annotations_per_query = Counter(query_id for query_id, _measure_id in annotation_pairs)
    if set(annotations_per_query) != {str(query_id) for query_id in query_ids}:
        raise ValueError("Every query must have at least one judged annotation pair")

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
            annotator_pairs = {(str(row.get("query_id")), str(row.get("measure_id"))) for row in rows}
            if annotator_pairs != annotation_pairs:
                raise ValueError(f"Annotator file {name} does not match the adjudicated pair matrix")

    return {
        "status": "passed",
        "dataset_dir": str(root),
        "package_id": manifest.get("package_id"),
        "dataset_version": manifest.get("dataset_version"),
        "schema_version": manifest.get("schema_version"),
        "query_count": len(queries),
        "measure_count": len(measures),
        "mapping_count": len(mappings),
        "annotation_count": len(annotations),
        "grade_counts": {str(key): grade_counts.get(key, 0) for key in range(4)},
        "label_source_counts": dict(label_sources),
        "annotator_files": annotator_files,
        "hashes": {"status": "passed", "verified_file_count": len(verified_hashes)},
        "matrix": {
            "status": "passed",
            "possible_pair_count": len(possible_pairs),
            "judged_pair_count": len(annotation_pairs),
            "unjudged_pair_count": len(possible_pairs) - len(annotation_pairs),
            "min_judged_pairs_per_query": min(annotations_per_query.values()),
            "max_judged_pairs_per_query": max(annotations_per_query.values()),
        },
        "hygiene": {
            "status": "passed",
            "forbidden_patterns": list(FORBIDDEN_INTERNAL_PATTERNS),
            "finding_count": 0,
        },
        "agreement": agreement,
    }


def validate_predictions(dataset_dir: str | Path, predictions_path: str | Path) -> dict[str, Any]:
    """Validate prediction JSONL rows before metric calculation."""
    root = Path(dataset_dir)
    predictions = read_jsonl(predictions_path)
    if not predictions:
        raise ValueError("Prediction file must contain at least one row")

    queries = read_jsonl(root / "queries.jsonl")
    measures = read_jsonl(root / "measure_corpus.jsonl")
    query_ids = {str(row["query_id"]) for row in queries}
    measure_ids = {str(row["measure_id"]) for row in measures}

    seen_queries: set[str] = set()
    for row_index, prediction in enumerate(predictions, start=1):
        query_id = str(prediction.get("query_id", ""))
        if query_id not in query_ids:
            raise ValueError(f"Prediction row {row_index} references unknown query_id: {query_id}")
        if query_id in seen_queries:
            raise ValueError(f"Duplicate prediction row for query_id: {query_id}")
        seen_queries.add(query_id)

        top_k = prediction.get("top_k")
        if not isinstance(top_k, list) or not top_k:
            raise ValueError(f"Prediction row {row_index} must contain a non-empty top_k list")

        ranks: set[int] = set()
        ranked_measures: set[str] = set()
        for item_index, item in enumerate(top_k, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Prediction row {row_index} top_k item {item_index} must be an object")
            rank = item.get("rank")
            if not isinstance(rank, int) or rank < 1:
                raise ValueError(f"Prediction row {row_index} has invalid rank: {rank}")
            if rank in ranks:
                raise ValueError(f"Prediction row {row_index} has duplicate rank: {rank}")
            ranks.add(rank)

            measure_id = str(item.get("measure_id", ""))
            if measure_id not in measure_ids:
                raise ValueError(f"Prediction row {row_index} references unknown measure_id: {measure_id}")
            if measure_id in ranked_measures:
                raise ValueError(f"Prediction row {row_index} repeats measure_id: {measure_id}")
            ranked_measures.add(measure_id)

        expected_ranks = set(range(1, len(top_k) + 1))
        if ranks != expected_ranks:
            raise ValueError(f"Prediction row {row_index} ranks must be contiguous from 1")

    return {
        "status": "passed",
        "prediction_count": len(predictions),
        "query_count": len(query_ids),
    }
