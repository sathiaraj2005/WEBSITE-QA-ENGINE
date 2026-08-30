from __future__ import annotations

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx


USER_AGENT = "WebsiteQAEngine/0.1"


class RobotsChecker:
    """Caches and evaluates robots.txt rules for a domain."""

    def __init__(self) -> None:
        self._parsers: dict[str, RobotFileParser] = {}

    async def can_fetch(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> bool:
        """Return whether our crawler may fetch the URL."""

        parsed = urlparse(url)

        origin = f"{parsed.scheme}://{parsed.netloc}"

        if origin not in self._parsers:
            parser = await self._load_robots(
                client,
                origin,
            )

            self._parsers[origin] = parser

        return self._parsers[origin].can_fetch(
            USER_AGENT,
            url,
        )

    async def _load_robots(
        self,
        client: httpx.AsyncClient,
        origin: str,
    ) -> RobotFileParser:
        """Download and parse robots.txt."""

        robots_url = f"{origin}/robots.txt"

        parser = RobotFileParser()

        try:
            response = await client.get(
                robots_url,
                headers={"User-Agent": USER_AGENT},
            )

            if response.status_code == 404:
                parser.parse([])
                return parser

            if response.status_code >= 400:
                # Fail closed when crawling policy cannot be determined.
                parser.parse(
                    [
                        "User-agent: *",
                        "Disallow: /",
                    ]
                )
                return parser

            parser.parse(
                response.text.splitlines()
            )

            return parser

        except httpx.HTTPError:
            parser.parse(
                [
                    "User-agent: *",
                    "Disallow: /",
                ]
            )

            return parser