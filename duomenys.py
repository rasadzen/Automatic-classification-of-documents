import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
from nltk.tokenize import word_tokenize
import docx
import os
import nltk
from nltk.tokenize import word_tokenize

directory = r"C:\Users\GS\PycharmProjects\Automatic-classification-of-documents\Dokumentai"

# Function to read .docx files from directory and tokenize
def tokenize_docx_files(directory):
    tokenized_texts = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".docx"):  # Assuming all files are .docx files
                file_path = os.path.join(root, file)
                doc = docx.Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                tokens = word_tokenize(text)  # Tokenizing text
                tokenized_texts.append(tokens)
    return tokenized_texts

# Call the function
tokenized_texts = tokenize_docx_files(directory)

# Example usage
for i, tokens in enumerate(tokenized_texts):
    print(f"Tokens from file {i+1}: {tokens[:10]}")  # Displaying first 10 tokens of each file
