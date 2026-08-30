from app.retrieval.chunker import (
    TextChunk,
)
from app.retrieval.index import (
    TFIDFIndex,
)


def test_tfidf_retrieval():

    chunks = [
        TextChunk(
            id=0,
            text=(
                "We provide web development "
                "and software engineering services."
            ),
            source_url="https://example.com/services",
            title="Services",
            depth=1,
        ),
        TextChunk(
            id=1,
            text=(
                "Our headquarters are located "
                "in Chennai."
            ),
            source_url="https://example.com/about",
            title="About",
            depth=1,
        ),
        TextChunk(
            id=2,
            text=(
                "The company was founded in 2018."
            ),
            source_url="https://example.com/about",
            title="About",
            depth=1,
        ),
    ]

    index = TFIDFIndex()

    index.build(chunks)

    results = index.search(
        "What services do you provide?",
        top_k=2,
    )

    assert len(results) == 2

    assert (
        "web development"
        in results[0].chunk.text
    )

    assert results[0].score > 0