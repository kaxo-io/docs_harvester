# Documentation Harvester

Automatically scrape and compile documentation websites into PDFs and JSON files.

## Quick Start (Zero Setup)

For OpenWebUI docs specifically:

```bash
# Make scripts executable
chmod +x setup.sh run_harvester.sh

# Run everything automatically
./run_harvester.sh
```

This will:
1. Set up the environment if needed
2. Harvest OpenWebUI docs (up to 50 pages)
3. Generate both PDF and JSON outputs

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

### 3. Run Harvester
```bash
# Basic usage
python doc_harvester.py https://docs.openwebui.com

# With options
python doc_harvester.py https://docs.openwebui.com --max-pages 100 --format pdf
```

## Options

- `--max-pages N`: Maximum pages to crawl (default: 100)
- `--format pdf|json|both`: Output format (default: both)
- `--output-dir DIR`: Output directory (default: harvested_docs)

## Requirements

- Python 3.8+
- System dependencies for PDF generation (auto-installed by setup script)

## Supported Documentation Sites

- Docusaurus (like OpenWebUI)
- GitBook
- MkDocs
- Custom documentation sites
- Most static documentation generators

## Troubleshooting

### PDF Generation Issues
If PDF generation fails, check the HTML output first. The harvester will always generate an HTML file even if PDF fails.

### Missing Pages
Some sites use JavaScript navigation. The harvester works best with static HTML links.

### Permission Errors
Run setup.sh with appropriate permissions for system package installation.
