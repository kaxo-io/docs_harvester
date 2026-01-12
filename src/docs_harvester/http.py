"""Shared HTTP client with retry logic and proper headers.

Copyright (c) 2025 Kaxo Technologies
Contact: tech@kaxo.io

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if TYPE_CHECKING:
    from requests import Session

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
USER_AGENT = "Kaxo-DocsHarvester/1.0 (https://kaxo.io)"


def create_session(
    *,
    github_token: str | None = None,
    retries: int = DEFAULT_RETRIES,
) -> Session:
    """Create a requests session with retry logic and proper headers.

    Args:
        github_token: Optional GitHub personal access token
        retries: Number of retries for failed requests

    Returns:
        Configured requests Session
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )

    # GitHub token from param, env var, or gh CLI
    token = github_token or os.environ.get("GITHUB_TOKEN")
    if token:
        session.headers.update({"Authorization": f"token {token}"})
        logger.debug("GitHub token configured")

    return session
