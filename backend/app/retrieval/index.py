from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.retrieval.chunker import TextChunk


@dataclass(slots=True)
class SearchResult:
    chunk: TextChunk
    score: float


class TFIDFIndex:
    """
    In-memory TF-IDF search index.

    The index converts website chunks and user queries
    into sparse vectors and ranks them using cosine similarity.
    """

    def __init__(self) -> None:

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=20_000,
            sublinear_tf=True,
        )

        self.chunks: list[TextChunk] = []

        self.matrix = None

    def build(
        self,
        chunks: list[TextChunk],
    ) -> None:
        """Build the TF-IDF matrix from website chunks."""

        if not chunks:
            raise ValueError(
                "Cannot build an index without chunks."
            )

        self.chunks = chunks

        documents = [
            chunk.text
            for chunk in chunks
        ]

        self.matrix = self.vectorizer.fit_transform(
            documents
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Return the most relevant chunks."""

        if self.matrix is None:
            raise RuntimeError(
                "Index has not been built."
            )

        if not query.strip():
            return []

        query_vector = self.vectorizer.transform(
            [query]
        )

        scores = cosine_similarity(
            query_vector,
            self.matrix,
        ).flatten()

        ranked_indices = scores.argsort()[::-1]

        results: list[SearchResult] = []

        for index in ranked_indices[:top_k]:

            score = float(
                scores[index]
            )

            results.append(
                SearchResult(
                    chunk=self.chunks[index],
                    score=score,
                )
            )

        return results