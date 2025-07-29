#!/usr/bin/env python3
"""
GitHub Documentation Fetcher - Downloads markdown files and converts to PDF
Works with any GitHub repository's docs folder or specific paths

Copyright (c) 2025 Kaxo Technologies
Contact: tech [ a t ] kaxo.io
Vibe coded by Kaxo Technologies

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.
"""

import requests
import os
import json
from pathlib import Path
import weasyprint
import time
from urllib.parse import urlparse
import markdown
from bs4 import BeautifulSoup
import argparse

class GitHubDocFetcher:
    def __init__(self, repo_url: str, output_dir: str = "harvested_docs"):
        self.repo_url = repo_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Parse GitHub repo info
        self._parse_github_url(repo_url)
        
        # Create subdirectory like: harvested_docs/github_docs_ollama
        self.repo_output_dir = self.output_dir / f"github_docs_{self.owner}_{self.repo}"
        self.repo_output_dir.mkdir(exist_ok=True)
        self.md_dir = self.repo_output_dir / "markdown"
        self.md_dir.mkdir(exist_ok=True)
        
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.docs_path}"
        self.raw_base = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{self.docs_path}"
        
        self.pages = []
        
        print(f"Repository: {self.owner}/{self.repo}")
        print(f"Branch: {self.branch}")
        print(f"Path: {self.docs_path}")
        print(f"Output: {self.repo_output_dir}")

    def _parse_github_url(self, repo_url):
        """Parse various GitHub URL formats"""
        # Handle different GitHub URL formats:
        # https://github.com/owner/repo
        # https://github.com/owner/repo/tree/branch
        # https://github.com/owner/repo/tree/branch/path/to/docs
        
        if not 'github.com' in repo_url:
            raise ValueError("Not a GitHub URL")
        
        # Remove domain and clean up
        path_part = repo_url.replace('https://github.com/', '').strip('/')
        parts = path_part.split('/')
        
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL - need at least owner/repo")
        
        self.owner = parts[0]
        self.repo = parts[1]
        self.branch = 'main'  # default
        self.docs_path = 'docs'  # default
        
        # Check if there's tree/branch/path info
        if len(parts) >= 4 and parts[2] == 'tree':
            self.branch = parts[3]
            
            # If there's a path after the branch
            if len(parts) > 4:
                self.docs_path = '/'.join(parts[4:])
        
        # If no tree info but there are more parts, assume they're path
        elif len(parts) > 2:
            # Could be a direct path like owner/repo/docs
            self.docs_path = '/'.join(parts[2:])

    def get_files_recursive(self, path=""):
        """Recursively get all markdown files from a GitHub directory"""
        current_path = f"{self.docs_path}/{path}".strip('/') if path else self.docs_path
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{current_path}"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            items = response.json()
            
            md_files = []
            
            for item in items:
                if item['type'] == 'file' and item['name'].endswith('.md'):
                    md_files.append({
                        'name': item['name'],
                        'download_url': item['download_url'],
                        'path': item['path'],
                        'relative_path': f"{path}/{item['name']}".strip('/')
                    })
                elif item['type'] == 'dir':
                    # Recursively get files from subdirectories
                    subdir_path = f"{path}/{item['name']}".strip('/')
                    sub_files = self.get_files_recursive(subdir_path)
                    md_files.extend(sub_files)
            
            return md_files
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Path not found: {current_path}")
                # Try alternative common paths
                if current_path == 'docs' and not path:
                    print("Trying alternative paths...")
                    alternatives = ['doc', 'documentation', '.', 'README.md']
                    for alt in alternatives:
                        try:
                            alt_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{alt}"
                            alt_response = requests.get(alt_url)
                            if alt_response.status_code == 200:
                                print(f"Found content at: {alt}")
                                self.docs_path = alt
                                return self.get_files_recursive()
                        except:
                            continue
            return []
        except Exception as e:
            print(f"Error fetching files from {current_path}: {e}")
            return []

    def get_markdown_files(self):
        """Get list of all markdown files"""
        md_files = self.get_files_recursive()
        
        print(f"\nFound {len(md_files)} markdown files:")
        for file in sorted(md_files, key=lambda x: x['relative_path']):
            print(f"  - {file['relative_path']}")
        
        return md_files

    def download_markdown_file(self, file_info):
        """Download a single markdown file"""
        try:
            response = requests.get(file_info['download_url'])
            response.raise_for_status()
            
            # Create subdirectory structure if needed
            relative_dir = Path(file_info['relative_path']).parent
            if relative_dir != Path('.'):
                (self.md_dir / relative_dir).mkdir(parents=True, exist_ok=True)
            
            # Save raw markdown
            md_path = self.md_dir / file_info['relative_path']
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Convert to HTML for processing
            html_content = markdown.markdown(response.text, extensions=['extra', 'codehilite', 'toc'])
            
            # Create a proper HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{file_info['name']}</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 2em; line-height: 1.6; }}
                    pre {{ background: #f6f8fa; padding: 1em; overflow: auto; border-radius: 6px; border: 1px solid #d0d7de; }}
                    code {{ background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }}
                    h1, h2, h3, h4, h5, h6 {{ color: #24292f; margin-top: 24px; margin-bottom: 16px; }}
                    h1 {{ border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }}
                    h2 {{ border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }}
                    blockquote {{ border-left: 4px solid #d0d7de; margin: 0; padding: 0 1em; color: #656d76; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
                    th, td {{ border: 1px solid #d0d7de; padding: 6px 13px; text-align: left; }}
                    th {{ background-color: #f6f8fa; font-weight: 600; }}
                    .toc {{ background: #f6f8fa; padding: 1em; border-radius: 6px; margin: 1em 0; }}
                </style>
            </head>
            <body>
                <h1>{file_info['relative_path']}</h1>
                <p><em>Source: <a href="{file_info['download_url']}">{file_info['path']}</a></em></p>
                <hr>
                {html_content}
            </body>
            </html>
            """
            
            page_data = {
                'name': file_info['name'],
                'relative_path': file_info['relative_path'],
                'path': file_info['path'],
                'url': file_info['download_url'],
                'content': full_html,
                'raw_markdown': response.text
            }
            
            print(f"Downloaded: {file_info['relative_path']}")
            return page_data
            
        except Exception as e:
            print(f"Error downloading {file_info['relative_path']}: {e}")
            return None

    def fetch_all_docs(self):
        """Download all markdown files"""
        md_files = self.get_markdown_files()
        
        if not md_files:
            print("No markdown files found!")
            return
        
        for file_info in md_files:
            page_data = self.download_markdown_file(file_info)
            if page_data:
                self.pages.append(page_data)
            time.sleep(0.3)  # Be nice to GitHub
        
        print(f"\nSuccessfully downloaded {len(self.pages)} files")

    def generate_pdf(self, filename: str = None):
        """Generate PDF from collected pages"""
        if not self.pages:
            print("No pages to generate PDF from!")
            return
            
        if not filename:
            filename = f"{self.owner}_{self.repo}_{self.docs_path.replace('/', '_')}_docs.pdf"
        
        # Sort pages by relative path
        self.pages.sort(key=lambda x: x['relative_path'])
        
        # Create combined HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.owner}/{self.repo} Documentation</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 2cm; line-height: 1.6; }}
                h1, h2, h3, h4, h5, h6 {{ color: #24292f; page-break-after: avoid; }}
                .page-break {{ page-break-before: always; }}
                .file-header {{ color: #656d76; font-size: 0.9em; margin-bottom: 1em; }}
                pre {{ background: #f6f8fa; padding: 1em; overflow: auto; border-radius: 6px; border: 1px solid #d0d7de; }}
                code {{ background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }}
                blockquote {{ border-left: 4px solid #d0d7de; margin: 0; padding: 0 1em; color: #656d76; }}
                table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
                th, td {{ border: 1px solid #d0d7de; padding: 6px 13px; text-align: left; }}
                th {{ background-color: #f6f8fa; font-weight: 600; }}
                .toc {{ page-break-after: always; }}
                .toc ul {{ list-style-type: none; padding-left: 0; }}
                .toc li {{ margin: 0.5em 0; }}
                .toc a {{ text-decoration: none; color: #0969da; }}
                .cover {{ text-align: center; page-break-after: always; }}
            </style>
        </head>
        <body>
            <div class="cover">
                <h1>{self.owner}/{self.repo}</h1>
                <h2>Documentation</h2>
                <p>Branch: {self.branch} | Path: {self.docs_path}</p>
                <p>Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="toc">
                <h2>Table of Contents</h2>
                <ul>
        """
        
        # Add table of contents
        for page in self.pages:
            html_content += f'<li><a href="#{page["relative_path"].replace("/", "_")}">{page["relative_path"]}</a></li>\n'
        
        html_content += """
                </ul>
            </div>
        """
        
        # Add pages
        for i, page in enumerate(self.pages):
            if i > 0:
                html_content += '<div class="page-break"></div>'
            
            # Extract body content from the page HTML
            soup = BeautifulSoup(page['content'], 'html.parser')
            body_content = soup.find('body')
            if body_content:
                # Remove the title and source info we added
                title = body_content.find('h1')
                if title:
                    title.decompose()
                source_p = body_content.find('p')
                if source_p and 'Source:' in source_p.get_text():
                    source_p.decompose()
                hr = body_content.find('hr')
                if hr:
                    hr.decompose()
                
                content = str(body_content).replace('<body>', '').replace('</body>', '')
            else:
                content = page['content']
            
            html_content += f"""
            <div id="{page['relative_path'].replace('/', '_')}">
                <div class="file-header">File: {page['relative_path']} | Repository: {self.owner}/{self.repo}</div>
                <h2>{page['relative_path']}</h2>
                {content}
            </div>
            <hr style="margin-top: 2em; margin-bottom: 2em; border: none; border-top: 1px solid #d0d7de;">
            """
        
        html_content += "</body></html>"
        
        # Save HTML
        html_file = self.repo_output_dir / f"{filename}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate PDF
        pdf_file = self.repo_output_dir / filename
        try:
            weasyprint.HTML(string=html_content).write_pdf(str(pdf_file))
            print(f"PDF generated: {pdf_file}")
        except Exception as e:
            print(f"PDF generation failed: {e}")
            print(f"HTML saved to: {html_file}")

    def save_json(self, filename: str = None):
        """Save collected data as JSON"""
        if not self.pages:
            print("No pages to save!")
            return
            
        if not filename:
            filename = f"{self.owner}_{self.repo}_{self.docs_path.replace('/', '_')}_docs.json"
        
        json_file = self.repo_output_dir / filename
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)
        
        print(f"JSON saved: {json_file}")

def main():
    parser = argparse.ArgumentParser(description='Fetch GitHub documentation and convert to PDF')
    parser.add_argument('repo_url', help='GitHub repository URL (e.g., https://github.com/owner/repo or https://github.com/owner/repo/tree/branch/docs)')
    parser.add_argument('--output-dir', default='harvested_docs', help='Output directory')
    parser.add_argument('--format', choices=['pdf', 'json', 'both'], default='both', help='Output format')
    
    args = parser.parse_args()
    
    fetcher = GitHubDocFetcher(args.repo_url, args.output_dir)
    fetcher.fetch_all_docs()
    
    if args.format in ['json', 'both']:
        fetcher.save_json()
    
    if args.format in ['pdf', 'both']:
        fetcher.generate_pdf()

if __name__ == "__main__":
    main()