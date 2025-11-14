#!/bin/bash
# Upgrade transformers to support Qwen2.5-1.5B-Instruct

echo "================================================"
echo "🔧 Upgrading transformers for Qwen support"
echo "================================================"
echo ""
echo "Current transformers version:"
python3.9 -m pip show transformers | grep Version

echo ""
echo "📥 Upgrading to latest transformers..."
python3.9 -m pip install --upgrade transformers

echo ""
echo "✅ New transformers version:"
python3.9 -m pip show transformers | grep Version

echo ""
echo "================================================"
echo "✨ Upgrade complete!"
echo "================================================"
echo ""
echo "📝 Next steps:"
echo "   1. Restart your server: python3.9 web_story_server_enhanced.py"
echo "   2. Server will now use Qwen2.5-1.5B-Instruct (much better!)"
echo ""
echo "💡 First run will download Qwen model (~3GB)"
echo "   This is a ONE-TIME download"
echo ""
