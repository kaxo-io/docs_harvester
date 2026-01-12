#!/usr/bin/env bash
# Universal GitHub Documentation Fetcher
#
# Copyright (c) 2025 Kaxo Technologies
# Contact: tech@kaxo.io
#
# Licensed for personal and non-commercial use.
# Commercial use requires permission from Kaxo Technologies.

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📚 Universal GitHub Documentation Fetcher"

# Default to Ollama if no URL provided
URL="${1:-https://github.com/ollama/ollama/tree/main/docs}"
echo "Target: $URL"

cd "$PROJECT_DIR"

# Use uv to run
if command -v uv &> /dev/null; then
    uv run github-docs "$URL" --format both
else
    echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Complete! Check the 'harvested_docs' folder."
