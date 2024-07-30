import discord
from discord.ext import commands
import logging

import openai
import json
import asyncio
import os
import shlex  # Import shlex for shell-like parsing

from config import STATIC_FRIEND_DATA, DISCORD_TO_REAL_NAME
from utils.context_management import update_history_with_extracted_info, truncate_history, summarize_conversation, split_message
from utils.friend_utils import replace_nicknames, handle_relationship_inquiry, handle_friend_inquiry, get_friend_data, check_sensitive_topics
from utils.feedback_utils import save_feedback
from utils.file_utils import load_json_files
from utils.summarization import truncate_text
from text_processing.relationship_detection import is_relationship_inquiry, is_friend_inquiry, is_feedback, is_general_inquiry
from tts.elevenlabs_tts import generate_custom_tts

# Setup logging for your application
logging.basicConfig(level=logging.INFO)  # Adjust this as needed for your application
logger = logging.getLogger(__name__)

# Adjust logging level for openai library to suppress debug messages
openai_logger = logging.getLogger('openai')
openai_logger.setLevel(logging.INFO)  # Set to INFO or higher to suppress DEBUG messages

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_histories = {}
        self.session_contexts = {}
        self.known_friend_names, self.nickname_to_full_name = self.extract_friend_names()
        self.active_polls = {}  # Dictionary to store active polls

    # Function to extract friend names from JSON files and static data
    def extract_friend_names(self):
        friend_names = set()
        nickname_to_full_name = {}

        for friend in STATIC_FRIEND_DATA:
            name = friend.get("name", "").lower()
            if name:
                friend_names.add(name)

        friend_data_json = load_json_files("data")
        for friend in friend_data_json.get("friends", []):
            name = friend.get("name").lower()
            nickname = friend.get("nickname", "").lower()
            if name:
                friend_names.add(name)
            if nickname:
                friend_names.add(nickname)
                nickname_to_full_name[nickname] = name

        for relationship_data in friend_data_json.get("relationships", []):
            for relationship in relationship_data.get("relationships", []):
                name = relationship.get("name", "").lower()
                nickname = relationship.get("nickname", "").lower()
                if name:
                    friend_names.add(name)
                if nickname:
                    friend_names.add(nickname)
                    nickname_to_full_name[nickname] = name

        return list(friend_names), nickname_to_full_name

    ### !talk command ###
    @commands.command(name='talk', help='Talk with the bot')
    async def talk(self, ctx, *, user_input: str):
        async with ctx.channel.typing():
            print(f"User input after trimming '!talk': {user_input}")

            discord_name = ctx.author.name
            channel_id = ctx.channel.id
            session_id = str(channel_id)  # Use channel ID as session ID

            print(f"Discord name: {discord_name}, Channel ID: {channel_id}, Session ID: {session_id}")

            user_name = DISCORD_TO_REAL_NAME.get(discord_name, discord_name)  # Use Discord username if real name is not found
            primary_person = user_name.lower()
            print(f"User name: {user_name}, Primary person: {primary_person}")

            user_input = replace_nicknames(user_input)
            print(f"User input after replacing nicknames: {user_input}")

            if session_id not in self.session_histories:
                self.session_histories[session_id] = []
                self.session_contexts[session_id] = {}
                print(f"Initialized session history and context for session ID: {session_id}")

            messages_to_send = []
            audio_path = None
            queried_friend_name = None

            def on_finished_playing(error):
                if error:
                    print(f"Error in playback: {error}")
                    # Retry logic or handle the error
                else:
                    print("Playback finished.")
                    # Optionally, add code to handle end of playback

            try:
                if is_feedback(user_input):
                    print("Detected feedback in user input")
                    save_feedback(user_input, discord_name)
                    await ctx.send("Thank you for the feedback. It has been noted.")
                    return

                if is_relationship_inquiry(user_input):
                    print("Detected relationship inquiry in user input")
                    relationship_info = handle_relationship_inquiry(user_input, user_name, primary_person, self.known_friend_names)

                    if relationship_info is None:
                        response_context = f"Sorry, I don't understand the request."
                        print("Relationship inquiry resulted in no information")
                    elif isinstance(relationship_info, dict):
                        response_context = relationship_info
                        self.session_contexts[session_id] = {
                            "last_inquiry": "relationship",
                            "primary_person": primary_person
                        }
                        print(f"Relationship JSON retrieved: {response_context}")
                    else:
                        response_context = relationship_info
                elif is_friend_inquiry(user_input, self.known_friend_names):
                    print("Detected friend inquiry in user input")
                    friend_data, queried_friend_name = handle_friend_inquiry(user_input, user_name, self.known_friend_names, self.nickname_to_full_name)

                    if friend_data is None:
                        response_context = f"Sorry, I don't understand the request."
                        print("Friend inquiry resulted in no information")
                    else:
                        response_context = friend_data
                        print(f"Friend data: {response_context}")
                elif is_general_inquiry(user_input):
                    print("Detected general inquiry in user input")
                    user_data = get_friend_data(user_name)
                    response_context = user_data
                else:
                    response_context = f"Sorry, I don't understand the request."
                    print("User input did not match any inquiry type")

                response_context = check_sensitive_topics(json.dumps(response_context, indent=2), user_input)

                self.session_histories[session_id] = update_history_with_extracted_info(self.session_histories[session_id], user_input, response_context)
                conversation_history = self.session_histories[session_id]
                conversation_history.append({"role": "system", "content": summarize_conversation(self.session_histories[session_id])})
                conversation_history = truncate_history(conversation_history)

                if queried_friend_name is None:
                    queried_friend_name = primary_person

                brendan_context = f"""
                Brendan is designed as a sassy, sarcastic chatbot, engaging users with a playful, sharp-witted manner that adapts to the personalities and interests of the user's friends.
                Brendan tailors each conversation to the friend's likes, personalities, and goals.
                This session is with {user_name}.
                Context: {truncate_text(json.dumps(response_context, indent=2))}
                """

                if queried_friend_name == "Fabio":
                    brendan_context = f"""
                    Brendan is not friendly, more reluctant, more sarcastic, sassy but still performs its usual functionality when talking to Fabio. Using its sharp-witted manner that adapts to the personalities and interests of the user's friends.
                    Brendan tailors each conversation to the friend's likes, personalities, and goals.
                    This session is with {user_name}.
                    Context: {truncate_text(json.dumps(response_context, indent=2))}
                    """

                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=conversation_history + [{"role": "system", "content": brendan_context}, {"role": "user", "content": user_input}]
                )

                self.session_histories[session_id].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
                messages_to_send = split_message(response['choices'][0]['message']['content'])

                audio_path = await generate_custom_tts(response['choices'][0]['message']['content'])
                print(f"Audio path: {audio_path}")

            except Exception as e:
                print(f"Error: {e}")
                await ctx.send("Sorry, I couldn't process your request at the moment.")
                return

        async def send_text_and_play_tts():
            voice_client = ctx.guild.voice_client
            music_was_playing = False
            current_source = None

            print("Sending text and playing TTS")
            if voice_client and voice_client.is_playing():
                voice_client.pause()
                current_source = voice_client.source
                music_was_playing = True
                await ctx.send("Pausing music to respond...")

            for msg in messages_to_send:
                await ctx.send(msg)
            if audio_path and ctx.guild.voice_client:
                voice_client = ctx.guild.voice_client
                tts_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=audio_path))
                tts_source.volume = 4.0
                voice_client.play(tts_source, after=on_finished_playing)
                while voice_client.is_playing():
                    await asyncio.sleep(1)
                os.remove(audio_path)
                print("Audio played and file removed")
            elif not ctx.guild.voice_client:
                await ctx.send("I need to be in a voice channel to speak!")
                print("Bot not in voice channel")

            if music_was_playing and current_source:
                await ctx.send("Resuming music...")
                music_source = discord.PCMVolumeTransformer(current_source)
                music_source.volume = 0.5
                voice_client.play(music_source, after=on_finished_playing)

        await asyncio.gather(send_text_and_play_tts())


    @commands.group(name='config', help='Configure settings for the bot')
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid config command. Use /config check, /config announce, or /config birthday-role.')
            logger.debug('Invalid config command used.')

    @config.command(name='check', help='Test the bot\'s current configuration and show the results')
    async def config_check(self, ctx):
        await ctx.send("Configuration is okay.")
        logger.debug('Configuration check performed')

    @config.command(name='announce', help='Settings for birthday announcements')
    async def config_announce(self, ctx):
        await ctx.send("Announcement settings configured.")
        logger.debug('Announcement settings configured')

    @config.command(name='birthday-role', help='Set the role given to users having a birthday')
    async def config_birthday_role(self, ctx, role: discord.Role):
        await ctx.send(f"Birthday role set to {role.name}.")
        logger.debug(f'Birthday role set to {role.name}')

    # Usage: !poll "Who is the best NBA player?" "Nikola Jokic" "Dequan Foster" "Joel Embiid"
    @commands.command(name='poll', help='Create a poll with multiple options. Use quotes for options with spaces.')
    async def create_poll(self, ctx, *, args):
        # Parse the arguments using shlex
        try:
            parsed_args = shlex.split(args)
        except ValueError as e:
            await ctx.send(f"Error parsing arguments: {e}. Make sure to close all quotes.")
            return

        # Ensure we have at least a question and two options
        if len(parsed_args) < 3:
            await ctx.send("You need to provide a question and at least two options for the poll.")
            return

        question = parsed_args[0]
        options = parsed_args[1:]

        # Define emoji options for poll choices
        emoji_options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        # Check if the number of options doesn't exceed the available emojis
        if len(options) > len(emoji_options):
            await ctx.send(f"The maximum number of options is {len(emoji_options)}.")
            return

        # Create the poll description with emojis and options
        description = "\n".join(f"{emoji_options[i]} {option}" for i, option in enumerate(options))

        # Create an embedded message for the poll
        embed = discord.Embed(
            title=question,
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text="React with the corresponding emoji to vote!")

        # Send the poll message and store it
        poll_message = await ctx.send(embed=embed)

        # Add reaction emojis to the message
        for i in range(len(options)):
            await poll_message.add_reaction(emoji_options[i])

        # Store the poll information
        self.active_polls[poll_message.id] = {
            'question': question,
            'options': options,
            'votes': {emoji: set() for emoji in emoji_options[:len(options)]}
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore bot reactions
        if user.bot:
            return

        message = reaction.message
        # Check if the reaction is for an active poll
        if message.id in self.active_polls:
            poll = self.active_polls[message.id]
            emoji = str(reaction.emoji)

            # If the emoji is valid for this poll
            if emoji in poll['votes']:
                # Remove user's previous votes
                for vote_set in poll['votes'].values():
                    vote_set.discard(user.id)

                # Add user's new vote
                poll['votes'][emoji].add(user.id)

                # Update the poll results
                await self.update_poll_results(message, poll)

    async def update_poll_results(self, message, poll):
        emoji_options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        description = ""

        # Generate the updated poll results
        for i, option in enumerate(poll['options']):
            emoji = emoji_options[i]
            vote_count = len(poll['votes'][emoji])
            # Calculate the length of the progress bar
            bar_length = min(int((vote_count / len(message.guild.members)) * 20), 20)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            description += f"{emoji} {option}\n{bar} {vote_count} votes\n\n"

        # Create an updated embed with the new results
        embed = discord.Embed(
            title=poll['question'],
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text="React with the corresponding emoji to vote!")

        # Edit the original message with the updated results
        await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
    print("⚙️  GeneralCog added")
