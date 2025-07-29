#!/bin/bash
# Universal GitHub Documentation Fetcher
#
# Copyright (c) 2025 Kaxo Technologies
# Contact: tech [ a t ] kaxo.io
# Vibe coded by Kaxo Technologies
#
# Licensed for personal and non-commercial use.
# Commercial use requires permission from Kaxo Technologies.

set -e

echo "📚 Universal GitHub Documentation Fetcher"

# Default to Ollama if no URL provided
if [ -z "$1" ]; then
    URL="https://github.com/ollama/ollama/tree/main/docs"
    echo "Using default: Ollama documentation"
else
    URL="$1"
fi

echo "Target: $URL"

# Check if virtual environment exists
if [ ! -d "doc_harvester_env" ]; then
    echo "❌ Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment
echo "🔧 Activating environment..."
source doc_harvester_env/bin/activate

# Fetch docs
echo "🕷️  Fetching documentation..."
python github_doc_fetcher.py "$URL" --format both

echo "✅ Complete! Check the 'harvested_docs' folder for output files."
echo ""
echo "Usage examples:"
echo "  ./fetch_github_docs.sh https://github.com/ollama/ollama/tree/main/docs"
echo "  ./fetch_github_docs.sh https://github.com/openai/openai-python"
echo "  ./fetch_github_docs.sh https://github.com/anthropic/anthropic-sdk-python/tree/main/docs"