from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
    urlunparse,
)

ALLOWED_SCHEMES = {"http", "https"}

BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "metadata",
}


class URLValidationError(ValueError):
    """Raised when a user-provided URL is unsafe or invalid."""


def validate_url(url: str) -> str:
    """
    Validate and normalize a user-provided URL.

    Security goals:
    - Only allow HTTP/HTTPS.
    - Reject credentials in URLs.
    - Reject localhost/internal hostnames.
    - Reject private, loopback, link-local and reserved IPs.
    """

    url = url.strip()

    if not url:
        raise URLValidationError("URL cannot be empty.")

    parsed = urlparse(url)

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise URLValidationError(
            "Only HTTP and HTTPS URLs are supported."
        )

    if not parsed.hostname:
        raise URLValidationError("URL must contain a valid hostname.")

    if parsed.username or parsed.password:
        raise URLValidationError(
            "URLs containing credentials are not allowed."
        )

    hostname = parsed.hostname.rstrip(".").lower()

    if hostname in BLOCKED_HOSTNAMES:
        raise URLValidationError(
            "Local or internal hosts are not allowed."
        )

    # Reject direct IP addresses that point to internal networks.
    try:
        ip = ipaddress.ip_address(hostname)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise URLValidationError(
                "Private or internal IP addresses are not allowed."
            )

    except ValueError:
        # Hostname is not an IP address.
        pass

    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc,
    )

    return normalized.geturl()


def resolve_hostname(hostname: str) -> list[str]:
    """
    Resolve a hostname and return its IP addresses.

    This helps prevent DNS-based SSRF where a public hostname
    resolves to an internal IP address.
    """

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise URLValidationError(
            f"Could not resolve hostname: {hostname}"
        ) from exc

    addresses = {
        result[4][0]
        for result in results
    }

    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise URLValidationError(
                "The target hostname resolves to a private or internal IP."
            )

    return sorted(addresses)

def normalize_url(url: str) -> str:
    """
    Normalize a URL for crawling.

    Removes:
    - fragments
    - common tracking parameters
    - trailing slash differences
    """

    parsed = urlparse(url)

    tracking_params = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid",
    }

    query_params = [
        (key, value)
        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True,
        )
        if key.lower() not in tracking_params
    ]

    path = parsed.path or "/"

    if path != "/":
        path = path.rstrip("/")

    normalized = urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",
            urlencode(query_params),
            "",
        )
    )

    return normalized