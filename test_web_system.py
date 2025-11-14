"""
Test script to verify the web story system is working correctly
Run this before starting the server to catch issues early
"""

import sys
import os

print("=" * 70)
print("  WASTELAND STORIES - SYSTEM VERIFICATION TEST")
print("=" * 70)
print()

# Test 1: Python version
print("✓ Test 1: Python version")
print(f"  Python {sys.version}")
print()

# Test 2: Required imports
print("✓ Test 2: Checking required packages...")
issues = []

try:
    import flask
    print(f"  ✓ Flask {flask.__version__}")
except ImportError as e:
    print(f"  ✗ Flask NOT FOUND")
    issues.append("Flask not installed")

try:
    import flask_cors
    print(f"  ✓ Flask-CORS installed")
except ImportError:
    print(f"  ✗ Flask-CORS NOT FOUND")
    issues.append("Flask-CORS not installed")

try:
    import transformers
    print(f"  ✓ Transformers {transformers.__version__}")
except ImportError:
    print(f"  ✗ Transformers NOT FOUND")
    issues.append("Transformers not installed")

try:
    import torch
    print(f"  ✓ PyTorch {torch.__version__}")
except ImportError:
    print(f"  ✗ PyTorch NOT FOUND")
    issues.append("PyTorch not installed")

print()

# Test 3: Import custom modules
print("✓ Test 3: Checking custom modules...")
try:
    from adaptive_story_engine import AdaptiveStoryEngine, StoryBeat
    print("  ✓ adaptive_story_engine.py imports successfully")
except Exception as e:
    print(f"  ✗ adaptive_story_engine.py IMPORT ERROR: {e}")
    issues.append(f"adaptive_story_engine import failed: {e}")

try:
    from web_story_server import app
    print("  ✓ web_story_server.py imports successfully")
except Exception as e:
    print(f"  ✗ web_story_server.py IMPORT ERROR: {e}")
    issues.append(f"web_story_server import failed: {e}")

print()

# Test 4: Check file structure
print("✓ Test 4: Checking file structure...")
required_files = [
    'adaptive_story_engine.py',
    'web_story_server.py',
    'templates/terminal.html',
    'static/terminal.css',
    'static/terminal.js'
]

for file in required_files:
    if os.path.exists(file):
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} MISSING")
        issues.append(f"Missing file: {file}")

print()

# Test 5: Test story engine initialization
print("✓ Test 5: Testing story engine initialization...")
try:
    print("  Loading DistilGPT2 model (this may take a moment)...")
    from adaptive_story_engine import AdaptiveStoryEngine
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    print("  ✓ Story engine initialized successfully")
    print(f"  ✓ Model loaded: distilgpt2")
    print(f"  ✓ Tokenizer ready: {len(engine.tokenizer)} vocab size")
except Exception as e:
    print(f"  ✗ Engine initialization FAILED: {e}")
    issues.append(f"Engine init failed: {e}")

print()

# Test 6: Quick generation test
print("✓ Test 6: Testing text generation...")
try:
    test_prompt = "It was a dark night"
    result = engine._generate_text(test_prompt, max_length=20)
    print(f"  ✓ Generation works")
    print(f"  Sample output: {result[:100]}...")
except Exception as e:
    print(f"  ✗ Generation FAILED: {e}")
    issues.append(f"Text generation failed: {e}")

print()

# Test 7: Test Flask routes
print("✓ Test 7: Checking Flask routes...")
try:
    from web_story_server import app
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    expected_routes = ['/api/start', '/api/action', '/api/chapters', '/api/search']
    for route in expected_routes:
        if route in routes:
            print(f"  ✓ {route}")
        else:
            print(f"  ✗ {route} MISSING")
            issues.append(f"Missing route: {route}")
except Exception as e:
    print(f"  ✗ Route check FAILED: {e}")
    issues.append(f"Route check failed: {e}")

print()

# Summary
print("=" * 70)
print("  TEST SUMMARY")
print("=" * 70)

if not issues:
    print("✅ ALL TESTS PASSED!")
    print()
    print("🚀 System is ready to run!")
    print("   Start the server with:")
    print("   ./bin/python web_story_server.py")
    print()
    print("   Then open: http://localhost:5000")
else:
    print(f"❌ {len(issues)} ISSUE(S) FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print()
    print("⚠️  Please fix these issues before running the server")

print("=" * 70)
