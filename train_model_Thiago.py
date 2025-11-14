# train_model.py

import numpy as np
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense
import pickle

# Load input_sequences
with open('input_sequences.pkl', 'rb') as file:
    input_sequences = pickle.load(file)

# Load tokenizer
with open('tokenizer.pkl', 'rb') as file:
    tokenizer = pickle.load(file)

vocab_size = len(tokenizer.word_index) + 1
sequences = np.array(input_sequences)

X, y = sequences[:, 0], sequences[:, 1]

# Create the model
model = Sequential()
model.add(Embedding(vocab_size, 10, input_length=1))
model.add(LSTM(1000, return_sequences=True))
model.add(LSTM(1000))
model.add(Dense(1000, activation='relu'))
model.add(Dense(vocab_size, activation='softmax'))

# Compile the model with sparse categorical crossentropy
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
model.fit(X, y, epochs=100, batch_size=64, verbose=1)

# Save the trained model
model.save('story_generator_model.h5')

print("Model training completed!")
