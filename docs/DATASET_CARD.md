# Dataset Card

## Dataset Name

Incident-to-Measure Relevance Dataset.

## Dataset Version

`1.0`, created on 2026-06-21.

## Intended Task

The dataset evaluates ranking systems that map cybersecurity incident descriptions to response or mitigation measures.

Input available to a ranker:

- `query_id` and `query_text` from `data/dataset/queries.jsonl`;
- `measure_id` and `measure_text` from `data/dataset/measure_corpus.jsonl`.

Target used only for evaluation:

- `relevance_grade`: ordinal label from 0 to 3.

## Size

| Item | Count |
|---|---:|
| Incident queries | 30 |
| Candidate measures | 25 |
| Judged incident-measure labels | 600 |
| Possible query-measure pairs | 750 |
| Unjudged query-measure pairs | 150 |
| Independent annotator files | 5 |
| Attack-defense mappings | 162 |

## Label Distribution

| Grade | Count |
|---:|---:|
| 0 | 428 |
| 1 | 82 |
| 2 | 88 |
| 3 | 2 |

## Data Sources

The package includes source identifiers and provenance records in `sources.jsonl`, `queries.jsonl`, and `measure_corpus.jsonl`. The main source families are:

- VCDB-style incident summaries used as query texts;
- MITRE ATT&CK mitigation descriptions;
- MITRE D3FEND-style defense technique descriptions;
- RE&CT-style response action descriptions;
- Codex subagent annotation and adjudication records.

The repository preserves source locators and hashes where available.

## Annotation Method

Five independent Codex subagent annotators evaluated the same blinded
incident-measure review queue in `5.5 xhigh` mode. The review queue hid model
outputs, prior candidate labels, sampling reasons, and final adjudication
decisions. Final labels were produced by median aggregation with conservative
downgrade rules for disagreement and incomplete strict applicability. Codex app
build/version was not captured in the dataset records.

Agreement summary:

| Measure | Value |
|---|---:|
| Fleiss kappa | 0.590665 |
| Krippendorff alpha, ordinal | 0.807456 |
| Mean Kendall concordance | 0.401724 |
| Strong disagreements | 23 |

## Recommended Evaluation

Use all three views:

- graded ranking: `graded nDCG@k` over labels 0..3;
- usable positives: `grade >= 2`;
- strict positives: `grade == 3`, with caution because there are only two strict positives.

The dataset is too small for a final production model decision by itself. It is suitable for diagnostic evaluation, method comparison, regression checks, and error analysis.

Each query currently has 20 judged candidate measures from the 25-measure catalog. Unjudged pairs should not be treated as expert-verified negatives.

Baseline results for BM25, masked BM25, and zero-shot dense retrieval are
summarized in `docs/BASELINES.md`.

## Prohibited Uses

The package policy forbids:

- model training;
- fine-tuning;
- hard negative mining;
- prompt tuning;
- hyperparameter tuning on this dataset.

## Known Limitations

- The labels come from a Codex subagent panel, not from external human experts.
- The corpus contains only 30 incidents and 25 candidate measures.
- Strict positives are rare: only two labels have grade 3.
- The measure catalog is not a complete SOC playbook.
- The dataset should not be presented as a production SOC benchmark.
