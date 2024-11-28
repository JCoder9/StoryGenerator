import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from keras.models import Sequential


import pandas as pd
import pickle

def loadData(maxSeqLength):
    df = pd.read_csv("gutenberg_texts.csv", nrows=1000)
    text = ' '.join(df['Text'].tolist())

    tokenizer = Tokenizer(lower=True)
    tokenizer.fit_on_texts([text])
    vocabSize = len(tokenizer.word_index) + 1

    sequences = tokenizer.texts_to_sequences([text])[0]
    # sequences = pad_sequences(sequences, maxlen=maxSeqLength, padding='post')

    input_sequences = []
    for i in range(1, len(sequences)):
        seq = sequences[i-1:i+1] ##creates pairs of indices that are beside eachother in sequences
        input_sequences.append(seq)
    

    sequences = np.array(input_sequences)

    trainInput, trainTarget = sequences[:, 0], sequences[:, 1]

    return trainInput, trainTarget, vocabSize, tokenizer

def buildModel(vocabSize, maxSeqLength):
    model = Sequential()
    model.add(Embedding(vocabSize, 10, input_length=1))
    model.add(LSTM(1000, return_sequences=True))
    model.add(LSTM(1000))
    model.add(Dense(1000, activation='relu'))
    model.add(Dense(vocabSize, activation='softmax'))

    # Compile the model with sparse categorical crossentropy
    model.compile(
        loss='sparse_categorical_crossentropy', 
        optimizer='adam', 
        metrics=['accuracy']
        )
    return model

def train_model():
    maxSeqLength = 100
    trainInput, trainTarget, vocabSize, tokenizer = loadData(maxSeqLength)

    model = buildModel(vocabSize, maxSeqLength)

    batchSize = 128
    epochs = 100

    model.fit(trainInput, trainTarget, epochs=epochs, batch_size=batchSize)

    model.save("story_generator_model.h5")

    with open('tokenizer.pkl', 'wb') as tokenizer_file:
        pickle.dump(tokenizer, tokenizer_file)

if __name__ == "__main__":
    train_model()
