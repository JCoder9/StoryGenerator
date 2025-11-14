"""
Quick test script to verify the trained model works
"""

import pickle
import numpy as np
from tensorflow import keras

print("Testing Story Generator Model...")
print("=" * 60)

# Load model
print("\n1. Loading model...")
try:
    model = keras.models.load_model('story_generator_model.h5')
    print("   ✓ Model loaded successfully")
except Exception as e:
    print(f"   ✗ Error loading model: {e}")
    exit(1)

# Load tokenizer
print("\n2. Loading tokenizer...")
try:
    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    vocab_size = len(tokenizer.word_index) + 1
    print(f"   ✓ Tokenizer loaded (vocab size: {vocab_size})")
except Exception as e:
    print(f"   ✗ Error loading tokenizer: {e}")
    exit(1)

# Test prediction
print("\n3. Testing model prediction...")
try:
    # Test with a simple word
    test_word = "the"
    seq = tokenizer.texts_to_sequences([test_word])
    if seq and seq[0]:
        token = seq[0][0]
        token_array = np.array([[token]])
        preds = model.predict(token_array, verbose=0)[0]
        
        # Get top 5 predictions
        top_5_indices = preds.argsort()[-5:][::-1]
        print(f"   ✓ Prediction successful!")
        print(f"\n   Input word: '{test_word}'")
        print(f"   Top 5 predicted next words:")
        for i, idx in enumerate(top_5_indices, 1):
            word = tokenizer.index_word.get(idx, '<unknown>')
            prob = preds[idx]
            print(f"      {i}. '{word}' (probability: {prob:.4f})")
    else:
        print("   ✗ Could not tokenize test word")
        exit(1)
except Exception as e:
    print(f"   ✗ Error during prediction: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test short generation
print("\n4. Testing short story generation...")
try:
    seed_text = "Once upon a time"
    generated = seed_text
    
    for _ in range(10):
        seq = tokenizer.texts_to_sequences([generated])
        if seq and seq[0]:
            token = seq[0][-1]
            token_array = np.array([[token]])
            preds = model.predict(token_array, verbose=0)[0]
            
            # Sample with temperature
            preds = np.log(preds + 1e-7) / 0.8
            preds = np.exp(preds) / np.sum(np.exp(preds))
            
            next_idx = np.random.choice(len(preds), p=preds)
            next_word = tokenizer.index_word.get(next_idx, '')
            
            if next_word:
                generated += " " + next_word
    
    print(f"   ✓ Generation successful!")
    print(f"\n   Generated text:\n   '{generated}'")
except Exception as e:
    print(f"   ✗ Error during generation: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! The model is working correctly.")
print("\nYou can now run interactive_story_generator.py for")
print("interactive story generation.")
print("=" * 60)
