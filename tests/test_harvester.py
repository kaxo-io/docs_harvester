"""Tests for docs_harvester.

Copyright (c) 2025 Kaxo Technologies
Contact: tech@kaxo.io

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

from docs_harvester.harvester import DocHarvester
from docs_harvester.http import create_session


def test_create_session_has_user_agent() -> None:
    """Session should have custom User-Agent."""
    session = create_session()
    assert "Kaxo" in session.headers["User-Agent"]


def test_create_session_with_github_token() -> None:
    """Session should include GitHub token when provided."""
    session = create_session(github_token="test_token")
    assert session.headers["Authorization"] == "token test_token"


def test_is_valid_doc_url_same_domain() -> None:
    """Should accept URLs from same domain."""
    harvester = DocHarvester("https://docs.example.com")
    assert harvester.is_valid_doc_url("https://docs.example.com/guide")
    assert not harvester.is_valid_doc_url("https://other.com/guide")


def test_is_valid_doc_url_skips_assets() -> None:
    """Should skip asset URLs."""
    harvester = DocHarvester("https://docs.example.com")
    assert not harvester.is_valid_doc_url("https://docs.example.com/images/logo.png")
    assert not harvester.is_valid_doc_url("https://docs.example.com/api/v1/data")


def test_is_valid_doc_url_skips_anchors() -> None:
    """Should skip anchor links."""
    harvester = DocHarvester("https://docs.example.com")
    assert not harvester.is_valid_doc_url("#section")


def test_is_valid_doc_url_skips_downloads() -> None:
    """Should skip download files."""
    harvester = DocHarvester("https://docs.example.com")
    assert not harvester.is_valid_doc_url("https://docs.example.com/download.pdf")
    assert not harvester.is_valid_doc_url("https://docs.example.com/archive.zip")
