# Provenance

## Source Preparation

This repository was prepared from internal project artifacts that assembled incident descriptions, response-measure descriptions, independent LLM annotations, and deterministic adjudication results.

The public repository intentionally uses self-contained paths and identifiers. Internal run names, temporary package names, and local source-project paths are not part of the public data contract.

## Preserved Files

The repository preserves:

- the evaluation manifest;
- source records;
- query records;
- measure corpus records;
- attack-defense mapping records;
- adjudicated relevance annotations;
- leakage and coverage reports;
- agreement reports;
- adjudication decisions;
- five independent annotator files;
- the blinded review queue;
- the sampling audit.

## Text Origin

Rows contain `text_provenance` fields where available. These fields include source locators, source hashes, source fields, and normalization steps. The model-facing text fields are source-derived or normalized source text; this repository does not add new semantic paraphrases to the dataset.

## Hashes

The dataset manifest stores SHA-256 hashes for the package files in `data/dataset/`. Use `scripts/validate_dataset.py` for structural validation and hash checks.

## Repository Remote

The repository is configured with:

```text
origin git@github.com:ivolake/incident-measure-result-dataset.git
```
