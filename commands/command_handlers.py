import discord
from discord.ext import commands
from utils.music_utils import get_audio_url
from utils.file_utils import load_json_files
import asyncio
import sqlite3
import os
from dateutil.parser import parse
from datetime import datetime
import logging
import random
import json


# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FFmpeg options
ffmpeg_opts = {
    'options': '-vn',
}

# Specify the path to the ffmpeg executable
ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"  # Update this path if necessary

# Global variables for song queue and playing status
song_queue = []
is_playing = False

# Specify the path for the database file in the data directory
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'birthdays.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Load DISCORD_TO_REAL_NAME mapping from environment variable
DISCORD_TO_REAL_NAME = json.loads(os.getenv('DISCORD_TO_REAL_NAME', '{}'))

# Database setup
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the birthday table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS birthdays (
        user_id TEXT PRIMARY KEY,
        birthday TEXT,
        timezone TEXT,
        message TEXT DEFAULT NULL
    )
''')
conn.commit()

### Helper Functions for Commands ###

# Helper function to parse dates
def parse_date(date_str):
    # Try known formats first
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Fallback to dateutil.parser for more flexible parsing
    try:
        return parse(date_str).strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Please use a recognizable date format.")

# Helper Function to play the next song in the queue
async def play_next(ctx):
    global is_playing
    if song_queue:
        next_song = song_queue.pop(0)
        audio_url, title = next_song
        voice_client = ctx.guild.voice_client
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice_client = ctx.guild.voice_client
            else:
                await ctx.send("You need to be in a voice channel to play music.")
                return
        voice_client.play(discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_path, **ffmpeg_opts), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), ctx.bot.loop))
        is_playing = True
        await ctx.send(f'Now playing: {title}')
        print(f"Playing audio: {title}")
    else:
        is_playing = False

# Command to make Brendan join the voice channel
@commands.command(name='join', help='Join the voice channel', aliases=['j'])
async def join(ctx):
    print("Join command received")
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        print(f"Joined voice channel: {channel.name}")
    else:
        await ctx.send("You need to be in a voice channel for me to join!")
        print("Author not in a voice channel")

# Command to make Brendan leave the voice channel
@commands.command(name='leave', help='Leave the voice channel', aliases=['l'])
async def leave(ctx):
    print("Leave command received")
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        print("Left the voice channel")
    else:
        await ctx.send("I'm not in a voice channel!")
        print("Bot not in a voice channel")

### Music Bot Commands ###

# Command to play a song from a URL or search term
@commands.command(name='play', help='Play a song from a URL or search term', aliases=['p'])
async def play(ctx, *, search: str):
    global is_playing
    print("Play command received")
    # Check if the bot is connected to a voice channel
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            print(f"Connected to voice channel: {channel.name}")
        else:
            await ctx.send("You need to be in a voice channel to play music.")
            print("User not in a voice channel")
            return

    # Fetch the audio URL
    audio_url, title_or_source = await get_audio_url(search)
    print(f"Audio URL: {audio_url}, Source: {title_or_source}")

    if not audio_url:
        await ctx.send("Could not retrieve audio from the provided search term.")
        print("Failed to retrieve audio")
        return

    # If a song is already playing, add to the queue
    if is_playing:
        song_queue.append((audio_url, title_or_source))
        await ctx.send(f'Song added to the queue: {title_or_source}')
        print(f"Song added to queue: {title_or_source}")
    else:
        # If no song is playing, play the song immediately
        song_queue.append((audio_url, title_or_source))
        await play_next(ctx)

# Command to pause the currently playing song
@commands.command(name='pause', help='Pause the currently playing song', aliases=['ps'])
async def pause(ctx):
    print("Pause command received")
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused.")
        print("Music paused")
    else:
        await ctx.send("No music is playing.")
        print("No music to pause")

# Command to resume the currently paused song
@commands.command(name='resume', help='Resume the currently paused song', aliases=['r'])
async def resume(ctx):
    print("Resume command received")
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed.")
        print("Music resumed")
    else:
        await ctx.send("No music is paused.")
        print("No music to resume")

# Command to stop the currently playing song
@commands.command(name='stop', help='Stop the currently playing song', aliases=['s'])
async def stop(ctx):
    global is_playing
    print("Stop command received")
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Music stopped.")
        print("Music stopped")
    else:
        await ctx.send("No music is playing.")
        print("No music to stop")
    song_queue.clear()
    is_playing = False
    print("Cleared song queue")

# Command to display the current queue
@commands.command(name='queue', help='Display the current music queue', aliases=['q'])
async def queue(ctx):
    print("Queue command received")
    if song_queue:
        queue_list = [title for _, title in song_queue]
        await ctx.send("Current queue:\n" + "\n".join(queue_list))
        print("Displayed current queue")
    else:
        await ctx.send("The queue is currently empty.")
        print("Queue is empty")

# Command to clear the current queue
@commands.command(name='clear', help='Clear the current music queue', aliases=['cl'])
async def clear(ctx):
    global is_playing
    print("Clear command received")
    song_queue.clear()
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Music stopped and queue cleared.")
        print("Music stopped and queue cleared")
    else:
        await ctx.send("Queue cleared.")
        print("Queue cleared")
    is_playing = False

# Command to skip the currently playing song
@commands.command(name='skip', help='Skip the currently playing song', aliases=['sk'])
async def skip(ctx):
    print("Skip command received")
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
        print("Skipped the current song")
    else:
        await ctx.send("No music is playing to skip.")
        print("No music to skip")
    if song_queue:
        await play_next(ctx)
    else:
        await ctx.send("No more songs in the queue.")
        print("No more songs in the queue")

### Birthday Bot Commands ###

# !birthday commands group
@commands.group(name='birthday', help='Commands related to managing birthdays')
async def birthday(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid birthday command. Use !birthday get, !birthday set, !birthday show-nearest, or !birthday remove.')
        logger.debug('Invalid birthday command used.')
        print('Invalid birthday command used.')

# Subcommand to import birthdays from friends data
# Example: !birthday import
@birthday.command(name='import', help='Import birthdays from friends data')
async def import_birthdays(ctx):
    logger.debug('Starting import of birthdays from friends data')
    print('Starting import of birthdays from friends data')
    
    # Load friends data from JSON files
    directory = os.path.join(os.path.dirname(__file__), '..', 'data')
    data = load_json_files(directory)
    friends = data.get("friends", [])
    
    # Reverse the DISCORD_TO_REAL_NAME dictionary
    real_name_to_discord = {v: k for k, v in DISCORD_TO_REAL_NAME.items()}
    
    for friend in friends:
        name = friend.get('name')
        if not name:
            continue
        
        basic_info = friend.get('basicInfo', {})
        birthday = basic_info.get('birthday')
        
        if not birthday:
            continue
        
        # Find the corresponding Discord name
        discord_name = real_name_to_discord.get(name)
        if not discord_name:
            continue
        
        # Fetch the Discord user object
        user = discord.utils.get(ctx.guild.members, name=discord_name)
        if not user:
            logger.error(f'User {discord_name} not found in the guild')
            print(f'User {discord_name} not found in the guild')
            continue
        
        # Parse the birthday to YYYY-MM-DD format
        try:
            parsed_date = parse_date(birthday)
        except ValueError as e:
            logger.error(f'Error parsing birthday for {name}: {e}')
            print(f'Error parsing birthday for {name}: {e}')
            continue
        
        # Insert or update the birthday in the database, assuming timezone is "EST"
        cursor.execute('REPLACE INTO birthdays (user_id, birthday, timezone) VALUES (?, ?, ?)', (user.id, parsed_date, 'EST'))
        conn.commit()
        logger.debug(f'Imported birthday for {name} ({user.id}): {parsed_date}')
        print(f'Imported birthday for {name} ({user.id}): {parsed_date}')
    
    await ctx.send('Birthdays have been imported successfully.')
    logger.debug('Finished importing birthdays')
    print('Finished importing birthdays')

# Command to get a user's birthday
# Example: !birthday get @Username
@birthday.command(name='get', help="Get a user's birthday")
async def get_birthday(ctx, user: discord.User):
    logger.debug(f'Fetching birthday for user {user.id}')
    print(f'Fetching birthday for user {user.id}')
    # Fetch birthday from the database
    cursor.execute('SELECT birthday, timezone FROM birthdays WHERE user_id = ?', (str(user.id),))
    result = cursor.fetchone()
    if result:
        await ctx.send(f"{user.name}'s birthday is on {result[0]} in timezone {result[1]}.")
        logger.debug(f'Fetched birthday for user {user.id}: {result}')
        print(f'Fetched birthday for user {user.id}: {result}')
    else:
        await ctx.send(f"{user.name} has not set a birthday.")
        logger.debug(f'No birthday set for user {user.id}')
        print(f'No birthday set for user {user.id}')

# Command to show the nearest upcoming birthdays
# Example: !birthday show-nearest
@birthday.command(name='show-nearest', help='Get a list of users with upcoming birthdays')
async def show_nearest(ctx):
    logger.debug('Fetching nearest upcoming birthdays')
    print('Fetching nearest upcoming birthdays')
    today = datetime.now().date()
    
    # Fetch all birthdays from the database
    cursor.execute('SELECT user_id, birthday FROM birthdays')
    all_birthdays = cursor.fetchall()
    print(f'All birthdays: {all_birthdays}')
    logger.debug(f'All birthdays: {all_birthdays}')
    
    upcoming_birthdays = []
    for user_id, bday_str in all_birthdays:
        bday = datetime.strptime(bday_str, "%Y-%m-%d").date()
        bday_this_year = bday.replace(year=today.year)
        if bday_this_year < today:
            bday_this_year = bday.replace(year=today.year + 1)
        upcoming_birthdays.append((user_id, bday_this_year))
    
    # Sort birthdays by how soon they are from today
    upcoming_birthdays = sorted(upcoming_birthdays, key=lambda x: x[1])
    print(f'Upcoming birthdays sorted: {upcoming_birthdays}')
    logger.debug(f'Upcoming birthdays sorted: {upcoming_birthdays}')
    
    # Filter for birthdays within the next 30 days
    nearest_birthdays = [user_id for user_id, bday in upcoming_birthdays if (bday - today).days < 30]
    print(f'Nearest birthdays within 30 days: {nearest_birthdays}')
    logger.debug(f'Nearest birthdays within 30 days: {nearest_birthdays}')
    
    if nearest_birthdays:
        users = [await ctx.bot.fetch_user(user_id) for user_id in nearest_birthdays]
        user_list = "\n".join([f"{user.name}" for user in users])
        await ctx.send(f"Users with upcoming birthdays:\n{user_list}")
        logger.debug(f'Nearest birthdays: {user_list}')
        print(f'Nearest birthdays: {user_list}')
    else:
        await ctx.send("No upcoming birthdays in the next 30 days.")
        logger.debug('No upcoming birthdays in the next 30 days')
        print('No upcoming birthdays in the next 30 days')

# Command to set or update your birthday
# Example: !birthday set 1990-05-15 UTC or !birthday set 06/10/1998 UTC
@birthday.command(name='set', help='Set or update your birthday')
async def set_birthday(ctx, date: str = None, timezone: str = None):
    user_id = str(ctx.author.id)

    # Check if date is provided
    if date is None:
        await ctx.send("You need to provide a date. Example: !birthday set 1990-05-15 UTC or !birthday set 06/10/1998 UTC")
        logger.debug(f'Date not provided by user {user_id}')
        print(f'Date not provided by user {user_id}')
        return

    # Check if timezone is provided
    if timezone is None:
        await ctx.send("You need to provide a timezone. Example: !birthday set 1990-05-15 UTC or !birthday set 06/10/1998 UTC")
        logger.debug(f'Timezone not provided by user {user_id}')
        print(f'Timezone not provided by user {user_id}')
        return

    try:
        parsed_date = parse_date(date)
    except ValueError as e:
        await ctx.send(str(e))
        logger.debug(f'Invalid date format provided by user {user_id}')
        print(f'Invalid date format provided by user {user_id}')
        return

    logger.debug(f'Setting birthday for user {user_id} to {parsed_date} with timezone {timezone}')
    print(f'Setting birthday for user {user_id} to {parsed_date} with timezone {timezone}')
    cursor.execute('REPLACE INTO birthdays (user_id, birthday, timezone) VALUES (?, ?, ?)', (user_id, parsed_date, timezone))
    conn.commit()
    
    # Verify that the data was written correctly
    cursor.execute('SELECT * FROM birthdays WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    print(f'Verified write: {result}')
    logger.debug(f'Verified write: {result}')
    
    await ctx.send(f"Your birthday has been set to {parsed_date} with timezone {timezone}.")
    logger.debug(f'Birthday set for user {user_id}')
    print(f'Birthday set for user {user_id}')

# Command to set a custom birthday message
# Example: !birthday set-message "Happy Birthday, {user}!"
@birthday.command(name='set-message', help='Set a custom birthday message')
async def set_message(ctx, *, message: str):
    user_id = str(ctx.author.id)
    logger.debug(f'Setting custom birthday message for user {user_id}')
    print(f'Setting custom birthday message for user {user_id}')
    cursor.execute('UPDATE birthdays SET message = ? WHERE user_id = ?', (message, user_id))
    conn.commit()
    
    # Verify that the data was written correctly
    cursor.execute('SELECT message FROM birthdays WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    print(f'Verified message write: {result}')
    logger.debug(f'Verified message write: {result}')
    
    await ctx.send(f"Your custom birthday message has been set to: {message}")
    logger.debug(f'Custom birthday message set for user {user_id}')
    print(f'Custom birthday message set for user {user_id}')


# Command to remove your birthday information
# Example: !birthday remove
@birthday.command(name='remove', help='Remove your birthday information')
async def remove_birthday(ctx):
    user_id = str(ctx.author.id)
    logger.debug(f'Removing birthday for user {user_id}')
    print(f'Removing birthday for user {user_id}')
    cursor.execute('DELETE FROM birthdays WHERE user_id = ?', (user_id,))
    conn.commit()
    await ctx.send("Your birthday information has been removed.")
    logger.debug(f'Birthday information removed for user {user_id}')
    print(f'Birthday information removed for user {user_id}')

# Command to test the birthday message
# Example: !birthday test-message
@birthday.command(name='test-message', help='Test the birthday message for user "yenyverse"')
async def test_message(ctx):
    YOUR_ANNOUNCEMENT_CHANNEL_ID = 692429647245213737  # Replace with your actual channel ID
    test_user_id = "202176522075897866"  # Replace with the actual user ID of the tester
    try:
        user = await ctx.bot.fetch_user(test_user_id)
        
        # Hardcoded birthday message for testing
        birthday_message = f"Happy Birthday, {user.mention}! This is a test message."
        
        # Select a random birthday GIF
        gif_url = random.choice(birthday_gifs)
        
        # Send the birthday message
        await ctx.bot.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(birthday_message)
        
        # Create an embed for the GIF
        embed = discord.Embed()
        embed.set_image(url=gif_url)
        
        # Send the GIF embed
        await ctx.bot.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(embed=embed)
        
        logger.debug(f'Test birthday message sent to {user.name}')
        print(f'Test birthday message sent to {user.name}')
    except discord.errors.HTTPException as e:
        logger.error(f'Failed to send test birthday message: {e}')
        print(f'Failed to send test birthday message: {e}')


# Moderator commands group
@commands.group(name='config', help='Configure settings for the bot')
async def config(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid config command. Use /config check, /config announce, or /config birthday-role.')
        logger.debug('Invalid config command used.')
        print('Invalid config command used.')

# Command to check the bot's configuration
# Example: /config check
@config.command(name='check', help='Test the bot\'s current configuration and show the results')
async def config_check(ctx):
    await ctx.send("Configuration is okay.")
    logger.debug('Configuration check performed')
    print('Configuration check performed')

# Command to configure birthday announcements
# Example: /config announce
@config.command(name='announce', help='Settings for birthday announcements')
async def config_announce(ctx):
    await ctx.send("Announcement settings configured.")
    logger.debug('Announcement settings configured')
    print('Announcement settings configured')

# Command to set the role given to users having a birthday
# Example: /config birthday-role @BirthdayRole
@config.command(name='birthday-role', help='Set the role given to users having a birthday')
async def config_birthday_role(ctx, role: discord.Role):
    await ctx.send(f"Birthday role set to {role.name}.")
    logger.debug(f'Birthday role set to {role.name}')
    print(f'Birthday role set to {role.name}')

# Command to export all known birthdays
# Example: /export-birthdays
@commands.command(name='export-birthdays', help='Generate a text file with all known and available birthdays')
async def export_birthdays(ctx):
    logger.debug('Exporting birthdays')
    print('Exporting birthdays')
    cursor.execute('SELECT user_id, birthday, timezone FROM birthdays')
    all_birthdays = cursor.fetchall()
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'birthdays.txt'), 'w') as f:
        for user_id, birthday, timezone in all_birthdays:
            f.write(f"{user_id},{birthday},{timezone}\n")
    await ctx.send(file=discord.File(os.path.join(os.path.dirname(__file__), '..', 'data', 'birthdays.txt')))
    logger.debug('Birthdays exported')
    print('Birthdays exported')

# Override commands group
@commands.group(name='override', help='Commands to set or remove options for other users')
async def override(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid override command. Use /override set-birthday, /override set-timezone, or /override remove.')
        logger.debug('Invalid override command used.')
        print('Invalid override command used.')

# Command to set another user's birthday
# Example: /override set-birthday @Username 1990-05-15 UTC
@override.command(name='set-birthday', help="Set another user's birthday")
async def override_set_birthday(ctx, user: discord.User, date: str, timezone: str):
    logger.debug(f'Setting birthday for user {user.id} to {date} with timezone {timezone}')
    print(f'Setting birthday for user {user.id} to {date} with timezone {timezone}')
    cursor.execute('REPLACE INTO birthdays (user_id, birthday, timezone) VALUES (?, ?, ?)', (str(user.id), date, timezone))
    conn.commit()
    await ctx.send(f"Birthday for {user.name} set to {date} with timezone {timezone}.")
    logger.debug(f'Birthday set for user {user.id}')
    print(f'Birthday set for user {user.id}')

# Command to set another user's timezone
# Example: /override set-timezone @Username UTC
@override.command(name='set-timezone', help="Set another user's timezone")
async def override_set_timezone(ctx, user: discord.User, timezone: str):
    logger.debug(f'Setting timezone for user {user.id} to {timezone}')
    print(f'Setting timezone for user {user.id} to {timezone}')
    cursor.execute('UPDATE birthdays SET timezone = ? WHERE user_id = ?', (timezone, str(user.id)))
    conn.commit()
    await ctx.send(f"Timezone for {user.name} set to {timezone}.")
    logger.debug(f'Timezone set for user {user.id}')
    print(f'Timezone set for user {user.id}')

# Command to remove another user's birthday information
# Example: /override remove @Username
@override.command(name='remove', help="Remove another user's birthday information")
async def override_remove_birthday(ctx, user: discord.User):
    logger.debug(f'Removing birthday for user {user.id}')
    print(f'Removing birthday for user {user.id}')
    cursor.execute('DELETE FROM birthdays WHERE user_id = ?', (str(user.id),))
    conn.commit()
    await ctx.send(f"Birthday information for {user.name} has been removed.")
    logger.debug(f'Birthday information removed for user {user.id}')
    print(f'Birthday information removed for user {user.id}')

### Birthday GIF URLs Helper Functions for Commands ###

# List of birthday GIF URLs
birthday_gifs = [
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjhyYnZ0Z3hkOW80N3I4cDFvNjQzZG52NnBndnQ3YWgxeGk4Z3M2MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/g5R9dok94mrIvplmZd/giphy.gif",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGswY2ppc3h4dmdpNXc3MnpyYWNnb2liY3o2bDE0OHd5bWd5dHkwcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l1Ku8SFqBdaV506fm/giphy.gif",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGRnMXAwYXA3bzB6MTRnYm9ld2RuY2prNDBjam1lanhiNDZzdGx3dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/S5oVZIvOlYInEgDtFX/giphy.gif",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWw2d2RzczJhZmdncml5M3JvbGg5cWh5OWJrOGdlejVpMjh5a21uMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mmndweRcDkkcU/giphy.gif",
    "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3FqODF5OGI1Y2o5MWM1bHh1djJ3OTRzZThhODZhdGo4MnlranI1ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IFjSbBHETzzr6GJdwW/giphy-downsized-large.gif"
]

# Daily check for birthdays and sending announcements
async def daily_birthday_check(client):
    YOUR_ANNOUNCEMENT_CHANNEL_ID = 692429647245213737  # Replace with your actual channel ID
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.now()
        if now.hour == 0:  # Check at midnight
            today = now.date()
            cursor.execute('SELECT user_id, message FROM birthdays WHERE strftime("%m-%d", birthday) = ?', (today.strftime("%m-%d"),))
            users_with_birthday = cursor.fetchall()
            for user_id, message in users_with_birthday:
                user = await client.fetch_user(user_id[0])
                if message:
                    birthday_message = message.replace("{user}", user.mention)
                else:
                    birthday_message = f"Happy Birthday, {user.mention}!"
                
                # Select a random birthday GIF
                gif_url = random.choice(birthday_gifs)
                
                # Send the birthday message
                await client.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(birthday_message)
                
                # Create an embed for the GIF
                embed = discord.Embed()
                embed.set_image(url=gif_url)
                
                # Send the GIF embed
                await client.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(embed=embed)
            
            logger.debug('Birthday announcements sent')
            print('Birthday announcements sent')
            await asyncio.sleep(86400)  # Wait a day
        else:
            await asyncio.sleep(3600)  # Wait an hour and check again


