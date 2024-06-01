import nltk
from config import NLTK_DATA

def setup_nltk():
    for data in NLTK_DATA:
        nltk.download(data)
