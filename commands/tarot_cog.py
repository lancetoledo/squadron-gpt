import discord
from discord.ext import commands
import random

class TarotCard:
    def __init__(self, name, meaning_upright, meaning_reversed, image_url):
        self.name = name
        self.meaning_upright = meaning_upright
        self.meaning_reversed = meaning_reversed
        self.image_url = image_url

class TarotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tarot_deck = [
            TarotCard("The Fool", "New beginnings, innocence, free spirit", 
                      "Recklessness, risk-taking, foolishness", 
                      "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg"),
            TarotCard("The Magician", "Manifestation, resourcefulness, power", 
                      "Manipulation, poor planning, untapped talents", 
                      "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg"),
            TarotCard("The High Priestess", "Intuition, sacred knowledge, divine feminine", 
                      "Secrets, disconnected from intuition, withdrawal", 
                      "https://upload.wikimedia.org/wikipedia/commons/8/88/RWS_Tarot_02_High_Priestess.jpg"),
            TarotCard("The Empress", "Femininity, beauty, nature", 
                      "Creative block, dependence on others", 
                      "https://upload.wikimedia.org/wikipedia/commons/d/d2/RWS_Tarot_03_Empress.jpg"),
            TarotCard("The Emperor", "Authority, establishment, structure", 
                      "Domination, excessive control, lack of discipline", 
                      "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg"),
            TarotCard("The Hierophant", "Spiritual wisdom, religious beliefs, conformity", 
                      "Personal beliefs, freedom, challenging the status quo", 
                      "https://upload.wikimedia.org/wikipedia/commons/8/8d/RWS_Tarot_05_Hierophant.jpg"),
            TarotCard("The Lovers", "Love, harmony, relationships", 
                      "Self-love, disharmony, imbalance", 
                      "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_06_Lovers.jpg"),
            TarotCard("The Chariot", "Control, willpower, success", 
                      "Lack of control, opposition, lack of direction", 
                      "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg"),
            TarotCard("Strength", "Courage, bravery, confidence", 
                      "Self-doubt, weakness, insecurity", 
                      "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg"),
            TarotCard("The Hermit", "Soul searching, introspection, being alone", 
                      "Isolation, loneliness, withdrawal", 
                      "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg"),
            TarotCard("Wheel of Fortune", "Good luck, karma, life cycles", 
                      "Bad luck, resistance to change, breaking cycles", 
                      "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg"),
            TarotCard("Justice", "Fairness, truth, law", 
                      "Unfairness, lack of accountability, dishonesty", 
                      "https://upload.wikimedia.org/wikipedia/commons/e/e0/RWS_Tarot_11_Justice.jpg"),
            TarotCard("The Hanged Man", "Pause, surrender, letting go", 
                      "Delays, resistance, stalling", 
                      "https://upload.wikimedia.org/wikipedia/commons/2/2b/RWS_Tarot_12_Hanged_Man.jpg"),
            TarotCard("Death", "Endings, change, transformation", 
                      "Resistance to change, personal transformation, inner purging", 
                      "https://upload.wikimedia.org/wikipedia/commons/d/d7/RWS_Tarot_13_Death.jpg"),
            TarotCard("Temperance", "Balance, moderation, patience", 
                      "Imbalance, excess, lack of long-term vision", 
                      "https://upload.wikimedia.org/wikipedia/commons/f/f8/RWS_Tarot_14_Temperance.jpg"),
            TarotCard("The Devil", "Shadow self, attachment, addiction", 
                      "Releasing limiting beliefs, exploring dark thoughts, detachment", 
                      "https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg"),
            TarotCard("The Tower", "Sudden change, upheaval, chaos", 
                      "Avoidance of disaster, fear of change", 
                      "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg"),
            TarotCard("The Star", "Hope, faith, purpose", 
                      "Lack of faith, despair, discouragement", 
                      "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg"),
            TarotCard("The Moon", "Illusion, fear, anxiety", 
                      "Release of fear, repressed emotion, inner confusion", 
                      "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg"),
            TarotCard("The Sun", "Positivity, fun, success", 
                      "Inner child, feeling down, overly optimistic", 
                      "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg"),
            TarotCard("Judgement", "Judgement, rebirth, inner calling", 
                      "Self-doubt, inner critic, ignoring the call", 
                      "https://upload.wikimedia.org/wikipedia/commons/d/dd/RWS_Tarot_20_Judgement.jpg"),
            TarotCard("The World", "Completion, integration, accomplishment", 
                      "Seeking closure, short-cuts, delays", 
                      "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg"),
            TarotCard("Ace of Wands", "Inspiration, new opportunities, growth", 
                    "Lack of direction, delays, missed opportunity", 
                    "https://upload.wikimedia.org/wikipedia/commons/1/11/Wands01.jpg"),
            TarotCard("Two of Wands", "Future planning, progress, decisions", 
                    "Fear of unknown, lack of planning, staying put", 
                    "https://upload.wikimedia.org/wikipedia/commons/0/0f/Wands02.jpg"),
            TarotCard("Three of Wands", "Expansion, foresight, overseas opportunities", 
                    "Obstacles, delays, frustration", 
                    "https://upload.wikimedia.org/wikipedia/commons/f/ff/Wands03.jpg"),
            TarotCard("Four of Wands", "Celebration, harmony, homecoming", 
                    "Personal celebration, inner harmony, conflict with others", 
                    "https://upload.wikimedia.org/wikipedia/commons/a/a4/Wands04.jpg"),
            TarotCard("Five of Wands", "Conflict, competition, tension", 
                    "Avoiding conflict, respecting differences", 
                    "https://upload.wikimedia.org/wikipedia/commons/9/9d/Wands05.jpg"),
            TarotCard("Six of Wands", "Success, public recognition, progress", 
                    "Egotism, lack of recognition, fall from grace", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/3b/Wands06.jpg"),
            TarotCard("Seven of Wands", "Challenge, competition, protection", 
                    "Exhaustion, giving up, overwhelmed", 
                    "https://upload.wikimedia.org/wikipedia/commons/e/e4/Wands07.jpg"),
            TarotCard("Eight of Wands", "Speed, action, movement", 
                    "Delays, frustration, resisting change", 
                    "https://upload.wikimedia.org/wikipedia/commons/6/6b/Wands08.jpg"),
            TarotCard("Nine of Wands", "Resilience, courage, persistence", 
                    "Ongoing battle, weary, lack of fight", 
                    "https://upload.wikimedia.org/wikipedia/commons/4/4d/Tarot_Nine_of_Wands.jpg"),
            TarotCard("Ten of Wands", "Burden, responsibility, hard work", 
                    "Avoiding responsibility, taking on too much, burnout", 
                    "https://upload.wikimedia.org/wikipedia/commons/0/0b/Wands10.jpg"),
            TarotCard("Page of Wands", "Inspiration, ideas, discovery", 
                    "Lack of direction, procrastination, newly formed ideas", 
                    "https://upload.wikimedia.org/wikipedia/commons/6/6a/Wands11.jpg"),
            TarotCard("Knight of Wands", "Energy, passion, inspired action", 
                    "Haste, scattered energy, delays", 
                    "https://upload.wikimedia.org/wikipedia/commons/1/16/Wands12.jpg"),
            TarotCard("Queen of Wands", "Courage, confidence, independence", 
                    "Self-respect, introverted, re-establish sense of self", 
                    "https://upload.wikimedia.org/wikipedia/commons/0/0d/Wands13.jpg"),
            TarotCard("King of Wands", "Natural leader, vision, entrepreneur", 
                    "Impulsiveness, overbearing, unachievable expectations", 
                    "https://upload.wikimedia.org/wikipedia/commons/c/ce/Wands14.jpg"),
            TarotCard("Ace of Cups", "Love, new relationships, compassion", 
                    "Self-love, intuition, repressed emotions", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/36/Cups01.jpg"),
            TarotCard("Two of Cups", "Unified love, partnership, attraction", 
                    "Self-love, break-ups, disharmony", 
                    "https://upload.wikimedia.org/wikipedia/commons/f/f8/Cups02.jpg"),
            TarotCard("Three of Cups", "Celebration, friendship, creativity", 
                    "Independence, alone time, hardcore partying", 
                    "https://upload.wikimedia.org/wikipedia/commons/7/7a/Cups03.jpg"),
            TarotCard("Four of Cups", "Meditation, contemplation, apathy", 
                    "Retreat, withdrawal, checking in for alignment", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/35/Cups04.jpg"),
            TarotCard("Five of Cups", "Regret, failure, disappointment", 
                    "Personal setbacks, self-forgiveness, moving on", 
                    "https://upload.wikimedia.org/wikipedia/commons/d/d7/Cups05.jpg"),
            TarotCard("Six of Cups", "Revisiting the past, childhood memories, innocence", 
                    "Living in the past, forgiveness, lacking playfulness", 
                    "https://upload.wikimedia.org/wikipedia/commons/1/17/Cups06.jpg"),
            TarotCard("Seven of Cups", "Opportunities, choices, illusion", 
                    "Lack of purpose, diversion, confusion", 
                    "https://upload.wikimedia.org/wikipedia/commons/a/ae/Cups07.jpg"),
            TarotCard("Eight of Cups", "Disappointment, abandonment, withdrawal", 
                    "Trying one more time, indecision, aimless drifting", 
                    "https://upload.wikimedia.org/wikipedia/commons/6/60/Cups08.jpg"),
            TarotCard("Nine of Cups", "Contentment, satisfaction, gratitude", 
                    "Inner happiness, materialism, dissatisfaction", 
                    "https://upload.wikimedia.org/wikipedia/commons/2/24/Cups09.jpg"),
            TarotCard("Ten of Cups", "Divine love, blissful relationships, harmony", 
                    "Disconnection, misaligned values, struggling relationships", 
                    "https://upload.wikimedia.org/wikipedia/commons/8/84/Cups10.jpg"),
            TarotCard("Page of Cups", "Creative opportunities, intuitive messages, curiosity", 
                    "New ideas, doubting intuition, creative blocks", 
                    "https://upload.wikimedia.org/wikipedia/commons/a/ad/Cups11.jpg"),
            TarotCard("Knight of Cups", "Romantic proposals, offers, invitations", 
                    "Overactive imagination, unrealistic, jealous", 
                    "https://upload.wikimedia.org/wikipedia/commons/f/fa/Cups12.jpg"),
            TarotCard("Queen of Cups", "Compassion, caring, emotionally stable", 
                    "Inner feelings, self-care, co-dependency", 
                    "https://upload.wikimedia.org/wikipedia/commons/6/62/Cups13.jpg"),
            TarotCard("King of Cups", "Emotional balance, control, generosity", 
                    "Emotional manipulation, moodiness, volatility", 
                    "https://upload.wikimedia.org/wikipedia/commons/0/04/Cups14.jpg"),
            TarotCard("Ace of Swords", "Breakthrough, clarity, sharp mind", 
                    "Confusion, miscommunication, hostility", 
                    "https://upload.wikimedia.org/wikipedia/commons/1/1a/Swords01.jpg"),
            TarotCard("Two of Swords", "Difficult decisions, weighing up options, an impasse", 
                    "Indecision, confusion, information overload", 
                    "https://upload.wikimedia.org/wikipedia/commons/9/9e/Swords02.jpg"),
            TarotCard("Three of Swords", "Heartbreak, emotional pain, sorrow", 
                    "Negative self-talk, releasing pain, optimism", 
                    "https://upload.wikimedia.org/wikipedia/commons/0/02/Swords03.jpg"),
            TarotCard("Four of Swords", "Rest, relaxation, contemplation", 
                    "Restlessness, burnout, stress", 
                    "https://upload.wikimedia.org/wikipedia/commons/b/bf/Swords04.jpg"),
            TarotCard("Five of Swords", "Conflict, disagreements, competition", 
                    "Reconciliation, making amends, past resentment", 
                    "https://upload.wikimedia.org/wikipedia/commons/2/23/Swords05.jpg"),
            TarotCard("Six of Swords", "Transition, change, rite of passage", 
                    "Resistance to change, unfinished business", 
                    "https://upload.wikimedia.org/wikipedia/commons/2/29/Swords06.jpg"),
            TarotCard("Seven of Swords", "Betrayal, deception, getting away with something", 
                    "Imposter syndrome, keeping secrets, lying to oneself", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/34/Swords07.jpg"),
            TarotCard("Eight of Swords", "Negative thoughts, self-imposed restriction, imprisonment", 
                    "Open to new perspectives, release, facing fears", 
                    "https://upload.wikimedia.org/wikipedia/commons/a/a7/Swords08.jpg"),
            TarotCard("Nine of Swords", "Anxiety, worry, fear", 
                    "Inner turmoil, deep-seated fears, secrets", 
                    "https://upload.wikimedia.org/wikipedia/commons/2/2f/Swords09.jpg"),
            TarotCard("Ten of Swords", "Painful endings, betrayal, loss", 
                    "Recovery, regeneration, resisting an inevitable end", 
                    "https://upload.wikimedia.org/wikipedia/commons/d/d4/Swords10.jpg"),
            TarotCard("Page of Swords", "New ideas, curiosity, thirst for knowledge", 
                    "Self-expression, all talk and no action, haphazard action", 
                    "https://upload.wikimedia.org/wikipedia/commons/4/4c/Swords11.jpg"),
            TarotCard("Knight of Swords", "Ambitious, action-oriented, driven", 
                    "Restless, unfocused, impulsive", 
                    "https://upload.wikimedia.org/wikipedia/commons/b/b0/Swords12.jpg"),
            TarotCard("Queen of Swords", "Independent, unbiased judgment, clear boundaries", 
                    "Overly emotional, easily influenced, cold-hearted", 
                    "https://upload.wikimedia.org/wikipedia/commons/d/d4/Swords13.jpg"),
            TarotCard("King of Swords", "Mental clarity, intellectual power, authority", 
                    "Manipulative, tyrannical, abusive", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/33/Swords14.jpg"),
            TarotCard("Ace of Pentacles", "Manifestation, new financial opportunity, prosperity", 
                    "Lost opportunity, lack of planning, foresight", 
                    "https://upload.wikimedia.org/wikipedia/commons/f/fd/Pents01.jpg"),
            TarotCard("Two of Pentacles", "Balance, adaptability, time management", 
                    "Disorganization, financial disarray, overcommitment", 
                    "https://upload.wikimedia.org/wikipedia/commons/9/9f/Pents02.jpg"),
            TarotCard("Three of Pentacles", "Teamwork, collaboration, learning", 
                    "Disharmony, misalignment, working alone", 
                    "https://upload.wikimedia.org/wikipedia/commons/4/42/Pents03.jpg"),
            TarotCard("Four of Pentacles", "Saving money, security, conservatism", 
                    "Greed, materialism, self-protection", 
                    "https://upload.wikimedia.org/wikipedia/commons/3/35/Pents04.jpg"),
            TarotCard("Five of Pentacles", "Financial loss, poverty, isolation", 
                    "Recovery from loss, spiritual poverty", 
                    "https://upload.wikimedia.org/wikipedia/commons/9/96/Pents05.jpg"),
            TarotCard("Six of Pentacles", "Giving, receiving, sharing wealth", 
                    "Self-care, unpaid debts, one-sided charity", 
                    "https://upload.wikimedia.org/wikipedia/commons/a/a6/Pents06.jpg"),
            TarotCard("Seven of Pentacles", "Long-term view, sustainable results, perseverance", 
                    "Lack of long-term vision, limited success or reward", 
                    "https://upload.wikimedia.org/wikipedia/commons/6/6a/Pents07.jpg"),
            TarotCard("Eight of Pentacles", "Apprenticeship, repetitive tasks, mastery", 
                    "Self-development, perfectionism, misdirected activity", 
                    "https://upload.wikimedia.org/wikipedia/commons/4/49/Pents08.jpg"),
            TarotCard("Nine of Pentacles", "Abundance, luxury, self-sufficiency", 
                    "Self-worth, over-investment in work, hustling", 
                    "https://upload.wikimedia.org/wikipedia/commons/f/f0/Pents09.jpg"),
            TarotCard("Ten of Pentacles", "Wealth, financial security, family", 
                    "Financial failure, loss, lack of stability", 
                    "https://upload.wikimedia.org/wikipedia/commons/4/42/Pents10.jpg"),
            TarotCard("Page of Pentacles", "Manifestation, financial opportunity, new job", 
                    "Lack of progress, procrastination, learn from failure", 
                    "https://upload.wikimedia.org/wikipedia/commons/e/ec/Pents11.jpg"),
            TarotCard("Knight of Pentacles", "Hard work, productivity, routine", 
                    "Self-discipline, boredom, feeling 'stuck'", 
                    "https://upload.wikimedia.org/wikipedia/commons/d/d5/Pents12.jpg"),
            TarotCard("Queen of Pentacles", "Practical, nurturing, providing financially", 
                    "Financial independence, self-care, work-home conflict", 
                    "https://upload.wikimedia.org/wikipedia/commons/8/88/Pents13.jpg"),
            TarotCard("King of Pentacles", "Wealth, business, leadership", 
                    "Financially inept, obsessed with wealth, stubborn", 
                    "https://upload.wikimedia.org/wikipedia/commons/1/1c/Pents14.jpg")
        ]


    @commands.command()
    async def draw_card(self, ctx):
        card = random.choice(self.tarot_deck)
        is_upright = random.choice([True, False])
        
        embed = discord.Embed(title="Tarot Card Reading", color=0x7289DA)
        embed.set_image(url=card.image_url)
        embed.add_field(name="Card", value=card.name, inline=False)
        embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
        embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def timeline_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 3)
        positions = ["Past", "Present", "Future"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    @commands.command()
    async def cross_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 5)
        positions = ["Present", "Challenge", "Past", "Future", "Outcome"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TarotCog(bot))
    print("🎴 TarotCog added")