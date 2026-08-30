from __future__ import annotations

from dataclasses import dataclass

from app.retrieval.evidence import Evidence


@dataclass(slots=True)
class SourceCitation:
    """
    A source referenced by the final answer.
    """

    url: str
    title: str
    evidence: str
    score: float


class CitationBuilder:
    """
    Builds deterministic source citations from evidence.

    Responsibilities:
        - preserve source URLs
        - preserve page titles
        - connect citations to evidence
        - remove duplicate sources
        - maintain relevance ordering
    """

    def build(
        self,
        evidence: list[Evidence],
    ) -> list[SourceCitation]:
        """
        Build citations from selected evidence.
        """

        if not evidence:
            return []

        citations: list[SourceCitation] = []

        seen_urls: set[str] = set()

        for item in evidence:

            if item.source_url in seen_urls:
                continue

            seen_urls.add(item.source_url)

            citations.append(
                SourceCitation(
                    url=item.source_url,
                    title=item.title,
                    evidence=item.sentence,
                    score=item.score,
                )
            )

        return citations