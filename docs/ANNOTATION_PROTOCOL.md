# Annotation Protocol

## Unit Of Annotation

Each annotation task contains:

```text
incident description + response phase + candidate measure
```

The annotator assigns four grades:

- `incident_fit_grade`;
- `phase_fit_grade`;
- `measure_applicability_grade`;
- final `relevance_grade`.

## Grade Scale

| Grade | Interpretation |
|---:|---|
| 0 | Not relevant, wrong object, wrong response phase, or potentially misleading. |
| 1 | Weak relation, generic security hygiene, or only indirect relevance. |
| 2 | Usable but partial, broad, conditional, or requiring local operational detail. |
| 3 | Directly applicable, concrete, phase-aligned, and suitable as a strong positive. |

## Five Independent Codex Subagent Annotators

The five files in `data/annotations/llm_panel/` correspond to independent
Codex subagent annotator runs performed in `5.5 xhigh` mode:

- `annotator_a.jsonl`: SOC response fit;
- `annotator_b.jsonl`: measure applicability;
- `annotator_c.jsonl`: phase fit;
- `annotator_d.jsonl`: conservative strict-positive check;
- `annotator_e.jsonl`: negative-control oriented review.

Each annotator saw the same review queue and produced a separate file.
Annotators did not read one another's labels. Codex app build/version was not
captured in the dataset records.

## Blinding

The review queue was designed to hide:

- prior candidate labels;
- model outputs;
- reasons why a pair was sampled;
- final adjudication decisions.

The sampling audit is stored separately in `data/review_audit/sampling_audit.jsonl` and must not be used as a model input.

## Adjudication

Final labels in `data/dataset/relevance_annotations.jsonl` were produced from the five annotation files. The adjudication rule is recorded as:

```text
median_with_conservative_disagreement_downgrade_v1
```

The policy favors conservative downgrading when a measure is broad,
conditional, mismatched to the response phase, or lacks a direct operational
action.

## Evidence Fields

The adjudicated annotation rows include:

- `label_basis`;
- `evidence_ref`;
- `annotator_ids`;
- `source_annotation_ids`;
- `downgrade_reasons`;
- `incident_fit_grade`;
- `phase_fit_grade`;
- `measure_applicability_grade`.

These fields are diagnostic. They must not be used by ranking models.
