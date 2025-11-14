"""
Interactive Story Generator
Generates dynamic narratives based on user input and trained LSTM model
"""

import pickle
import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

def load_model_and_tokenizer(model_path, tokenizer_path):
    """Load the trained model and tokenizer"""
    try:
        model = keras.models.load_model(model_path)
        with open(tokenizer_path, 'rb') as tokenizer_file:
            tokenizer = pickle.load(tokenizer_file)
        return model, tokenizer
    except FileNotFoundError as e:
        print(f"ERROR: Could not find {e.filename}")
        print("Please ensure you have:")
        print("1. Run gutenberg_spider_fixed.py to generate data")
        print("2. Run data_preprocessing.py to create tokenizer")
        print("3. Run train_model.py to train the model")
        exit(1)

def generate_text(model, tokenizer, seed_text, num_words=50, temperature=1.0):
    """
    Generate text based on seed text
    
    Args:
        model: Trained Keras model
        tokenizer: Fitted tokenizer
        seed_text: Starting text
        num_words: Number of words to generate
        temperature: Controls randomness (higher = more random)
    
    Returns:
        Generated text string
    """
    generated_text = seed_text
    
    for _ in range(num_words):
        # Tokenize current text
        seq = tokenizer.texts_to_sequences([generated_text])
        
        if not seq or not seq[0]:
            # If tokenization fails, try with just the last few words
            words = generated_text.split()
            if len(words) > 5:
                generated_text = " ".join(words[-5:])
                seq = tokenizer.texts_to_sequences([generated_text])
            
            if not seq or not seq[0]:
                print("Warning: Could not tokenize text. Stopping generation.")
                break
        
        # Get the last token
        token = seq[0][-1] if seq[0] else 0
        token_array = np.array([[token]])
        
        # Predict next word
        preds = model.predict(token_array, verbose=0)[0]
        
        # Apply temperature to predictions
        preds = np.log(preds + 1e-7) / temperature
        preds = np.exp(preds)
        preds = preds / np.sum(preds)
        
        # Sample next word index
        next_word_index = np.random.choice(len(preds), p=preds)
        
        # Convert index to word
        next_word = tokenizer.index_word.get(next_word_index, '')
        
        if not next_word:
            continue
            
        # Append to generated text
        generated_text += " " + next_word
        
        # Stop at sentence end for natural breaks
        if next_word in ['.', '!', '?'] and len(generated_text.split()) > 10:
            # 30% chance to stop at sentence end
            if np.random.random() < 0.3:
                break
    
    return generated_text

def interactive_story():
    """Main interactive story generation loop"""
    model_path = 'story_generator_model.h5'
    tokenizer_path = 'tokenizer.pkl'
    
    print("=" * 60)
    print("INTERACTIVE STORY GENERATOR")
    print("=" * 60)
    print("\nLoading model and tokenizer...")
    
    model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
    
    print("✓ Model loaded successfully!")
    print(f"✓ Vocabulary size: {len(tokenizer.word_index)}")
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("- Type your story beginning or character action")
    print("- Press ENTER to let the AI continue the story")
    print("- Type 'new' to start a fresh story")
    print("- Type 'quit' to exit")
    print("=" * 60)
    
    # Default starting prompts
    default_prompts = [
        "Once upon a time in a distant land",
        "The old castle stood on the hill",
        "She walked into the mysterious forest",
        "It was a dark and stormy night",
        "The treasure map led them to"
    ]
    
    seed_text = np.random.choice(default_prompts)
    
    while True:
        print(f"\n{'─' * 60}")
        print("Current story start:", seed_text)
        print("─" * 60)
        
        user_input = input("\nYour input (or press ENTER to generate): ").strip()
        
        if user_input.lower() == 'quit':
            print("\nThank you for using the Story Generator!")
            break
        elif user_input.lower() == 'new':
            seed_text = np.random.choice(default_prompts)
            print(f"\nNew story started: {seed_text}")
            continue
        elif user_input:
            # User provided new text
            seed_text = user_input
        
        # Generate story continuation
        print("\n📖 Generating story...\n")
        generated_story = generate_text(
            model, 
            tokenizer, 
            seed_text, 
            num_words=50,
            temperature=0.8  # Slightly random but coherent
        )
        
        print("─" * 60)
        print(generated_story)
        print("─" * 60)
        
        # Update seed for next iteration
        seed_text = generated_story

def main():
    """Entry point"""
    try:
        interactive_story()
    except KeyboardInterrupt:
        print("\n\nStory generation interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
