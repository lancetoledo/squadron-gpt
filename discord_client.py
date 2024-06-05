import discord
from discord.ext import commands
from events.message_events import on_message
from commands.command_handlers import join, leave, play, pause, resume, stop, queue, clear, skip, birthday, config, export_birthdays, override, daily_birthday_check
import logging
logging.basicConfig(level=logging.DEBUG)

# Class definition for the Discord client, inheriting from commands.Bot
class DiscordClient(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        # Add custom commands to the bot
        self.add_command(join)
        self.add_command(leave)
        self.add_command(play)
        self.add_command(pause)
        self.add_command(resume)
        self.add_command(stop)
        self.add_command(queue)
        self.add_command(clear)
        self.add_command(skip)
        self.add_command(birthday)
        self.add_command(config)
        self.add_command(export_birthdays)
        self.add_command(override)

    # Event handler for when the bot is ready and connected
    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')  # Print bot's username and ID
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Lance's memories 🔬"))
        # Start the daily birthday check task
        self.loop.create_task(daily_birthday_check(self))

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
