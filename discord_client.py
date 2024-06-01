import discord
from discord.ext import commands
from events.message_events import on_message
from commands.command_handlers import join, leave

# Class definition for the Discord client, inheriting from commands.Bot
class DiscordClient(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        # Add custom commands to the bot
        self.add_command(join)
        self.add_command(leave)

    # Event handler for when the bot is ready and connected
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')  # Print bot's username and ID

    # Event handler for when a message is received
    async def on_message(self, message):
        # Ignore messages sent by the bot itself
        if message.author == self.user:
            return

        # Pass the message to the custom on_message function from message_events
        await on_message(self, message)

# Define the intents required by the bot
intents = discord.Intents.default()
intents.messages = True  # Enable message events
intents.message_content = True  # Enable access to message content
intents.guilds = True  # Enable guild events
intents.voice_states = True  # Enable voice state events

# Create an instance of the DiscordClient with the specified command prefix and intents
client = DiscordClient(command_prefix='!', intents=intents)
