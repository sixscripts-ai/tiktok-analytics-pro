import os
import json
import random
from typing import Dict, Optional

import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
]


def get_random_user_agent() -> str:
    """Return a user-agent string, preferring the TIKTOK_USER_AGENT env var."""
    return os.getenv("TIKTOK_USER_AGENT") or random.choice(USER_AGENTS)


def _base_headers() -> Dict[str, str]:
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": os.getenv(
            "TIKTOK_ACCEPT",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        ),
        "Accept-Language": os.getenv("TIKTOK_ACCEPT_LANGUAGE", "en-US,en;q=0.9"),
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
    }
    extra = os.getenv("TIKTOK_EXTRA_HEADERS")
    if extra:
        try:
            headers.update(json.loads(extra))
        except Exception:
            pass
    return headers


def get_proxy() -> Optional[str]:
    """Return proxy URL from env if configured."""
    return (
        os.getenv("TIKTOK_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("HTTPS_PROXY")
    )


def create_session() -> requests.Session:
    """Create a configured requests session with headers and optional proxy."""
    session = requests.Session()
    session.headers.update(_base_headers())
    proxy = get_proxy()
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})
    return session


def rotate_user_agent(session: requests.Session) -> None:
    """Rotate the User-Agent header on an existing session."""
    session.headers.update({"User-Agent": get_random_user_agent()})
