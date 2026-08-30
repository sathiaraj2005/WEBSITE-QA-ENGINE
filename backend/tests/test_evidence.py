from app.retrieval.evidence import (
    EvidenceExtractor,
)
from app.retrieval.sentence_ranker import (
    RankedSentence,
)


def test_evidence_extraction():

    ranked_sentences = [
        RankedSentence(
            sentence=(
                "We provide web development "
                "services."
            ),
            score=0.92,
            source_url=(
                "https://example.com/services"
            ),
            title="Services",
            chunk_id=0,
        ),
        RankedSentence(
            sentence=(
                "We provide web development "
                "services."
            ),
            score=0.88,
            source_url=(
                "https://example.com/services"
            ),
            title="Services",
            chunk_id=0,
        ),
        RankedSentence(
            sentence=(
                "Our software engineering team "
                "builds scalable applications."
            ),
            score=0.72,
            source_url=(
                "https://example.com/services"
            ),
            title="Services",
            chunk_id=0,
        ),
        RankedSentence(
            sentence=(
                "Our office is located in Chennai."
            ),
            score=0.05,
            source_url=(
                "https://example.com/about"
            ),
            title="About",
            chunk_id=1,
        ),
    ]

    extractor = EvidenceExtractor(
        min_score=0.15,
        max_evidence=5,
    )

    evidence = extractor.extract(
        ranked_sentences
    )

    assert len(evidence) == 2

    assert (
        evidence[0].sentence
        == "We provide web development services."
    )

    assert (
        evidence[1].sentence
        == (
            "Our software engineering team "
            "builds scalable applications."
        )
    )

    assert evidence[0].score == 0.92

    assert (
        evidence[0].source_url
        == "https://example.com/services"
    )


def test_evidence_limit():

    ranked_sentences = [
        RankedSentence(
            sentence=f"Relevant sentence {i}.",
            score=0.8 - (i * 0.01),
            source_url="https://example.com",
            title="Test",
            chunk_id=i,
        )
        for i in range(10)
    ]

    extractor = EvidenceExtractor(
        min_score=0.15,
        max_evidence=3,
    )

    evidence = extractor.extract(
        ranked_sentences
    )

    assert len(evidence) == 3


def test_low_score_evidence_is_removed():

    ranked_sentences = [
        RankedSentence(
            sentence="Weak evidence.",
            score=0.08,
            source_url="https://example.com",
            title="Test",
            chunk_id=0,
        )
    ]

    extractor = EvidenceExtractor(
        min_score=0.15,
    )

    evidence = extractor.extract(
        ranked_sentences
    )

    assert evidence == []