import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils.file_utils import load_json_files
from utils.context_management import parse_date

import sqlite3
import os
import random
import logging
import openai
import json
from config import DISCORD_TO_REAL_NAME
from utils.summarization import truncate_text
from utils.friend_utils import get_friend_data

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'birthdays.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

logger = logging.getLogger(__name__)

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'birthdays.db')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.birthday_gifs = [
            "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjhyYnZ0Z3hkOW80N3I4cDFvNjQzZG52NnBndnQ3YWgxeGk4Z3M2MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/g5R9dok94mrIvplmZd/giphy.gif",
            "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGswY2ppc3h4dmdpNXc3MnpyYWNnb2liY3o2bDE0OHd5bWd5dHkwcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l1Ku8SFqBdaV506fm/giphy.gif",
            "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGRnMXAwYXA3bzB6MTRnYm9ld2RuY2prNDBjam1lanhiNDZzdGx3dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/S5oVZIvOlYInEgDtFX/giphy.gif",
            "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWw2d2RzczJhZmdncml5M3JvbGg5cWh5OWJrOGdlejVpMjh5a21uMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mmndweRcDkkcU/giphy.gif",
            "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3FqODF5OGI1Y2o5MWM1bHh1djJ3OTRzZThhODZhdGo4MnlranI1ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IFjSbBHETzzr6GJdwW/giphy-downsized-large.gif"
        ]
        self.create_table_if_not_exists()
        self.daily_birthday_check.start() # Turn back on when you figure out how to not send another message if the message is already sent that day

    def create_table_if_not_exists(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS birthdays (
                user_id TEXT PRIMARY KEY,
                birthday TEXT,
                timezone TEXT,
                message TEXT DEFAULT NULL
            )
        ''')
        self.conn.commit()

    @tasks.loop(hours=24)
    async def daily_birthday_check(self):
        await self.bot.wait_until_ready()
        YOUR_ANNOUNCEMENT_CHANNEL_ID = 692429647245213737  # Replace with your actual channel ID
        GUILD_ID = 123456789012345678  # Replace with your actual guild ID
        BIRTHDAY_ROLE_NAME = "🎉 BIRTHDAY BITCH 🎂"  # The exact name of the birthday role

        today = datetime.now().date()
        self.cursor.execute('SELECT user_id, message FROM birthdays WHERE strftime("%m-%d", birthday) = ?', (today.strftime("%m-%d"),))
        users_with_birthday = self.cursor.fetchall()

        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Guild not found")
            return

        birthday_role = discord.utils.get(guild.roles, name=BIRTHDAY_ROLE_NAME)
        if not birthday_role:
            print(f"Role '{BIRTHDAY_ROLE_NAME}' not found")
            return

        # Debug print statement
        print(f"Users with birthdays today: {users_with_birthday}")

        for user_id, message in users_with_birthday:
            # Debug print statement
            print(f"Processing user: {user_id}, with message: {message}")

            member = guild.get_member(user_id)
            if not member:
                print(f"Member with ID {user_id} not found in the guild")
                continue

            if birthday_role in member.roles:
                print(f"User {member.name} already has the birthday role, skipping...")
                continue

            personalized_message = await self.generate_personalized_message(member)
            gif_url = random.choice(self.birthday_gifs)
            await self.send_birthday_message(member, personalized_message, gif_url, YOUR_ANNOUNCEMENT_CHANNEL_ID)

            # Assign the birthday role to the user
            await member.add_roles(birthday_role)
            print(f"Assigned birthday role to user {member.name}")

        logger.debug('Birthday announcements sent')
        print('Birthday announcements sent')


    def calculate_age(self, birthday):
        today = datetime.today()
        birth_date = datetime.strptime(birthday, "%Y-%m-%d")
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    async def generate_personalized_message(self, user):
        # Retrieve friend data
        discord_name = user.name
        friend_name = DISCORD_TO_REAL_NAME.get(discord_name, discord_name)  # Use Discord username if real name is not found
        friend_data = get_friend_data(friend_name)
        
        # Retrieve birthday from the database
        self.cursor.execute('SELECT birthday FROM birthdays WHERE user_id = ?', (user.id,))
        result = self.cursor.fetchone()
        if result:
            birthday = result[0]
            age = self.calculate_age(birthday)
        else:
            # Handle case where birthday is not found
            age = "unknown"

        # Create context for Brendan
        brendan_context = f"""
        Brendan is designed as a sassy, sarcastic chatbot, engaging users with a playful, sharp-witted manner that adapts to the personalities and interests of the user's friends.
        Brendan tailors each conversation to the friend's likes, personalities, and goals.
        This session is with {friend_name} and they are {age} years old now.
        Context: {truncate_text(json.dumps(friend_data, indent=2))}
        """

        if friend_name == "Fabio":
            brendan_context = f"""
            Brendan is extremely sarcastic, sassy but still performs its usual functionality he's just reluctant to help Fabio. Using its sharp-witted manner that adapts to the personalities and interests of the user's friends.
            Brendan tailors each conversation to the friend's likes, personalities, and goals.
            This session is with {friend_name} and they are {age} years old now.
            Context: {truncate_text(json.dumps(friend_data, indent=2))}
            """

        # Send request to Chat GPT-4o to generate message
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": brendan_context},
                {"role": "user", "content": f"Write a sincere and personalized birthday message for {friend_name} who is turning {age} and that message would make their day."}
            ]
        )
        personalized_message = response['choices'][0]['message']['content']
        return personalized_message

    async def send_birthday_message(self, user, personalized_message, gif_url, channel_id):
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            return

        # Include the @mention in the personalized message
        message_with_mention = f"{user.mention} {personalized_message}"
        
        # Send the birthday message
        await channel.send(message_with_mention)
        
        # Create an embed for the GIF
        embed = discord.Embed()
        embed.set_image(url=gif_url)
        
        # Send the GIF embed
        await channel.send(embed=embed)
        
        print(f"Sent birthday message to {user.name} in channel {channel_id}")

    @commands.group(name='birthday', help='Commands related to managing birthdays', invoke_without_command=True)
    async def birthday(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid birthday command. Use !birthday get, !birthday set, !birthday show-nearest, !birthday remove, !birthday list-birthdays, !birthday import-birthdays, or !birthday test-message.')
            logger.debug('Invalid birthday command used.')

    @birthday.command(name='import-birthdays', help='Import birthdays from friends data')
    async def import_birthdays(self, ctx):
        logger.debug('Starting import of birthdays from friends data')

        directory = os.path.join(os.path.dirname(__file__), '..', 'data')
        data = load_json_files(directory)
        friends = data.get("friends", [])

        real_name_to_discord = {v: k for k, v in DISCORD_TO_REAL_NAME.items()}

        for friend in friends:
            name = friend.get('name')
            if not name:
                logger.debug('Skipping friend with no name')
                continue

            basic_info = friend.get('basicInfo', {})
            birthday = basic_info.get('birthday')

            if not birthday:
                logger.debug(f'Skipping {name} with no birthday')
                continue

            discord_name = real_name_to_discord.get(name)
            if not discord_name:
                logger.debug(f'Skipping {name} with no matching Discord name')
                continue

            user = discord.utils.get(ctx.guild.members, name=discord_name)
            if not user:
                logger.error(f'User {discord_name} not found in the guild')
                continue

            try:
                parsed_date = parse_date(birthday)
                logger.debug(f'Parsed birthday for {name}: {parsed_date}')
            except ValueError as e:
                logger.error(f'Error parsing birthday for {name}: {e}')
                continue

            self.cursor.execute('REPLACE INTO birthdays (user_id, birthday, timezone) VALUES (?, ?, ?)', (user.id, parsed_date, 'EST'))
            self.conn.commit()
            logger.debug(f'Imported birthday for {name} ({user.id}): {parsed_date}')

        await ctx.send('Birthdays have been imported successfully.')
        logger.debug('Finished importing birthdays')


    @birthday.command(name='get', help="Get a user's birthday")
    async def get_birthday(self, ctx, user: discord.User):
        logger.debug(f'Fetching birthday for user {user.id}')
        self.cursor.execute('SELECT birthday, timezone FROM birthdays WHERE user_id = ?', (str(user.id),))
        result = self.cursor.fetchone()
        if result:
            await ctx.send(f"{user.name}'s birthday is on {result[0]} in timezone {result[1]}.")
            logger.debug(f'Fetched birthday for user {user.id}: {result}')
        else:
            await ctx.send(f"{user.name} has not set a birthday.")
            logger.debug(f'No birthday set for user {user.id}')

    @birthday.command(name='show-nearest', help='Get a list of users with upcoming birthdays')
    async def show_nearest(self, ctx):
        logger.debug('Fetching nearest upcoming birthdays')
        today = datetime.now().date()

        self.cursor.execute('SELECT user_id, birthday FROM birthdays')
        all_birthdays = self.cursor.fetchall()

        upcoming_birthdays = []
        for user_id, bday_str in all_birthdays:
            bday = datetime.strptime(bday_str, "%Y-%m-%d").date()
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday.replace(year=today.year + 1)
            upcoming_birthdays.append((user_id, bday_this_year))

        upcoming_birthdays = sorted(upcoming_birthdays, key=lambda x: x[1])

        nearest_birthdays = [user_id for user_id, bday in upcoming_birthdays if (bday - today).days < 30]

        if nearest_birthdays:
            users = [await ctx.bot.fetch_user(user_id) for user_id in nearest_birthdays]
            user_list = "\n".join([f"{user.name}" for user in users])
            await ctx.send(f"Users with upcoming birthdays:\n{user_list}")
            logger.debug(f'Nearest birthdays: {user_list}')
        else:
            await ctx.send("No upcoming birthdays in the next 30 days.")
            logger.debug('No upcoming birthdays in the next 30 days')

    @birthday.command(name='set', help='Set or update your birthday')
    async def set_birthday(self, ctx, date: str = None, timezone: str = None):
        user_id = str(ctx.author.id)

        if date is None:
            await ctx.send("You need to provide a date. Example: !birthday set 1990-05-15 UTC or !birthday set 06/10/1998 UTC")
            logger.debug(f'Date not provided by user {user_id}')
            return

        if timezone is None:
            await ctx.send("You need to provide a timezone. Example: !birthday set 1990-05-15 UTC or !birthday set 06/10/1998 UTC")
            logger.debug(f'Timezone not provided by user {user_id}')
            return

        try:
            parsed_date = parse_date(date)
        except ValueError as e:
            await ctx.send(str(e))
            logger.debug(f'Invalid date format provided by user {user_id}')
            return

        logger.debug(f'Setting birthday for user {user_id} to {parsed_date} with timezone {timezone}')
        self.cursor.execute('REPLACE INTO birthdays (user_id, birthday, timezone) VALUES (?, ?, ?)', (user_id, parsed_date, timezone))
        self.conn.commit()

        self.cursor.execute('SELECT * FROM birthdays WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        logger.debug(f'Verified write: {result}')

        await ctx.send(f"Your birthday has been set to {parsed_date} with timezone {timezone}.")
        logger.debug(f'Birthday set for user {user_id}')

    @birthday.command(name='set-message', help='Set a custom birthday message')
    async def set_message(self, ctx, *, message: str):
        user_id = str(ctx.author.id)
        logger.debug(f'Setting custom birthday message for user {user_id}')
        self.cursor.execute('UPDATE birthdays SET message = ? WHERE user_id = ?', (message, user_id))
        self.conn.commit()

        self.cursor.execute('SELECT message FROM birthdays WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        logger.debug(f'Verified message write: {result}')

        await ctx.send(f"Your custom birthday message has been set to: {message}")
        logger.debug(f'Custom birthday message set for user {user_id}')

    @birthday.command(name='remove', help='Remove your birthday information')
    async def remove_birthday(self, ctx):
        user_id = str(ctx.author.id)
        logger.debug(f'Removing birthday for user {user_id}')
        self.cursor.execute('DELETE FROM birthdays WHERE user_id = ?', (user_id,))
        self.conn.commit()
        await ctx.send("Your birthday information has been removed.")
        logger.debug(f'Birthday information removed for user {user_id}')
    
    @birthday.command(name='list-birthdays', help='List all birthdays')
    async def list_birthdays(self, ctx):
        logger.debug('Listing all birthdays')
        self.cursor.execute('SELECT user_id, birthday FROM birthdays')
        all_birthdays = self.cursor.fetchall()
        
        if all_birthdays:
            birthday_list = []
            for user_id, birthday in all_birthdays:
                user = await ctx.bot.fetch_user(user_id)
                birthday_list.append(f"{user.name}: {birthday}")
            
            await ctx.send("Birthdays:\n" + "\n".join(birthday_list))
            logger.debug(f'Listed all birthdays: {birthday_list}')
        else:
            await ctx.send("No birthdays found.")
            logger.debug('No birthdays found')

    @birthday.command(name='test-message', help='Test the birthday message for user "yenyverse"')
    async def test_message(self, ctx):
        YOUR_ANNOUNCEMENT_CHANNEL_ID = 692429647245213737  # Replace with your actual channel ID
        test_user_id = "487600607016910849"  # Replace with the actual user ID of the tester
        try:
            user = await ctx.bot.fetch_user(test_user_id)
            
            # Generate personalized birthday message
            personalized_message = await self.generate_personalized_message(user)
            
            # Select a random birthday GIF
            gif_url = random.choice(self.birthday_gifs)
            
            # Send the birthday message and GIF embed
            await self.send_birthday_message(user, personalized_message, gif_url, YOUR_ANNOUNCEMENT_CHANNEL_ID)
            
            logger.debug(f'Test birthday message sent to {user.name}')
            print(f'Test birthday message sent to {user.name}')
        except discord.errors.HTTPException as e:
            logger.error(f'Failed to send test birthday message: {e}')
            print(f'Failed to send test birthday message: {e}')

async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
    print("🎂 BirthdayCog added")
