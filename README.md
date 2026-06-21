# Incident-to-Measure Relevance Gold Candidate Dataset

This repository contains a small gold-candidate dataset for evaluating incident-to-measure ranking systems in cybersecurity incident response.

The task is:

```text
incident description + candidate response measure description -> relevance grade
```

The dataset is intended for cold-start ranking evaluation: the ranker receives the incident text and the candidate measure text at inference time, and must choose relevant measures from an external measure catalog. The dataset must not be used for training, fine-tuning, hard negative mining, prompt tuning, or hyperparameter tuning.

## What is included

- 30 source-derived incident descriptions.
- 25 source-derived or source-normalized candidate response measures.
- 600 adjudicated relevance labels for all incident-measure pairs.
- Five independent LLM-annotator files used to produce the adjudicated labels.
- Agreement and adjudication reports.
- Minimal Python utilities for validation, BM25 ranking, optional embedding ranking, and metric calculation.

## Important limitation

This is not a human expert gold dataset. The labels were produced by an internal panel of five independent LLM annotators and then adjudicated by a deterministic project procedure. The dataset should be described as a gold-labeled candidate or internal gold candidate, not as an externally validated human expert benchmark.

## Repository layout

```text
data/
  external_gold_seed_8_8_35/          # Main dataset package
  annotations/subagent_annotations/   # Five independent annotation files
  review_seed/                        # Blinded review queue and sampling audit
docs/
  DATASET_CARD.md
  ANNOTATION_PROTOCOL.md
  EVALUATION_GUIDE.md
  PROVENANCE.md
  SOURCES_AND_LICENSES.md
src/incident_measure_result/          # Lightweight validation/ranking/evaluation code
scripts/                              # CLI wrappers
tests/                                # Smoke tests
```

## Quick start

Create and activate a virtual environment, then install the package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

Validate the dataset:

```powershell
python scripts\validate_dataset.py --dataset data\external_gold_seed_8_8_35 --annotations data\annotations\subagent_annotations --out outputs\validation_report.json
```

Run a dependency-free BM25 baseline:

```powershell
python scripts\rank_bm25.py --dataset data\external_gold_seed_8_8_35 --top-k 5 --out outputs\bm25_topk.jsonl
python scripts\evaluate.py --dataset data\external_gold_seed_8_8_35 --predictions outputs\bm25_topk.jsonl --out outputs\bm25_metrics.json
```

Optional embedding ranking requires additional dependencies:

```powershell
python -m pip install -e .[embeddings]
python scripts\rank_embeddings.py --dataset data\external_gold_seed_8_8_35 --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --top-k 5 --out outputs\miniLM_topk.jsonl
python scripts\evaluate.py --dataset data\external_gold_seed_8_8_35 --predictions outputs\miniLM_topk.jsonl --out outputs\miniLM_metrics.json
```

You can also use the installed command:

```powershell
incident-measure-result validate --dataset data\external_gold_seed_8_8_35 --annotations data\annotations\subagent_annotations
incident-measure-result rank-bm25 --dataset data\external_gold_seed_8_8_35 --out outputs\bm25_topk.jsonl
incident-measure-result evaluate --dataset data\external_gold_seed_8_8_35 --predictions outputs\bm25_topk.jsonl
```

## Label scale

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

For evaluation, the original project used:

- strict positive: `grade == 3`;
- usable positive: `grade >= 2`;
- graded ranking: full `0..3` scale.

Because there are only two strict positives, strict metrics should not be used as the only decision criterion.

## Built-in baseline check

The included BM25 implementation is aligned with the source project lexical baseline on this dataset. A smoke run should produce:

| Method | graded nDCG@5 | usable recall@5 | usable MRR@5 |
|---|---:|---:|---:|
| BM25 | 0.349872 | 0.418340 | 0.391667 |

## Citation and reuse

No formal citation has been assigned yet. If you use this repository, cite the repository URL and preserve the provenance files. Source texts and source-derived records may be subject to their upstream terms. See `docs/SOURCES_AND_LICENSES.md`.
