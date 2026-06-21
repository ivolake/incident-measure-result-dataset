# Incident-to-Measure Relevance Dataset

This repository contains a small adjudicated candidate dataset for evaluating incident-to-measure ranking systems in cybersecurity incident response.

The task is:

```text
incident description + candidate response measure description -> relevance grade
```

The dataset is intended for cold-start ranking evaluation. A ranker receives only the incident text and candidate measure text at inference time, then ranks measures from the catalog. The dataset must not be used for training, fine-tuning, hard negative mining, prompt tuning, or hyperparameter tuning.

## What Is Included

- 30 source-derived incident descriptions.
- 25 source-derived or source-normalized candidate response measures.
- 600 adjudicated relevance labels for judged incident-measure pairs.
- Five independent LLM annotator files used to produce the adjudicated labels.
- Agreement, adjudication, coverage, leakage, review-audit, and provenance records.
- Minimal Python utilities for validation, BM25 ranking, optional embedding ranking, and metric calculation.

## Important Limitation

This is not a human expert benchmark. The labels were produced by an internal panel of five independent LLM annotators and then resolved by a deterministic adjudication procedure. Describe the dataset as an adjudicated candidate evaluation set, not as an externally validated expert benchmark.

## Repository Layout

```text
data/
  dataset/                 # Main dataset package
  annotations/llm_panel/   # Five independent annotator files
  review_audit/            # Blinded review queue and sampling audit
docs/
  DATASET_CARD.md
  SCHEMA.md
  ANNOTATION_PROTOCOL.md
  EVALUATION_GUIDE.md
  PROVENANCE.md
  SOURCES_AND_LICENSES.md
src/incident_measure_result/
scripts/
tests/
```

## Quick Start

Create and activate a virtual environment, then install the package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

Validate the dataset:

```powershell
python scripts\validate_dataset.py --dataset data\dataset --annotations data\annotations\llm_panel --out outputs\validation_report.json
```

Run a dependency-free BM25 baseline:

```powershell
python scripts\rank_bm25.py --dataset data\dataset --top-k 5 --out outputs\bm25_topk.jsonl
python scripts\evaluate.py --dataset data\dataset --predictions outputs\bm25_topk.jsonl --out outputs\bm25_metrics.json
```

Optional embedding ranking requires additional dependencies:

```powershell
python -m pip install -e .[embeddings]
python scripts\rank_embeddings.py --dataset data\dataset --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --top-k 5 --out outputs\miniLM_topk.jsonl
python scripts\evaluate.py --dataset data\dataset --predictions outputs\miniLM_topk.jsonl --out outputs\miniLM_metrics.json
```

You can also use the installed command:

```powershell
incident-measure-result validate --dataset data\dataset --annotations data\annotations\llm_panel
incident-measure-result rank-bm25 --dataset data\dataset --out outputs\bm25_topk.jsonl
incident-measure-result evaluate --dataset data\dataset --predictions outputs\bm25_topk.jsonl
```

## Label Scale

| Grade | Meaning |
|---:|---|
| 0 | Not relevant or misleading for the incident and response phase. |
| 1 | Weakly related, too generic, wrong phase, or only indirectly useful. |
| 2 | Usable but partial: relevant to the incident or phase, yet broad or conditional. |
| 3 | Strictly relevant: directly applicable, concrete, and well aligned with the response phase. |

The current adjudicated distribution is:

| Grade | Count |
|---:|---:|
| 0 | 428 |
| 1 | 82 |
| 2 | 88 |
| 3 | 2 |

For evaluation, use:

- strict positive: `grade == 3`;
- usable positive: `grade >= 2`;
- graded ranking: full `0..3` scale.

Because there are only two strict positives, strict metrics should not be used as the only decision criterion.

The global catalog contains 25 measures. Each query currently has 20 judged candidate measures, for 600 judged pairs total. Unjudged pairs should not be interpreted as human-verified negatives.

## Built-In Baseline Check

The included BM25 implementation is aligned with the source project lexical baseline on this dataset. A smoke run should produce:

| Method | graded nDCG@5 | usable recall@5 | usable MRR@5 |
|---|---:|---:|---:|
| BM25 | 0.349872 | 0.418340 | 0.391667 |

## Citation and Reuse

No formal citation has been assigned yet. If you use this repository, cite the repository URL and preserve the provenance files. Source texts and source-derived records may be subject to upstream terms. See `docs/SOURCES_AND_LICENSES.md`.
