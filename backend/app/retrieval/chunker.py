from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class TextChunk:
    """A searchable piece of website content."""

    id: int
    text: str
    source_url: str
    title: str
    depth: int


def split_sentences(text: str) -> list[str]:
    """
    Split text into approximate sentences.

    This intentionally avoids heavyweight NLP dependencies.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def chunk_text(
    text: str,
    max_words: int = 120,
    overlap_words: int = 20,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    Overlap preserves context between neighboring chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks: list[str] = []

    start = 0

    while start < len(words):

        end = min(
            start + max_words,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap_words

    return chunks


def build_chunks(
    pages,
    max_words: int = 120,
    overlap_words: int = 20,
) -> list[TextChunk]:
    """Convert crawled pages into searchable chunks."""

    chunks: list[TextChunk] = []

    chunk_id = 0

    for page in pages:

        page_chunks = chunk_text(
            page.page.text,
            max_words=max_words,
            overlap_words=overlap_words,
        )

        for text in page_chunks:

            chunks.append(
                TextChunk(
                    id=chunk_id,
                    text=text,
                    source_url=page.url,
                    title=page.page.title,
                    depth=page.depth,
                )
            )

            chunk_id += 1

    return chunks