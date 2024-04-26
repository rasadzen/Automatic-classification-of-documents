import re
import string
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import sqlite3


 # Nuskaityti duomenys iš .docx failų
def read_docx(docx_file):
    doc = Document(docx_file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


# Sutvarkyti nuskaitytą tekstą
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text


 # Nuskaityti visus failus iš direkturijų ir pritaikyti funkciją teksto nuskaitymui
def read_all_docx_files(directories):
    all_data = []
    for directory in directories:
        category = os.path.basename(directory)
        for filename in os.listdir(directory):
            if filename.endswith(".docx"):
                docx_file = os.path.join(directory, filename)
                text = read_docx(docx_file)
                preprocessed_text = preprocess_text(text)
                all_data.append((preprocessed_text, category))
    return all_data


 # Nurodome direktorijas, iš kurių nuskaitome failus
directories = ['Dokumentai/isakymai', 'Dokumentai/potvarkiai', 'Dokumentai/sprendimai']

 # Pritaikome funkciją failų nuskaitymui iš nurodytų direktorijų
all_data = read_all_docx_files(directories)

 # Sukūriame prisijungimą prie duomenų bazės
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()
 # Sukuriame lentelę, nuskaitytiems duomenims
cursor.execute('''CREATE TABLE IF NOT EXISTS documents
                (text TEXT,
                label TEXT)''')

 # Įkeliame duomenis į lenteelę
for text, label in all_data:
    cursor.execute("INSERT INTO documents (text, label) VALUES (?, ?)", (text, label))

 # Baigiame ryšį
conn.commit()
conn.close()