import discord
from discord.ext import commands
import requests
import os
from config import FREE_ASTROLOGY_API_KEY

class AstrologyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = 'https://api.freeastrologyapi.com'
        self.api_key = FREE_ASTROLOGY_API_KEY
        print("AstrologyCog initialized with base URL and API key")

    # Function to get headers for API requests
    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        print(f"Generated headers: {headers}")
        return headers

    # Example usage: !horoscope aries
    @commands.command(name='horoscope', help='Get your daily horoscope')
    async def horoscope(self, ctx, sign: str):
        # Fetches the daily horoscope for a given zodiac sign
        print(f"Received command to fetch horoscope for sign: {sign}")
        url = f'{self.base_url}/horoscope'
        params = {'sign': sign}
        print(f"Fetching horoscope for sign: {sign} with URL: {url} and params: {params}")
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            horoscope = response.json().get('horoscope')
            await ctx.send(f"Today's horoscope for {sign.capitalize()}:\n{horoscope}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch horoscope: {e}")
            await ctx.send("Couldn't retrieve horoscope. Please try again later.")

    # Example usage: !zodiac 3 21
    @commands.command(name='zodiac', help='Get your zodiac sign based on your birth date')
    async def zodiac(self, ctx, month: int, day: int):
        # Determines the zodiac sign based on the birth month and day
        print(f"Received command to determine zodiac sign for month: {month} and day: {day}")
        url = f'{self.base_url}/zodiac'
        params = {'month': month, 'day': day}
        print(f"Determining zodiac sign for month: {month} and day: {day} with URL: {url} and params: {params}")
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            sign = response.json().get('sign')
            await ctx.send(f"The zodiac sign for {month}/{day} is {sign}.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to determine zodiac sign: {e}")
            await ctx.send("Couldn't determine zodiac sign. Please try again later.")

    # Example usage: !compatibility aries libra
    @commands.command(name='compatibility', help='Get compatibility between two zodiac signs')
    async def compatibility(self, ctx, sign1: str, sign2: str):
        # Fetches compatibility information between two zodiac signs
        print(f"Received command to fetch compatibility between {sign1} and {sign2}")
        url = f'{self.base_url}/compatibility'
        params = {'sign1': sign1, 'sign2': sign2}
        print(f"Fetching compatibility between {sign1} and {sign2} with URL: {url} and params: {params}")
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            compatibility = response.json().get('compatibility')
            await ctx.send(f"Compatibility between {sign1.capitalize()} and {sign2.capitalize()}:\n{compatibility}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch compatibility: {e}")
            await ctx.send("Couldn't retrieve compatibility information. Please try again later.")

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(AstrologyCog(bot))
    print("🔮 AstrologyCog added")
