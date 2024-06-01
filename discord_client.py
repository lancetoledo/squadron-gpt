import discord
from discord.ext import commands
from utils.feedback_utils import detect_and_handle_feedback
from events.message_events import on_message
from commands.command_handlers import join, leave

class DiscordClient(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.add_command(join)
        self.add_command(leave)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Detect and handle feedback
        if detect_and_handle_feedback(message):
            await message.channel.send("Thank you for your feedback! It has been noted for future review")
            return

        await on_message(self, message)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

client = DiscordClient(command_prefix='!', intents=intents)
