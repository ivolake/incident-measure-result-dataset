# Набор данных для оценки релевантности мер инцидентам

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Queries](https://img.shields.io/badge/queries-30-informational)
![Measures](https://img.shields.io/badge/measures-25-informational)
![Labels](https://img.shields.io/badge/labels-600-informational)
![Annotation](https://img.shields.io/badge/annotation-LLM--panel-orange)
![Data Notice](https://img.shields.io/badge/data-notice-lightgrey)

Небольшой публичный evaluation seed для ранжирования мер реагирования на киберинциденты.

Задача простая:

```text
описание инцидента + описание кандидатной меры реагирования -> ранжированный список мер
```

Датасет предназначен для диагностической cold-start оценки ранжирования. Метод ранжирования получает только текст инцидента и текст кандидатной меры, а затем ранжирует каталог из 25 мер. Нельзя использовать label-поля, audit-поля, source locators, предшествующую кандидатную метаинформацию или annotation artifacts как вход модели.

## Что Это

- 30 source-derived описаний киберинцидентов.
- 25 source-derived или source-normalized кандидатных мер из смешанного response/defense каталога.
- 600 согласованных labels для размеченных пар `инцидент -> мера`.
- Пять независимых файлов Codex subagent annotators, полученных в режиме `5.5 xhigh`.
- Детерминированная adjudication поверх пяти файлов аннотаторов.
- Утилиты для валидации, BM25-ранжирования, опционального embedding-ранжирования и расчета метрик.

## Чем Это Не Является

- Это не human expert benchmark.
- Это не датасет для training, fine-tuning, hard-negative mining, prompt tuning или hyperparameter tuning.
- Это не полный SOC playbook и не production benchmark для incident response.
- Это не доказательство, что метод операционно безопасен без отдельной экспертной проверки.

Используйте его как компактный evaluation seed для regression checks, ranking diagnostics, method comparison и error analysis.

## Датасет Кратко

| Показатель | Значение |
|---|---:|
| Incident queries | 30 |
| Candidate measures | 25 |
| Judged pairs | 600 |
| Possible query-measure pairs | 750 |
| Unjudged pairs | 150 |
| Independent annotators | 5 |
| Grade scale | 0..3 |

Состав источников:

| Слой | Семейство источников | Кол-во |
|---|---|---:|
| Incident queries | VCDB validated incident summaries | 30 |
| Candidate measures | ATC RE&CT response actions | 7 |
| Candidate measures | MITRE D3FEND defensive techniques | 13 |
| Candidate measures | MITRE ATT&CK mitigations | 5 |

Распределение labels:

| Grade | Count |
|---:|---:|
| 0 | 428 |
| 1 | 82 |
| 2 | 88 |
| 3 | 2 |

Для оценки используйте:

- graded ranking: полная шкала `0..3`;
- usable positives: `grade >= 2`;
- strict positives: `grade == 3`.

Строгих положительных labels всего два, поэтому strict-positive метрики нестабильны и не должны быть единственным критерием решения.

## Как Собран Датасет

Model-facing текст является source-derived, а не заново сгенерированным для этого репозитория:

- `queries.jsonl` содержит 30 incident summaries из VCDB validated incident records.
- `measure_corpus.jsonl` содержит 25 описаний кандидатных мер из MITRE ATT&CK mitigations, MITRE D3FEND defensive techniques и ATC RE&CT response actions.
- Текстовые поля инцидентов и мер являются verbatim или normalized source text; source locators и SHA-256 hashes сохранены там, где это доступно.
- Репозиторий не генерировал новый текст инцидентов или новый текст мер для model input.

Каталог мер намеренно смешанный. RE&CT дает конкретные SOC response actions, D3FEND дает defensive techniques, а ATT&CK дает более широкие mitigation controls. Поэтому задача проверяет не только тематическое сходство текста: ranker должен предпочитать меры, которые практически применимы к инциденту и фазе реагирования, и не завышать широкие или лишь соседние controls.

Размеченные пары `incident -> candidate measure` были собраны в blinded review queue. Каждый выбранный инцидент получил 20 размеченных кандидатных мер из каталога на 25 мер. Candidate selection использовал audit-only candidate signals и response-phase coverage, но причины выбора были скрыты от аннотаторов и не являются model inputs.

Annotation layer создан в этом репозитории: Codex subagents оценили выбранные пары, а deterministic adjudication сформировала финальные `relevance_grade` labels. Source datasets дают текст и provenance; Codex дал annotation judgments; логика репозитория дала candidate-pair selection и финальную агрегацию.

Unjudged query-measure pairs не являются negative examples.

## Быстрый Старт

Создайте и активируйте virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

Провалидируйте датасет:

```powershell
python scripts\validate_dataset.py --dataset data\dataset --annotations data\annotations\llm_panel --out outputs\validation_report.json
```

Запустите dependency-free BM25 baseline:

```powershell
python scripts\rank_bm25.py --dataset data\dataset --top-k 5 --out outputs\bm25_topk.jsonl
python scripts\evaluate.py --dataset data\dataset --predictions outputs\bm25_topk.jsonl --out outputs\bm25_metrics.json
```

Опциональное embedding ranking требует extra `embeddings`:

```powershell
python -m pip install -e .[embeddings]
python scripts\rank_embeddings.py --dataset data\dataset --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --top-k 5 --out outputs\miniLM_topk.jsonl
python scripts\evaluate.py --dataset data\dataset --predictions outputs\miniLM_topk.jsonl --out outputs\miniLM_metrics.json
```

Форма через установленную команду:

```powershell
incident-measure-result validate --dataset data\dataset --annotations data\annotations\llm_panel
incident-measure-result rank-bm25 --dataset data\dataset --out outputs\bm25_topk.jsonl
incident-measure-result evaluate --dataset data\dataset --predictions outputs\bm25_topk.jsonl
```

## Baselines

Эти результаты взяты из prior internal evaluation run на том же 30-query / 25-measure adjudicated candidate dataset. Здесь перечислены только public-safe методы, не обученные на этом датасете. См. `docs/BASELINES.md` для определений и caveats.

| Method | Model / setup | Trained on this dataset? | graded nDCG@5 | usable recall@5 | usable MRR@5 |
|---|---|---:|---:|---:|---:|
| BM25 | raw lexical baseline | No | 0.349872 | 0.418340 | 0.391667 |
| Masked BM25 | lexical baseline with leakage-prone fields masked | No | 0.349872 | 0.418340 | 0.391667 |
| Zero-shot EmbeddingGemma | `google/embeddinggemma-300m` | No | 0.317921 | 0.220459 | 0.445833 |
| Zero-shot multilingual E5 | `intfloat/multilingual-e5-base` | No | 0.158707 | 0.125568 | 0.128472 |

Dense baselines являются off-the-shelf / zero-shot. Для публичной baseline-таблицы не использовались fine-tuning, hard-negative mining, prompt tuning или hyperparameter tuning на этом датасете.

## Annotation And Adjudication

Label layer получен пятью независимыми Codex subagent annotators в режиме `5.5 xhigh`. Каждый annotator просматривал одну и ту же blinded queue и записывал независимый файл. Очередь скрывала model outputs, prior candidate labels, pair-selection reasons, решения других annotators и финальные adjudication decisions.

Каждый annotator заполнял:

- `relevance_grade`;
- `incident_fit_grade`;
- `phase_fit_grade`;
- `measure_applicability_grade`;
- `grade3_rule_satisfied`;
- downgrade и non-applicability reasons.

Финальные labels получены deterministic median aggregation с conservative downgrade rules:

1. Вычислить медиану пяти значений `relevance_grade`.
2. Вычислить медианы для `incident_fit_grade`, `phase_fit_grade` и `measure_applicability_grade`.
3. Ограничить начальную финальную оценку самым слабым median subgrade.
4. Если disagreement между annotators сильный и кандидатная финальная оценка `>= 2`, понизить ее на один уровень.
5. Разрешить финальный grade `3` только если минимум 4 из 5 annotators поставили `3` и все median subgrades равны `3`.
6. Применить caps по measure concreteness: `specific_action <= 3`, `partial_action <= 2`, `reference_only <= 1`, `non_measure <= 0`.
7. Сохранить merged downgrade и non-applicability reasons для audit. Эти поля не являются model inputs.

Codex app build/version не был сохранен в dataset records.

## Структура Репозитория

```text
data/
  dataset/                 # Основной пакет датасета
  annotations/llm_panel/   # Пять независимых файлов annotators
  review_audit/            # Blinded review queue и sampling audit
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

## Документация

| Документ | Назначение |
|---|---|
| `docs/DATASET_CARD.md` | Scope датасета, размер, label distribution, intended use, limitations. |
| `docs/BASELINES.md` | Baseline metrics, определения методов и политика исключения методов. |
| `docs/SCHEMA.md` | Model-facing, label-only, audit-only и provenance fields. |
| `docs/ANNOTATION_PROTOCOL.md` | Annotation units, Codex subagent setup, blinding, adjudication. |
| `docs/EVALUATION_GUIDE.md` | Prediction contract и использование метрик. |
| `docs/PROVENANCE.md` | Source preparation, preserved records, hashes. |
| `docs/SOURCES_AND_LICENSES.md` | Source families и upstream reuse notes. |
| `DATA_NOTICE.md` | Практическое data reuse notice. |

## Цитирование И Повторное Использование

Формальная citation пока не назначена. Если вы используете этот репозиторий, укажите repository URL и сохраните provenance files.

Code и repository documentation покрываются `LICENSE`. Dataset files в `data/` содержат source-derived records и подпадают под upstream notices, кратко описанные в `DATA_NOTICE.md` и `docs/SOURCES_AND_LICENSES.md`. Сохраняйте attribution, upstream notices и source provenance при повторном распространении датасета или производных records.
