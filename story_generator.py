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

def generate_text(model, tokenizer, seed_text, maxLength, top_n=5):
    generatedText = seed_text
    seq = tokenizer.texts_to_sequences([generatedText])[0]
    paddedSeq = pad_sequences([seq], maxlen=maxLength-1, padding='pre')
    predictedSentence = generatedText + ""  # Start from an empty string
    for _ in range(maxLength):
        predictions = model.predict(paddedSeq)
        
        # Pick from the top-N probable words
        topNIndices = predictions[0].argsort()[-top_n:][::-1]
        predictedWordIndex = np.random.choice(topNIndices)
        
        predictedWord = tokenizer.index_word.get(predictedWordIndex, '')
        
        predictedSentence += " " + predictedWord
        tokenizedInput = tokenizer.texts_to_sequences([predictedSentence])
        paddedSeq = pad_sequences(tokenizedInput, maxlen=maxLength-1, padding='pre')
        
        # Early stopping
        stopEarlyProb = 0.05
        if np.random.rand() < stopEarlyProb or len(predictedSentence.split()) > maxLength:
            break
            
    return predictedSentence.strip()  # Strip to remove leading space




def main():
    model_path = 'best_story_generator_model.h5'
    tokenizer_path = 'best_tokenizer.pkl'
    
    model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
    
    max_length = 200 
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
