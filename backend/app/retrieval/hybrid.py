from __future__ import annotations

import re
from dataclasses import dataclass

from app.retrieval.chunker import TextChunk
from app.retrieval.index import TFIDFIndex


@dataclass(slots=True)
class HybridSearchResult:
    chunk: TextChunk
    score: float
    tfidf_score: float
    keyword_score: float


class HybridRetriever:
    """
    Hybrid deterministic retriever.

    Combines:
        1. TF-IDF cosine similarity
        2. Keyword overlap

    Final score:

        0.70 * TF-IDF
        + 0.30 * keyword overlap
    """

    TFIDF_WEIGHT = 0.70
    KEYWORD_WEIGHT = 0.30

    def __init__(self) -> None:
        self.tfidf_index = TFIDFIndex()
        self.chunks: list[TextChunk] = []

    def build(
        self,
        chunks: list[TextChunk],
    ) -> None:
        """Build the underlying TF-IDF index."""

        if not chunks:
            raise ValueError(
                "Cannot build hybrid index without chunks."
            )

        self.chunks = chunks

        self.tfidf_index.build(chunks)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """
        Convert text into normalized keyword tokens.
        """

        return set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                text.lower(),
            )
        )

    @classmethod
    def _keyword_score(
        cls,
        query: str,
        document: str,
    ) -> float:
        """
        Calculate normalized keyword overlap.

        Score is between 0 and 1.
        """

        query_tokens = cls._tokenize(query)
        document_tokens = cls._tokenize(document)

        if not query_tokens:
            return 0.0

        matched_tokens = (
            query_tokens & document_tokens
        )

        return len(matched_tokens) / len(
            query_tokens
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[HybridSearchResult]:
        """Return hybrid-ranked chunks."""

        if not query.strip():
            return []

        # Retrieve a larger candidate pool first.
        candidate_k = min(
            max(top_k * 3, 10),
            len(self.chunks),
        )

        tfidf_results = self.tfidf_index.search(
            query,
            top_k=candidate_k,
        )

        results: list[HybridSearchResult] = []

        for result in tfidf_results:
            keyword_score = self._keyword_score(
                query,
                result.chunk.text,
            )

            hybrid_score = (
                self.TFIDF_WEIGHT * result.score
                + self.KEYWORD_WEIGHT * keyword_score
            )

            results.append(
                HybridSearchResult(
                    chunk=result.chunk,
                    score=hybrid_score,
                    tfidf_score=result.score,
                    keyword_score=keyword_score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]