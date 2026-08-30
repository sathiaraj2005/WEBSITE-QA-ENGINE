from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "svg",
    "canvas",
    "iframe",
    "nav",
    "footer",
    "form",
}


@dataclass(slots=True)
class ExtractedPage:
    title: str
    text: str


def normalize_whitespace(text: str) -> str:
    """Collapse unnecessary whitespace."""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_page(html: str) -> ExtractedPage:
    """Extract meaningful textual content from HTML."""

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    for tag in soup.find_all(REMOVE_TAGS):
        tag.decompose()

    title = ""

    if soup.title:
        title = normalize_whitespace(
            soup.title.get_text(" ", strip=True)
        )

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.body
        or soup
    )

    text = main_content.get_text(
        separator=" ",
        strip=True,
    )

    text = normalize_whitespace(text)

    return ExtractedPage(
        title=title,
        text=text,
    )