from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.crawler.robots import (
    USER_AGENT,
    RobotsChecker,
)
from app.crawler.url_utils import (
    URLValidationError,
    normalize_url,
    resolve_hostname,
    validate_url,
)
from app.extraction.parser import (
    ExtractedPage,
    extract_page,
)


REQUEST_TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)

MAX_RESPONSE_SIZE = 5 * 1024 * 1024

MAX_PAGES = 10
MAX_DEPTH = 2


class CrawlError(RuntimeError):
    """Raised when a website cannot be crawled safely."""


@dataclass(slots=True)
class CrawledPage:
    url: str
    depth: int
    page: ExtractedPage


@dataclass(slots=True)
class CrawlResult:
    start_url: str
    pages: list[CrawledPage]
    failed_urls: list[str]


def is_same_domain(
    url: str,
    root_hostname: str,
) -> bool:
    """Check whether a URL belongs to the root domain."""

    hostname = urlparse(url).hostname

    if hostname is None:
        return False

    return hostname.lower() == root_hostname.lower()


def extract_links(
    html: str,
    base_url: str,
    root_hostname: str,
) -> set[str]:
    """Extract normalized internal HTML links."""

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    links: set[str] = set()

    for anchor in soup.find_all("a", href=True):

        href = anchor.get("href")

        if not isinstance(href, str):
            continue

        absolute_url = urljoin(
            base_url,
            href,
        )

        try:
            normalized = normalize_url(
                absolute_url
            )

            normalized = validate_url(
                normalized
            )

        except URLValidationError:
            continue

        parsed = urlparse(normalized)

        if parsed.scheme not in {"http", "https"}:
            continue

        if not is_same_domain(
            normalized,
            root_hostname,
        ):
            continue

        links.add(normalized)

    return links


async def fetch_document(
    client: httpx.AsyncClient,
    robots: RobotsChecker,
    url: str,
) -> tuple[ExtractedPage, str]:
    """
    Fetch a webpage and return both extracted content
    and the raw HTML for link discovery.
    """

    normalized_url = validate_url(url)

    hostname = httpx.URL(
        normalized_url
    ).host

    if hostname is None:
        raise CrawlError(
            "Invalid hostname."
        )

    resolve_hostname(hostname)

    allowed = await robots.can_fetch(
        client,
        normalized_url,
    )

    if not allowed:
        raise CrawlError(
            "Crawling this URL is disallowed by robots.txt."
        )

    try:
        response = await client.get(
            normalized_url,
        )

    except httpx.TimeoutException as exc:
        raise CrawlError(
            "The website took too long to respond."
        ) from exc

    except httpx.HTTPError as exc:
        raise CrawlError(
            f"Failed to fetch website: {exc}"
        ) from exc

    if response.status_code >= 400:
        raise CrawlError(
            f"Website returned HTTP {response.status_code}."
        )

    content_type = response.headers.get(
        "content-type",
        "",
    ).lower()

    if (
        "text/html" not in content_type
        and "application/xhtml+xml" not in content_type
    ):
        raise CrawlError(
            "URL does not point to an HTML page."
        )

    content_length = response.headers.get(
        "content-length"
    )

    if content_length:
        try:
            if int(content_length) > MAX_RESPONSE_SIZE:
                raise CrawlError(
                    "The webpage is too large to process."
                )
        except ValueError:
            pass

    if len(response.content) > MAX_RESPONSE_SIZE:
        raise CrawlError(
            "The webpage is too large to process."
        )

    page = extract_page(
        response.text
    )

    return page, response.text


async def crawl_website(
    start_url: str,
    max_pages: int = MAX_PAGES,
    max_depth: int = MAX_DEPTH,
) -> CrawlResult:
    """
    Crawl a website using breadth-first traversal.

    Only pages belonging to the same hostname are followed.
    """

    normalized_start = normalize_url(
        validate_url(start_url)
    )

    root_hostname = urlparse(
        normalized_start
    ).hostname

    if root_hostname is None:
        raise CrawlError(
            "Could not determine website hostname."
        )

    queue: deque[tuple[str, int]] = deque()

    queue.append(
        (normalized_start, 0)
    )

    visited: set[str] = set()

    pages: list[CrawledPage] = []
    failed_urls: list[str] = []

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,"
            "application/xhtml+xml"
        ),
    }

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        headers=headers,
    ) as client:

        robots = RobotsChecker()

        while queue and len(pages) < max_pages:

            current_url, depth = queue.popleft()

            if current_url in visited:
                continue

            visited.add(current_url)

            try:
                page, raw_html = await fetch_document(
                    client,
                    robots,
                    current_url,
                )

                pages.append(
                    CrawledPage(
                        url=current_url,
                        depth=depth,
                        page=page,
                    )
                )

            except (
                CrawlError,
                URLValidationError,
            ):
                failed_urls.append(
                    current_url
                )
                continue

            if depth >= max_depth:
                continue

            links = extract_links(
                raw_html,
                current_url,
                root_hostname,
            )

            for link in sorted(links):

                if link in visited:
                    continue

                if any(
                    queued_url == link
                    for queued_url, _ in queue
                ):
                    continue

                queue.append(
                    (link, depth + 1)
                )

    return CrawlResult(
        start_url=normalized_start,
        pages=pages,
        failed_urls=failed_urls,
    )