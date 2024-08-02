from text_processing.nltk_setup import setup_nltk
from text_processing.spacy_setup import load_spacy_models
from config import DISCORD_BOT_TOKEN
from discord_client import client

# Download necessary NLTK data
setup_nltk()

# Load spaCy models
nlp, relationship_model = load_spacy_models()

# Function to load cogs
async def load_cogs(bot):
    extensions = [
        'commands.music_cog',
        'commands.birthday_cog',
        'commands.general_cog',
        'commands.tarot_cog',
        'commands.nba2k_cog'
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f'Loaded extension: {ext}')
        except Exception as e:
            print(f'Failed to load extension {ext}.')
            print(e)

# Run the Discord bot
if __name__ == "__main__":
    print("Starting bot")
    import asyncio
    asyncio.run(load_cogs(client))
    client.run(DISCORD_BOT_TOKEN)
