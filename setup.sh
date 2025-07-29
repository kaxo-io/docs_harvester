#!/bin/bash
# Documentation Harvester Setup Script

set -e  # Exit on any error

echo "🚀 Setting up Documentation Harvester..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv doc_harvester_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source doc_harvester_env/bin/activate

# Install system dependencies for WeasyPrint (varies by OS)
echo "🔨 Installing system dependencies..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
    elif command -v yum &> /dev/null; then
        sudo yum install -y pango harfbuzz
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y pango harfbuzz
    else
        echo "⚠️  Please install pango and harfbuzz manually for your Linux distribution"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install pango
    else
        echo "⚠️  Please install Homebrew and run: brew install pango"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "⚠️  On Windows, WeasyPrint dependencies are automatically handled by pip"
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To use the harvester:"
echo "1. Activate the environment: source doc_harvester_env/bin/activate"
echo "2. Run: python doc_harvester.py <URL>"
echo ""
echo "Example: python doc_harvester.py https://docs.openwebui.com"
