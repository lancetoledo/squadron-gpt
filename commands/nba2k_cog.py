import json
import discord
from discord.ext import commands
from enum import Enum
from typing import Dict, List
import asyncio
import re
from datetime import datetime, timedelta
import os


class TradeStatus(Enum):
    PENDING = 0
    ADMIN_REVIEWING = 0
    USER_REVIEWING = 0
    CLOSED = 3

class TradeRequest:
    def __init__(self, user_id: int, message: str, channel_id: int):
        self.user_id = user_id
        self.message = message
        self.status = TradeStatus.PENDING
        self.admin_message_id = None
        self.channel_id = channel_id
        self.proposals: List[str] = []

class NBA2KCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_id = 202176522075897866  # Your user ID
        self.nba2k_channel_id = 1260619444171047013  # The specific NBA2K channel
        self.free_agents = {}  # {player_name: [list of interested user IDs]}
        self.user_interests = {}  # {user_id: [list of interested player names]}
        self.free_agency_end_time = None
        self.trade_requests = {}
        
        # Load the JSON data
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'MyNBA.json')
        with open(json_path, 'r') as f:
            self.nba2k_data = json.load(f)

    # !send # Important Update\nThe league draft will be held next Friday at 8 PM EST.
    @commands.command(name='send', help='Send an embedded message to the specified channel')
    @commands.has_permissions(administrator=True)
    async def send_embed(self, ctx, channel: discord.TextChannel, *, message: str):
        title, content = self.split_title_content(message)
        formatted_content = self.format_message(content)
        
        embed = self.create_embed(title, formatted_content)
        await channel.send(embed=embed)
        await ctx.send("Embedded message sent successfully!")

    def split_title_content(self, message):
        lines = message.split('\n', 1)
        if len(lines) > 1 and lines[0].startswith('# '):
            return lines[0][2:].strip(), lines[1].strip()
        return None, message.strip()

    def format_message(self, message):
        message = message.replace('\\n', '\n')
        message = re.sub(r'^## (.+)$', r'**__\1__**', message, flags=re.MULTILINE)
        message = re.sub(r'^### (.+)$', r'**\1**', message, flags=re.MULTILINE)
        message = re.sub(r'\|\|(.+?)\|\|', r'||\1||', message)
        return message

    def create_embed(self, title, content):
        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(text="NBA 2K League Bot", icon_url=self.bot.user.avatar.url)
        return embed

    def generate_title(self, request_type):
        title_map = {
            "player information": "Player Profile",
            "team information": "Team Overview",
            "player stats": "Player Statistics",
            "player attributes": "Player Attributes",
            "league standings": "League Standings",
            "upcoming games schedule": "Upcoming Games",
            "team roster": "Team Roster",
            "league leaders information": "League Leaders"
        }
        return title_map.get(request_type, request_type.capitalize())

    async def relay_to_admin(self, ctx, request_type: str):
        admin = await self.bot.fetch_user(self.admin_id)
        await admin.send(f"{ctx.author.name} is requesting {request_type}. Please respond with the information.")
        await ctx.send(f"Your request for {request_type} has been sent to the admin. Please wait for a response.")

        def check(m):
            return m.author.id == self.admin_id and isinstance(m.channel, discord.DMChannel)

        try:
            # Changed from 300 seconds (5 minutes) to 7200 seconds (2 hours)
            admin_response = await self.bot.wait_for('message', check=check, timeout=7200.0)
            
            formatted_message = self.format_message(admin_response.content)
            
            channel = self.bot.get_channel(self.nba2k_channel_id)
            await channel.send(f"**{request_type.capitalize()}**\n\n{formatted_message}")
            
            if ctx.channel.id != self.nba2k_channel_id:
                await ctx.send(f"Your requested information has been posted in the NBA2K channel.")
        except asyncio.TimeoutError:
            await ctx.send("The admin did not respond within 2 hours. Please try your request again later.")

    @commands.command(name='myplayer', help='Get information about your player')
    async def my_player(self, ctx):
        player_info = self.get_player_info(ctx.author.id)
        if player_info:
            embed = self.create_player_embed(player_info)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have a player in this league. Please contact an admin if you believe this is an error.")

    @commands.command(name='myteam', help='Get information about your team')
    async def my_team(self, ctx):
        team_info = self.get_team_info(ctx.author.id)
        if team_info:
            embed = self.create_team_embed(team_info)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have a team in this league. Please contact an admin if you believe this is an error.")

    def get_player_info(self, user_id):
        if self.nba2k_data['staff']['gm']['userid'] == user_id:
            gm_name = self.nba2k_data['staff']['gm']['name']
            for player in self.nba2k_data['roster']:
                if player['name'] == gm_name:
                    return player
        return None

    def get_team_info(self, user_id):
        if self.nba2k_data['staff']['gm']['userid'] == user_id:
            return self.nba2k_data
        return None

    def create_player_embed(self, player):
        embed = discord.Embed(title=f"{player['name']} - {player['position']}", color=discord.Color.blue())
        embed.add_field(name="Overall", value=player['overall'], inline=True)
        embed.add_field(name="Age", value=player['age'], inline=True)
        embed.add_field(name="Years in NBA", value=player['yearsInNBA'], inline=True)
        embed.add_field(name="Potential", value=player['potential'], inline=True)
        embed.add_field(name="Skills", value=', '.join(player['skills']), inline=False)
        embed.add_field(name="Contract Years Left", value=player['contract']['yearsLeft'], inline=True)
        if player['narratives']:
            embed.add_field(name="Narratives", value='\n'.join(player['narratives']), inline=False)
        if player['rivals']:
            embed.add_field(name="Rivals", value=', '.join(player['rivals']), inline=False)
        return embed

    def create_team_embed(self, team_data):
        embed = discord.Embed(title=f"{team_data['team']['name']} - {team_data['season']} Season", color=discord.Color.gold())
        embed.add_field(name="Arena", value=team_data['team']['arena'], inline=True)
        embed.add_field(name="Cap Space", value=f"${team_data['team']['capSpace']:,}", inline=True)
        
        # Sort players by overall rating
        sorted_players = sorted(team_data['roster'], key=lambda x: x['overall'], reverse=True)
        
        # Top 5 players
        top_players = sorted_players[:5]
        top_players_text = '\n'.join([f"{p['name']} ({p['overall']} OVR) - {p['position']}" for p in top_players])
        embed.add_field(name="Top Players", value=top_players_text, inline=False)
        
        # Rest of the roster
        other_players = sorted_players[5:]
        other_players_text = '\n'.join([f"{p['name']} ({p['overall']} OVR) - {p['position']}" for p in other_players])
        embed.add_field(name="Rest of Roster", value=other_players_text if other_players_text else "No other players", inline=False)
        
        # Staff
        embed.add_field(name="Head Coach", value=f"{team_data['staff']['headCoach']['name']} ({team_data['staff']['headCoach']['overallRating']} OVR)", inline=False)
        embed.add_field(name="GM", value=team_data['staff']['gm']['name'], inline=True)
        
        # Goals
        embed.add_field(name="Short Term Goal", value=team_data['goals']['shortTerm'], inline=False)
        embed.add_field(name="Long Term Goal", value=team_data['goals']['longTerm'], inline=False)
        
        # Rivals
        if team_data['rivals']:
            embed.add_field(name="Team Rivals", value=', '.join(team_data['rivals']), inline=False)
        
        return embed

    @commands.command(name='mystats', help='Get your player stats')
    async def my_stats(self, ctx):
        await self.relay_to_admin(ctx, "player stats")

    @commands.command(name='myattributes', help='Get your player attributes')
    async def my_attributes(self, ctx):
        await self.relay_to_admin(ctx, "player attributes")

    @commands.command(name='standings', help='Get league standings')
    async def standings(self, ctx):
        await self.relay_to_admin(ctx, "league standings")

    @commands.command(name='schedule', help='Get upcoming games schedule')
    async def schedule(self, ctx):
        await self.relay_to_admin(ctx, "upcoming games schedule")

    @commands.command(name='teamroster', help='Get your team\'s roster')
    async def team_roster(self, ctx):
        await self.relay_to_admin(ctx, "team roster")

    @commands.command(name='leagueleaders', help='Get league leaders in various categories')
    async def league_leaders(self, ctx):
        await self.relay_to_admin(ctx, "league leaders information")

    # !postfreeagents 24h30m LeBron James, Stephen Curry, Kevin Durant
    @commands.command(name='postfreeagents', help='Post a list of free agents')
    @commands.has_permissions(administrator=True)
    async def post_free_agents(self, ctx, duration: str, *, players: str):
        # Parse duration (e.g., "2h30m" for 2 hours and 30 minutes)
        hours, minutes = map(int, duration[:-1].replace('h', ':').replace('m', '').split(':'))
        self.free_agency_end_time = datetime.now() + timedelta(hours=hours, minutes=minutes)

        # Clear previous free agents
        self.free_agents.clear()
        self.user_interests.clear()

        # Add new free agents
        for player in players.split(','):
            self.free_agents[player.strip()] = []

        await self.update_free_agents_message(ctx)
        await ctx.send(f"Free agents posted. Free agency will end at {self.free_agency_end_time.strftime('%Y-%m-%d %H:%M:%S')}.")

    # !interest LeBron James
    @commands.command(name='interest', help='Express interest in a free agent')
    async def express_interest(self, ctx, *, player_name: str):
        if datetime.now() > self.free_agency_end_time:
            await ctx.send("Free agency period has ended.")
            return

        if player_name not in self.free_agents:
            await ctx.send("This player is not in the free agent list.")
            return

        if ctx.author.id not in self.user_interests:
            self.user_interests[ctx.author.id] = []

        if player_name in self.user_interests[ctx.author.id]:
            await ctx.send("You've already expressed interest in this player.")
            return

        if len(self.user_interests[ctx.author.id]) >= 3:
            await ctx.send("You can only be interested in up to 3 free agents at a time.")
            return

        self.free_agents[player_name].append(ctx.author.id)
        self.user_interests[ctx.author.id].append(player_name)

        await self.update_free_agents_message(ctx)
        await ctx.send(f"You've expressed interest in {player_name}.")

    # !removeinterest Stephen Curry
    @commands.command(name='removeinterest', help='Remove interest in a free agent')
    async def remove_interest(self, ctx, *, player_name: str):
        if ctx.author.id not in self.user_interests or player_name not in self.user_interests[ctx.author.id]:
            await ctx.send("You haven't expressed interest in this player.")
            return

        self.free_agents[player_name].remove(ctx.author.id)
        self.user_interests[ctx.author.id].remove(player_name)

        await self.update_free_agents_message(ctx)
        await ctx.send(f"You've removed your interest in {player_name}.")

    # !signplayer Kevin Durant
    @commands.command(name='signplayer', help='Sign a free agent to a team')
    @commands.has_permissions(administrator=True)
    async def sign_player(self, ctx, *, player_name: str):
        if player_name not in self.free_agents:
            await ctx.send("This player is not in the free agent list.")
            return

        del self.free_agents[player_name]
        for user_id in self.user_interests:
            if player_name in self.user_interests[user_id]:
                self.user_interests[user_id].remove(player_name)

        await self.update_free_agents_message(ctx)
        await ctx.send(f"{player_name} has been signed and removed from the free agent list.")

    async def update_free_agents_message(self, ctx):
        channel = self.bot.get_channel(self.nba2k_channel_id)
        message = "**Current Free Agents:**\n\n"
        for player, interested_users in self.free_agents.items():
            message += f"• {player} - {len(interested_users)} interested\n"

        message += f"\nFree agency ends at: {self.free_agency_end_time.strftime('%Y-%m-%d %H:%M:%S')}"

        await channel.send(message)

    # !myinterests - shows interest in the game
    @commands.command(name='myinterests', help='View your current free agent interests')
    async def my_interests(self, ctx):
        if ctx.author.id not in self.user_interests or not self.user_interests[ctx.author.id]:
            await ctx.send("You haven't expressed interest in any free agents.")
            return

        interests = ", ".join(self.user_interests[ctx.author.id])
        await ctx.send(f"You're currently interested in: {interests}")

    # !viewinterests LeBron James
    @commands.command(name='viewinterests', help='View detailed interests for a player')
    @commands.has_permissions(administrator=True)
    async def view_interests(self, ctx, *, player_name: str):
        if player_name not in self.free_agents:
            await ctx.send("This player is not in the free agent list.")
            return

        interested_users = self.free_agents[player_name]
        if not interested_users:
            await ctx.send(f"No users are currently interested in {player_name}.")
            return

        message = f"Users interested in {player_name} (in order of expression):\n"
        for i, user_id in enumerate(interested_users, 1):
            user = await self.bot.fetch_user(user_id)
            message += f"{i}. {user.name}\n"

        await ctx.send(message)

    @commands.command(name='requesttrade', help='Request a trade')
    async def request_trade(self, ctx, *, message: str):
        trade_request = TradeRequest(ctx.author.id, message, ctx.channel.id)
        self.trade_requests[ctx.author.id] = trade_request

        await ctx.send(f"{ctx.author.mention}, your trade request has been submitted. You will receive a response here shortly.")

        admin = await self.bot.fetch_user(self.admin_id)
        admin_message = await admin.send(embed=self.create_admin_embed(ctx.author, trade_request))
        trade_request.admin_message_id = admin_message.id
        
        await self.add_admin_buttons(admin_message, ctx.author.id)

    async def add_admin_buttons(self, message, user_id):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label="Approve", custom_id=f"approve_{user_id}"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.red, label="Deny", custom_id=f"deny_{user_id}"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.grey, label="Request More Info", custom_id=f"more_info_{user_id}"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label="Propose Trade", custom_id=f"propose_{user_id}"))
        
        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != self.admin_id:
                await interaction.response.send_message("You're not authorized to respond to this request.", ephemeral=True)
                return

            custom_id = interaction.data['custom_id']
            action, user_id = custom_id.split('_')
            user_id = int(user_id)
            
            await self.handle_admin_action(interaction, action, user_id)

        for item in view.children:
            item.callback = button_callback

        await message.edit(view=view)

    async def handle_admin_action(self, interaction: discord.Interaction, action: str, user_id: int):
        trade_request = self.trade_requests.get(user_id)

        if not trade_request:
            await interaction.response.send_message("This trade request no longer exists.", ephemeral=True)
            return

        channel = self.bot.get_channel(trade_request.channel_id)
        user = await self.bot.fetch_user(user_id)

        if action == "approve":
            await channel.send(f"{user.mention}, your trade request has been approved. The admin will send trade proposals shortly.")
            await interaction.response.send_message("Trade request approved. Use the 'Propose Trade' button to send offers.", ephemeral=True)
            trade_request.status = TradeStatus.ADMIN_REVIEWING
        elif action == "deny":
            await channel.send(f"{user.mention}, your trade request has been denied.")
            await interaction.response.send_message("Trade request denied.", ephemeral=True)
            trade_request.status = TradeStatus.CLOSED
        elif action == "more_info":
            await channel.send(f"{user.mention}, the admin has requested more information about your trade request. Please use the `!addinfo` command to provide additional details.")
            await interaction.response.send_message("Requested more information from the user.", ephemeral=True)
        elif action == "propose":
            await interaction.response.send_modal(TradeProposalModal(self, user_id))
            return  # Don't update the message yet, as we're showing a modal

        if trade_request.status == TradeStatus.CLOSED:
            del self.trade_requests[user_id]

        await self.update_admin_message(interaction.message, trade_request, user)

    @commands.command(name='addinfo', help='Add more information to your trade request')
    async def add_info(self, ctx, *, message: str):
        trade_request = self.trade_requests.get(ctx.author.id)
        if not trade_request:
            await ctx.send("You don't have an active trade request.")
            return

        trade_request.message += f"\n\nAdditional Info: {message}"
        await ctx.send("Your trade request has been updated with the new information.")

        admin = await self.bot.fetch_user(self.admin_id)
        admin_message = await admin.fetch_message(trade_request.admin_message_id)
        await self.update_admin_message(admin_message, trade_request, ctx.author)

    async def update_admin_message(self, message, trade_request, user):
        await message.edit(embed=self.create_admin_embed(user, trade_request))

    def create_admin_embed(self, user, trade_request):
        embed = discord.Embed(
            title=f"Trade Request from {user.name}",
            description=trade_request.message,
            color=discord.Color.blue()
        )
        embed.add_field(name="Status", value=trade_request.status.name)
        return embed

    async def send_trade_proposals(self, user_id, proposals):
        trade_request = self.trade_requests.get(user_id)
        if not trade_request:
            return

        channel = self.bot.get_channel(trade_request.channel_id)
        user = await self.bot.fetch_user(user_id)
        trade_request.proposals = proposals
        trade_request.status = TradeStatus.USER_REVIEWING

        embed = discord.Embed(
            title="Trade Proposals",
            description=f"{user.mention}, the admin has sent you the following trade proposals. Please choose one or decline all.",
            color=discord.Color.green()
        )
        for i, proposal in enumerate(proposals, 1):
            embed.add_field(name=f"Proposal {i}", value=proposal, inline=False)

        view = discord.ui.View()
        for i in range(len(proposals)):
            view.add_item(discord.ui.Button(style=discord.ButtonStyle.primary, label=f"Accept Proposal {i+1}", custom_id=f"accept_{i}"))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.red, label="Decline All", custom_id="decline_all"))

        async def user_response_callback(interaction: discord.Interaction):
            if interaction.user.id != user_id:
                await interaction.response.send_message("You are not authorized to respond to this trade proposal.", ephemeral=True)
                return
            await self.handle_user_response(interaction, user_id)

        for item in view.children:
            item.callback = user_response_callback

        await channel.send(embed=embed, view=view)

        admin = await self.bot.fetch_user(self.admin_id)
        admin_message = await admin.fetch_message(trade_request.admin_message_id)
        await self.update_admin_message(admin_message, trade_request, user)

    async def handle_user_response(self, interaction: discord.Interaction, user_id: int):
        trade_request = self.trade_requests.get(user_id)

        if not trade_request:
            await interaction.response.send_message("This trade request no longer exists.", ephemeral=True)
            return

        custom_id = interaction.data['custom_id']
        action = custom_id.split('_')[0]

        admin = await self.bot.fetch_user(self.admin_id)

        if action == "accept":
            proposal_index = int(custom_id.split('_')[1])
            accepted_proposal = trade_request.proposals[proposal_index]
            await interaction.response.send_message(f"You've accepted the following proposal:\n{accepted_proposal}")
            await admin.send(f"{interaction.user.name} has accepted the following trade proposal:\n{accepted_proposal}")
            trade_request.status = TradeStatus.CLOSED
        elif action == "decline":
            await interaction.response.send_message("You've declined all trade proposals.")
            await admin.send(f"{interaction.user.name} has declined all trade proposals.")
            trade_request.status = TradeStatus.CLOSED

        if trade_request.status == TradeStatus.CLOSED:
            del self.trade_requests[user_id]

        admin_message = await admin.fetch_message(trade_request.admin_message_id)
        await self.update_admin_message(admin_message, trade_request, interaction.user)

        # Create a new view with disabled buttons
        new_view = discord.ui.View()
        for component in interaction.message.components:
            for button in component.children:
                new_button = discord.ui.Button(
                    style=button.style,
                    label=button.label,
                    custom_id=button.custom_id,
                    disabled=True
                )
                new_view.add_item(new_button)

        # Edit the message with the new view
        await interaction.message.edit(view=new_view)

class TradeProposalModal(discord.ui.Modal, title="Trade Proposals"):
    def __init__(self, cog, user_id):
        super().__init__()
        self.cog = cog
        self.user_id = user_id
        self.proposals = []

        for i in range(1, 4):  # Allow up to 3 proposals
            self.add_item(discord.ui.TextInput(label=f"Proposal {i}", required=False, style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction: discord.Interaction):
        self.proposals = [proposal.value for proposal in self.children if proposal.value]
        await self.cog.send_trade_proposals(self.user_id, self.proposals)
        await interaction.response.send_message("Trade proposals sent to the user.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NBA2KCog(bot))
    print("🏀 NBA2KCog added")