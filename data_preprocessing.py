# data_preprocessing.py
# This script preprocesses text data from gutenberg_texts.csv for story generation

import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
import pickle

# Load the data
print("Loading data from gutenberg_texts.csv...")
num_rows_to_load = 1000  # Adjust this to process more/fewer rows
try:
    df = pd.read_csv("gutenberg_texts.csv", nrows=num_rows_to_load)
    print(f"Loaded {len(df)} chapters from CSV")
except FileNotFoundError:
    print("ERROR: gutenberg_texts.csv not found!")
    print("Please run gutenberg_spider_fixed.py first to generate the training data.")
    exit(1)

# Combine all text into one corpus
text = ' '.join(df['Text'].tolist())
print(f"Total text length: {len(text)} characters")

# Tokenize the text
print("Tokenizing text...")
tokenizer = Tokenizer()
tokenizer.fit_on_texts([text])
sequences = tokenizer.texts_to_sequences([text])[0]

vocab_size = len(tokenizer.word_index) + 1
print(f"Vocabulary size: {vocab_size}")
print(f"Total tokens: {len(sequences)}")

# Create input sequences (pairs of consecutive words)
# This creates training data where X is one word and y is the next word
input_sequences = []
for i in range(1, len(sequences)):
    seq = sequences[i-1:i+1]  # Creates pairs of consecutive token indices
    input_sequences.append(seq)

print(f"Created {len(input_sequences)} training sequences")

# Save tokenizer
with open('tokenizer.pkl', 'wb') as tokenizer_file:
    pickle.dump(tokenizer, tokenizer_file)
print("Saved tokenizer.pkl")

# Save input_sequences for training
with open('input_sequences.pkl', 'wb') as file:
    pickle.dump(input_sequences, file)
print("Saved input_sequences.pkl")

print("\nData preprocessing completed successfully!")
print(f"Sample sequence (first 5): {input_sequences[:5]}")
