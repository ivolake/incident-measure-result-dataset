from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .io import read_jsonl

TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(text)]


class BM25Ranker:
    """Dependency-free BM25-like implementation aligned with the source evaluation run."""

    def __init__(self, documents: list[dict[str, Any]], text_key: str = "measure_text", k1: float = 1.5, b: float = 0.75):
        if not documents:
            raise ValueError("BM25Ranker requires at least one document")
        self.documents = documents
        self.text_key = text_key
        self.k1 = k1
        self.b = b
        self.term_frequencies = [Counter(tokenize(str(doc.get(text_key, ""))) ) for doc in documents]
        self.doc_lengths = [sum(freqs.values()) for freqs in self.term_frequencies]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)
        document_frequency: Counter[str] = Counter()
        for frequencies in self.term_frequencies:
            document_frequency.update(frequencies.keys())
        document_count = len(documents)
        self.idf = {
            term: math.log(1 + (document_count - freq + 0.5) / (freq + 0.5))
            for term, freq in document_frequency.items()
        }

    def score(self, query: str, doc_index: int) -> float:
        query_terms = Counter(tokenize(query))
        frequencies = self.term_frequencies[doc_index]
        doc_length = self.doc_lengths[doc_index]
        score = 0.0
        for token, query_count in query_terms.items():
            term_frequency = frequencies.get(token, 0)
            if term_frequency == 0:
                continue
            length_factor = 1 - self.b
            if self.avg_doc_length:
                length_factor += self.b * (doc_length / self.avg_doc_length)
            denominator = term_frequency + self.k1 * length_factor
            score += query_count * self.idf.get(token, 0.0) * (term_frequency * (self.k1 + 1)) / denominator
        return score

    def rank(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        scored = [(self.score(query, index), doc) for index, doc in enumerate(self.documents)]
        scored.sort(key=lambda item: (-item[0], str(item[1].get("measure_id", ""))))
        return [
            {
                "rank": rank,
                "measure_id": doc.get("measure_id"),
                "score": round(float(score), 6),
            }
            for rank, (score, doc) in enumerate(scored[:top_k], start=1)
        ]


def rank_bm25(dataset_dir: str | Path, top_k: int = 5) -> list[dict[str, Any]]:
    root = Path(dataset_dir)
    queries = read_jsonl(root / "external_queries.jsonl")
    measures = read_jsonl(root / "external_measure_corpus.jsonl")
    ranker = BM25Ranker(measures)
    return [
        {
            "method": "bm25",
            "query_id": query.get("query_id"),
            "top_k": ranker.rank(str(query.get("query_text", "")), top_k=top_k),
        }
        for query in queries
    ]


def rank_embeddings(dataset_dir: str | Path, model_name: str, top_k: int = 5, batch_size: int = 32) -> list[dict[str, Any]]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Embedding ranking requires optional dependencies. Install with: pip install -e .[embeddings]"
        ) from exc

    import numpy as np

    root = Path(dataset_dir)
    queries = read_jsonl(root / "external_queries.jsonl")
    measures = read_jsonl(root / "external_measure_corpus.jsonl")
    model = SentenceTransformer(model_name)
    query_texts = [str(query.get("query_text", "")) for query in queries]
    measure_texts = [str(measure.get("measure_text", "")) for measure in measures]
    query_vectors = model.encode(query_texts, batch_size=batch_size, normalize_embeddings=True, convert_to_numpy=True)
    measure_vectors = model.encode(measure_texts, batch_size=batch_size, normalize_embeddings=True, convert_to_numpy=True)
    scores = np.matmul(query_vectors, measure_vectors.T)
    outputs: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        ranked_indexes = np.argsort(-scores[query_index])[:top_k]
        outputs.append(
            {
                "method": f"embedding:{model_name}",
                "query_id": query.get("query_id"),
                "top_k": [
                    {
                        "rank": rank,
                        "measure_id": measures[int(index)].get("measure_id"),
                        "score": round(float(scores[query_index, int(index)]), 6),
                    }
                    for rank, index in enumerate(ranked_indexes, start=1)
                ],
            }
        )
    return outputs
