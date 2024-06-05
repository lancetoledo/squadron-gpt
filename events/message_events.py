from discord.ext import commands
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Event triggered when a message is received
async def on_message(bot, message):
    if message.author == bot.user:
        return

    # Process commands, including the '!talk' command
    await bot.process_commands(message)