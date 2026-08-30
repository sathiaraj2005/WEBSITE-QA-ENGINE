from __future__ import annotations

from dataclasses import dataclass

from app.retrieval.sentence_ranker import RankedSentence


@dataclass(slots=True)
class Evidence:
    """
    A selected piece of evidence used to construct
    the final deterministic answer.
    """

    sentence: str
    score: float
    source_url: str
    title: str
    chunk_id: int


class EvidenceExtractor:
    """
    Selects high-quality evidence from ranked sentences.

    The extractor is deliberately deterministic.

    Responsibilities:
        - relevance filtering
        - duplicate removal
        - evidence limits
        - metadata preservation
    """

    # def __init__(
    #     self,
    #     min_score: float = 0.15,
    #     max_evidence: int = 5,
    # ) -> None:

    def __init__(
    self,
    min_score: float = 0.15,
    max_evidence: int = 5,
) -> None:

        if not 0.0 <= min_score <= 1.0:
            raise ValueError(
                "min_score must be between 0 and 1."
            )

        if max_evidence < 1:
            raise ValueError(
                "max_evidence must be at least 1."
            )

        self.min_score = min_score
        self.max_evidence = max_evidence

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize text for duplicate detection.
        """

        return " ".join(
            text.lower().split()
        )

    def extract(
        self,
        ranked_sentences: list[RankedSentence],
    ) -> list[Evidence]:
        """
        Extract the strongest evidence sentences.
        """

        if not ranked_sentences:
            return []

        evidence: list[Evidence] = []

        seen: set[str] = set()

        for ranked in ranked_sentences:

            # Stop once relevance falls below threshold.
            if ranked.score < self.min_score:
                continue

            normalized = self._normalize(
                ranked.sentence
            )

            # Skip exact duplicate evidence.
            if normalized in seen:
                continue

            seen.add(normalized)

            evidence.append(
                Evidence(
                    sentence=ranked.sentence,
                    score=ranked.score,
                    source_url=ranked.source_url,
                    title=ranked.title,
                    chunk_id=ranked.chunk_id,
                )
            )

            if len(evidence) >= self.max_evidence:
                break

        return evidence