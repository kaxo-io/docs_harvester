#!/bin/bash
# One-click harvester runner for OpenWebUI docs

set -e

echo "🕷️  Starting OpenWebUI Documentation Harvester..."

# Check if virtual environment exists
if [ ! -d "doc_harvester_env" ]; then
    echo "❌ Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment
echo "🔧 Activating environment..."
source doc_harvester_env/bin/activate

# Run harvester on OpenWebUI docs
echo "📚 Harvesting OpenWebUI documentation..."
python doc_harvester.py https://docs.openwebui.com --max-pages 50 --format both

echo "✅ Complete! Check the 'harvested_docs' folder for:"
echo "   - PDF: docs_openwebui_com_docs.pdf"
echo "   - JSON: docs_openwebui_com_docs.json"
echo "   - HTML: docs_openwebui_com_docs.pdf.html"
