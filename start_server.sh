#!/bin/bash

# Story Generator Enhanced Server - Startup Script
# This script handles environment setup and starts the server

echo "🎮 Story Generator Enhanced - Starting Server"
echo "=============================================="
echo ""

# Fix OpenMP library conflict on macOS (CRITICAL for PyTorch)
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1

# Suppress OpenMP warnings
export KMP_WARNINGS=FALSE

# Prevent TensorFlow import issues (transformers tries to import it)
export TF_CPP_MIN_LOG_LEVEL=3
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ℹ️  Not in a virtual environment"
    # Try to activate virtual environment if it exists
    if [ -f "bin/activate" ]; then
        echo "🔄 Activating virtual environment..."
        source bin/activate
        echo "✓ Virtual environment activated"
    fi
else
    echo "✓ Using virtual environment: $VIRTUAL_ENV"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "✓ Python: $PYTHON_VERSION"

# Check dependencies
echo ""
echo "Checking dependencies..."

python3 -c "import flask" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Flask installed"
else
    echo "❌ Flask not found. Install with: pip install flask flask-cors"
    exit 1
fi

python3 -c "import flask_cors" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Flask-CORS installed"
else
    echo "❌ Flask-CORS not found. Install with: pip install flask-cors"
    exit 1
fi

python3 -c "import transformers" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Transformers installed"
else
    echo "❌ Transformers not found. Install with: pip install transformers"
    exit 1
fi

python3 -c "import torch" 2>/dev/null
if [ $? -eq 0 ]; then
    TORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)" 2>/dev/null)
    echo "✓ PyTorch $TORCH_VERSION installed"
else
    echo "❌ PyTorch not found. Install with: pip install torch"
    exit 1
fi

echo ""
echo "All dependencies OK!"
echo ""
echo "Starting Flask server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
python3 web_story_server_enhanced.py

# If server exits, show message
echo ""
echo "Server stopped."
