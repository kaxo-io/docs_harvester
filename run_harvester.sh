#!/bin/bash
# One-click harvester runner for OpenWebUI docs

set -e

echo "🕷️  Starting Documentation Harvester..."

# Check which docs to harvest
if [ "$1" = "ollama" ]; then
    URL="https://github.com/ollama/ollama/tree/main/docs"
    echo "📚 Harvesting Ollama documentation..."
else
    URL="https://docs.openwebui.com"
    echo "📚 Harvesting OpenWebUI documentation..."
fi

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