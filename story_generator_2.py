import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras_preprocessing.sequence import pad_sequences

def load_model_and_tokenizer(model_path, tokenizer_path):
    model = keras.models.load_model(model_path)
    with open(tokenizer_path, 'rb') as tokenizer_file:
        unpickler = pickle.Unpickler(tokenizer_file)
        tokenizer = unpickler.load()
    return model, tokenizer

def find_max_index(row):
    max_index = 0
    max_value = row[0]

    for i, value in enumerate(row):

        if value > max_value:
            max_index = i
            max_value = value

    return max_index

def generate_text(model, tokenizer, seed_text, max_length):
    generated_text = seed_text

    for _ in range(max_length):  # loop for as many words as max_length
        # Tokenize and pad the seed text
        seq = tokenizer.texts_to_sequences([generated_text])[0]
        padded_seq = pad_sequences([seq], maxlen=max_length-1, padding='pre')

        # Predict the next word
        preds = model.predict(padded_seq, verbose=0)[0]
        
        # Find the index of the maximum value in each row
        next_word_indices = [find_max_index(row) for row in preds]

        # Convert index to actual word using tokenizer's index_word mapping
        next_words = [tokenizer.index_word.get(idx, '') for idx in next_word_indices]
        
        # Append the next words to the generated text
        generated_text += " " + " ".join(next_words)

        # Stop if the generated text ends with a period
        if any(next_word == "." for next_word in next_words):
            break

    return generated_text




def main():
    model_path = 'story_generator_model.h5'
    tokenizer_path = 'tokenizer.pkl'
   
    model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
   
    max_length = 50
    seed_text = "Valancy wakened early, in the lifeless, hopeless hour just preceding dawn."
   
    user_input = input("Type 'start' to generate the story: ")
    if user_input.lower() == 'start':
        while True:
            generated_story = generate_text(model, tokenizer, seed_text, max_length)
            print(generated_story)
           
            user_input = input("Press Enter to continue or type your character's response: ")
            if user_input:
                seed_text = user_input  # Set the user's response as the new seed text
            else:
                break

if __name__ == "__main__":
    main()
