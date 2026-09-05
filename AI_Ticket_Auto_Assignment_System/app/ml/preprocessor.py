"""
NLP Text Preprocessor
Full pipeline: cleaning → tokenization → stopword removal → lemmatization → TF-IDF
"""
import re
import string
import nltk
import numpy as np
from typing import List


def _ensure_nltk_data():
    """Download required NLTK data silently."""
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        try:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
            nltk.download("stopwords", quiet=True)
            nltk.download("wordnet", quiet=True)
            nltk.download("averaged_perceptron_tagger", quiet=True)
        except Exception:
            pass

_ensure_nltk_data()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

# Domain-specific stop words to remove (too common in IT to be useful)
DOMAIN_STOP_WORDS = {
    "please", "help", "issue", "problem", "error", "getting", "using",
    "need", "want", "would", "could", "trying", "happened", "work",
    "working", "also", "one", "two", "three", "first", "second",
}
ALL_STOP_WORDS = STOP_WORDS | DOMAIN_STOP_WORDS


def clean_text(text: str) -> str:
    """
    Full text cleaning pipeline:
    1. Lowercase
    2. Remove URLs
    3. Remove email addresses
    4. Remove special characters / punctuation
    5. Remove extra whitespace
    """
    if not isinstance(text, str):
        return ""

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http[s]?://\S+", " ", text)
    text = re.sub(r"www\.\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove IP addresses
    text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", " ipaddress ", text)

    # Replace numbers with a token
    text = re.sub(r"\b\d+\b", " numtoken ", text)

    # Remove punctuation and special characters
    text = re.sub(r"[^\w\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize_and_lemmatize(text: str) -> List[str]:
    """
    Tokenize → filter stopwords → lemmatize
    """
    tokens = word_tokenize(text)
    tokens = [
        LEMMATIZER.lemmatize(token)
        for token in tokens
        if token not in ALL_STOP_WORDS and len(token) > 2
    ]
    return tokens


def preprocess(text: str) -> str:
    """Full preprocessing pipeline returning a clean string."""
    cleaned = clean_text(text)
    tokens = tokenize_and_lemmatize(cleaned)
    return " ".join(tokens)


def preprocess_batch(texts: List[str], verbose: bool = False) -> List[str]:
    """Preprocess a list of texts."""
    results = []
    total = len(texts)
    for i, text in enumerate(texts):
        results.append(preprocess(text))
        if verbose and (i + 1) % 1000 == 0:
            print(f"  Preprocessed {i + 1}/{total} texts...")
    return results


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """Extract the most meaningful keywords from a text."""
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    # Filter and get meaningful tokens
    keywords = [
        t for t in tokens
        if t not in ALL_STOP_WORDS and len(t) > 3
        and t not in {"numtoken", "ipaddress"}
    ]
    # Deduplicate while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    return unique_keywords[:top_n]
