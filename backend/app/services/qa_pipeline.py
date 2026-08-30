from __future__ import annotations

from dataclasses import dataclass

from app.answer.generator import (
    DeterministicAnswerGenerator,
    GeneratedAnswer,
)
from app.citations.builder import (
    CitationBuilder,
    SourceCitation,
)
from app.retrieval.chunker import (
    TextChunk,
    build_chunks,
)
from app.retrieval.evidence import (
    Evidence,
    EvidenceExtractor,
)
from app.retrieval.hybrid import (
    HybridRetriever,
)
from app.retrieval.sentence_ranker import (
    SentenceRanker,
)
from app.services.session_store import (
    WebsiteSession,
    session_store,
)

@dataclass(slots=True)
class AnalysisResult:
    session: WebsiteSession
    pages_crawled: int
    pages_failed: int
    total_characters: int


@dataclass(slots=True)
class QuestionResult:
    generated_answer: GeneratedAnswer
    citations: list[SourceCitation]


class QAPipeline:
    """
    Orchestrates the complete deterministic QA pipeline.

    Analysis:
        crawled pages
            ↓
        chunks
            ↓
        hybrid index
            ↓
        session

    Question answering:
        question
            ↓
        hybrid retrieval
            ↓
        sentence ranking
            ↓
        evidence extraction
            ↓
        deterministic answer
            ↓
        source citations
    """

    def __init__(self) -> None:
        self.sentence_ranker = SentenceRanker()

        self.evidence_extractor = (
            EvidenceExtractor()
        )

        self.answer_generator = (
            DeterministicAnswerGenerator()
        )

        self.citation_builder = (
            CitationBuilder()
        )

    def create_session(
        self,
        url: str,
        pages: list,
        pages_failed: int,
    ) -> AnalysisResult:

        chunks: list[TextChunk] = build_chunks(
            pages
        )

        if not chunks:
            raise ValueError(
                "No searchable content could be "
                "created from the crawled pages."
            )

        retriever = HybridRetriever()

        retriever.build(chunks)

        session = session_store.create(
            url=url,
            chunks=chunks,
            retriever=retriever,
        )

        total_characters = sum(
            len(page.page.text)
            for page in pages
        )

        return AnalysisResult(
            session=session,
            pages_crawled=len(pages),
            pages_failed=pages_failed,
            total_characters=total_characters,
        )

    def answer_question(
        self,
        session: WebsiteSession,
        question: str,
        top_k: int = 5,
    ) -> QuestionResult:

        search_results = session.retriever.search(
            question,
            top_k=top_k,
        )

        candidate_chunks = [
            result.chunk
            for result in search_results
        ]

        ranked_sentences = (
            self.sentence_ranker.rank(
                question,
                candidate_chunks,
                top_k=top_k,
            )
        )

        evidence = (
            self.evidence_extractor.extract(
                ranked_sentences
            )
        )

        # Short-page fallback:
        # Tiny pages can produce weak lexical scores even when
        # the available sentence is the best possible evidence.
        if (
            not evidence
            and ranked_sentences
            and sum(
                len(chunk.text)
                for chunk in session.chunks
         ) <= 500
        ):
            strongest = ranked_sentences[0]

            if strongest.score > 0.0:
                evidence = [
                    Evidence(
                        sentence=strongest.sentence,
                        score=strongest.score,
                        source_url=strongest.source_url,
                        title=strongest.title,
                        chunk_id=strongest.chunk_id,
                    )
                ]

        generated_answer = (
            self.answer_generator.generate(
                question,
                evidence,
            )
        )

        citations = (
            self.citation_builder.build(
                evidence
            )
        )

        return QuestionResult(
            generated_answer=generated_answer,
            citations=citations
        )


qa_pipeline = QAPipeline()