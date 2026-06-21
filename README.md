# Incident-to-Measure Relevance Dataset

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Queries](https://img.shields.io/badge/queries-30-informational)
![Measures](https://img.shields.io/badge/measures-25-informational)
![Labels](https://img.shields.io/badge/labels-600-informational)
![Annotation](https://img.shields.io/badge/annotation-LLM--panel-orange)
![Data Notice](https://img.shields.io/badge/data-notice-lightgrey)

A small public evaluation seed for ranking cybersecurity response measures against incident descriptions.

The task is simple:

```text
incident description + candidate response measure description -> ranked response measures
```

The dataset is designed for diagnostic cold-start ranking evaluation. A ranking method receives only incident text and candidate measure text, then ranks the 25-measure catalog. It must not use label fields, audit fields, source locators, prior candidate metadata, or annotation artifacts as model inputs.

## What This Is

- 30 source-derived cybersecurity incident descriptions.
- 25 source-derived or source-normalized candidate response measures.
- 600 adjudicated labels for judged incident-measure pairs.
- Five independent Codex subagent annotator files produced in `5.5 xhigh` mode.
- Deterministic adjudication over the five annotator files.
- Validation, BM25 ranking, optional embedding ranking, and metric utilities.

## What This Is Not

- Not a human expert benchmark.
- Not a training, fine-tuning, hard-negative mining, prompt-tuning, or hyperparameter-tuning dataset.
- Not a complete SOC playbook or production incident-response benchmark.
- Not evidence that a method is operationally safe without separate expert review.

Use it as a compact evaluation seed for regression checks, ranking diagnostics, method comparison, and error analysis.

## Dataset At A Glance

| Item | Value |
|---|---:|
| Incident queries | 30 |
| Candidate measures | 25 |
| Judged pairs | 600 |
| Possible query-measure pairs | 750 |
| Unjudged pairs | 150 |
| Independent annotators | 5 |
| Grade scale | 0..3 |

Label distribution:

| Grade | Count |
|---:|---:|
| 0 | 428 |
| 1 | 82 |
| 2 | 88 |
| 3 | 2 |

For evaluation, use:

- graded ranking: full `0..3` scale;
- usable positives: `grade >= 2`;
- strict positives: `grade == 3`.

There are only two strict positives, so strict-positive metrics are unstable and should not be the only decision criterion.

## Quick Start

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

Validate the dataset:

```powershell
python scripts\validate_dataset.py --dataset data\dataset --annotations data\annotations\llm_panel --out outputs\validation_report.json
```

Run the dependency-free BM25 baseline:

```powershell
python scripts\rank_bm25.py --dataset data\dataset --top-k 5 --out outputs\bm25_topk.jsonl
python scripts\evaluate.py --dataset data\dataset --predictions outputs\bm25_topk.jsonl --out outputs\bm25_metrics.json
```

Optional embedding ranking requires the `embeddings` extra:

```powershell
python -m pip install -e .[embeddings]
python scripts\rank_embeddings.py --dataset data\dataset --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --top-k 5 --out outputs\miniLM_topk.jsonl
python scripts\evaluate.py --dataset data\dataset --predictions outputs\miniLM_topk.jsonl --out outputs\miniLM_metrics.json
```

Installed command form:

```powershell
incident-measure-result validate --dataset data\dataset --annotations data\annotations\llm_panel
incident-measure-result rank-bm25 --dataset data\dataset --out outputs\bm25_topk.jsonl
incident-measure-result evaluate --dataset data\dataset --predictions outputs\bm25_topk.jsonl
```

## Baselines

These results come from a prior internal evaluation run on the same 30-query / 25-measure adjudicated candidate dataset. Only public-safe, not-trained-on-this-dataset methods are listed here. See `docs/BASELINES.md` for definitions and caveats.

| Method | Model / setup | Trained on this dataset? | graded nDCG@5 | usable recall@5 | usable MRR@5 |
|---|---|---:|---:|---:|---:|
| BM25 | raw lexical baseline | No | 0.349872 | 0.418340 | 0.391667 |
| Masked BM25 | lexical baseline with leakage-prone fields masked | No | 0.349872 | 0.418340 | 0.391667 |
| Zero-shot EmbeddingGemma | `google/embeddinggemma-300m` | No | 0.317921 | 0.220459 | 0.445833 |
| Zero-shot multilingual E5 | `intfloat/multilingual-e5-base` | No | 0.158707 | 0.125568 | 0.128472 |

Dense baselines are off-the-shelf / zero-shot. No fine-tuning, hard-negative mining, prompt tuning, or hyperparameter tuning on this dataset was used for the public baseline table.

## Annotation Provenance

The label layer was produced by five independent Codex subagent annotators using `5.5 xhigh` mode. Each annotator reviewed the same blinded queue and wrote an independent file. The queue hid model outputs, prior candidate labels, pair-selection reasons, and final adjudication decisions.

Final labels were produced by deterministic median aggregation with conservative downgrade rules for broad, conditional, phase-mismatched, or insufficiently direct measures. Codex app build/version was not captured in the dataset records.

## Repository Layout

```text
data/
  dataset/                 # Main dataset package
  annotations/llm_panel/   # Five independent annotator files
  review_audit/            # Blinded review queue and sampling audit
docs/
  DATASET_CARD.md
  BASELINES.md
  SCHEMA.md
  ANNOTATION_PROTOCOL.md
  EVALUATION_GUIDE.md
  PROVENANCE.md
  SOURCES_AND_LICENSES.md
benchmarks/
  baselines_v1.json
src/incident_measure_result/
scripts/
tests/
DATA_NOTICE.md
LICENSE
```

## Documentation

| Document | Purpose |
|---|---|
| `docs/DATASET_CARD.md` | Dataset scope, size, label distribution, intended use, limitations. |
| `docs/BASELINES.md` | Baseline metrics, method definitions, and excluded-method policy. |
| `docs/SCHEMA.md` | Model-facing, label-only, audit-only, and provenance fields. |
| `docs/ANNOTATION_PROTOCOL.md` | Annotation units, Codex subagent setup, blinding, adjudication. |
| `docs/EVALUATION_GUIDE.md` | Prediction contract and metric usage. |
| `docs/PROVENANCE.md` | Source preparation, preserved records, hashes. |
| `docs/SOURCES_AND_LICENSES.md` | Source families and upstream reuse notes. |
| `DATA_NOTICE.md` | Practical data reuse notice. |

## Citation And Reuse

No formal citation has been assigned yet. If you use this repository, cite the repository URL and preserve the provenance files.

Code and repository documentation are covered by `LICENSE`. Dataset files under `data/` contain source-derived records and are subject to the upstream notices summarized in `DATA_NOTICE.md` and `docs/SOURCES_AND_LICENSES.md`. Preserve attribution, upstream notices, and source provenance when redistributing the dataset or derived records.
