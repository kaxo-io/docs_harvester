"""Command-line interface for GitHub documentation fetcher.

Copyright (c) 2025 Kaxo Technologies
Contact: tech@kaxo.io

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

from __future__ import annotations

import argparse
import logging

from docs_harvester.github_fetcher import GitHubDocFetcher


def main() -> None:
    """Main entry point for github-docs CLI."""
    parser = argparse.ArgumentParser(
        description="Download markdown files from GitHub repositories and convert to PDF"
    )
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument(
        "--output-dir",
        default="harvested_docs",
        help="Output directory (default: harvested_docs)",
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "json", "both"],
        default="both",
        help="Output format (default: both)",
    )
    parser.add_argument(
        "--github-token",
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create fetcher and run
    fetcher = GitHubDocFetcher(args.repo_url, args.output_dir, args.github_token)
    fetcher.download_markdown_files()

    # Generate outputs
    if args.format in ["json", "both"]:
        fetcher.save_json()

    if args.format in ["pdf", "both"]:
        fetcher.generate_pdf()


if __name__ == "__main__":
    main()
