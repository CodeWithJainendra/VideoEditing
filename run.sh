#!/bin/bash
# ClipForge - Setup and Run Script

echo "🎬 ClipForge Video Editor"
echo "========================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Install it from https://www.python.org/downloads/"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo "   Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Please install FFmpeg manually:"
        echo "   macOS: brew install ffmpeg"
        echo "   Windows: choco install ffmpeg"
        exit 1
    fi
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Run the app
echo ""
echo "🚀 Starting ClipForge..."
echo ""
python main.py
