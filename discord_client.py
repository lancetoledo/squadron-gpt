import discord
from discord.ext import commands
from events.message_events import on_message

class DiscordClient(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Lance's memories 🔬"))

    async def on_message(self, message):
        if message.author == self.user:
            return
        await on_message(self, message)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

client = DiscordClient(command_prefix='!', intents=intents)
