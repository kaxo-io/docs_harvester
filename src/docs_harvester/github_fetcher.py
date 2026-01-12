"""GitHub repository documentation fetcher.

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

import markdown
import weasyprint
from bs4 import BeautifulSoup

from docs_harvester.http import DEFAULT_TIMEOUT, create_session

if TYPE_CHECKING:
    from requests import Session

logger = logging.getLogger(__name__)


class GitHubFileInfo(TypedDict):
    """Information about a GitHub file."""

    name: str
    path: str
    url: str


class MarkdownPage(TypedDict):
    """Data structure for a markdown page."""

    title: str
    content: str
    path: str


class GitHubDocFetcher:
    """Download markdown files from GitHub repositories and convert to PDF."""

    def __init__(
        self,
        repo_url: str,
        output_dir: str = "harvested_docs",
        github_token: str | None = None,
    ) -> None:
        """Initialize the GitHub documentation fetcher.

        Args:
            repo_url: GitHub repository URL
            output_dir: Output directory for harvested documents
            github_token: Optional GitHub personal access token
        """
        self.repo_url = repo_url.rstrip("/")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Parse GitHub repo info
        self._parse_github_url(repo_url)

        # Create subdirectory
        self.repo_output_dir = self.output_dir / f"github_docs_{self.owner}_{self.repo}"
        self.repo_output_dir.mkdir(exist_ok=True)
        self.md_dir = self.repo_output_dir / "markdown"
        self.md_dir.mkdir(exist_ok=True)

        self.api_base = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.docs_path}"
        )
        self.raw_base = (
            f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/"
            f"{self.branch}/{self.docs_path}"
        )

        self.pages: list[MarkdownPage] = []

        # Create HTTP session with GitHub token
        self.session: Session = create_session(github_token=github_token)

        logger.info("Repository: %s/%s", self.owner, self.repo)
        logger.info("Branch: %s", self.branch)
        logger.info("Path: %s", self.docs_path)
        logger.info("Output: %s", self.repo_output_dir)

    def _parse_github_url(self, repo_url: str) -> None:
        """Parse various GitHub URL formats.

        Args:
            repo_url: GitHub repository URL

        Raises:
            ValueError: If URL is not a valid GitHub URL
        """
        if "github.com" not in repo_url:
            raise ValueError("Not a GitHub URL")

        # Remove domain and clean up
        path_part = repo_url.replace("https://github.com/", "").strip("/")
        parts = path_part.split("/")

        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL - need at least owner/repo")

        self.owner = parts[0]
        self.repo = parts[1]
        self.branch = "main"  # default
        self.docs_path = "docs"  # default

        # Check if there's tree/branch/path info
        if len(parts) >= 4 and parts[2] == "tree":
            self.branch = parts[3]

            # If there's a path after the branch
            if len(parts) > 4:
                self.docs_path = "/".join(parts[4:])

        # If no tree info but there are more parts, assume they're path
        elif len(parts) > 2:
            self.docs_path = "/".join(parts[2:])

    def get_files_recursive(self, path: str = "") -> list[GitHubFileInfo]:
        """Recursively get all markdown files from a GitHub directory.

        Args:
            path: Subdirectory path relative to docs_path

        Returns:
            List of markdown file information dicts
        """
        current_path = f"{self.docs_path}/{path}".strip("/") if path else self.docs_path
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{current_path}"

        try:
            response = self.session.get(api_url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            items = response.json()

            md_files: list[GitHubFileInfo] = []

            for item in items:
                if item["type"] == "file" and item["name"].endswith(".md"):
                    md_files.append(
                        GitHubFileInfo(
                            name=item["name"],
                            path=item["path"],
                            url=item["download_url"],
                        )
                    )
                elif item["type"] == "dir":
                    # Recursively get files from subdirectories
                    sub_path = f"{path}/{item['name']}" if path else item["name"]
                    md_files.extend(self.get_files_recursive(sub_path))

            return md_files

        except Exception as e:
            logger.error("Error fetching files from %s: %s", api_url, e)
            return []

    def download_markdown_files(self, auto_save_interval: int = 10) -> None:
        """Download all markdown files from the repository.

        Args:
            auto_save_interval: Save progress every N files (0 to disable)
        """
        logger.info("Fetching markdown files from %s/%s", self.owner, self.repo)

        md_files = self.get_files_recursive()

        if not md_files:
            logger.warning("No markdown files found")
            return

        logger.info("Found %d markdown files", len(md_files))
        files_since_save = 0

        for idx, file_info in enumerate(md_files, 1):
            try:
                logger.info("Downloading [%d/%d]: %s", idx, len(md_files), file_info["name"])
                response = self.session.get(file_info["url"], timeout=DEFAULT_TIMEOUT)
                response.raise_for_status()
                content = response.text

                # Save raw markdown
                output_path = self.md_dir / file_info["name"]
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Convert to HTML and store
                html_content = markdown.markdown(content, extensions=["extra", "codehilite"])

                # Extract title from first h1 or use filename
                soup = BeautifulSoup(html_content, "html.parser")
                h1 = soup.find("h1")
                title = h1.get_text() if h1 else file_info["name"].replace(".md", "")

                self.pages.append(
                    MarkdownPage(
                        title=title,
                        content=html_content,
                        path=file_info["path"],
                    )
                )

                files_since_save += 1

                # Auto-save progress
                if auto_save_interval > 0 and files_since_save >= auto_save_interval:
                    logger.info("Auto-saving progress (%d files downloaded)...", len(self.pages))
                    self.save_json()
                    files_since_save = 0

                # Be nice to GitHub
                time.sleep(0.5)

            except Exception as e:
                logger.error("Error downloading %s: %s", file_info["name"], e)

        logger.info("Downloaded %d files", len(self.pages))

    def generate_pdf(self, filename: str | None = None) -> None:
        """Generate PDF from collected markdown files.

        Args:
            filename: Output filename (default: {owner}_{repo}_docs.pdf)
        """
        if not filename:
            filename = f"{self.owner}_{self.repo}_docs.pdf"

        if not self.pages:
            logger.warning("No pages to generate PDF from")
            return

        # Sort pages by path for logical order
        self.pages.sort(key=lambda x: x["path"])

        # Create HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.owner}/{self.repo} Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2cm; }}
                h1, h2, h3 {{ color: #333; page-break-after: avoid; }}
                .page-break {{ page-break-before: always; }}
                .path {{ color: #666; font-size: 0.8em; margin-bottom: 1em; }}
                pre {{ background: #f5f5f5; padding: 1em; overflow: auto; }}
                code {{ background: #f0f0f0; padding: 0.2em; }}
            </style>
        </head>
        <body>
            <h1>{self.owner}/{self.repo} Documentation</h1>
            <p>Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
            <hr>
        """

        for i, page in enumerate(self.pages):
            if i > 0:
                html_content += '<div class="page-break"></div>'

            html_content += f"""
            <div class="path">Path: {page["path"]}</div>
            <h2>{page["title"]}</h2>
            {page["content"]}
            <hr>
            """

        html_content += "</body></html>"

        # Save HTML
        html_file = self.repo_output_dir / f"{filename}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Generate PDF
        pdf_file = self.repo_output_dir / filename
        try:
            weasyprint.HTML(string=html_content).write_pdf(str(pdf_file))
            logger.info("PDF generated: %s", pdf_file)
        except Exception as e:
            logger.error("PDF generation failed: %s", e)
            logger.info("HTML saved to: %s", html_file)

    def save_json(self, filename: str | None = None) -> None:
        """Save collected data as JSON.

        Args:
            filename: Output filename (default: {owner}_{repo}_docs.json)
        """
        if not filename:
            filename = f"{self.owner}_{self.repo}_docs.json"

        if not self.pages:
            logger.warning("No pages to save to JSON")
            return

        json_file = self.repo_output_dir / filename
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)

        logger.info("JSON saved: %s", json_file)
