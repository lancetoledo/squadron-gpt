import spacy
from text_processing.spacy_setup import nlp  # Ensure nlp is loaded correctly

# Load spaCy model for relationship detection
relationship_model = spacy.load("models/best_relationship_inquiry_model")

def is_relationship_inquiry(user_input):
    doc = relationship_model(user_input)
    score = doc.cats["relationship_inquiry"]
    return score > 0.5

# Function to detect if the inquiry is about a friend
def is_friend_inquiry(user_input, known_friend_names):
    doc = nlp(user_input)
    entities = [ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON" and ent.text.lower() in known_friend_names]
    print(f"Named entities detected: {entities}")
    if entities:
        print(f"Entities recognized as friends: {entities}")
        return True
    else:
        print(f"No entities recognized as friends.")
        # Fallback to check known friend names
        for word in user_input.lower().split():
            clean_word = word.strip(".,!?").lower()
            if clean_word.endswith("'s"):
                clean_word = clean_word[:-2]  # Remove 's from the word
            if clean_word in known_friend_names:
                print(f"Found '{clean_word}' in known friend names.")
                return True
    print(f"Checking if any entities match known friend names: {known_friend_names}")
    return False  # Ensure function returns False if no matches found

def is_feedback(user_input):
    doc = relationship_model(user_input)
    score = doc.cats["feedback"]
    return score > 0.5
