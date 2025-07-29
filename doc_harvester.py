#!/usr/bin/env python3
"""
Documentation Harvester - Scrapes and compiles documentation into PDF
Supports common doc sites like GitBook, Docusaurus, MkDocs, etc.

Copyright (c) 2025 Kaxo Technologies
Contact: tech [ a t ] kaxo.io
Vibe coded by Kaxo Technologies

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
import weasyprint
from typing import Set, List, Dict
import argparse

class DocHarvester:
    def __init__(self, base_url: str, output_dir: str = "harvested_docs"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create project-specific subdirectory like: harvested_docs/openwebui_com_site_docs
        site_name = self.domain.replace('.', '_').replace('docs_', '')
        self.project_dir = self.output_dir / f"{site_name}_site_docs"
        self.project_dir.mkdir(exist_ok=True)
        
        self.visited_urls: Set[str] = set()
        self.pages: List[Dict] = []
        
        # Safety limits
        self.non_docs_count = 0
        self.max_non_docs = 5  # Stop if we hit too many non-docs pages
        
        # For GitHub, restrict to the specific path
        self.github_path_restriction = None
        if 'github.com' in self.domain and '/tree/' in base_url:
            # Extract the path restriction from URL like /owner/repo/tree/branch/docs
            parts = base_url.split('/tree/')
            if len(parts) > 1:
                self.github_path_restriction = parts[1]  # e.g., "main/docs"
        
        # Common selectors for different doc frameworks
        self.content_selectors = [
            'main',
            '.markdown-body',          # GitHub
            '.content',
            'article',
            '.docusaurus-content',
            '.gitbook-content',
            '.md-content',
            '[role="main"]',
            '#readme',                 # GitHub README
            '.Box-body'                # GitHub file content
        ]
        
        self.nav_selectors = [
            'nav a[href]',
            '.sidebar a[href]',
            '.navigation a[href]',
            '.toc a[href]',
            '.menu a[href]',
            '.js-navigation-item a[href]',  # GitHub file browser
            '.Box a[href]'             # GitHub directory listings
        ]

    def get_page_content(self, url: str) -> Dict:
        """Extract main content from a documentation page"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main content using common selectors
            content = None
            for selector in self.content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup.find('body')
            
            # Clean up navigation and footer elements
            for elem in content.find_all(['nav', 'footer', '.sidebar', '.navigation']):
                elem.decompose()
            
            # Get title
            title = soup.find('h1')
            if title:
                title = title.get_text().strip()
            else:
                title = soup.title.get_text().strip() if soup.title else url
                
            return {
                'url': url,
                'title': title,
                'content': str(content),
                'text': content.get_text().strip()
            }
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None

    def find_doc_links(self, url: str) -> Set[str]:
        """Find all documentation links from a page"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            
            # Try navigation-specific selectors first
            for selector in self.nav_selectors:
                nav_links = soup.select(selector)
                for link in nav_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        if self.is_valid_doc_url(full_url):
                            links.add(full_url)
            
            # If no nav links found, get all links
            if not links:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    if self.is_valid_doc_url(full_url):
                        links.add(full_url)
            
            return links
            
        except Exception as e:
            print(f"Error finding links in {url}: {e}")
            return set()

    def is_valid_doc_url(self, url: str) -> bool:
        """Check if URL is a valid documentation page"""
        parsed = urlparse(url)
        
        # Must be same domain
        if parsed.netloc != self.domain:
            return False
            
        # Skip anchors, external links, files
        if url.startswith('#') or url.endswith(('.pdf', '.zip', '.tar.gz')):
            return False
            
        # Skip API endpoints, images, etc.
        skip_patterns = ['/api/', '/images/', '/assets/', '/static/', '/_next/']
        if any(pattern in url for pattern in skip_patterns):
            return False
        
        # For GitHub, be very restrictive
        if 'github.com' in self.domain:
            # Skip issues, pulls, releases, etc.
            github_skip = ['/issues/', '/pull/', '/releases/', '/actions/', '/security/', '/pulse/', '/graphs/', '/wiki/', '/projects/', '/settings/']
            if any(pattern in url for pattern in github_skip):
                return False
            
            # If we have a path restriction, enforce it strictly
            if self.github_path_restriction:
                restriction_parts = self.github_path_restriction.split('/')
                expected_base = f"/{'/'.join(url.split('/')[3:5])}/blob/{restriction_parts[0]}/{'/'.join(restriction_parts[1:])}"
                if not url.startswith(f"https://github.com{expected_base}"):
                    return False
            
            # Only include markdown files in docs areas
            if '/blob/' in url:
                return url.endswith('.md')
            elif '/tree/' in url:
                # Only allow directory navigation within docs
                return self.github_path_restriction and self.github_path_restriction in url
                
        return True

    def crawl_documentation(self, max_pages: int = 100):
        """Crawl the documentation site"""
        print(f"Starting crawl of {self.base_url}")
        if self.github_path_restriction:
            print(f"GitHub path restriction: {self.github_path_restriction}")
        
        to_visit = {self.base_url}
        
        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop()
            
            if url in self.visited_urls:
                continue
                
            # Safety check for non-docs URLs
            if not self.is_valid_doc_url(url):
                self.non_docs_count += 1
                if self.non_docs_count > self.max_non_docs:
                    print(f"⚠️  Hit safety limit: {self.max_non_docs} non-docs URLs. Stopping crawl.")
                    break
                continue
                
            print(f"Processing: {url}")
            self.visited_urls.add(url)
            
            # Get page content
            page_data = self.get_page_content(url)
            if page_data:
                self.pages.append(page_data)
            
            # Find more links
            new_links = self.find_doc_links(url)
            to_visit.update(new_links - self.visited_urls)
            
            # Be nice to the server
            time.sleep(0.5)
        
        print(f"Crawled {len(self.pages)} pages")
        if self.non_docs_count > 0:
            print(f"Skipped {self.non_docs_count} non-docs URLs")

    def generate_pdf(self, filename: str = None):
        """Generate PDF from collected pages"""
        if not filename:
            filename = f"{self.domain.replace('.', '_')}_docs.pdf"
        
        # Sort pages by URL for logical order
        self.pages.sort(key=lambda x: x['url'])
        
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
            <p>Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
        """
        
        for i, page in enumerate(self.pages):
            if i > 0:
                html_content += '<div class="page-break"></div>'
            
            html_content += f"""
            <div class="url">Source: {page['url']}</div>
            <h2>{page['title']}</h2>
            {page['content']}
            <hr>
            """
        
        html_content += "</body></html>"
        
        # Save HTML
        html_file = self.project_dir / f"{filename}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate PDF
        pdf_file = self.project_dir / filename
        try:
            weasyprint.HTML(string=html_content).write_pdf(str(pdf_file))
            print(f"PDF generated: {pdf_file}")
        except Exception as e:
            print(f"PDF generation failed: {e}")
            print(f"HTML saved to: {html_file}")

    def save_json(self, filename: str = None):
        """Save collected data as JSON"""
        if not filename:
            filename = f"{self.domain.replace('.', '_')}_docs.json"
        
        json_file = self.project_dir / filename
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)
        
        print(f"JSON saved: {json_file}")

def main():
    parser = argparse.ArgumentParser(description='Harvest documentation from websites')
    parser.add_argument('url', help='Base URL of documentation site')
    parser.add_argument('--max-pages', type=int, default=100, help='Maximum pages to crawl')
    parser.add_argument('--output-dir', default='harvested_docs', help='Output directory')
    parser.add_argument('--format', choices=['pdf', 'json', 'both'], default='both', help='Output format')
    
    args = parser.parse_args()
    
    harvester = DocHarvester(args.url, args.output_dir)
    harvester.crawl_documentation(args.max_pages)
    
    if args.format in ['json', 'both']:
        harvester.save_json()
    
    if args.format in ['pdf', 'both']:
        harvester.generate_pdf()

if __name__ == "__main__":
    main()