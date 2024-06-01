import spacy

# Load spaCy model for relationship detection
relationship_model = spacy.load("models/best_relationship_inquiry_model")

def is_relationship_inquiry(user_input):
    doc = relationship_model(user_input)
    score = doc.cats["relationship_inquiry"]
    return score > 0.5

def is_friend_inquiry(user_input, known_friend_names, nlp):
    doc = nlp(user_input)
    entities = [ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON" and ent.text.lower() in known_friend_names]
    if entities:
        return True
    else:
        for word in user_input.lower().split():
            clean_word = word.strip(".,!?").lower()
            if clean_word.endswith("'s"):
                clean_word = clean_word[:-2]  # Remove 's from the word
            if clean_word in known_friend_names:
                return True
    return False

def is_feedback(user_input):
    doc = relationship_model(user_input)
    score = doc.cats["feedback"]
    return score > 0.5
