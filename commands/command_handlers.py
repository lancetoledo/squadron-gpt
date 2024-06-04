import discord
from discord.ext import commands
from utils.music_utils import get_audio_url

# FFmpeg options
ffmpeg_opts = {
    'options': '-vn',
}

# Specify the path to the ffmpeg executable
ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"  # Update this path if necessary

# Global variables for song queue and playing status
song_queue = []
is_playing = False

# Function to play the next song in the queue
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
        voice_client.play(discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_path, **ffmpeg_opts), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
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
