import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt

# Prisijungti prie SQLite databazes
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()

# Pasirinkt text ir label
cursor.execute("SELECT text, label FROM documents")
documents = cursor.fetchall()

conn.close()

# Indeksuoti teksta ir labelius
texts = [doc[0] for doc in documents]
labels = [doc[1] for doc in documents]


# Padaliname database i test ir train
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.33, random_state=42)


# Sukuriame TfidfVectorizer
vectorizer = TfidfVectorizer()

# Treniruojame TfidfVectorizer
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Sukuriame parametrus kryžminiam patikrinimui
param_grid = {
    'alpha': [0.1, 0.2, 0.3, 0.5, 0.6, 0.7, 0.8, 1.0],
}

# Apibrėžiame modelį
model = MultinomialNB()

# Vykdome kryžmynį patikrinimą
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train_vectorized, y_train)

# Apibrėžiąme geriausius hyperparametrus
best_params = grid_search.best_params_
print("Best Hyperparameters:", best_params)

# Treniruojame modelį
model.fit(X_train_vectorized, y_train)

# Vykdome spėjimus
predicted_categories = model.predict(X_test_vectorized)

# Atspausdiname spėjimus (teksto indeksas, tikra kategorija ir spėjama kategorija)
for idx, (text, actual_category, predicted_category) in enumerate(zip(X_test_vectorized, y_test, predicted_categories)):
    print(f"Index: {idx}, Tikra kategorija: {actual_category} Spėjama kategorija: {predicted_category}")


# Tikriname ikslumą
accuracy = accuracy_score(y_test, predicted_categories)
print(f'Accuracy: {accuracy*100:.2f}%')

plt.figure(figsize=(6,4))
plt.bar(['Accuracy'], [accuracy*100], color='red')
plt.ylabel('Procentai')
plt.title('Modelio tikslumas')
plt.ylim(0, 100)
plt.show()