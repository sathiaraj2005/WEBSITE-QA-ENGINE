from app.citations.builder import (
    CitationBuilder,
)
from app.retrieval.evidence import Evidence


def make_evidence(
    sentence: str,
    url: str,
    title: str,
    score: float,
) -> Evidence:

    return Evidence(
        sentence=sentence,
        score=score,
        source_url=url,
        title=title,
        chunk_id=0,
    )


def test_build_citations():

    evidence = [
        make_evidence(
            sentence=(
                "We provide web development services."
            ),
            url="https://example.com/services",
            title="Services",
            score=0.92,
        ),
        make_evidence(
            sentence=(
                "The company was founded in 2018."
            ),
            url="https://example.com/about",
            title="About",
            score=0.75,
        ),
    ]

    builder = CitationBuilder()

    citations = builder.build(evidence)

    assert len(citations) == 2

    assert (
        citations[0].url
        == "https://example.com/services"
    )

    assert (
        citations[0].title
        == "Services"
    )

    assert (
        citations[0].evidence
        == "We provide web development services."
    )

    assert citations[0].score == 0.92


def test_duplicate_sources_are_removed():

    evidence = [
        make_evidence(
            sentence="We provide web development services.",
            url="https://example.com/services",
            title="Services",
            score=0.92,
        ),
        make_evidence(
            sentence="We also build software.",
            url="https://example.com/services",
            title="Services",
            score=0.80,
        ),
        make_evidence(
            sentence="We are based in Chennai.",
            url="https://example.com/about",
            title="About",
            score=0.70,
        ),
    ]

    builder = CitationBuilder()

    citations = builder.build(evidence)

    assert len(citations) == 2

    assert (
        citations[0].url
        == "https://example.com/services"
    )

    assert (
        citations[1].url
        == "https://example.com/about"
    )


def test_empty_evidence_returns_no_citations():

    builder = CitationBuilder()

    citations = builder.build([])

    assert citations == []