# Documentation Harvester Suite

Automatically scrape and compile documentation from websites and GitHub repositories into PDFs and JSON files.

## Tools Included

1. **Website Documentation Harvester** (`doc_harvester.py`) - For documentation sites
2. **GitHub Documentation Fetcher** (`github_doc_fetcher.py`) - For GitHub repositories

## Quick Start

### For Any GitHub Repository
```bash
# Make scripts executable
chmod +x setup.sh fetch_github_docs.sh

# Fetch any GitHub repo's docs
./fetch_github_docs.sh https://github.com/owner/repo
./fetch_github_docs.sh https://github.com/owner/repo/tree/branch/docs
```

### For Documentation Websites
```bash
# For traditional doc sites (OpenWebUI example)
./run_harvester.sh
```

## GitHub Fetcher Features

- **Smart URL parsing** - handles various GitHub URL formats
- **Recursive directory crawling** - finds all markdown files in subdirectories  
- **Auto path detection** - tries common paths like `docs/`, `doc/`, `documentation/`
- **Organized output** - separate folders per repository
- **GitHub-style formatting** - matches GitHub's markdown rendering

## Examples

```bash
# Ollama documentation
./fetch_github_docs.sh https://github.com/ollama/ollama/tree/main/docs

# OpenAI Python SDK
./fetch_github_docs.sh https://github.com/openai/openai-python

# Anthropic SDK docs
./fetch_github_docs.sh https://github.com/anthropic/anthropic-sdk-python/tree/main/docs

# Any repo with docs in root
./fetch_github_docs.sh https://github.com/owner/repo
```

## Manual Setup

### 1. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Activate Environment
```bash
source doc_harvester_env/bin/activate
```

### 3. Run Tools

**For GitHub repos:**
```bash
python github_doc_fetcher.py https://github.com/owner/repo --format both
```

**For doc sites:**
```bash
python doc_harvester.py https://docs.example.com --format both
```

## Options

- `--format pdf|json|both`: Output format (default: both)
- `--output-dir DIR`: Output directory (default: github_docs or harvested_docs)

## Output Structure

```
github_docs/
├── owner_repo_docs/
│   ├── markdown/           # Raw .md files
│   ├── owner_repo_docs.pdf # Combined PDF
│   ├── owner_repo_docs.json # JSON data
│   └── owner_repo_docs.pdf.html # HTML version
```

## Requirements

- Python 3.8+
- System dependencies for PDF generation (auto-installed by setup script)

## Supported Sources

### GitHub Repositories
- Any public GitHub repository
- Markdown files in any directory structure
- Handles various URL formats automatically

### Documentation Sites
- Docusaurus (like OpenWebUI)
- GitBook
- MkDocs  
- Custom documentation sites
- Most static documentation generators

## Troubleshooting

### PDF Generation Issues
If PDF generation fails, check the HTML output first. The tools will always generate an HTML file even if PDF fails.

### GitHub API Rate Limits
The GitHub fetcher uses the public API and respects rate limits. For private repos, you'd need to add authentication.

### Missing Files
GitHub fetcher tries common documentation paths automatically. If files aren't found, check the repository structure and specify the exact path.