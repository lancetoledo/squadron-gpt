import discord
from discord.ext import commands
from utils.music_utils import get_audio_url
import asyncio
import os

ffmpeg_opts = {
    'options': '-vn',
}

ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"  # Update this path if necessary

song_queue = []
is_playing = False

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='Join the voice channel', aliases=['j'])
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You need to be in a voice channel for me to join!")

    @commands.command(name='leave', help='Leave the voice channel', aliases=['l'])
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("I'm not in a voice channel!")

    @commands.command(name='play', help='Play a song from a URL or search term', aliases=['p'])
    async def play(self, ctx, *, search: str):
        global is_playing
        if not ctx.voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
            else:
                await ctx.send("You need to be in a voice channel to play music.")
                return

        audio_url, title_or_source = await get_audio_url(search)

        if not audio_url:
            await ctx.send("Could not retrieve audio from the provided search term.")
            return

        if is_playing:
            song_queue.append((audio_url, title_or_source))
            await ctx.send(f'Song added to the queue: {title_or_source}')
        else:
            song_queue.append((audio_url, title_or_source))
            await self.play_next(ctx)

    async def play_next(self, ctx):
        global is_playing
        if song_queue:
            next_song = song_queue.pop(0)
            audio_url, title = next_song
            voice_client = ctx.guild.voice_client
            voice_client.play(discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_path, **ffmpeg_opts), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), ctx.bot.loop))
            is_playing = True
            await ctx.send(f'Now playing: {title}')
        else:
            is_playing = False

    @commands.command(name='pause', help='Pause the currently playing song', aliases=['ps'])
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Music paused.")
        else:
            await ctx.send("No music is playing.")

    @commands.command(name='resume', help='Resume the currently paused song', aliases=['r'])
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Music resumed.")
        else:
            await ctx.send("No music is paused.")

    @commands.command(name='stop', help='Stop the currently playing song', aliases=['s'])
    async def stop(self, ctx):
        global is_playing
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Music stopped.")
        else:
            await ctx.send("No music is playing.")
        song_queue.clear()
        is_playing = False

    @commands.command(name='queue', help='Display the current music queue', aliases=['q'])
    async def queue(self, ctx):
        if song_queue:
            queue_list = [title for _, title in song_queue]
            await ctx.send("Current queue:\n" + "\n".join(queue_list))
        else:
            await ctx.send("The queue is currently empty.")

    @commands.command(name='clear', help='Clear the current music queue', aliases=['cl'])
    async def clear(self, ctx):
        global is_playing
        song_queue.clear()
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Music stopped and queue cleared.")
        else:
            await ctx.send("Queue cleared.")
        is_playing = False

    @commands.command(name='skip', help='Skip the currently playing song', aliases=['sk'])
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("No music is playing to skip.")
        if song_queue:
            await self.play_next(ctx)
        else:
            await ctx.send("No more songs in the queue.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
    print("🎶 MusicCog added")
