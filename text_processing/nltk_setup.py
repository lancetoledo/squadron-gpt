import nltk
from config import NLTK_DATA

# NLTK (Natural Language Toolkit) is a comprehensive library for natural language processing (NLP) in Python.
# It provides easy-to-use interfaces to over 50 corpora and lexical resources, along with text processing libraries.

def setup_nltk():
    for data in NLTK_DATA:
        nltk.download(data)
