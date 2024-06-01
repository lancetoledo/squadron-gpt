# DIFFERENT VOICE IDS FOR TTS:
# Custom Brendan Voice:
# ELEVENLABS_VOICE_ID = 'OQ9vgPN68ly6P7YjwRpa'
# Funny British Timmy Voice:
# ELEVENLABS_VOICE_ID = 'chcMmmtY1cmQh2ye1oXi' 
# Regular British Voice
# ELEVENLABS_VOICE_ID = 'z0DcTcYlLxVjFO7tr9yB' 


from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Configuration settings and API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# ElevenLabs voice ID and API URL
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
ELEVENLABS_API_URL = f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}'

# Discord bot token
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# spaCy model
SPACY_MODEL = os.getenv('SPACY_MODEL')
RELATIONSHIP_MODEL = os.getenv('RELATIONSHIP_MODEL')

# JSON filenames for relationships and friends data
RELATIONSHIPS_DATA1 = os.getenv('RELATIONSHIPS_DATA1')
RELATIONSHIPS_DATA2 = os.getenv('RELATIONSHIPS_DATA2')
FRIEND_DATA1 = os.getenv('FRIEND_DATA1')
FRIEND_DATA2 = os.getenv('FRIEND_DATA2')

# Static friend data and discord to real name mapping
STATIC_FRIEND_DATA = json.loads(os.getenv('STATIC_FRIEND_DATA'))
DISCORD_TO_REAL_NAME = json.loads(os.getenv('DISCORD_TO_REAL_NAME'))

# Other configurations
NLTK_DATA = os.getenv('NLTK_DATA').split(',')


