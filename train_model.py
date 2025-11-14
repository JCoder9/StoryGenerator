# train_model.py
# This script trains an LSTM model for story generation

import numpy as np
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import pickle

print("Loading preprocessed data...")

# Load input_sequences
try:
    with open('input_sequences.pkl', 'rb') as file:
        input_sequences = pickle.load(file)
    print(f"Loaded {len(input_sequences)} training sequences")
except FileNotFoundError:
    print("ERROR: input_sequences.pkl not found!")
    print("Please run data_preprocessing.py first.")
    exit(1)

# Load tokenizer
try:
    with open('tokenizer.pkl', 'rb') as file:
        tokenizer = pickle.load(file)
    vocab_size = len(tokenizer.word_index) + 1
    print(f"Vocabulary size: {vocab_size}")
except FileNotFoundError:
    print("ERROR: tokenizer.pkl not found!")
    print("Please run data_preprocessing.py first.")
    exit(1)

# Prepare training data
sequences = np.array(input_sequences)
X, y = sequences[:, 0], sequences[:, 1]

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"Sample X (first 5): {X[:5]}")
print(f"Sample y (first 5): {y[:5]}")

# Reshape X to add sequence dimension for LSTM
X = X.reshape(-1, 1)
print(f"Reshaped X: {X.shape}")

# Create the model
print("\nBuilding model...")
model = Sequential([
    Embedding(vocab_size, 100, input_length=1),
    LSTM(150, return_sequences=False),
    Dropout(0.2),
    Dense(100, activation='relu'),
    Dense(vocab_size, activation='softmax')
])

# Compile the model with sparse categorical crossentropy
# This is efficient for integer labels (no need to one-hot encode)
model.compile(
    loss='sparse_categorical_crossentropy', 
    optimizer='adam', 
    metrics=['accuracy']
)

model.summary()

# Set up callbacks
checkpoint = ModelCheckpoint(
    'story_generator_model.h5',
    monitor='accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)

early_stop = EarlyStopping(
    monitor='accuracy',
    patience=10,
    restore_best_weights=True,
    verbose=1
)

# Train the model
print("\nTraining model...")
print("Note: This may take a while depending on your dataset size...")

history = model.fit(
    X, y, 
    epochs=100, 
    batch_size=128, 
    verbose=1,
    callbacks=[checkpoint, early_stop]
)

# Save the final trained model
model.save('story_generator_model.h5')
print("\n✓ Model training completed!")
print("✓ Model saved as 'story_generator_model.h5'")
print(f"\nFinal accuracy: {history.history['accuracy'][-1]:.4f}")
