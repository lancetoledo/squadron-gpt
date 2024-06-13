import discord
from discord.ext import commands
import requests

class TarotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_base_url = 'https://tarotapi.dev/api/v1'

    def get_random_cards(self, n=1):
        response = requests.get(f"{self.api_base_url}/cards/random?n={n}")
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print("Error: Unable to parse JSON response")
                return None
        else:
            print(f"Error: Received status code {response.status_code}")
            return None

    def get_card_by_name(self, name_short):
        response = requests.get(f"{self.api_base_url}/cards/{name_short}")
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print("Error: Unable to parse JSON response")
                return None
        else:
            print(f"Error: Received status code {response.status_code}")
            return None

    def search_cards(self, query):
        response = requests.get(f"{self.api_base_url}/cards/search?q={query}")
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print("Error: Unable to parse JSON response")
                return None
        else:
            print(f"Error: Received status code {response.status_code}")
            return None

    # Example usage: !tarot_card
    @commands.command(name='tarot_card', help='Draw a random tarot card', aliases=['draw_card'])
    async def tarot_card(self, ctx):
        cards = self.get_random_cards(1)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) > 0:
                card = cards[0]
                await ctx.send(f"You drew the {card['name']}.\nDescription: {card['desc']}")
            else:
                await ctx.send("Could not retrieve a tarot card. Please try again later.")
        else:
            await ctx.send("Could not retrieve a tarot card. Please try again later.")

    # Example usage: !tarot_spread
    @commands.command(name='tarot_spread', help='Perform a 3-card tarot spread', aliases=['three_card'])
    async def tarot_spread(self, ctx):
        cards = self.get_random_cards(3)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) == 3:
                response = []
                for i, card in enumerate(cards, start=1):
                    response.append(f"Card {i}: {card['name']}\nDescription: {card['desc']}")
                await ctx.send("\n\n".join(response))
            else:
                await ctx.send("Could not retrieve a tarot spread. Please try again later.")
        else:
            await ctx.send("Could not retrieve a tarot spread. Please try again later.")

    # Example usage: !search_tarot love
    @commands.command(name='search_tarot', help='Search tarot cards by keyword', aliases=['find_card'])
    async def search_tarot(self, ctx, *, query):
        results = self.search_cards(query)
        if results:
            print(results)  # Debug: Log the response
            if isinstance(results, list) and len(results) > 0:
                response = []
                for card in results:
                    response.append(f"{card['name']}: {card['desc']}")
                await ctx.send("\n\n".join(response))
            else:
                await ctx.send("No cards found with that keyword.")
        else:
            await ctx.send("No cards found with that keyword.")

    # Example usage: !yes_no_tarot Will I get a promotion?
    @commands.command(name='yes_no_tarot', help='Get a yes or no answer from a tarot card', aliases=['yesno'])
    async def yes_no_tarot(self, ctx, *, question):
        cards = self.get_random_cards(1)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) > 0:
                card = cards[0]
                answer = "Yes" if card['meaning_up'].lower().startswith('yes') else "No"
                await ctx.send(f"Question: {question}\nAnswer: {answer}\nCard: {card['name']}\nDescription: {card['desc']}")
            else:
                await ctx.send("Could not retrieve a tarot card. Please try again later.")
        else:
            await ctx.send("Could not retrieve a tarot card. Please try again later.")

    # Example usage: !tarot_day
    @commands.command(name='tarot_day', help='Draw the tarot card of the day', aliases=['daily_card'])
    async def tarot_day(self, ctx):
        cards = self.get_random_cards(1)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) > 0:
                card = cards[0]
                await ctx.send(f"Today's card is the {card['name']}.\nDescription: {card['desc']}")
            else:
                await ctx.send("Could not retrieve the tarot card of the day. Please try again later.")
        else:
            await ctx.send("Could not retrieve the tarot card of the day. Please try again later.")

    # Example usage: !tarot_career
    @commands.command(name='tarot_career', help='Get a career tarot card reading', aliases=['career_reading'])
    async def tarot_career(self, ctx):
        cards = self.get_random_cards(1)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) > 0:
                card = cards[0]
                await ctx.send(f"Career Reading:\nCard: {card['name']}\nDescription: {card['desc']}\nMeaning: {card['meaning_up']}")
            else:
                await ctx.send("Could not retrieve a career tarot card. Please try again later.")
        else:
            await ctx.send("Could not retrieve a career tarot card. Please try again later.")

    # Example usage: !tarot_love
    @commands.command(name='tarot_love', help='Get a love tarot card reading', aliases=['love_reading'])
    async def tarot_love(self, ctx):
        cards = self.get_random_cards(1)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) > 0:
                card = cards[0]
                await ctx.send(f"Love Reading:\nCard: {card['name']}\nDescription: {card['desc']}\nMeaning: {card['meaning_up']}")
            else:
                await ctx.send("Could not retrieve a love tarot card. Please try again later.")
        else:
            await ctx.send("Could not retrieve a love tarot card. Please try again later.")

    # Example usage: !tarot_finance
    @commands.command(name='tarot_finance', help='Get a finance tarot card reading', aliases=['finance_reading'])
    async def tarot_finance(self, ctx):
        cards = self.get_random_cards(1)
        if cards:
            print(cards)  # Debug: Log the response
            if isinstance(cards, list) and len(cards) > 0:
                card = cards[0]
                await ctx.send(f"Finance Reading:\nCard: {card['name']}\nDescription: {card['desc']}\nMeaning: {card['meaning_up']}")
            else:
                await ctx.send("Could not retrieve a finance tarot card. Please try again later.")
        else:
            await ctx.send("Could not retrieve a finance tarot card. Please try again later.")

async def setup(bot):
    await bot.add_cog(TarotCog(bot))
    print("🎴 TarotCog added")
