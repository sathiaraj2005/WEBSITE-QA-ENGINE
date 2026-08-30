from app.retrieval.chunker import TextChunk
from app.retrieval.hybrid import HybridRetriever


def test_hybrid_retrieval():

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

    retriever = HybridRetriever()

    retriever.build(chunks)

    results = retriever.search(
        "What services do you provide?",
        top_k=2,
    )

    assert len(results) == 2

    assert (
        "web development"
        in results[0].chunk.text
    )

    assert results[0].score > 0

    assert results[0].tfidf_score > 0

    assert results[0].keyword_score > 0