import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils.file_utils import load_json_files
from dateutil.parser import parse
import sqlite3
import os
import asyncio
import random
import logging

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
        self.daily_birthday_check.start()

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
        today = datetime.now().date()
        self.cursor.execute('SELECT user_id, message FROM birthdays WHERE strftime("%m-%d", birthday) = ?', (today.strftime("%m-%d"),))
        users_with_birthday = self.cursor.fetchall()
        for user_id, message in users_with_birthday:
            user = await self.bot.fetch_user(user_id)
            if message:
                birthday_message = message.replace("{user}", user.mention)
            else:
                birthday_message = f"Happy Birthday, {user.mention}!"

            gif_url = random.choice(self.birthday_gifs)
            await self.bot.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(birthday_message)
            embed = discord.Embed()
            embed.set_image(url=gif_url)
            await self.bot.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(embed=embed)
        logger.debug('Birthday announcements sent')
        print('Birthday announcements sent')

    @commands.group(name='birthday', help='Commands related to managing birthdays')
    async def birthday(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid birthday command. Use !birthday get, !birthday set, !birthday show-nearest, or !birthday remove.')
            logger.debug('Invalid birthday command used.')

    @birthday.command(name='import', help='Import birthdays from friends data')
    async def import_birthdays(self, ctx):
        logger.debug('Starting import of birthdays from friends data')

        directory = os.path.join(os.path.dirname(__file__), '..', 'data')
        data = load_json_files(directory)
        friends = data.get("friends", [])

        real_name_to_discord = {v: k for k, v in DISCORD_TO_REAL_NAME.items()}

        for friend in friends:
            name = friend.get('name')
            if not name:
                continue

            basic_info = friend.get('basicInfo', {})
            birthday = basic_info.get('birthday')

            if not birthday:
                continue

            discord_name = real_name_to_discord.get(name)
            if not discord_name:
                continue

            user = discord.utils.get(ctx.guild.members, name=discord_name)
            if not user:
                logger.error(f'User {discord_name} not found in the guild')
                continue

            try:
                parsed_date = parse_date(birthday)
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

async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
    print("🎂 BirthdayCog added")
