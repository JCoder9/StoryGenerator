import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from kerastuner.tuners import RandomSearch
import matplotlib.pyplot as plt


import pandas as pd
import pickle


def loadData():
    df = pd.read_csv("gutenberg_texts_2.csv", nrows=5000)
    text = ' '.join(df['Text'].tolist())

    tokenizer = Tokenizer(lower=True)
    tokenizer.fit_on_texts([text])
    vocabSize = len(tokenizer.word_index) + 1

    sequences = tokenizer.texts_to_sequences([text])[0]

    input_sequences = []
    for i in range(1, len(sequences)):
        # creates pairs of indices that are beside eachother in sequences
        seq = sequences[i-1:i+1]
        input_sequences.append(seq)

    sequences = np.array(input_sequences)

    trainInput, trainTarget = sequences[:, 0], sequences[:, 1]

    with open('best_tokenizer.pkl', 'wb') as tokenizer_file:
        pickle.dump(tokenizer, tokenizer_file)

    return trainInput, trainTarget, vocabSize, tokenizer


def buildModel(hp, vocabSize):
    model = Sequential()

    # Hyperparameters for tuning
    embedding_dim = hp.Int('embedding_dim', min_value=50,
                           max_value=300, step=50)
    lstm_units = hp.Int('lstm_units', min_value=64, max_value=256, step=64)
    dropout_rate = hp.Float(
        'dropout_rate', min_value=0.1, max_value=0.5, step=0.1)
    learning_rate = hp.Float(
        'learning_rate', min_value=1e-4, max_value=1e-2, sampling='LOG')

    model.add(Embedding(vocabSize, embedding_dim, input_length=1))
    model.add(LSTM(lstm_units, return_sequences=True))
    model.add(LSTM(lstm_units))
    model.add(Dense(lstm_units, activation='relu'))
    model.add(Dropout(dropout_rate))  # Adding Dropout layer
    model.add(Dense(vocabSize, activation='softmax'))

    # Compile the model with sparse categorical crossentropy
    model.compile(
        loss='sparse_categorical_crossentropy',
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        metrics=['accuracy']
    )
    return model


def plot_training_progress(history):
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(history['loss'], label='Training Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Loss over Epochs')

    plt.subplot(1, 2, 2)
    plt.plot(history['accuracy'], label='Training Accuracy')
    plt.plot(history['val_accuracy'], label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.title('Accuracy over Epochs')

    plt.tight_layout()
    plt.show()


def train_model():
    trainInput, trainTarget, vocabSize, tokenizer = loadData()

    tuner = RandomSearch(
        lambda hp: buildModel(hp, vocabSize),
        # You can change the objective to 'val_accuracy' if using validation data
        objective='accuracy',
        max_trials=3,  # Number of trials for hyperparameter search
        executions_per_trial=1,  # Number of executions per trial
        directory='tuning_dir_3'  # Directory to save tuner results
    )

    # Search for the best hyperparameters
    tuner.search(trainInput, trainTarget, epochs=50, batch_size=128)

    best_model = tuner.get_best_models(num_models=1)[0]

    best_model.save("best_story_generator_model.h5")

    # Visualize training
    best_trial_history = tuner.oracle.get_best_trials()[0].history
    plot_training_progress(best_trial_history)

    with open('best_tokenizer.pkl', 'wb') as tokenizer_file:
        pickle.dump(tokenizer, tokenizer_file)


if __name__ == "__main__":
    train_model()
