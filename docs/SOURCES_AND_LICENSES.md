# Sources and Licenses

This repository contains source-derived cybersecurity incident and measure records. The dataset package preserves source identifiers, locators, and text provenance where available.

See the root `DATA_NOTICE.md` for the short reuse notice that should travel with redistributed dataset records.

## Repository Licensing Structure

- Repository code and documentation: covered by `LICENSE`, unless a file states otherwise.
- Dataset records under `data/`: source-derived records plus repository-created annotation and audit metadata.
- Source-derived text and metadata remain subject to upstream source terms.

## Source Families Represented

The package includes records derived or normalized from sources such as:

- VCDB incident summaries used as query text;
- MITRE ATT&CK mitigation and technique-derived records;
- MITRE D3FEND defensive technique-derived records;
- ATC RE&CT response action-derived records;
- repository-created LLM-panel annotation, adjudication, and audit records.

## Upstream Terms Summary

| Source family | Practical obligation |
|---|---|
| VCDB | Treat source-derived incident records conservatively under Creative Commons Attribution-ShareAlike 4.0 International: preserve attribution, indicate modifications where applicable, and use compatible ShareAlike terms for adapted material. |
| MITRE ATT&CK | Reproduce MITRE copyright and license notices when redistributing ATT&CK-derived records. Do not imply ATT&CK guarantees defensive coverage. |
| MITRE D3FEND | Preserve D3FEND project notices and applicable license terms for D3FEND-derived records. |
| ATC RE&CT | Preserve ATC RE&CT project notices and applicable Apache-2.0 terms for RE&CT-derived records. |
| Repository annotation layer | Report as LLM-panel adjudicated labels, not as external human expert labels. |

## Provenance Files

Primary provenance is stored in:

- `data/dataset/sources.jsonl`;
- `data/dataset/queries.jsonl`;
- `data/dataset/measure_corpus.jsonl`;
- `data/dataset/eval_manifest.json`;
- `docs/PROVENANCE.md`.

Preserve these records when redistributing the dataset or publishing derivative datasets.
