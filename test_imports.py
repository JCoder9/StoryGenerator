"""Quick validation that imports work"""
print("Testing imports...")

try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    print("✓ transformers imported")
except ImportError as e:
    print(f"✗ transformers import failed: {e}")
    exit(1)

try:
    import torch
    print("✓ torch imported")
except ImportError as e:
    print(f"✗ torch import failed: {e}")
    exit(1)

try:
    from adaptive_story_engine import AdaptiveStoryEngine
    print("✓ adaptive_story_engine imported")
except Exception as e:
    print(f"✗ adaptive_story_engine import failed: {e}")
    exit(1)

print("\n✅ All imports successful!")
print("\nReady to run:")
print("  python adaptive_story_engine.py")
