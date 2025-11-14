import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences

def load_model_and_tokenizer(model_path, tokenizer_path):
    model = keras.models.load_model(model_path)
    with open(tokenizer_path, 'rb') as tokenizer_file:
        unpickler = pickle.Unpickler(tokenizer_file)
        tokenizer = unpickler.load()
    return model, tokenizer

def generate_text(model, tokenizer, seed_text, max_length):
    generated_text = seed_text
    seq = tokenizer.texts_to_sequences([generated_text])[0]
    padded_seq = pad_sequences([seq], maxlen=max_length-1, padding='pre')
    preds = model.predict(padded_seq)[0]
    
    # Find the index of the highest probability value for each row
    next_word_indices = [] 
    for row in preds:
        next_word_indices.append(np.argmax(row))


    for next_word_index in next_word_indices:

        # Convert index to actual word using tokenizer's index_word mapping
        next_word = tokenizer.index_word[next_word_index+1]
        
        # Append the next word to the generated text
        generated_text += " " + next_word
    
        generated_words = generated_text.split()

        # Stop if the generated text is too long or ends with a period
        if len(generated_words) > max_length or next_word == ".":
            break
    
    return generated_text




def main():
    model_path = 'story_generator_model.h5'
    tokenizer_path = 'tokenizer.pkl'
    
    model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
    
    max_length = 100 
    seed_text = "There was a big man"
    
    user_input = input("Type 'start' to generate the story: ")
    if user_input.lower() == 'start':
        while True:
            generated_story = generate_text(model, tokenizer, seed_text, max_length)
            print(generated_story)
            
            user_input = input("Press Enter to continue or type your character's response: ")
            if user_input:
                seed_text = user_input
            else:
                break


if __name__ == "__main__":
    main()
