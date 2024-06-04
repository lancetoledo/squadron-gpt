import discord
from discord.ext import commands
from utils.music_utils import get_audio_url

# FFmpeg options
ffmpeg_opts = {
    'options': '-vn',
}

# Specify the path to the ffmpeg executable
ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"  # Update this path if necessary

# Command to make Brendan join the voice channel
@commands.command(name='join', help='Join the voice channel')
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
@commands.command(name='leave', help='Leave the voice channel')
async def leave(ctx):
    print("Leave command received")
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        print("Left the voice channel")
    else:
        await ctx.send("I'm not in a voice channel!")
        print("Bot not in a voice channel")

# Command to play a song from a URL or search term
@commands.command(name='play', help='Play a song from a URL or search term')
async def play(ctx, *, search: str):
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

    # Play the extracted audio
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        print("Stopped currently playing audio")

    voice_client.play(discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_path, **ffmpeg_opts))
    print("Playing audio")
    await ctx.send(f'Now playing: {title_or_source}')

# Command to pause the currently playing song
@commands.command(name='pause', help='Pause the currently playing song')
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
@commands.command(name='resume', help='Resume the currently paused song')
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
@commands.command(name='stop', help='Stop the currently playing song')
async def stop(ctx):
    print("Stop command received")
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Music stopped.")
        print("Music stopped")
    else:
        await ctx.send("No music is playing.")
        print("No music to stop")
