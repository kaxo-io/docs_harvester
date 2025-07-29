                                                                                                                                        
                                     ..:++++-... ........  ..                                       
                                     .:+@@@@#=.... ......  ..                                       
                                  ...-*@@@@@@%*:....... .....                                       
                                ...:+%@@@@@@@@@#=...... .  ..                                       
                                .:+%@@@@@-.#@@@@@*=......  ..                                       
                           ....:+%@@@@@%....-@@@@@@#=........                                       
                          ...-#@@@@@@@-.......*@@@@@@%*:.....                                       
                        ..=%@@@@@@@@+..........:#@@@@@@@@*:..                                       
                        .=@@@@@@@@=..............:#@@@@@@@%-.                                       
                        .=%%%@@@@#.............::.:@@@@#%%#-.   ....                                
                ......  .-%@@@@@@@@:....... .....+@@@@@@@@*:......                                  
                ..=+=.......-%@@@@@+.............@@@@@@+.......:--:..                               
               ..+@@@*...... ..@%@@*.............@@@@*...... .:%@@@-.                               
              ..*@@%@@#........@@@@+......  .....@@@@+.......-@@@@@@=.                              
            ...#@@@@@@@%:......@@@@+.:.... ......@@@@+......=@@@@@@@@*...                           
           ..=@@@@@@@@@@@@@@@@@@%@@*...... ......@@#@@@@@@@@@@@@@@@@@@%:..                          
        ...:%@@@@@@-%@@@@@@@@@@@@@@+.............@@@@@@@@@@@@@@@++@@@@@@#....                       
       ..-@@@@@@@*...*@@@@@@@@@@@@@-.............+@@@@@@@@@@@@@-..:@@@@@@@#...                      
 ......=@@@@@@@@-.....::......:.....................................*@@@@@@@%:.                     
 ...-@@@@@@@@@=..............:............ ...........................#@@@@@@@@#:...                
 .%@@@@@@@@@+.................. ........................................#@@@@@@@@@*.                
 .@@==@--%-...............................................................*%.#@-:@#.                
 .%@@@@@@@@@-........................................................ ..#@@@@@@@@@*.                
   .=@@@@@@@@@-..........................................:............+@@@@@@@@@-...                
 ......*@@@@@@@%:..::........  .....................................=%@@@@@@@=......                
 .... ...=@@@@@@@+...+@@@##%%%%%@@%:.............+@@@%%%####@@%...:%@@@@@@@:........                
   ..... ..=@@@@@@%:%@@@@@@@@@@@@@@=.............@@@@@@@@@@@@@@@++@@@@@@@:....   .                  
   ....  ....#@@@@@@@@@@@@@@@@@@@+@*.............@%+@@@@@@@@@@@@@@@@@@@-...                         
     ..   ....-@@@@%%@@@=......@@*@*... ........:@##@#......#@@@**@@@%....                          
 ........     ..@@@+@@@:. ... .@@#@*.............@%#@#... ...+@@@@@@*....                           
 .........    ...%@@@@....... .@@%@*.............@%%@#...   ..=@@@@=.....                           
 .........     ...#@#..   .   .@@%@+.. ..........@@%@#...     .-*#=..                               
 ..  ....       .......       .@@@@+.......... ..@@%@#...       .....                               
                             ..@@@@+.............@@%@# ..                                           
                             ..@@@@+........... .@@@@*..                                            
                             ..@@@@+.............@@@@*...                                           
                             ..@@@@+.............@@@@*...                                           
                             ..@@@@+.............@@@@*...                                           
                            ..+@@@@=.............@@@@@-..                                           
                        .....+@@@@@:.............+@@@@@:....                                        
                        ...:#@@@@@-...............*@@@@@*....                                       
                        :+@@@@@@@-.................*@@@@@@@=.                                       
                      ..:**-%@@@+...................#@@@=-#+.                                       
                     ...:+@@@@@@@@%..............-@@@@@@@@@=.                                       
                      ....:+%@@@@@@@%:... ... .-@@@@@@@@%=...                                       
                       ......:*@@@@@@@#.......@@@@@@@%=......                                       
                       .........=#@@@@@@-...+@@@@@%*-........                                       
                               ...=%@@@@@+.%@@@@%*-....... ..                                       
                               .....=#@@@@@@@@@*-............                                       
                                   ..-*@@@@@@%+..... ........                                       
                                                                                                             
                               ╔═══════════════════════╗
                               ║  SOLI • DEO • GLORIA  ║
                               ╚═══════════════════════╝
Copyright (c) 2025 Kaxo Technologies
Contact: tech [ a t ] kaxo.io

# Documentation Harvester Suite

Automatically scrape and compile documentation from websites and GitHub repositories into PDFs and JSON files.

## Tools Included

1. **Website Documentation Harvester** (`doc_harvester.py`) - For documentation sites like Docusaurus, GitBook, MkDocs
2. **GitHub Documentation Fetcher** (`github_doc_fetcher.py`) - For GitHub repositories with markdown files

## Quick Start (Zero Setup)

### For Any GitHub Repository
```bash
# Make scripts executable
chmod +x setup.sh fetch_github_docs.sh

# Fetch any GitHub repo's docs (defaults to Ollama if no URL provided)
./fetch_github_docs.sh
./fetch_github_docs.sh https://github.com/owner/repo
./fetch_github_docs.sh https://github.com/owner/repo/tree/branch/docs
```

### For Documentation Websites
```bash
# Make scripts executable  
chmod +x setup.sh run_harvester.sh

# Run OpenWebUI docs (default) or specify URL
./run_harvester.sh
./run_harvester.sh ollama  # Not applicable for website harvester
```

## Example Usage

```bash
# GitHub repositories
./fetch_github_docs.sh https://github.com/ollama/ollama/tree/main/docs
./fetch_github_docs.sh https://github.com/openai/openai-python
./fetch_github_docs.sh https://github.com/anthropic/anthropic-sdk-python/tree/main/docs

# Documentation websites
python doc_harvester.py https://docs.openwebui.com
python doc_harvester.py https://docs.anthropic.com
python doc_harvester.py https://platform.openai.com/docs
```

## GitHub Fetcher Features

- **Smart URL parsing** - handles various GitHub URL formats
- **Recursive directory crawling** - finds all markdown files in subdirectories  
- **Auto path detection** - tries common paths like `docs/`, `doc/`, `documentation/`
- **Organized output** - separate folders per repository
- **GitHub-style formatting** - matches GitHub's markdown rendering

## Website Harvester Features

- **Framework detection** - automatically handles Docusaurus, GitBook, MkDocs, etc.
- **Smart navigation** - follows documentation site structure
- **Content extraction** - filters out navigation and focuses on main content
- **Safety limits** - prevents runaway crawling

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

### Common Options
- `--format pdf|json|both`: Output format (default: both)
- `--output-dir DIR`: Output directory

### Website Harvester Specific
- `--max-pages N`: Maximum pages to crawl (default: 100)

### GitHub Fetcher Specific
- Automatically detects and processes all markdown files in repository

## Output Structure

### GitHub Documentation
```
github_docs/
├── owner_repo_docs/
│   ├── markdown/              # Raw .md files with directory structure
│   ├── owner_repo_docs.pdf    # Combined PDF with TOC
│   ├── owner_repo_docs.json   # JSON data
│   └── owner_repo_docs.pdf.html # HTML version
```

### Website Documentation
```
harvested_docs/
├── docs_example_com.pdf       # Combined PDF
├── docs_example_com.json      # JSON data
└── docs_example_com.pdf.html  # HTML version
```

## Requirements

- Python 3.8+
- System dependencies for PDF generation (auto-installed by setup script)

## Supported Sources

### GitHub Repositories
- Any public GitHub repository
- Markdown files in any directory structure
- Handles various URL formats automatically
- Recursive directory traversal

### Documentation Sites
- Docusaurus (like OpenWebUI)
- GitBook
- MkDocs
- Custom documentation sites
- Most static documentation generators

## Troubleshooting

### PDF Generation Issues
If PDF generation fails, check the HTML output first. Both tools will always generate an HTML file even if PDF fails.

### GitHub API Rate Limits
The GitHub fetcher uses the public API and respects rate limits. For private repos, you'd need to add authentication.

### Website Crawling Issues
Some sites use JavaScript navigation. The website harvester works best with static HTML links.

### Missing Files/Pages
- **GitHub**: Fetcher tries common documentation paths automatically
- **Websites**: Check that the site uses standard navigation patterns

### Permission Errors
Run setup.sh with appropriate permissions for system package installation.

## Files in This Directory

- `doc_harvester.py` - Website documentation scraper
- `github_doc_fetcher.py` - GitHub repository documentation fetcher  
- `setup.sh` - Environment setup script
- `run_harvester.sh` - Quick runner for website docs
- `fetch_github_docs.sh` - Quick runner for GitHub docs
- `requirements.txt` - Python dependencies
- `README.md` - This file

Both tools are designed to work together and share the same virtual environment setup.on
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