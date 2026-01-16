#!/bin/bash
# ======================================
# ClipForge - Build Script
# Creates a standalone executable
# ======================================

echo "🎬 ClipForge Build Script"
echo "========================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "   Run: python3 -m venv venv"
    exit 1
fi

# Install PyInstaller if not present
pip show pyinstaller > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Create app icon placeholder if not exists
mkdir -p assets/icons
if [ ! -f "assets/icons/app_icon.icns" ]; then
    echo "⚠️  No app icon found. Using default."
fi

# Build the executable
echo ""
echo "🔨 Building ClipForge..."
echo ""

pyinstaller build_exe.spec --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build complete!"
    echo ""
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "📦 Output: dist/ClipForge.app"
        echo ""
        echo "To run: open dist/ClipForge.app"
        echo "To distribute: zip the .app folder"
    else
        echo "📦 Output: dist/ClipForge.exe"
        echo ""
        echo "To run: double-click ClipForge.exe"
    fi
else
    echo ""
    echo "❌ Build failed! Check errors above."
fi
