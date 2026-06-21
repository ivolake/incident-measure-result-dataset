# Dataset Schema

## Model-Facing Files

Rankers may read only:

- `data/dataset/queries.jsonl`
  - required fields: `query_id`, `query_text`;
  - optional diagnostic fields must not be used as model inputs unless explicitly allowed by an evaluation protocol.
- `data/dataset/measure_corpus.jsonl`
  - required fields: `measure_id`, `measure_text`;
  - optional diagnostic fields must not be used as labels.

## Label And Evaluation Files

Evaluation code may read:

- `data/dataset/relevance_annotations.jsonl`
  - required fields: `query_id`, `measure_id`, `relevance_grade`;
  - grades are integers from 0 to 3.
- `data/dataset/eval_manifest.json`
  - package metadata, file hashes, allowed uses, and metric policy.

The annotation matrix contains judged query-measure pairs. The current package has 750 possible query-measure pairs and 600 judged pairs. Unjudged pairs are not expert-verified negatives.

## Audit And Provenance Files

These files are for traceability and diagnostics only:

- `data/dataset/sources.jsonl`;
- `data/dataset/attack_defense_mappings.jsonl`;
- `data/dataset/adjudication_decisions.jsonl`;
- `data/dataset/agreement_report.json`;
- `data/dataset/agreement_report.md`;
- `data/dataset/leakage_report.json`;
- `data/dataset/coverage_report.json`;
- `data/annotations/llm_panel/*.jsonl`;
- `data/review_audit/*.jsonl`.

Rankers must not use these files as inference-time inputs.

## Prediction JSONL

Each row must contain:

```json
{"method":"bm25","query_id":"q_vcdb_...","top_k":[{"rank":1,"measure_id":"m_...","score":12.34}]}
```

Validation requires:

- known `query_id`;
- known `measure_id`;
- non-empty `top_k`;
- unique, contiguous ranks starting from 1;
- no duplicate measures per query;
- no duplicate prediction row for the same query.
