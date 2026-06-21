# Evaluation Guide

## Ranking contract

A valid ranker may read only:

- `query_id` and `query_text` from `external_queries.jsonl`;
- `measure_id` and `measure_text` from `external_measure_corpus.jsonl`.

A valid ranker must not read:

- `relevance_grade`;
- annotator files;
- adjudication decisions;
- model outputs;
- sampling audit fields;
- downgrade reasons;
- source labels that reveal relevance.

## Built-in BM25 baseline

```powershell
python scripts\rank_bm25.py --dataset data\external_gold_seed_8_8_35 --top-k 5 --out outputs\bm25_topk.jsonl
python scripts\evaluate.py --dataset data\external_gold_seed_8_8_35 --predictions outputs\bm25_topk.jsonl --out outputs\bm25_metrics.json
```

Expected smoke-run metrics:

| Method | graded nDCG@5 | usable recall@5 | usable MRR@5 |
|---|---:|---:|---:|
| BM25 | 0.349872 | 0.418340 | 0.391667 |

## Optional embedding ranking

Install optional dependencies first:

```powershell
python -m pip install -e .[embeddings]
```

Run any SentenceTransformers-compatible embedding model:

```powershell
python scripts\rank_embeddings.py `
  --dataset data\external_gold_seed_8_8_35 `
  --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 `
  --top-k 5 `
  --out outputs\miniLM_topk.jsonl

python scripts\evaluate.py --dataset data\external_gold_seed_8_8_35 --predictions outputs\miniLM_topk.jsonl --out outputs\miniLM_metrics.json
```

## Prediction format

The evaluator expects JSONL rows like:

```json
{"method":"bm25","query_id":"q_vcdb_...","top_k":[{"rank":1,"measure_id":"m_...","score":12.34}]}
```

## Metrics

The included evaluator computes:

- `graded_ndcg@1`, `graded_ndcg@3`, `graded_ndcg@5`;
- `usable_recall@1`, `usable_recall@3`, `usable_recall@5` with `grade >= 2`;
- `strict_recall@1`, `strict_recall@3`, `strict_recall@5` with `grade == 3`;
- `usable_mrr@k`;
- query counts for graded, usable, and strict slices.

Because strict positives are rare, do not make a model decision from strict recall alone.
