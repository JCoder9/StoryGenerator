#!/bin/bash

# One-Command Build Script for All Platforms
# Creates production-ready distribution files

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   AI Story Generator - Complete Build Process     ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    echo ""
    echo "Install with: brew install node"
    echo "Or download: https://nodejs.org/"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --quiet
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf AIStoryGenerator-darwin-x64 AIStoryGenerator-win32-x64 AIStoryGenerator-linux-x64
rm -f AIStoryGenerator-*.zip AIStoryGenerator-*.tar.gz

echo ""
echo "🔨 Building for all platforms..."
echo ""

# Build Mac
echo "   📱 macOS..."
npm run package-mac --silent

# Build Windows  
echo "   🪟 Windows..."
npm run package-win --silent

# Build Linux
echo "   🐧 Linux..."
npm run package-linux --silent

echo ""
echo "📦 Creating distribution packages..."
echo ""

# Zip Mac
echo "   Compressing macOS app..."
cd AIStoryGenerator-darwin-x64
zip -r -q ../AIStoryGenerator-mac-v1.0.0.zip AIStoryGenerator.app
cd ..

# Zip Windows
echo "   Compressing Windows app..."
cd AIStoryGenerator-win32-x64
zip -r -q ../AIStoryGenerator-windows-v1.0.0.zip .
cd ..

# Tar Linux
echo "   Compressing Linux app..."
cd AIStoryGenerator-linux-x64
tar -czf ../AIStoryGenerator-linux-v1.0.0.tar.gz .
cd ..

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║                  ✅ BUILD COMPLETE!                ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📦 Distribution files created:"
echo ""

# Show file sizes
if command -v du &> /dev/null; then
    echo "   🍎 Mac:     $(du -h AIStoryGenerator-mac-v1.0.0.zip | cut -f1)"
    echo "   🪟 Windows: $(du -h AIStoryGenerator-windows-v1.0.0.zip | cut -f1)"
    echo "   🐧 Linux:   $(du -h AIStoryGenerator-linux-v1.0.0.tar.gz | cut -f1)"
else
    ls -lh AIStoryGenerator-*.{zip,tar.gz} 2>/dev/null | awk '{print "   " $9 ": " $5}'
fi

echo ""
echo "📤 Upload these files to your website!"
echo ""
echo "Ready to distribute:"
echo "   • AIStoryGenerator-mac-v1.0.0.zip"
echo "   • AIStoryGenerator-windows-v1.0.0.zip"
echo "   • AIStoryGenerator-linux-v1.0.0.tar.gz"
echo ""
