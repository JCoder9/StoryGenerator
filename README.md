# Story Generator - Procedural Storytelling for Gaming

## Project Overview

This project develops procedural storytelling models that generate dynamic and personalized narratives for gaming applications. Unlike traditional linear stories, this system adapts to player preferences and decisions, enhancing player independence and immersion.

## Project Goals

- Generate dynamic narratives that adapt to player actions
- Create personalized story experiences based on user input
- Provide immersive storytelling using LSTM neural networks
- Enable interactive story generation for gaming applications

## Architecture

The project uses a sequence-to-sequence LSTM (Long Short-Term Memory) neural network trained on fiction texts from Project Gutenberg to learn narrative patterns and generate coherent story continuations.

### Components

1. **Data Collection** (`gutenberg_spider_fixed.py`)
   - Scrapes fiction texts from Project Gutenberg
   - Extracts and cleans chapter text
   - Generates `gutenberg_texts.csv`

2. **Data Preprocessing** (`data_preprocessing.py`)
   - Tokenizes text data
   - Creates word sequences for training
   - Generates `tokenizer.pkl` and `input_sequences.pkl`

3. **Model Training** (`train_model.py`)
   - Trains LSTM model on preprocessed sequences
   - Implements next-word prediction
   - Saves trained model as `story_generator_model.h5`

4. **Story Generation** (`interactive_story_generator.py`)
   - Interactive story generation interface
   - Adapts to user input
   - Generates dynamic narrative continuations

## Setup Instructions

### Prerequisites

- Python 3.9+
- Virtual environment (already configured in this project)

### Required Packages

All required packages are already installed in the virtual environment:
- tensorflow 2.13.0
- keras 2.13.1
- scrapy 2.9.0
- pandas 2.0.3
- nltk 3.8.1
- numpy 1.24.3

## Usage

### Step 1: Generate Training Data

Run the Gutenberg spider to collect fiction texts:

```bash
/Users/jordanhiggins/Desktop/Story_Generator/bin/python gutenberg_spider_fixed.py
```

This will:
- Scrape 20 fiction books from Project Gutenberg
- Extract chapters from each book
- Clean and tokenize the text
- Save to `gutenberg_texts.csv`

**Note**: This process may take 10-30 minutes depending on network speed.

### Step 2: Preprocess Data

Process the collected text data:

```bash
/Users/jordanhiggins/Desktop/Story_Generator/bin/python data_preprocessing.py
```

This will:
- Load text from `gutenberg_texts.csv`
- Tokenize the text
- Create word sequence pairs for training
- Save `tokenizer.pkl` and `input_sequences.pkl`

### Step 3: Train the Model

Train the LSTM story generation model:

```bash
/Users/jordanhiggins/Desktop/Story_Generator/bin/python train_model.py
```

This will:
- Load preprocessed sequences
- Build and train an LSTM neural network
- Save the best model as `story_generator_model.h5`

**Note**: Training may take 30-60 minutes depending on dataset size and hardware.

### Step 4: Generate Stories

Run the interactive story generator:

```bash
/Users/jordanhiggins/Desktop/Story_Generator/bin/python interactive_story_generator.py
```

Commands:
- Type a story beginning or character action
- Press ENTER to generate AI continuation
- Type 'new' to start a fresh story
- Type 'quit' to exit

## Model Architecture

```
Input Layer: Word embeddings (100 dimensions)
    ↓
LSTM Layer: 150 units
    ↓
Dropout Layer: 0.2 (prevents overfitting)
    ↓
Dense Layer: 100 units (ReLU activation)
    ↓
Output Layer: Softmax (vocabulary size)
```

## File Structure

```
Story_Generator/
├── gutenberg_spider_fixed.py      # Data collection (FIXED)
├── data_preprocessing.py          # Data preprocessing (FIXED)
├── train_model.py                 # Model training (FIXED)
├── interactive_story_generator.py # Story generation (NEW)
├── gutenberg_texts.csv            # Training data (generated)
├── tokenizer.pkl                  # Word tokenizer (generated)
├── input_sequences.pkl            # Training sequences (generated)
└── story_generator_model.h5       # Trained model (generated)
```

## Issues Fixed

### Original Code Problems

1. **Deprecated Imports**: Updated from `keras_preprocessing` to `tensorflow.keras.preprocessing`
2. **Model Architecture Mismatch**: Fixed input shape to match training data structure
3. **Generation Logic**: Improved word prediction and sampling
4. **Error Handling**: Added proper exception handling and user feedback
5. **Spider Configuration**: Updated Scrapy settings for reliability

### Improvements Made

1. **Temperature Sampling**: Added temperature parameter for controlling randomness
2. **Interactive Interface**: Better user experience with clear instructions
3. **Robust Tokenization**: Handles edge cases in text generation
4. **Model Checkpointing**: Saves best model during training
5. **Progress Feedback**: Clear logging throughout the pipeline

## Customization

### Adjust Dataset Size

In `data_preprocessing.py`, change:
```python
num_rows_to_load = 1000  # Increase for more training data
```

### Adjust Model Complexity

In `train_model.py`, modify:
```python
LSTM(150, ...)  # Increase units for more capacity
Dense(100, ...)  # Adjust hidden layer size
```

### Adjust Generation Length

In `interactive_story_generator.py`, modify:
```python
num_words=50  # Change number of words to generate
temperature=0.8  # Adjust randomness (0.5-1.5)
```

## Future Enhancements

- [ ] Add player choice branching
- [ ] Implement character tracking and memory
- [ ] Add genre-specific generation
- [ ] Implement sentiment analysis for adaptive tone
- [ ] Create web interface for easier interaction
- [ ] Add save/load story functionality
- [ ] Implement multiple character perspectives

## Troubleshooting

### "gutenberg_texts.csv not found"
Run Step 1 to generate training data.

### "tokenizer.pkl not found"
Run Step 2 to preprocess data.

### "story_generator_model.h5 not found"
Run Step 3 to train the model.

### Poor quality generations
- Increase training data (more books in spider)
- Increase training epochs
- Adjust model architecture (more LSTM units)

### Spider not working
- Check internet connection
- Project Gutenberg may have changed their HTML structure
- Try reducing number of books to scrape

## License

Educational project for procedural storytelling research.

## Authors

Jordan Higgins
