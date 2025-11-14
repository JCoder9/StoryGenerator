#!/usr/bin/env python3
"""
Quick diagnostic test before starting the server
"""

import os
import sys

# Set environment variables BEFORE any imports
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

print("🔍 Running Pre-Startup Diagnostics...")
print("=" * 50)

# Test 1: Python version
print(f"\n✓ Python {sys.version}")

# Test 2: Flask
try:
    import flask
    print(f"✓ Flask {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask not installed: {e}")
    sys.exit(1)

# Test 3: Flask-CORS
try:
    import flask_cors
    print(f"✓ Flask-CORS installed")
except ImportError as e:
    print(f"❌ Flask-CORS not installed: {e}")
    sys.exit(1)

# Test 4: Transformers (this is the critical one)
try:
    print("\n🔄 Testing transformers import (may take 10-15 seconds)...")
    from transformers import GPT2Tokenizer
    print("✓ Transformers imported successfully")
except Exception as e:
    print(f"❌ Transformers import failed: {e}")
    sys.exit(1)

# Test 5: PyTorch
try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
except ImportError as e:
    print(f"❌ PyTorch not installed: {e}")
    sys.exit(1)

# Test 6: Check if models exist in cache
cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
if os.path.exists(cache_dir):
    models = [d for d in os.listdir(cache_dir) if d.startswith('models--')]
    if models:
        print(f"\n📦 Found {len(models)} cached models:")
        for model in models[:5]:  # Show first 5
            model_name = model.replace('models--', '').replace('--', '/')
            print(f"   - {model_name}")
    else:
        print("\n📦 No models cached yet (will download on first run)")
else:
    print("\n📦 Model cache directory doesn't exist (will be created)")

# Test 7: Import our modules
try:
    print("\n🔄 Testing story engine import...")
    from adaptive_story_engine_enhanced import AdaptiveStoryEngine
    print("✓ AdaptiveStoryEngine imported")
except Exception as e:
    print(f"❌ Story engine import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ ALL DIAGNOSTICS PASSED!")
print("\nYou can now start the server with:")
print("  ./start_server.sh")
print("  OR")
print("  python3 web_story_server_enhanced.py")
print("=" * 50)
