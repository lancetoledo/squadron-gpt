import discord
from discord.ext import commands
import random
import openai
import asyncio

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

    # Example: !draw_card
    # Draw a single card and provide quick insight or answer to a simple question.
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

    # Example: !timeline_spread
    # The timeline spread provides insight into the past, present, and future of a situation.
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

    # Example: !cross_spread
    # The cross spread offers an analysis of a specific question or situation, focusing on various factors influencing it.
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

    # Example: !celtic_cross_spread
    # The Celtic Cross spread provides a detailed examination of a specific question or situation, considering multiple aspects and influences.
    @commands.command()
    async def celtic_cross_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 10)
        positions = ["Present", "Challenge", "Past", "Future", "Goal", "Immediate Future", "Self-Perception", "External Influences", "Hopes and Fears", "Outcome"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    # Example: !horseshoe_spread
    # The horseshoe spread offers insights into the present situation, obstacles, external influences, and possible outcomes.
    @commands.command()
    async def horseshoe_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 7)
        positions = ["Past", "Present", "Hidden Influences", "Obstacles", "External Influences", "Suggested Actions", "Outcome"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    # Example: !five_card_spread
    # The five-card spread provides a deeper look into a situation, exploring causes, hidden factors, advice, and potential outcomes.
    @commands.command()
    async def five_card_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 5)
        positions = ["Present Situation", "Causes", "Hidden Factors", "Advice", "Likely Outcome"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    # Example: !seven_card_horseshoe_spread
    # The seven-card horseshoe spread provides a detailed exploration of a situation and its various influences, offering advice and potential outcomes.
    @commands.command()
    async def seven_card_horseshoe_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 7)
        positions = ["Past", "Present", "Future", "Advice", "External Influences", "Hopes and Fears", "Outcome"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    # Example: !astrological_spread
    # The astrological spread provides insight into different aspects of life based on the twelve astrological houses.
    @commands.command()
    async def astrological_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 12)
        positions = ["Self", "Money", "Communication", "Home", "Pleasure", "Work", "Partnerships", "Shared Resources", "Philosophy", "Career", "Friendships", "Subconscious"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} House: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    # Example: !relationship_spread
    # The relationship spread provides insight into romantic relationships or partnerships, examining both parties and the relationship dynamics.
    @commands.command()
    async def relationship_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 5)
        positions = ["You", "Your Partner", "Relationship Foundation", "Current State", "Future of the Relationship"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)

    # Example: !career_path_spread
    # The career path spread provides guidance and insight into career-related questions, examining current job, challenges, skills, opportunities, and future path.
    @commands.command()
    async def career_path_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 5)
        positions = ["Current Job", "Career Challenges", "Skills and Talents", "Potential Opportunities", "Future Career Path"]
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed = discord.Embed(title=f"{position} Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
            embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)


    # New command: !tarot_card_reading
    # Perform a three-card spread reading using ChatGPT
    @commands.command()
    async def tarot_card_reading(self, ctx):
        async with ctx.typing():
            # Draw three cards
            cards = random.sample(self.tarot_deck, 3)
            positions = ["Past", "Present", "Future"]
            card_positions = [random.choice(["Upright", "Reversed"]) for _ in range(3)]
            
            # Prepare card embeds
            card_embeds = []
            for card, position, card_position in zip(cards, positions, card_positions):
                embed = discord.Embed(title=f"{position}: {card.name}", color=0x7289DA)
                embed.set_image(url=card.image_url)
                embed.add_field(name="Position", value=card_position, inline=False)
                card_embeds.append(embed)

            # Prepare the cards information for the API call
            cards_info = [f"{pos}: {card.name} ({card_pos})" 
                          for pos, card, card_pos in zip(positions, cards, card_positions)]
            
            # Prepare the context for the API call
            context = """
            You are an experienced and intuitive Tarot card reader, skilled in performing the three-card spread. Your role is to provide insightful, balanced, and thoughtful readings that help users gain new perspectives on their situations. The cards drawn for this reading are: {cards}

            Remember these key points:
            1. Approach: You approach each reading with empathy, objectivity, and an open mind. You're here to guide and offer insights, not to make definitive predictions.
            2. Three-Card Spread: You specialize in the three-card spread. Interpret the cards as Past, Present, and Future.
            3. Card Meanings: You have a deep understanding of Tarot symbolism and can interpret both the traditional and intuitive meanings of each card. Consider both upright and reversed positions as specified in {cards}.
            4. Interconnected Reading: Don't just interpret each card in isolation. Explain how the cards in {cards} relate to each other and tell a cohesive story.
            5. Ethical Considerations: Maintain high ethical standards. Avoid making absolute predictions about health, legal matters, or major life decisions. Instead, offer perspectives that empower the user to make their own choices.
            6. Language: Use clear, respectful language. Avoid being overly dramatic or fear-mongering. Frame challenges as opportunities for growth.
            7. Intuition: Trust your intuition to provide nuanced interpretations of {cards}, but always ground them in the traditional meanings of the cards.
            8. User Interaction: Encourage users to reflect on the reading and find personal meaning in the cards drawn.
            9. Scope: Stick to interpreting the three cards drawn in {cards}. Don't introduce additional cards.
            10. Closing: End the reading with a summary that ties the insights from {cards} together and offers a constructive perspective on the user's situation.

            Base your entire reading on the cards specified in {cards}.
            """.format(cards=", ".join(cards_info))

            # Make the API call to ChatGPT
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4",  # or "gpt-3.5-turbo", depending on your preference and availability
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": "Provide a Tarot card reading based on the three cards drawn."}
                ]
            )

            # Get the generated reading
            reading = response.choices[0].message['content']

            # Create the embed with the interpretation
            interpretation_embed = discord.Embed(title="Tarot Card Reading Interpretation", color=0x7289DA)
            
            # Split the reading into smaller chunks to fit within Discord's embed field limits
            chunk_size = 1024
            chunks = [reading[i:i+chunk_size] for i in range(0, len(reading), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                interpretation_embed.add_field(name=f"Reading (Part {i+1})", value=chunk, inline=False)

            interpretation_embed.set_footer(text="Remember, this reading is for entertainment purposes only. Always use your own judgment for important life decisions.")

        # Send all messages
        for embed in card_embeds:
            await ctx.send(embed=embed)
        await ctx.send(embed=interpretation_embed)

async def setup(bot):
    await bot.add_cog(TarotCog(bot))
    print("🎴 TarotCog added")
