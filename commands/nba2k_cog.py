import discord
from discord.ext import commands
import re

class NBA2KCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = 1203493071602327653  # Your specific channel ID

    @commands.command(name='setchannel', help='Set the target channel for embedded messages')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        self.target_channel_id = channel.id
        await ctx.send(f"Target channel set to: {channel.name}")

    @commands.command(name='send', help='Send an embedded message to the target channel')
    @commands.has_permissions(administrator=True)
    async def send_embed(self, ctx, *, message: str):
        target_channel = self.bot.get_channel(self.target_channel_id)
        if target_channel is None:
            await ctx.send("The target channel could not be found. Please check the channel ID.")
            return

        # Split the message into title and content
        title, content = self.split_title_content(message)

        # Process markdown-style formatting
        formatted_content = self.format_message(content)

        embed = discord.Embed(
            title=title,
            description=formatted_content,
            color=discord.Color.blue()
        )

        await target_channel.send(embed=embed)
        await ctx.send("Embedded message sent successfully!")

    def split_title_content(self, message):
        lines = message.split('\n', 1)
        if len(lines) > 1 and lines[0].startswith('# '):
            return lines[0][2:].strip(), lines[1].strip()
        return None, message.strip()

    def format_message(self, message):
        # Replace escaped newlines with actual newlines
        message = message.replace('\\n', '\n')
        
        # Format headers
        message = re.sub(r'^## (.+)$', r'**__\1__**', message, flags=re.MULTILINE)
        message = re.sub(r'^### (.+)$', r'**\1**', message, flags=re.MULTILINE)
        
        # Format spoilers (corrected)
        message = re.sub(r'\|\|(.+?)\|\|', r'||\1||', message)
        
        # The rest of the formatting (bold, italic, underline, strikethrough) 
        # can be left as-is, as Discord will interpret them correctly

        return message

async def setup(bot):
    await bot.add_cog(NBA2KCog(bot))
    print("🏀 NBA2KCog added")