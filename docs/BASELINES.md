# Baselines

Baseline results below come from a prior internal evaluation run on the same
30-query / 25-measure adjudicated candidate dataset. This public summary keeps
only methods that were not trained or tuned on this dataset.

No prediction files, top-k artifacts, model weights, internal project names, or
run identifiers are included in this repository.

## Metric Definitions

| Metric | Meaning |
|---|---|
| `graded nDCG@5` | Ranking quality over the full ordinal `0..3` relevance scale. |
| `usable recall@5` | Recall at five for labels with `relevance_grade >= 2`. |
| `usable MRR@5` | Reciprocal rank of the first label with `relevance_grade >= 2` in the top five. |

Strict-positive metrics based on `relevance_grade == 3` are intentionally not
emphasized because the dataset contains only two grade-3 labels.

## Public Baseline Table

| Method | Model / setup | Trained on this dataset? | graded nDCG@5 | usable recall@5 | usable MRR@5 |
|---|---|---:|---:|---:|---:|
| BM25 | raw lexical baseline | No | 0.349872 | 0.418340 | 0.391667 |
| Masked BM25 | lexical baseline with leakage-prone fields masked | No | 0.349872 | 0.418340 | 0.391667 |
| Zero-shot EmbeddingGemma | `google/embeddinggemma-300m` | No | 0.317921 | 0.220459 | 0.445833 |
| Zero-shot multilingual E5 | `intfloat/multilingual-e5-base` | No | 0.158707 | 0.125568 | 0.128472 |

## Method Notes

BM25 is the dependency-free lexical baseline implemented in this repository.

Masked BM25 uses the same lexical scoring idea after removing leakage-prone
non-model fields from the ranking surface. On the public model-facing package,
it matches raw BM25 because the exposed ranking inputs are already limited to
incident text and candidate measure text.

The dense baselines use off-the-shelf embedding models in zero-shot mode. They
were not fine-tuned, prompt-tuned, trained with hard negatives, or selected by
hyperparameter tuning on this dataset.

Prior internal training-based experiments existed, but they are intentionally
excluded from this public benchmark table. This repository does not publish
trained model paths, model weights, training objectives, or training artifacts.
