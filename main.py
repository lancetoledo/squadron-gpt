from text_processing.nltk_setup import setup_nltk
from text_processing.spacy_setup import load_spacy_models
from config import DISCORD_BOT_TOKEN
from discord_client import client

# Download necessary NLTK data
setup_nltk()

# Load spaCy models
nlp, relationship_model = load_spacy_models()

# Run the Discord bot
if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
