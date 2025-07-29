#!/bin/bash
# One-click harvester runner for documentation websites
#
# Copyright (c) 2025 Kaxo Technologies
# Contact: tech [ a t ] kaxo.io
# Vibe coded by Kaxo Technologies
#
# Licensed for personal and non-commercial use.
# Commercial use requires permission from Kaxo Technologies.

set -e

echo "🕷️  Starting Documentation Harvester..."

# Default to OpenWebUI docs if no URL provided
if [ -z "$1" ]; then
    URL="https://docs.openwebui.com"
    echo "Using default: OpenWebUI documentation"
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

# Run harvester
python doc_harvester.py "$URL" --max-pages 50 --format both

echo "✅ Complete! Check the 'harvested_docs' folder for output files."
echo ""
echo "Usage examples:"
echo "  ./run_harvester.sh https://docs.openwebui.com"
echo "  ./run_harvester.sh https://docs.anthropic.com"
echo "  ./run_harvester.sh https://platform.openai.com/docs"