# Data Notice

This repository separates repository code and documentation from the dataset records.

- Code and repository documentation are covered by `LICENSE`, unless a file states otherwise.
- Dataset files under `data/` contain source-derived incident text, source-derived or source-normalized response-measure text, provenance metadata, audit records, and adjudicated LLM-panel labels.
- Upstream source terms continue to apply to source-derived records. This notice is a practical reuse summary; upstream license texts and terms control.

## Dataset Reuse

You may use the dataset for evaluation, diagnostics, regression checks, and error analysis, subject to the upstream notices below and the dataset policy in the manifest.

Do not use this dataset for model training, fine-tuning, hard negative mining, prompt tuning, or hyperparameter tuning. The dataset is an adjudicated candidate evaluation set, not an externally validated human expert benchmark.

## Upstream Notices

| Source family | Use in this repository | Upstream notice |
|---|---|---|
| VCDB | Incident summaries used as query text | Creative Commons Attribution-ShareAlike 4.0 International. Preserve attribution, indicate modifications where applicable, and apply compatible ShareAlike terms to adapted material. |
| MITRE ATT&CK | Mitigation and technique-derived measure/provenance records | MITRE permits ATT&CK use for research, development, and commercial purposes when MITRE copyright and license notices are reproduced. ATT&CK is provided as-is and does not guarantee defensive coverage. |
| MITRE D3FEND | Defensive technique-derived measure/provenance records | Preserve D3FEND project notices and applicable license terms. |
| ATC RE&CT | Response action-derived measure/provenance records | Preserve ATC RE&CT project notices and applicable Apache-2.0 license terms. |
| Repository annotation layer | LLM-panel annotations, adjudication records, and audit metadata | Covered by this repository notice and `LICENSE`; report it as LLM-panel adjudicated data, not as human expert labeling. |

Source locators and hashes are recorded in `data/dataset/sources.jsonl`, `data/dataset/queries.jsonl`, and `data/dataset/measure_corpus.jsonl`.

## Attribution

When redistributing this dataset or derived records, preserve:

- this `DATA_NOTICE.md`;
- `LICENSE`;
- `docs/SOURCES_AND_LICENSES.md`;
- source identifiers, locators, and hashes from the dataset files where practical.

Do not imply endorsement by VCDB, MITRE, D3FEND, ATC RE&CT, or any upstream project.

## Warranty

The dataset is provided as-is, without warranty. It is small, diagnostic, and source-derived. It should not be used as the sole basis for production security decisions, procurement decisions, or claims about operational incident-response quality.
