import spacy
from config import SPACY_MODEL, RELATIONSHIP_MODEL

def load_spacy_models():
    nlp = spacy.load(SPACY_MODEL)
    relationship_model = spacy.load(RELATIONSHIP_MODEL)
    return nlp, relationship_model
