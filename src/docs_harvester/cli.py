"""Command-line interface for website documentation harvester.

Copyright (c) 2025 Kaxo Technologies
Contact: tech@kaxo.io

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

from __future__ import annotations

import argparse
import logging

from docs_harvester.harvester import DocHarvester


def main() -> None:
    """Main entry point for docs-harvester CLI."""
    parser = argparse.ArgumentParser(description="Harvest documentation from websites")
    parser.add_argument("url", help="Base URL of documentation site")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum pages to crawl (default: 100)",
    )
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

    # Create harvester and run
    harvester = DocHarvester(args.url, args.output_dir)
    harvester.crawl_documentation(args.max_pages)

    # Generate outputs
    if args.format in ["json", "both"]:
        harvester.save_json()

    if args.format in ["pdf", "both"]:
        harvester.generate_pdf()


if __name__ == "__main__":
    main()
