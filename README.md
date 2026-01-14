```
                                           :*++*-
                                            +**+
                                            =**=
                                            =**=
                                            =**=
                                 -*+=-------+**+-------=+*=
                                 .+**********************+.
                                 -----------=**=---------:-
                                            =**=
                                            =**=
                                            =**=
                                            =**=
                                            =**=
                                            =**=
                                            +**+
                                           :*++*:

                                ╔═══════════════════════╗
                                ║  SOLI • DEO • GLORIA  ║
                                ╚═══════════════════════╝
```

# Documentation Harvester

**Built in 2025, before MCP and context7 existed.**

Scrape documentation from websites and GitHub repositories into PDFs and JSON for LLM context ingestion.

## The Problem We Solved

In early 2025, LLMs would hallucinate APIs. You'd ask for code using a library and get methods that didn't exist, parameters that were wrong, deprecated patterns that would fail.

The solution was obvious: give the LLM the actual documentation. But documentation sites don't come in LLM-friendly formats.

So we built this.

## How It Compares to Modern Solutions

| Feature | docs_harvester | context7 | MCP |
|---------|---------------|----------|-----|
| Offline use | ✅ | ❌ | ❌ |
| Version snapshots | ✅ | ❌ | ❌ |
| Private/internal docs | ✅ | ❌ | ✅ |
| PDF output | ✅ | ❌ | ❌ |
| Zero config | ✅ | ✅ | ❌ |
| Real-time updates | ❌ | ✅ | ✅ |
| Token efficiency | ❌ | ✅ | ✅ |
| Air-gapped environments | ✅ | ❌ | ❌ |

### When to Use docs_harvester

- Niche libraries not covered by context7
- Need offline access (air-gapped, travel, etc.)
- Want a specific version snapshot frozen in time
- Internal/private documentation
- Need PDF output for sharing or printing

### When to Use context7/MCP Instead

- Common libraries with good coverage
- Need latest docs always
- Token-conscious (on-demand loading)
- Working with always-online tooling

## Quick Start

### Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Install

```bash
# Clone
git clone https://github.com/kaxo-io/docs_harvester.git
cd docs_harvester

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Usage

**Harvest a documentation website (scrapes all pages):**
```bash
uv run docs-harvester https://docs.n8n.io
```

**Limit to specific number of pages:**
```bash
uv run docs-harvester https://docs.n8n.io --max-pages 50
```

**Incremental scraping (continue from where you left off):**
```bash
# First run: scrape 50 pages
uv run docs-harvester https://docs.example.com --max-pages 50

# Second run: continue to 300 pages
uv run docs-harvester https://docs.example.com --max-pages 300 --incremental
```

**JSON-only output without images:**
```bash
uv run docs-harvester https://docs.example.com --format json --no-images
```

**Enable HTTP caching for faster re-scraping:**
```bash
uv run docs-harvester https://docs.example.com --cache-ttl 3600  # 1 hour cache
```

**Fetch GitHub repository docs:**
```bash
uv run github-docs https://github.com/ollama/ollama/tree/main/docs
```

**With GitHub token (for higher rate limits):**
```bash
export GITHUB_TOKEN=your_token
uv run github-docs https://github.com/anthropics/anthropic-sdk-python
```

### Output

```
harvested_docs/
├── example_com_site_docs/
│   ├── example_com_docs.pdf     # Combined PDF with TOC
│   ├── example_com_docs.json    # Structured JSON
│   └── example_com_docs.html    # HTML version
└── github_docs_owner_repo/
    ├── markdown/                 # Raw .md files
    ├── owner_repo_docs.pdf
    └── owner_repo_docs.json
```

## CLI Options

### Website Harvester

```bash
uv run docs-harvester <URL> [OPTIONS]

Options:
  --max-pages N        Maximum pages to crawl (default: unlimited)
  --output-dir DIR     Output directory (default: harvested_docs)
  --format FORMAT      Output format: pdf, json, html, or both (default: both)
  --no-images          Strip images from output (useful for JSON-only scraping)
  --incremental        Skip already-scraped pages and continue from last run
  --cache-ttl SECONDS  Enable HTTP caching with TTL (e.g., 3600 for 1 hour)
  -v, --verbose        Enable debug logging
```

### GitHub Fetcher

```bash
uv run github-docs <REPO_URL> [OPTIONS]

Options:
  --output-dir DIR     Output directory (default: harvested_docs)
  --format FORMAT      Output format: pdf, json, or both (default: both)
  --github-token TOKEN GitHub PAT (or set GITHUB_TOKEN env var)
  -v, --verbose        Enable debug logging
```

## Features

### Performance Optimizations
- **lxml parser** - 2-5x faster HTML parsing than default html.parser
- **HTTP caching** - Optional response caching with configurable TTL
- **Incremental scraping** - Resume interrupted scrapes, continue from where you left off
- **Smart retry logic** - Automatic retries with exponential backoff

### Output Flexibility
- **Multiple formats** - PDF, JSON, HTML, or combined output
- **Image control** - Include images (with fixed URLs) or strip them entirely
- **Unlimited scraping** - No arbitrary page limits (or set --max-pages for control)
- **Auto-save** - Progress saved every 10 pages (recoverable if interrupted)

### Safety Features
- **Non-docs detection** - Stops if too many non-documentation URLs found
- **Rate limiting** - Configurable delays between requests
- **Proper User-Agent** - Identifies as Kaxo-DocsHarvester
- **GitHub token support** - Avoid rate limits on public repos

## Supported Sources

### Documentation Sites
- Docusaurus
- GitBook
- MkDocs
- Sphinx
- Most static documentation generators

### GitHub Repositories
- Any public repository
- Markdown files in any directory structure
- Automatic path detection (docs/, doc/, documentation/)

## Development

```bash
# Install with dev dependencies
uv sync --all-extras

# Format
uv run ruff format .

# Lint
uv run ruff check --fix .

# Type check
uv run mypy src/

# Test
uv run pytest
```

## License

Copyright (c) 2025 Kaxo Technologies

Licensed for personal and non-commercial use.
Commercial use requires permission from Kaxo Technologies.

Contact: tech@kaxo.io

---

**Kaxo Technologies** — AI automation for Canadian businesses.
[kaxo.io](https://kaxo.io)
