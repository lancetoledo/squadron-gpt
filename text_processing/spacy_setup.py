import spacy
from config import SPACY_MODEL, RELATIONSHIP_MODEL

# spaCy is an open-source library for advanced Natural Language Processing (NLP) in Python.
# It is used to build applications that process and understand large volumes of text, including
# functionalities like tokenization, part-of-speech tagging, named entity recognition, and more.

# Function to load spaCy models
def load_spacy_models():
    nlp = spacy.load(SPACY_MODEL)  # Load the main spaCy model for general NLP tasks
    relationship_model = spacy.load(RELATIONSHIP_MODEL)  # Load a custom model for relationship inquiry detection
    return nlp, relationship_model

# Initialize and load models at the module level
nlp, relationship_model = load_spacy_models()
