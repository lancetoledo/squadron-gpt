import json
import logging
import discord
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from enum import Enum
from typing import Dict, List
import asyncio
import re
from datetime import datetime, timedelta
import os
import firebase_admin
from firebase_admin import credentials, firestore


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
        self.db = None
        self.nba2k_data = None
        self.load_local_data()  # Load local data in __init__
        
    def load_local_data(self):
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'MyNBA.json')
            with open(json_path, 'r') as f:
                self.nba2k_data = json.load(f)
            logging.info("Local JSON data loaded successfully")
        except Exception as e:
            logging.error(f"Error loading local JSON data: {e}")
            self.nba2k_data = None

    async def cog_load(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(current_dir, '..', 'data', 'firebase', 'nba-goat-calculator-e4983-firebase-adminsdk-jbrx7-32c0936656.json')
            
            if not os.path.exists(key_path):
                logging.error(f"Firebase key file not found at {key_path}")
                return

            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logging.info("Firebase initialized successfully")
            
            # Start the Firebase listener
            players_ref = self.db.collection('players')
            
            def on_snapshot(doc_snapshot, changes, read_time):
                for change in changes:
                    if change.type.name == 'MODIFIED':
                        asyncio.create_task(self.handle_player_update(change.document))
            
            players_ref.on_snapshot(on_snapshot)
            logging.info("Firebase listener set up successfully")
        except Exception as e:
            logging.error(f"Error initializing Firebase: {e}")
            self.db = None



    async def handle_player_update(self, player_doc):
        player_data = player_doc.to_dict()
        channel = self.bot.get_channel(self.nba2k_channel_id)
        
        old_goat_points = player_data.get('old_Total GOAT Points', 0)
        new_goat_points = player_data.get('Total GOAT Points', 0)
        
        if new_goat_points > old_goat_points:
            await channel.send(f"🏆 {player_data['Player Name']} has earned {new_goat_points - old_goat_points} new G.O.A.T points! Their total is now {new_goat_points}.")
        
        old_achievements = set(player_data.get('old_Achievements', []))
        new_achievements = set(player_data.get('Achievements', []))
        earned_achievements = new_achievements - old_achievements
        
        for achievement in earned_achievements:
            await channel.send(f"🎉 Congratulations to {player_data['Player Name']} for earning the '{achievement}' achievement!")
        
        # Update the 'old' fields for future comparisons
        player_doc.reference.update({
            'old_Total GOAT Points': new_goat_points,
            'old_Achievements': list(new_achievements)
        })

    def get_team_data(self, user_id):
        if not self.nba2k_data or 'teams' not in self.nba2k_data:
            logging.error("NBA2K data is not properly loaded")
            return None
        
        for team in self.nba2k_data['teams']:
            if 'staff' in team and 'gm' in team['staff'] and 'userid' in team['staff']['gm']:
                if team['staff']['gm']['userid'] == user_id:
                    return team
        return None

    def get_player_info(self, user_id):
        logging.info(f"Fetching player info for user ID: {user_id}")
        firebase_data = None
        local_data = None

        # Fetch data from Firebase
        try:
            logging.info("Attempting to fetch data from Firebase")
            players_ref = self.db.collection('players')
            query = players_ref.where(filter=firestore.FieldFilter("discordId", "==", str(user_id)))
            docs = query.get()

            for doc in docs:
                firebase_data = doc.to_dict()
                logging.info(f"Firebase data fetched: {firebase_data}")
                break
        except Exception as e:
            logging.error(f"Error fetching data from Firebase: {str(e)}", exc_info=True)

        # If Firebase data is not available, proceed with local data
        if not firebase_data:
            logging.warning("Firebase data not available, proceeding with local data only")

        # Fetch data from local JSON
        logging.info("Fetching data from local JSON")
        team_data = self.get_team_data(user_id)
        if team_data:
            gm_name = team_data['staff']['gm']['name']
            for player in team_data['roster']:
                if player['name'] == gm_name:
                    local_data = player
                    logging.info(f"Local data fetched: {local_data}")
                    break

        # Combine the data
        if firebase_data and local_data:
            logging.info("Combining Firebase and local data")
            combined_data = {**local_data, **firebase_data}
            logging.info(f"Combined data: {combined_data}")
            return combined_data
        elif firebase_data:
            logging.info("Returning Firebase data only")
            return firebase_data
        elif local_data:
            logging.info("Returning local data only")
            return local_data
        
        logging.warning("No player data found")
        return None

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

    @commands.command(name='myplayer', help='Get detailed information about your player')
    async def my_player(self, ctx):
        logging.info(f"my_player command invoked by user ID: {ctx.author.id}")
        
        try:
            player_info = self.get_player_info(ctx.author.id)
            logging.info(f"Player info retrieved: {player_info}")
            
            if player_info:
                logging.info("Creating player embed")
                embed = self.create_player_embed(player_info)
                logging.info(f"Embed created: {embed.to_dict()}")
                
                embed.set_footer(text="Player Info v2.2")  # Updated version
                view = self.create_stats_button(ctx.author.id)
                await ctx.send(embed=embed, view=view)
            else:
                logging.warning(f"No player information found for user ID: {ctx.author.id}")
                await ctx.send("No player information found. Please contact an admin if you believe this is an error.")
        
        except Exception as e:
            logging.error(f"Error in my_player command: {str(e)}")
            await ctx.send("An error occurred while retrieving your player information. Please try again later.")

    def create_player_embed(self, player):
        logging.info(f"Creating embed for player: {player.get('Player Name', player.get('name', 'Unknown'))}")
        embed = discord.Embed(
            title=f"{player.get('Player Name', player.get('name', 'Unknown'))} - {player.get('position', 'N/A')}",
            color=discord.Color.blue()
        )
        
        # GOAT Points and Tier (from Firebase)
        goat_points = player.get('Total GOAT Points', 0)
        tier = player.get('Tier', 'N/A')
        logging.info(f"GOAT Points: {goat_points}, Tier: {tier}")
        embed.add_field(name="🏆 GOAT Points", value=f"{goat_points:,}", inline=True)
        embed.add_field(name="🏅 Tier", value=tier, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Empty field for alignment
        
        # Player attributes
        embed.add_field(name="👤 Overall", value=player.get('overall', 'N/A'), inline=True)
        embed.add_field(name="🎂 Age", value=player.get('age', 'N/A'), inline=True)
        embed.add_field(name="🏀 Years in NBA", value=player.get('yearsInNBA', 'N/A'), inline=True)
        
        embed.add_field(name="📈 Potential", value=player.get('potential', 'N/A'), inline=True)
        if 'contract' in player:
            embed.add_field(name="📄 Contract Years Left", value=player['contract'].get('yearsLeft', 'N/A'), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Empty field for alignment

        if 'skills' in player:
            embed.add_field(name="💪 Skills", value=', '.join(player['skills']), inline=False)

        # Completed achievements (from Firebase)
        completed_achievements = [
            achievement for achievement, value in player.get('Achievements', {}).items()
            if value is True or (isinstance(value, (int, float)) and value > 0)
        ]
        if completed_achievements:
            achievements_text = ", ".join(completed_achievements[:5])
            if len(completed_achievements) > 5:
                achievements_text += f", and {len(completed_achievements) - 5} more"
            embed.add_field(name="🏆 Completed Achievements", value=achievements_text, inline=False)

        # Narratives and rivals (from local JSON)
        if player.get('narratives'):
            embed.add_field(name="📖 Narratives", value='\n'.join(player['narratives']), inline=False)
        if player.get('rivals'):
            embed.add_field(name="⚔️ Rivals", value=', '.join(player['rivals']), inline=False)

        logging.info(f"Final embed: {embed.to_dict()}")
        return embed

    def create_stats_button(self, user_id):
        logging.info(f"Creating stats button for user ID: {user_id}")
        view = View()
        button = Button(style=ButtonStyle.primary, label="View Detailed Stats", custom_id=f"stats_{user_id}")
        button.callback = self.stats_button_callback
        view.add_item(button)
        return view

    async def stats_button_callback(self, interaction: discord.Interaction):
        logging.info(f"Stats button clicked by user ID: {interaction.user.id}")
        custom_id = interaction.data['custom_id']
        user_id = int(custom_id.split('_')[1])
        if interaction.user.id != user_id:
            await interaction.response.send_message("You can only view your own stats.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        player_info = self.get_player_info(user_id)
        if not player_info:
            await interaction.followup.send("Stats not available for your player.")
            return

        embed = discord.Embed(
            title=f"{player_info.get('Player Name', player_info.get('name', 'Unknown'))}'s Detailed Stats",
            color=discord.Color.green()
        )
        
        if 'stats' in player_info:
            stats = player_info['stats']
            embed.add_field(
                name="🏀 Scoring",
                value=f"PPG: {stats.get('ppg', 'N/A')}\n"
                    f"FG%: {stats.get('fgp', 'N/A')}%\n"
                    f"3P%: {stats.get('tpp', 'N/A')}%\n"
                    f"FT%: {stats.get('ftp', 'N/A')}%",
                inline=True
            )
            embed.add_field(
                name="📊 Other Stats",
                value=f"RPG: {stats.get('rpg', 'N/A')}\n"
                    f"APG: {stats.get('apg', 'N/A')}\n"
                    f"SPG: {stats.get('spg', 'N/A')}\n"
                    f"BPG: {stats.get('bpg', 'N/A')}",
                inline=True
            )
        else:
            embed.description = "No detailed stats available for this player."

        logging.info(f"Sending detailed stats embed: {embed.to_dict()}")
        await interaction.followup.send(embed=embed)
    
    @commands.command(name='myteam', help='Get information about your team')
    async def my_team(self, ctx):
        team_info = self.get_team_data(ctx.author.id)
        if team_info:
            embed = self.create_team_embed(team_info)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have a team in this league. Please contact an admin if you believe this is an error.")

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
        
        # Parse and format cap space
        cap_space = team_data['team']['capSpace']
        # Extract the numeric value and convert to float
        cap_value = float(re.sub(r'[^\d.]', '', cap_space))
        # Format the cap space value
        formatted_cap = f"${cap_value:.2f}M"
        embed.add_field(name="Cap Space", value=formatted_cap, inline=True)
        
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
        player_info = self.get_player_info(ctx.author.id)
        if not player_info or 'stats' not in player_info:
            await ctx.send("Stats not available for your player.")
            return

        stats = player_info['stats']
        embed = discord.Embed(title=f"{player_info['name']}'s Detailed Stats", color=discord.Color.green())
        embed.add_field(name="Scoring", value=f"PPG: {stats['ppg']}\nFG%: {stats['fgp']}%\n3P%: {stats['tpp']}%\nFT%: {stats['ftp']}%", inline=True)
        embed.add_field(name="Other", value=f"RPG: {stats['rpg']}\nAPG: {stats['apg']}\nSPG: {stats['spg']}\nBPG: {stats['bpg']}", inline=True)
        
        # You can add more detailed stats here

        await ctx.send(embed=embed)

    @commands.command(name='myattributes', help='Get your player attributes')
    async def my_attributes(self, ctx):
        await self.relay_to_admin(ctx, "player attributes")

    @commands.command(name='leaderboard', help='View the G.O.A.T points leaderboard')
    async def leaderboard(self, ctx):
        try:
            # Use a simple string for the field name
            total_goat_points_field = 'Total GOAT Points'
            
            print(f"Attempting to query Firestore with field: {total_goat_points_field}")
            
            # Fetch all players and sort them in Python
            players = self.db.collection('players').get()
            
            # Sort players by GOAT points
            sorted_players = sorted(
                players, 
                key=lambda x: x.to_dict().get(total_goat_points_field, 0),
                reverse=True
            )[:10]  # Get top 10
            
            embed = discord.Embed(title="G.O.A.T Points Leaderboard", color=discord.Color.gold())
            
            for i, player in enumerate(sorted_players, 1):
                player_data = player.to_dict()
                print(f"Player data: {player_data}")  # Debug print
                
                goat_points = player_data.get(total_goat_points_field, 0)
                player_name = player_data.get('Player Name', 'Unknown Player')
                
                embed.add_field(
                    name=f"{i}. {player_name}", 
                    value=f"{goat_points:,} points", 
                    inline=False
                )

            if not sorted_players:
                embed.description = "No players found in the leaderboard."

            await ctx.send(embed=embed)
        
        except Exception as e:
            error_message = f"An error occurred while fetching the leaderboard: {str(e)}"
            await ctx.send(error_message)
            print(f"Leaderboard Error: {error_message}")
            
            # Print the full traceback for debugging
            traceback.print_exc()
            
            # Additional debug information
            print(f"Firestore database: {self.db}")
            print(f"Players collection: {self.db.collection('players')}")
            
            # Try to print a sample document
            try:
                sample_doc = next(self.db.collection('players').limit(1).stream())
                print(f"Sample document: {sample_doc.to_dict()}")
            except StopIteration:
                print("No documents found in the 'players' collection.")
            except Exception as sample_error:
                print(f"Error fetching sample document: {str(sample_error)}")

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
        view.add_item(discord.ui.Button(style=ButtonStyle.green, label="Approve", custom_id=f"approve_{user_id}"))
        view.add_item(discord.ui.Button(style=ButtonStyle.red, label="Deny", custom_id=f"deny_{user_id}"))
        view.add_item(discord.ui.Button(style=ButtonStyle.grey, label="Request More Info", custom_id=f"more_info_{user_id}"))
        view.add_item(discord.ui.Button(style=ButtonStyle.blurple, label="Propose Trade", custom_id=f"propose_{user_id}"))
        
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