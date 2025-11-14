# data_preprocessing.py

import pandas as pd
from keras_preprocessing.text import Tokenizer
import pickle

# Load the data
num_rows_to_load = 1000 #change this to go through all rows. It will take a lot of time process tho
df = pd.read_csv("gutenberg_texts.csv", nrows=num_rows_to_load)
text = ' '.join(df['Text'].tolist())

# Tokenize
tokenizer = Tokenizer()
tokenizer.fit_on_texts([text])
sequences = tokenizer.texts_to_sequences([text])[0]

input_sequences = []
for i in range(1, len(sequences)):
    seq = sequences[i-1:i+1] ##creates pairs of indices that are beside eachother in sequences
    input_sequences.append(seq)

# Save tokenizer
with open('tokenizer.pkl', 'wb') as tokenizer_file:
    pickle.dump(tokenizer, tokenizer_file)

# Save input_sequences for training
with open('input_sequences.pkl', 'wb') as file:
    pickle.dump(input_sequences, file)

print("Data preprocessing completed!")