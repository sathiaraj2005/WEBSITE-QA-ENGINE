from app.retrieval.chunker import TextChunk
from app.retrieval.sentence_ranker import (
    SentenceRanker,
)


def test_sentence_ranking():

    chunks = [
        TextChunk(
            id=0,
            text=(
                "Welcome to our company. "
                "We provide web development "
                "and software engineering services. "
                "Our office is open from 9 AM to 6 PM."
            ),
            source_url="https://example.com/services",
            title="Services",
            depth=1,
        ),
        TextChunk(
            id=1,
            text=(
                "Our headquarters are located "
                "in Chennai. "
                "The company was founded in 2018."
            ),
            source_url="https://example.com/about",
            title="About",
            depth=1,
        ),
    ]

    ranker = SentenceRanker()

    results = ranker.rank(
        query="What web development services do you provide?",
        chunks=chunks,
        top_k=3,
    )

    assert len(results) == 3

    assert (
        "web development"
        in results[0].sentence
    )

    assert results[0].score > 0

    assert (
        results[0].source_url
        == "https://example.com/services"
    )