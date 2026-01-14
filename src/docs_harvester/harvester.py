"""Website documentation harvester.

Copyright (c) 2025 Kaxo Technologies
Contact: tech@kaxo.io

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict
from urllib.parse import urljoin, urlparse

import weasyprint
from bs4 import BeautifulSoup

from docs_harvester.http import DEFAULT_TIMEOUT, create_session

if TYPE_CHECKING:
    from requests import Session
    from requests_cache import CachedSession

logger = logging.getLogger(__name__)


class PageData(TypedDict):
    """Data structure for a harvested page."""

    url: str
    title: str
    content: str
    text: str


class DocHarvester:
    """Scrape and compile documentation into PDF and JSON formats."""

    def __init__(
        self,
        base_url: str,
        output_dir: str = "harvested_docs",
        no_images: bool = False,
        incremental: bool = False,
        cache_ttl: int | None = None,
    ) -> None:
        """Initialize the documentation harvester.

        Args:
            base_url: Base URL of the documentation site
            output_dir: Output directory for harvested documents
            no_images: Strip images from output content
            incremental: Skip pages that were already scraped
            cache_ttl: Optional HTTP cache TTL in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create project-specific subdirectory
        site_name = self.domain.replace(".", "_").replace("docs_", "")
        self.project_dir = self.output_dir / f"{site_name}_site_docs"
        self.project_dir.mkdir(exist_ok=True)

        self.visited_urls: set[str] = set()
        self.pages: list[PageData] = []
        self.no_images = no_images
        self.incremental = incremental

        # Safety limits
        self.non_docs_count = 0
        self.max_non_docs = 5

        # For GitHub, restrict to the specific path
        self.github_path_restriction: str | None = None
        if "github.com" in self.domain and "/tree/" in base_url:
            parts = base_url.split("/tree/")
            if len(parts) > 1:
                self.github_path_restriction = parts[1]

        # Create HTTP session
        self.session: Session | CachedSession = create_session(cache_ttl=cache_ttl)

        # Common selectors for different doc frameworks
        self.content_selectors = [
            "main",
            ".markdown-body",  # GitHub
            ".content",
            "article",
            ".docusaurus-content",
            ".gitbook-content",
            ".md-content",
            '[role="main"]',
            "#readme",  # GitHub README
            ".Box-body",  # GitHub file content
        ]

        self.nav_selectors = [
            "nav a[href]",
            ".sidebar a[href]",
            ".navigation a[href]",
            ".toc a[href]",
            ".menu a[href]",
            ".js-navigation-item a[href]",  # GitHub file browser
            ".Box a[href]",  # GitHub directory listings
        ]

    def get_page_content(self, url: str) -> PageData | None:
        """Extract main content from a documentation page.

        Args:
            url: The URL to fetch and parse

        Returns:
            PageData dict with url, title, content, text or None if failed
        """
        try:
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")

            # Find main content using common selectors
            content = None
            for selector in self.content_selectors:
                content = soup.select_one(selector)
                if content:
                    break

            if not content:
                body = soup.find("body")
                # Ensure we have a Tag, not NavigableString
                from bs4 import Tag

                if body and isinstance(body, Tag):
                    content = body

            if not content:
                logger.warning("No content found for %s", url)
                return None

            # Clean up navigation and footer elements
            # Remove by tag name
            for tag in ("nav", "footer", "aside", "header"):
                for elem in content.find_all(tag):
                    elem.decompose()

            # Remove by class name
            for class_name in ("sidebar", "navigation", "nav", "toc", "menu"):
                for elem in content.find_all(class_=class_name):
                    elem.decompose()

            # Strip images if requested
            if self.no_images:
                for img in content.find_all("img"):
                    img.decompose()
            else:
                # Fix relative image URLs to absolute (for WeasyPrint)
                for img in content.find_all("img"):
                    src = img.get("src")
                    if src and isinstance(src, str):
                        # Convert relative URLs to absolute
                        absolute_url = urljoin(url, src)
                        img["src"] = absolute_url

            # Get title
            title_elem = soup.find("h1")
            if title_elem:
                title = title_elem.get_text().strip()
            else:
                title = soup.title.get_text().strip() if soup.title else url

            return PageData(
                url=url,
                title=title,
                content=str(content),
                text=content.get_text().strip(),
            )

        except Exception as e:
            logger.error("Error processing %s: %s", url, e)
            return None

    def find_doc_links(self, url: str) -> set[str]:
        """Find all documentation links from a page.

        Args:
            url: The URL to extract links from

        Returns:
            Set of valid documentation URLs
        """
        try:
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            soup = BeautifulSoup(response.content, "html.parser")

            links: set[str] = set()

            # Try navigation-specific selectors first
            for selector in self.nav_selectors:
                nav_links = soup.select(selector)
                for link in nav_links:
                    href = link.get("href")
                    if href and isinstance(href, str):
                        full_url = urljoin(url, href)
                        if self.is_valid_doc_url(full_url):
                            links.add(full_url)

            # If no nav links found, get all links
            if not links:
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    full_url = urljoin(url, href)
                    if self.is_valid_doc_url(full_url):
                        links.add(full_url)

            return links

        except Exception as e:
            logger.error("Error finding links in %s: %s", url, e)
            return set()

    def is_valid_doc_url(self, url: str) -> bool:
        """Check if URL is a valid documentation page.

        Args:
            url: The URL to validate

        Returns:
            True if URL is a valid documentation page
        """
        parsed = urlparse(url)

        # Must be same domain
        if parsed.netloc != self.domain:
            return False

        # Skip anchors, external links, files
        if url.startswith("#") or url.endswith((".pdf", ".zip", ".tar.gz")):
            return False

        # Skip API endpoints, images, etc.
        skip_patterns = ["/api/", "/images/", "/assets/", "/static/", "/_next/"]
        if any(pattern in url for pattern in skip_patterns):
            return False

        # For GitHub, be very restrictive
        if "github.com" in self.domain:
            github_skip = [
                "/issues/",
                "/pull/",
                "/releases/",
                "/actions/",
                "/security/",
                "/pulse/",
                "/graphs/",
                "/wiki/",
                "/projects/",
                "/settings/",
            ]
            if any(pattern in url for pattern in github_skip):
                return False

            # If we have a path restriction, enforce it strictly
            if self.github_path_restriction:
                restriction_parts = self.github_path_restriction.split("/")
                expected_base = (
                    f"/{'/'.join(url.split('/')[3:5])}/blob/"
                    f"{restriction_parts[0]}/{'/'.join(restriction_parts[1:])}"
                )
                if not url.startswith(f"https://github.com{expected_base}"):
                    return False

            # Only include markdown files in docs areas
            if "/blob/" in url:
                return url.endswith(".md")
            elif "/tree/" in url:
                return bool(self.github_path_restriction and self.github_path_restriction in url)

        return True

    def load_existing_pages(self) -> None:
        """Load previously scraped pages from JSON file for incremental scraping."""
        json_file = self.project_dir / f"{self.domain.replace('.', '_')}_docs.json"

        if not json_file.exists():
            logger.info("No existing JSON file found. Starting fresh crawl.")
            return

        try:
            with open(json_file, encoding="utf-8") as f:
                existing_pages = json.load(f)

            # Load existing pages and mark URLs as visited
            self.pages = existing_pages
            self.visited_urls = {page["url"] for page in existing_pages}

            logger.info(
                "Loaded %d existing pages from %s (incremental mode)",
                len(self.pages),
                json_file,
            )
        except Exception as e:
            logger.error("Failed to load existing pages: %s", e)
            logger.info("Starting fresh crawl.")

    def crawl_documentation(self, max_pages: int = 100, auto_save_interval: int = 10) -> None:
        """Crawl the documentation site.

        Args:
            max_pages: Maximum number of pages to crawl
            auto_save_interval: Save progress every N pages (0 to disable)
        """
        logger.info("Starting crawl of %s", self.base_url)
        if self.github_path_restriction:
            logger.info("GitHub path restriction: %s", self.github_path_restriction)

        # Load existing pages if in incremental mode
        if self.incremental:
            self.load_existing_pages()

        to_visit = {self.base_url}
        pages_since_save = 0

        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop()

            if url in self.visited_urls:
                continue

            # Safety check for non-docs URLs
            if not self.is_valid_doc_url(url):
                self.non_docs_count += 1
                if self.non_docs_count > self.max_non_docs:
                    logger.warning(
                        "Hit safety limit: %d non-docs URLs. Stopping crawl.",
                        self.max_non_docs,
                    )
                    break
                continue

            logger.info("Processing [%d/%d]: %s", len(self.visited_urls) + 1, max_pages, url)
            self.visited_urls.add(url)

            # Get page content
            page_data = self.get_page_content(url)
            if page_data:
                self.pages.append(page_data)
                pages_since_save += 1

                # Auto-save progress
                if auto_save_interval > 0 and pages_since_save >= auto_save_interval:
                    logger.info("Auto-saving progress (%d pages collected)...", len(self.pages))
                    self.save_json()
                    pages_since_save = 0

            # Find more links
            new_links = self.find_doc_links(url)
            to_visit.update(new_links - self.visited_urls)

            # Be nice to the server
            time.sleep(0.5)

        logger.info("Crawled %d pages", len(self.pages))
        if self.non_docs_count > 0:
            logger.info("Skipped %d non-docs URLs", self.non_docs_count)

    def generate_pdf(self, filename: str | None = None) -> None:
        """Generate PDF from collected pages.

        Args:
            filename: Output filename (default: {domain}_docs.pdf)
        """
        if not filename:
            filename = f"{self.domain.replace('.', '_')}_docs.pdf"

        # Sort pages by URL for logical order
        self.pages.sort(key=lambda x: x["url"])

        # Create HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.domain} Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2cm; }}
                h1, h2, h3 {{ color: #333; page-break-after: avoid; }}
                .page-break {{ page-break-before: always; }}
                .url {{ color: #666; font-size: 0.8em; margin-bottom: 1em; }}
                pre {{ background: #f5f5f5; padding: 1em; overflow: auto; }}
                code {{ background: #f0f0f0; padding: 0.2em; }}
            </style>
        </head>
        <body>
            <h1>{self.domain} Documentation</h1>
            <p>Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
            <hr>
        """

        for i, page in enumerate(self.pages):
            if i > 0:
                html_content += '<div class="page-break"></div>'

            html_content += f"""
            <div class="url">Source: {page["url"]}</div>
            <h2>{page["title"]}</h2>
            {page["content"]}
            <hr>
            """

        html_content += "</body></html>"

        # Save HTML
        html_file = self.project_dir / f"{filename}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Generate PDF
        pdf_file = self.project_dir / filename
        try:
            weasyprint.HTML(string=html_content).write_pdf(str(pdf_file))
            logger.info("PDF generated: %s", pdf_file)
        except Exception as e:
            logger.error("PDF generation failed: %s", e)
            logger.info("HTML saved to: %s", html_file)

    def save_html(self, filename: str | None = None) -> None:
        """Save collected pages as a single HTML file.

        Args:
            filename: Output filename (default: {domain}_docs.html)
        """
        if not filename:
            filename = f"{self.domain.replace('.', '_')}_docs.html"

        # Sort pages by URL for logical order
        self.pages.sort(key=lambda x: x["url"])

        # Create HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.domain} Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2cm; }}
                h1, h2, h3 {{ color: #333; }}
                .page-break {{ margin-top: 3em; padding-top: 2em; border-top: 2px solid #ddd; }}
                .url {{ color: #666; font-size: 0.8em; margin-bottom: 1em; }}
                pre {{ background: #f5f5f5; padding: 1em; overflow: auto; }}
                code {{ background: #f0f0f0; padding: 0.2em; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>{self.domain} Documentation</h1>
            <p>Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
            <hr>
        """

        for i, page in enumerate(self.pages):
            if i > 0:
                html_content += '<div class="page-break"></div>'

            html_content += f"""
            <div class="url">Source: {page["url"]}</div>
            <h2>{page["title"]}</h2>
            {page["content"]}
            <hr>
            """

        html_content += "</body></html>"

        # Save HTML
        html_file = self.project_dir / filename
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("HTML saved: %s", html_file)

    def save_json(self, filename: str | None = None) -> None:
        """Save collected data as JSON.

        Args:
            filename: Output filename (default: {domain}_docs.json)
        """
        if not filename:
            filename = f"{self.domain.replace('.', '_')}_docs.json"

        json_file = self.project_dir / filename
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)

        logger.info("JSON saved: %s", json_file)
