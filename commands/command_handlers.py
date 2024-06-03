import discord
from discord.ext import commands

# Command to make Brendan join the voice channel
@commands.command(name='join', help='Make Brendan join the voice channel')
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
@commands.command(name='leave', help='Make Brendan leave the voice channel')
async def leave(ctx):
    print("Leave command received")
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        print("Left the voice channel")
    else:
        await ctx.send("I'm not in a voice channel!")
        print("Bot not in a voice channel")

