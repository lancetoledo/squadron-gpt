import spacy
from config import SPACY_MODEL, RELATIONSHIP_MODEL

# Function to load spaCy models
def load_spacy_models():
    nlp = spacy.load(SPACY_MODEL)
    relationship_model = spacy.load(RELATIONSHIP_MODEL)
    return nlp, relationship_model

# Initialize and load models at the module level
nlp, relationship_model = load_spacy_models()
