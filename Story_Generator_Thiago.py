import numpy as np
import tensorflow as tf
from keras_preprocessing.sequence import pad_sequences
from keras.models import load_model
import pickle

MAX_SEQ_LENGTH = 50  # Adjust this based on your training data and preference

def load_chatbot_elements(model_path, tokenizer_path):
    model = load_model(model_path)
    with open(tokenizer_path, 'rb') as handle:
        tokenizer = pickle.load(handle)
    return model, tokenizer

def generate_response(model, tokenizer, user_input, max_seq_length=MAX_SEQ_LENGTH, top_n=5):
    tokenized_input = tokenizer.texts_to_sequences([user_input])
    padded_input = pad_sequences(tokenized_input, maxlen=max_seq_length-1, padding='pre')
    
    predicted_sentence = ""  # Start from an empty string
    for _ in range(max_seq_length):
        predictions = model.predict(padded_input)
        
        # Pick from the top-N probable words
        top_n_indices = predictions[0].argsort()[-top_n:][::-1]
        predicted_word_index = np.random.choice(top_n_indices)
        
        predicted_word = tokenizer.index_word.get(predicted_word_index, '')
        
        predicted_sentence += " " + predicted_word
        tokenized_input = tokenizer.texts_to_sequences([predicted_sentence])
        padded_input = pad_sequences(tokenized_input, maxlen=max_seq_length-1, padding='pre')
        
        # Early stopping
        stop_early_prob = 0.05
        if np.random.rand() < stop_early_prob or len(predicted_sentence.split()) > max_seq_length:
            break
            
    return predicted_sentence.strip()  # Strip to remove leading space

# Driver code
if __name__ == '__main__':
    MODEL_PATH = 'story_generator_model.h5'
    TOKENIZER_PATH = 'tokenizer.pkl'

    model, tokenizer = load_chatbot_elements(MODEL_PATH, TOKENIZER_PATH)

    print("Gutenberg Chatbot: Type 'exit' to leave the chat.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = generate_response(model, tokenizer, user_input)
        print("Bot:", response)
