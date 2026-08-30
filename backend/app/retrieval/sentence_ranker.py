from __future__ import annotations

import re
from dataclasses import dataclass

from app.retrieval.chunker import TextChunk
from app.retrieval.hybrid import HybridRetriever


@dataclass(slots=True)
class RankedSentence:
    sentence: str
    score: float
    source_url: str
    title: str
    chunk_id: int


class SentenceRanker:
    """
    Deterministic sentence-level ranking.

    Ranking signals:

        60% TF-IDF similarity
        30% keyword overlap
        10% phrase overlap
    """

    TFIDF_WEIGHT = 0.60
    KEYWORD_WEIGHT = 0.30
    PHRASE_WEIGHT = 0.10

    def __init__(self) -> None:
        self.tfidf = None

    @staticmethod
    def split_sentences(text: str) -> list[str]:
        """
        Split text into sentences while handling
        common punctuation.
        """

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text.strip(),
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @staticmethod
    def tokenize(text: str) -> set[str]:
        """Return normalized word tokens."""

        return set(
            re.findall(
                r"\b[a-zA-Z0-9]+\b",
                text.lower(),
            )
        )

    @classmethod
    def keyword_score(
        cls,
        query: str,
        sentence: str,
    ) -> float:
        """
        Calculate normalized keyword overlap.
        """

        query_tokens = cls.tokenize(query)
        sentence_tokens = cls.tokenize(sentence)

        if not query_tokens:
            return 0.0

        overlap = (
            query_tokens & sentence_tokens
        )

        return len(overlap) / len(query_tokens)

    @classmethod
    def phrase_score(
        cls,
        query: str,
        sentence: str,
    ) -> float:
        """
        Detect consecutive query-word phrases.

        Returns a value between 0 and 1.
        """

        query_tokens = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            query.lower(),
        )

        if len(query_tokens) < 2:
            return 0.0

        sentence_lower = sentence.lower()

        phrase_matches = 0
        phrase_count = len(query_tokens) - 1

        for index in range(phrase_count):
            phrase = (
                f"{query_tokens[index]} "
                f"{query_tokens[index + 1]}"
            )

            if phrase in sentence_lower:
                phrase_matches += 1

        return phrase_matches / phrase_count

    def rank(
        self,
        query: str,
        chunks: list[TextChunk],
        top_k: int = 5,
    ) -> list[RankedSentence]:
        """
        Rank sentences extracted from candidate chunks.
        """

        if not query.strip():
            return []

        if not chunks:
            return []

        documents: list[str] = []
        sentence_records: list[
            tuple[str, TextChunk]
        ] = []

        for chunk in chunks:
            sentences = self.split_sentences(
                chunk.text
            )

            for sentence in sentences:
                documents.append(sentence)
                sentence_records.append(
                    (sentence, chunk)
                )

        if not documents:
            return []

        from sklearn.feature_extraction.text import (
            TfidfVectorizer,
        )
        from sklearn.metrics.pairwise import (
            cosine_similarity,
        )

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        try:
            matrix = vectorizer.fit_transform(
                documents
            )
        except ValueError:
            return []

        query_vector = vectorizer.transform(
            [query]
        )

        tfidf_scores = cosine_similarity(
            query_vector,
            matrix,
        ).flatten()

        ranked: list[RankedSentence] = []

        for index, (
            sentence,
            chunk,
        ) in enumerate(sentence_records):

            tfidf_score = float(
                tfidf_scores[index]
            )

            keyword_score = (
                self.keyword_score(
                    query,
                    sentence,
                )
            )

            phrase_score = (
                self.phrase_score(
                    query,
                    sentence,
                )
            )

            final_score = (
                self.TFIDF_WEIGHT * tfidf_score
                + self.KEYWORD_WEIGHT * keyword_score
                + self.PHRASE_WEIGHT * phrase_score
            )

            ranked.append(
                RankedSentence(
                    sentence=sentence,
                    score=final_score,
                    source_url=chunk.source_url,
                    title=chunk.title,
                    chunk_id=chunk.id,
                )
            )

        ranked.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return ranked[:top_k]