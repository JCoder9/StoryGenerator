#!/bin/bash

echo "======================================================="
echo "🎮 AI Story Generator - Desktop App Builder"
echo "======================================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo ""
    echo "📦 Install Node.js first:"
    echo "   Option 1: brew install node"
    echo "   Option 2: Download from https://nodejs.org/"
    echo ""
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ npm found: $(npm --version)"
echo ""

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Electron dependencies..."
    echo "   (This will take 1-2 minutes on first run)"
    npm install
    echo ""
fi

# Ask what to do
echo "What would you like to do?"
echo ""
echo "1) Test app in development mode (quick test)"
echo "2) Build for Mac only"
echo "3) Build for Windows only"  
echo "4) Build for Linux only"
echo "5) Build for ALL platforms (Mac + Windows + Linux)"
echo "6) Build + Zip for distribution (ready to upload)"
echo "7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting app in development mode..."
        echo ""
        echo "   This will:"
        echo "   - Start Flask server on localhost:5000"
        echo "   - Open Electron window"
        echo "   - Load the story generator UI"
        echo ""
        echo "   Press Ctrl+C to stop"
        echo ""
        npm start
        ;;
    2)
        echo ""
        echo "📦 Building for macOS..."
        echo "   This creates: AIStoryGenerator-darwin-x64/AIStoryGenerator.app"
        echo ""
        npm run package-mac
        echo ""
        echo "✅ Done! Mac app created at:"
        echo "   ./AIStoryGenerator-darwin-x64/AIStoryGenerator.app"
        echo ""
        echo "To test it:"
        echo "   open ./AIStoryGenerator-darwin-x64/AIStoryGenerator.app"
        echo ""
        echo "To create zip for distribution:"
        echo "   npm run zip-mac"
        ;;
    3)
        echo ""
        echo "📦 Building for Windows..."
        echo "   This creates: AIStoryGenerator-win32-x64/"
        echo ""
        npm run package-win
        echo ""
        echo "✅ Done! Windows app created at:"
        echo "   ./AIStoryGenerator-win32-x64/AIStoryGenerator.exe"
        echo ""
        echo "To create zip for distribution:"
        echo "   npm run zip-win"
        ;;
    4)
        echo ""
        echo "📦 Building for Linux..."
        echo "   This creates: AIStoryGenerator-linux-x64/"
        echo ""
        npm run package-linux
        echo ""
        echo "✅ Done! Linux app created at:"
        echo "   ./AIStoryGenerator-linux-x64/AIStoryGenerator"
        echo ""
        echo "To create tar.gz for distribution:"
        echo "   npm run zip-linux"
        ;;
    5)
        echo ""
        echo "📦 Building for ALL platforms..."
        echo "   This will take 5-10 minutes on first run"
        echo ""
        npm run package-all
        echo ""
        echo "✅ Done! Apps created at:"
        echo "   ./AIStoryGenerator-darwin-x64/    (Mac)"
        echo "   ./AIStoryGenerator-win32-x64/     (Windows)"
        echo "   ./AIStoryGenerator-linux-x64/     (Linux)"
        echo ""
        echo "To create distribution files:"
        echo "   npm run zip-all"
        ;;
    6)
        echo ""
        echo "📦 Building + Zipping for ALL platforms..."
        echo "   This creates production-ready files for distribution"
        echo "   This will take 5-10 minutes on first run"
        echo ""
        npm run build-all
        echo ""
        echo "✅ Done! Distribution files created:"
        echo ""
        echo "   📦 AIStoryGenerator-mac-v1.0.0.zip         (Mac)"
        echo "   📦 AIStoryGenerator-windows-v1.0.0.zip     (Windows)"
        echo "   📦 AIStoryGenerator-linux-v1.0.0.tar.gz    (Linux)"
        echo ""
        echo "Upload these files to your website!"
        echo ""
        ls -lh AIStoryGenerator-*.{zip,tar.gz} 2>/dev/null
        ;;
    7)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "======================================================="
echo "Done!"
echo "======================================================="
