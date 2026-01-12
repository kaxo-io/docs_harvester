#!/usr/bin/env bash
# Documentation Website Harvester
#
# Copyright (c) 2025 Kaxo Technologies
# Contact: tech@kaxo.io
#
# Licensed for personal and non-commercial use.
# Commercial use requires permission from Kaxo Technologies.

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📚 Documentation Website Harvester"

# Require URL argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <documentation_url> [max_pages]"
    echo "Example: $0 https://docs.n8n.io 50"
    exit 1
fi

URL="$1"
MAX_PAGES="${2:-100}"

echo "Target: $URL"
echo "Max pages: $MAX_PAGES"

cd "$PROJECT_DIR"

# Use uv to run
if command -v uv &> /dev/null; then
    uv run docs-harvester "$URL" --max-pages "$MAX_PAGES" --format both
else
    echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Complete! Check the 'harvested_docs' folder."
