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
                "Recklessness, risk-taking, embracing spontaneity", 
                "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg"),
        TarotCard("The Magician", "Manifestation, resourcefulness, power", 
                "Manipulation, untapped talents, missed opportunities", 
                "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg"),
        TarotCard("The High Priestess", "Intuition, sacred knowledge, divine feminine", 
                "Secrets revealed, intuitive awakening, spiritual guidance", 
                "https://upload.wikimedia.org/wikipedia/commons/8/88/RWS_Tarot_02_High_Priestess.jpg"),
        TarotCard("The Empress", "Femininity, beauty, nature", 
                "Creative block resolved, self-care, nurturing others", 
                "https://upload.wikimedia.org/wikipedia/commons/d/d2/RWS_Tarot_03_Empress.jpg"),
        TarotCard("The Emperor", "Authority, establishment, structure", 
                "Structured approach, leadership, stability restored", 
                "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg"),
        TarotCard("The Hierophant", "Spiritual wisdom, religious beliefs, conformity", 
                "Challenging traditions, personal belief system, spiritual awakening", 
                "https://upload.wikimedia.org/wikipedia/commons/8/8d/RWS_Tarot_05_Hierophant.jpg"),
        TarotCard("The Lovers", "Love, harmony, relationships", 
                "Self-love, harmony restored, alignment of values", 
                "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_06_Lovers.jpg"),
        TarotCard("The Chariot", "Control, willpower, success", 
                "Inner alignment, focused direction, overcoming obstacles", 
                "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg"),
        TarotCard("Strength", "Courage, bravery, confidence", 
                "Inner strength, self-confidence, resilience", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg"),
        TarotCard("The Hermit", "Soul searching, introspection, being alone", 
                "Inner guidance, introspective clarity, mentorship received", 
                "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg"),
        TarotCard("Wheel of Fortune", "Good luck, karma, life cycles", 
                "Change of fortune, unexpected luck, cycles completed", 
                "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg"),
        TarotCard("Justice", "Fairness, truth, law", 
                "Fair outcome, accountability, legal matters resolved", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e0/RWS_Tarot_11_Justice.jpg"),
        TarotCard("The Hanged Man", "Pause, surrender, letting go", 
                "New perspective gained, personal sacrifice, spiritual growth", 
                "https://upload.wikimedia.org/wikipedia/commons/2/2b/RWS_Tarot_12_Hanged_Man.jpg"),
        TarotCard("Death", "Endings, change, transformation", 
                "Resistance to change overcome, new beginnings, transformation embraced", 
                "https://upload.wikimedia.org/wikipedia/commons/d/d7/RWS_Tarot_13_Death.jpg"),
        TarotCard("Temperance", "Balance, moderation, patience", 
                "Inner peace, moderation achieved, spiritual harmony", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f8/RWS_Tarot_14_Temperance.jpg"),
        TarotCard("The Devil", "Shadow self, attachment, addiction", 
                "Breaking free from addiction, releasing limiting beliefs, reclaiming power", 
                "https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg"),
        TarotCard("The Tower", "Sudden change, upheaval, chaos", 
                "Avoiding disaster, releasing old ways, revelation", 
                "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg"),
        TarotCard("The Star", "Hope, faith, purpose", 
                "Renewed hope, faith restored, spiritual connection", 
                "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg"),
        TarotCard("The Moon", "Illusion, fear, anxiety", 
                "Facing fears, inner clarity, intuitive awakening", 
                "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg"),
        TarotCard("The Sun", "Positivity, fun, success", 
                "Inner child, optimism renewed, happiness", 
                "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg"),
        TarotCard("Judgement", "Judgement, rebirth, inner calling", 
                "Self-reflection, inner transformation, forgiveness", 
                "https://upload.wikimedia.org/wikipedia/commons/d/dd/RWS_Tarot_20_Judgement.jpg"),
        TarotCard("The World", "Completion, integration, accomplishment", 
                "Closure, achievement, reaching goals", 
                "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg"),
        TarotCard("Ace of Wands", "Inspiration, new opportunities, growth", 
                "New creative spark, opportunity taken, inspired action", 
                "https://upload.wikimedia.org/wikipedia/commons/1/11/Wands01.jpg"),
        TarotCard("Two of Wands", "Future planning, progress, decisions", 
                "Long-term planning, decisions made, progress assured", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0f/Wands02.jpg"),
        TarotCard("Three of Wands", "Expansion, foresight, overseas opportunities", 
                "Foresight realized, opportunities seized, expansion successful", 
                "https://upload.wikimedia.org/wikipedia/commons/f/ff/Wands03.jpg"),
        TarotCard("Four of Wands", "Celebration, harmony, homecoming", 
                "Celebrations, harmony with others, joyful reunions", 
                "https://upload.wikimedia.org/wikipedia/commons/a/a4/Wands04.jpg"),
        TarotCard("Five of Wands", "Conflict, competition, tension", 
                "Resolution of conflicts, healthy competition, cooperation", 
                "https://upload.wikimedia.org/wikipedia/commons/9/9d/Wands05.jpg"),
        TarotCard("Six of Wands", "Success, public recognition, progress", 
                "Recognition received, success maintained, progress celebrated", 
                "https://upload.wikimedia.org/wikipedia/commons/3/3b/Wands06.jpg"),
        TarotCard("Seven of Wands", "Challenge, competition, protection", 
                "Overcoming challenges, standing up for oneself, victory assured", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e4/Wands07.jpg"),
        TarotCard("Eight of Wands", "Speed, action, movement", 
                "Rapid progress, quick decisions, forward momentum", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6b/Wands08.jpg"),
        TarotCard("Nine of Wands", "Resilience, courage, persistence", 
                "Resilience tested, courage fortified, persistence rewarded", 
                "https://upload.wikimedia.org/wikipedia/commons/4/4d/Tarot_Nine_of_Wands.jpg"),
        TarotCard("Ten of Wands", "Burden, responsibility, hard work", 
                "Burden lifted, responsibilities shared, hard work rewarded", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0b/Wands10.jpg"),
        TarotCard("Page of Wands", "Inspiration, ideas, discovery", 
                "New inspiration, creative ideas, curiosity piqued", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6a/Wands11.jpg"),
        TarotCard("Knight of Wands", "Energy, passion, inspired action", 
                "Focused energy, passionate pursuit, inspired endeavors", 
                "https://upload.wikimedia.org/wikipedia/commons/1/16/Wands12.jpg"),
        TarotCard("Queen of Wands", "Courage, confidence, independence", 
                "Self-assuredness, confidence restored, independent spirit", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0d/Wands13.jpg"),
        TarotCard("King of Wands", "Natural leader, vision, entrepreneur", 
                "Visionary leadership, entrepreneurial spirit, inspired action", 
                "https://upload.wikimedia.org/wikipedia/commons/c/ce/Wands14.jpg"),
        TarotCard("Ace of Cups", "Love, new relationships, compassion", 
                "New love, compassion deepened, emotional fulfillment", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e2/Cups01.jpg"),
        TarotCard("Two of Cups", "Unified love, partnership, connection", 
                "Unified partnership, mutual attraction, emotional balance", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6f/Cups02.jpg"),
        TarotCard("Three of Cups", "Celebration, friendship, creativity", 
                "Celebration with friends, creative collaborations, joyous occasions", 
                "https://upload.wikimedia.org/wikipedia/commons/0/02/Cups03.jpg"),
        TarotCard("Four of Cups", "Meditation, contemplation, apathy", 
                "Meditation benefits, contemplation rewarded, apathy overcome", 
                "https://upload.wikimedia.org/wikipedia/commons/5/5e/Cups04.jpg"),
        TarotCard("Five of Cups", "Loss, regret, disappointment", 
                "Acceptance of loss, moving on from regret, emotional healing", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0f/Cups05.jpg"),
        TarotCard("Six of Cups", "Innocence, nostalgia, childhood memories", 
                "Childhood joy remembered, innocence cherished, generosity", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f3/Cups06.jpg"),
        TarotCard("Seven of Cups", "Opportunities, choices, wishful thinking", 
                "Focused choices, realistic opportunities, decision clarity", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e4/Cups07.jpg"),
        TarotCard("Eight of Cups", "Disappointment, abandonment, withdrawal", 
                "Moving on emotionally, walking away from disappointment, seeking fulfillment", 
                "https://upload.wikimedia.org/wikipedia/commons/8/88/Cups08.jpg"),
        TarotCard("Nine of Cups", "Wishes fulfilled, contentment, satisfaction", 
                "Wishes granted, emotional satisfaction, joyous fulfillment", 
                "https://upload.wikimedia.org/wikipedia/commons/a/a0/Cups09.jpg"),
        TarotCard("Ten of Cups", "Emotional happiness, alignment, family bliss", 
                "Emotional fulfillment, harmony in relationships, domestic happiness", 
                "https://upload.wikimedia.org/wikipedia/commons/7/72/Cups10.jpg"),
        TarotCard("Page of Cups", "Creative opportunities, intuitive messages, curiosity", 
                "Creative inspiration, intuitive messages, emotional exploration", 
                "https://upload.wikimedia.org/wikipedia/commons/8/81/Cups11.jpg"),
        TarotCard("Knight of Cups", "Romantic proposal, imagination, charm", 
                "Romantic gestures, creative proposals, emotional depth", 
                "https://upload.wikimedia.org/wikipedia/commons/8/80/Cups12.jpg"),
        TarotCard("Queen of Cups", "Compassion, calm, comfort", 
                "Emotional security, loving nature, intuitive insight", 
                "https://upload.wikimedia.org/wikipedia/commons/4/4e/Cups13.jpg"),
        TarotCard("King of Cups", "Emotional balance, compassion, control", 
                "Compassionate leadership, emotional maturity, calm authority", 
                "https://upload.wikimedia.org/wikipedia/commons/d/d8/Cups14.jpg"),
        TarotCard("Ace of Swords", "Clarity, mental breakthroughs, truth", 
                "Clarity of mind, breakthroughs, new ideas", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e7/Swords01.jpg"),
        TarotCard("Two of Swords", "Difficult decisions, indecision, stalemate", 
                "Decision made, stalemate ended, compromise reached", 
                "https://upload.wikimedia.org/wikipedia/commons/3/32/Swords02.jpg"),
        TarotCard("Three of Swords", "Heartbreak, emotional pain, sorrow", 
                "Healing from heartbreak, forgiveness, emotional release", 
                "https://upload.wikimedia.org/wikipedia/commons/3/31/Swords03.jpg"),
        TarotCard("Four of Swords", "Rest, relaxation, meditation", 
                "Restoration, contemplation, rejuvenation", 
                "https://upload.wikimedia.org/wikipedia/commons/9/9d/Swords04.jpg"),
        TarotCard("Five of Swords", "Conflict, tension, winning at all costs", 
                "Compromise, making amends, leaving conflict behind", 
                "https://upload.wikimedia.org/wikipedia/commons/1/1d/Swords05.jpg"),
        TarotCard("Six of Swords", "Transition, leaving behind, moving on", 
                "Smooth transition, personal growth, leaving troubles behind", 
                "https://upload.wikimedia.org/wikipedia/commons/1/14/Swords06.jpg"),
        TarotCard("Seven of Swords", "Deception, betrayal, stealth", 
                "Reevaluation of motives, avoiding deception, strategic withdrawal", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0c/Swords07.jpg"),
        TarotCard("Eight of Swords", "Isolation, restriction, self-imposed prison", 
                "Freedom from restriction, new perspectives, self-acceptance", 
                "https://upload.wikimedia.org/wikipedia/commons/6/61/Swords08.jpg"),
        TarotCard("Nine of Swords", "Anxiety, worry, fear", 
                "Overcoming anxiety, finding solutions, inner turmoil resolved", 
                "https://upload.wikimedia.org/wikipedia/commons/3/3d/Swords09.jpg"),
        TarotCard("Ten of Swords", "Betrayal, pain, endings", 
                "Recovery, healing from betrayal, new hope", 
                "https://upload.wikimedia.org/wikipedia/commons/6/61/Swords10.jpg"),
        TarotCard("Page of Swords", "Curiosity, new ideas, exploration", 
                "New perspectives, curiosity rewarded, intellectual growth", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f6/Swords11.jpg"),
        TarotCard("Knight of Swords", "Ambitious, action-oriented, driven", 
                "Focused action, determination, fast-paced change", 
                "https://upload.wikimedia.org/wikipedia/commons/7/73/Swords12.jpg"),
        TarotCard("Queen of Swords", "Clarity, perception, independence", 
                "Clear communication, independence, impartial judgement", 
                "https://upload.wikimedia.org/wikipedia/commons/2/2d/Swords13.jpg"),
        TarotCard("King of Swords", "Intellectual power, authority, truth", 
                "Mental clarity, assertive communication, fair decisions", 
                "https://upload.wikimedia.org/wikipedia/commons/2/29/Swords14.jpg"),
        TarotCard("Ace of Pentacles", "New opportunities, prosperity, abundance", 
                "New financial opportunity, manifesting abundance, prosperity", 
                "https://upload.wikimedia.org/wikipedia/commons/1/1f/Pentacles01.jpg"),
        TarotCard("Two of Pentacles", "Balance, adaptability, prioritization", 
                "Adapting to change, managing priorities, financial decisions", 
                "https://upload.wikimedia.org/wikipedia/commons/7/7e/Pentacles02.jpg"),
        TarotCard("Three of Pentacles", "Teamwork, collaboration, building", 
                "Initial success, recognition, collaboration", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f9/Pentacles03.jpg"),
        TarotCard("Four of Pentacles", "Stability, security, conservation", 
                "Financial control, conservatism, saving for the future", 
                "https://upload.wikimedia.org/wikipedia/commons/9/94/Pentacles04.jpg"),
        TarotCard("Five of Pentacles", "Hard times, challenges, isolation", 
                "Financial assistance, social support, overcoming challenges", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f6/Pentacles05.jpg"),
        TarotCard("Six of Pentacles", "Generosity, charity, giving and receiving", 
                "Generosity received, giving back, balance in charity", 
                "https://upload.wikimedia.org/wikipedia/commons/d/d1/Pentacles06.jpg"),
        TarotCard("Seven of Pentacles", "Patience, long-term view, perseverance", 
                "Long-term investments, sustainability, perseverance", 
                "https://upload.wikimedia.org/wikipedia/commons/0/03/Pentacles07.jpg"),
        TarotCard("Eight of Pentacles", "Apprenticeship, mastery, skill development", 
                "Diligence rewarded, skill mastery, attention to detail", 
                "https://upload.wikimedia.org/wikipedia/commons/4/45/Pentacles08.jpg"),
        TarotCard("Nine of Pentacles", "Fruitfulness, independence, luxury", 
                "Financial independence, self-sufficiency, material success", 
                "https://upload.wikimedia.org/wikipedia/commons/5/5b/Pentacles09.jpg"),
        TarotCard("Ten of Pentacles", "Legacy, inheritance, culmination", 
                "Financial legacy, long-term success, family wealth", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6d/Pentacles10.jpg"),
        TarotCard("Page of Pentacles", "Manifestation, new financial opportunity, prosperity", 
                "New skills learned, financial opportunity, manifestation", 
                "https://upload.wikimedia.org/wikipedia/commons/d/db/Pentacles11.jpg"),
        TarotCard("Knight of Pentacles", "Hard work, diligence, responsibility", 
                "Reliability, diligence, achieving goals through perseverance", 
                "https://upload.wikimedia.org/wikipedia/commons/1/19/Pentacles12.jpg"),
        TarotCard("Queen of Pentacles", "Practicality, creature comforts, financial security", 
                "Nurturing abundance, financial pragmatism, domestic security", 
                "https://upload.wikimedia.org/wikipedia/commons/a/a8/Pentacles13.jpg"),
        TarotCard("King of Pentacles", "Abundance, prosperity, security", 
                "Wealth management, financial security, abundance mindset", 
                "https://upload.wikimedia.org/wikipedia/commons/7/70/Pentacles14.jpg")
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
        You are an experienced and intuitive Tarot card reader, skilled in performing the three-card spread. Your role is to provide insightful, balanced, and uplifting readings that help users gain new perspectives on their situations. The cards drawn for this reading are: {cards}

        Remember these key points:
        1. Approach: You approach each reading with empathy, objectivity, and an open mind. Your aim is to guide and offer insights that empower the user, rather than making definitive predictions.
        2. Three-Card Spread: Specialize in interpreting the cards as Past, Present, and Future, uncovering the narrative they weave together.
        3. Card Meanings: You deeply understand Tarot symbolism, interpreting both upright and reversed positions as specified in {cards}. You believe that reversed Tarot cards often deliver good news, or simply strengthen, weaken, or redirect the primary message of the upright card, without inherent negativity.
        4. Interconnected Reading: Don't interpret each card in isolation. Explain how the cards in {cards} relate to each other, telling a cohesive story that empowers the user.
        5. Ethical Considerations: Maintain high ethical standards. Avoid making absolute predictions about health, legal matters, or major life decisions. Instead, offer perspectives that empower the user to make informed choices.
        6. Language: Use clear, respectful language. Avoid dramatic tones or fear-mongering. Frame challenges as opportunities for growth and transformation.
        7. Intuition: Trust your intuition to provide nuanced interpretations of {cards}, grounded in both traditional meanings and intuitive insights.
        8. User Interaction: Encourage users to reflect on the reading and discover personal meaning in the cards drawn.
        9. Scope: Focus on interpreting the three cards drawn in {cards}. Avoid introducing additional cards to maintain clarity and relevance.
        10. Closing: Summarize the insights from {cards}, offering a constructive perspective on the user's situation that fosters optimism, empowerment and positivity.

        Base your entire reading on the cards specified in {cards}.

            """.format(cards=", ".join(cards_info))

            # Make the API call to ChatGPT
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4o",  # or "gpt-3.5-turbo", depending on your preference and availability
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
