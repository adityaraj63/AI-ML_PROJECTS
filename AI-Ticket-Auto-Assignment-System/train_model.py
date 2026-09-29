import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

print("1. Loading dataset...")
df = pd.read_csv('dataset/tickets.csv')

print("2. Understanding dataset...")
print(df.head())
print("Missing values:")
print(df.isnull().sum())

print("3. Data cleaning...")
df = df.dropna()

print("4. Category distribution:")
print(df['category'].value_counts())

print("5. Train-test split...")
X = df['ticket_description']
y = df['category']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("6. TF-IDF feature extraction...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("7. Train Logistic Regression...")
model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train_tfidf, y_train)

print("8. Make predictions...")
y_pred = model.predict(X_test_tfidf)

print("9. Evaluate Model...")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("10. Testing custom examples...")
test_tickets = [
    "My internet is not working even though my Wi-Fi is connected.",
    "I was charged twice for my subscription.",
    "I forgot my password.",
    "The app is crashing when I open it.",
    "What are your business hours?"
]
test_tfidf = vectorizer.transform(test_tickets)
predictions = model.predict(test_tfidf)
probs = model.predict_proba(test_tfidf)

for ticket, pred, prob in zip(test_tickets, predictions, probs):
    confidence = max(prob) * 100
    print(f"Ticket: {ticket}\nPrediction: {pred} (Confidence: {confidence:.2f}%)\n")

print("11. Saving model and vectorizer...")
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/ticket_classifier.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
print("Model saved to models/ticket_classifier.pkl")
print("Vectorizer saved to models/tfidf_vectorizer.pkl")
