# Dataset Card

## Dataset name

Incident-to-Measure Relevance Gold Candidate Dataset.

## Dataset version

`external-gold-seed-8-8-35`, created on 2026-06-21.

## Intended task

The dataset evaluates ranking systems that map cybersecurity incident descriptions to response or mitigation measures.

Input available to a ranker:

- `query_text`: source-derived incident description;
- `measure_text`: source-derived or source-normalized response measure description.

Target used only for evaluation:

- `relevance_grade`: ordinal label from 0 to 3.

## Size

| Item | Count |
|---|---:|
| Incident queries | 30 |
| Candidate measures | 25 |
| Incident-measure labels | 600 |
| Independent annotator files | 5 |
| Attack-defense mappings | 162 |

## Label distribution

| Grade | Count |
|---:|---:|
| 0 | 428 |
| 1 | 82 |
| 2 | 88 |
| 3 | 2 |

## Data sources

The package includes source identifiers and provenance records in `external_sources.jsonl`, `external_queries.jsonl`, and `external_measure_corpus.jsonl`. The main source families are:

- VCDB-style incident summaries used as query texts;
- MITRE ATT&CK mitigation descriptions;
- MITRE D3FEND and RE&CT-style response measures;
- a gold annotation source representing the internal five-annotator LLM panel.

The repository preserves source locators and hashes where available.

## Annotation method

Five independent LLM annotators evaluated the same blinded incident-measure review queue. The review queue hid model outputs, previous silver labels, and sampling reasons. The final labels were produced by median aggregation with conservative downgrade rules for disagreement and incomplete strict applicability.

Agreement summary:

| Measure | Value |
|---|---:|
| Fleiss kappa | 0.590665 |
| Krippendorff alpha, ordinal | 0.807456 |
| Mean Kendall concordance | 0.401724 |
| Strong disagreements | 23 |

## Recommended evaluation

Use all three views:

- graded ranking: `graded nDCG@k` over labels 0..3;
- usable positives: `grade >= 2`;
- strict positives: `grade == 3`, with caution because there are only two strict positives.

The dataset is too small for a final production model decision by itself. It is suitable for diagnostic evaluation, method comparison, regression checks, and error analysis.

## Prohibited uses

The original package policy forbids:

- model training;
- fine-tuning;
- hard negative mining;
- prompt tuning;
- hyperparameter tuning on this dataset.

## Known limitations

- The labels come from an internal LLM panel, not from external human experts.
- The corpus contains only 30 incidents and 25 candidate measures.
- Strict positives are rare: only two labels have grade 3.
- The measure catalog is not a complete SOC playbook.
- The dataset should not be presented as a production SOC benchmark.
