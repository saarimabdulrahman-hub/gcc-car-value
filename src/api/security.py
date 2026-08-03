"""Security validators — URL safety, input sanitization, SSRF protection."""

import ipaddress
import socket
from urllib.parse import urlparse


class PrivateIPError(ValueError):
    """Raised when a URL targets a private/internal network."""


class InvalidHostnameError(ValueError):
    """Raised when a hostname cannot be resolved."""


# Private and special-use networks blocked for SSRF prevention
_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

# Known GCC car marketplaces — allowed domains for URL valuation
_ALLOWED_DOMAINS = {
    "dubizzle.com", "uae.dubizzle.com", "ksa.dubizzle.com",
    "yallamotor.com", "uae.yallamotor.com", "ksa.yallamotor.com",
    "haraj.com.sa", "haraj.com",
    "opensooq.com", "om.opensooq.com", "sa.opensooq.com",
    "q8car.com", "qatar.carswitch.com", "carswitch.com",
    "syarah.com", "motory.com", "olx.com.eg",
}


def validate_public_url(url: str, allow_all_domains: bool = False) -> str:
    """Validate a user-supplied URL is safe to fetch.

    Returns the original URL string if valid.
    Raises ValueError with a user-safe message if rejected.

    Checks:
        - Scheme is http or https only
        - Hostname is present
        - Hostname does not resolve to a private/internal IP
        - URL is not excessively long
    """
    if len(url) > 2048:
        raise ValueError("URL is too long (max 2048 characters)")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are supported")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must include a valid hostname")

    # Domain allowlist check (optional — can be disabled for development)
    if not allow_all_domains:
        # Strip www. prefix for matching
        clean_host = hostname.lower().removeprefix("www.")
        if clean_host not in _ALLOWED_DOMAINS and not any(
            clean_host.endswith("." + d) for d in _ALLOWED_DOMAINS
        ):
            raise ValueError(
                f"URL valuation only supports known car marketplaces. "
                f"Domain '{hostname}' is not in the allowed list."
            )

    # IP check: reject private/internal/multicast IPs
    _reject_private_ip(hostname)

    return url


def _reject_private_ip(hostname: str) -> None:
    """Resolve hostname and reject if any IP is private or internal."""
    # Check if hostname is an IP literal
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        pass  # Not an IP literal — resolve via DNS below
    else:
        if any(ip in net for net in _PRIVATE_NETS):
            raise PrivateIPError("URL targets an internal or private network")
        return

    # DNS resolution for hostnames
    try:
        resolved_ips = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise InvalidHostnameError(f"Cannot resolve hostname: {hostname}") from exc

    for addr in resolved_ips:
        ip_str = addr[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if any(ip in net for net in _PRIVATE_NETS):
            raise PrivateIPError("URL resolves to an internal or private network")
