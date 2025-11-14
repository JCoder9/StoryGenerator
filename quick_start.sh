#!/bin/bash
# Quick start script for Story Tree System

echo "🚀 Starting Story Tree System..."
echo ""

# Set environment variables
export KMP_DUPLICATE_LIB_OK=TRUE
export USE_TF=NO
export USE_TORCH=YES
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1
export TF_CPP_MIN_LOG_LEVEL=3

# Change to script directory
cd "$(dirname "$0")"

# Start server
echo "📡 Starting Flask server at http://localhost:5000"
echo "⏱️  First startup takes 30-60 seconds (model loading)..."
echo "🎮 Press Ctrl+C to shutdown"
echo ""

./bin/python web_story_server_enhanced.py
