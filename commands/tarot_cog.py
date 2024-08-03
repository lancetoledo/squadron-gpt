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
        TarotCard("The Fool", "New beginnings, innocence, spontaneity", 
                "Embracing spontaneity, new perspectives, leap of faith", 
                "https://i.imgur.com/IgSeRkv.png"),
        TarotCard("The Magician", "Manifestation, resourcefulness, power", 
                "Untapped talents, realizing potential, inner resources", 
                "https://i.imgur.com/DD4AHHV.png"),
        TarotCard("The High Priestess", "Intuition, sacred knowledge, divine feminine", 
                "Inner wisdom, unconscious mind, trusting intuition", 
                "https://i.imgur.com/BxswQ9b.png"),
        TarotCard("The Empress", "Femininity, beauty, nature, abundance", 
                "Self-care, nurturing others, creative expression", 
                "https://i.imgur.com/4CKVcVv.png"),
        TarotCard("The Emperor", "Authority, establishment, structure, father figure", 
                "Inner authority, balancing structure and flexibility", 
                "https://i.imgur.com/nWhFgsw.png"),
        TarotCard("The Hierophant", "Spiritual wisdom, religious beliefs, tradition, conformity", 
                "Personal beliefs, challenging traditions, inner guidance", 
                "https://i.imgur.com/Iqpq2Bt.png"),
        TarotCard("The Lovers", "Love, harmony, relationships, choices, alignment of values", 
                "Self-love, aligning values, inner harmony", 
                "https://i.imgur.com/fzD5TPJ.png"),
        TarotCard("The Chariot", "Control, willpower, success, action, determination", 
                "Inner motivation, balancing opposing forces, self-discipline", 
                "https://i.imgur.com/oxQvurg.png"),
        TarotCard("Strength", "Courage, patience, influence, compassion", 
                "Inner strength, gentleness, quiet confidence", 
                "https://i.imgur.com/kcS198t.png"),
        TarotCard("The Hermit", "Soul searching, introspection, being alone, inner guidance", 
                "Inner guidance, silent wisdom, self-reflection", 
                "https://i.imgur.com/KvtoxfJ.png"),
        TarotCard("Wheel of Fortune", "Good luck, karma, life cycles, destiny, turning point", 
                "Personal responsibility, adapting to change, seizing opportunities", 
                "https://i.imgur.com/xLfgIOc.png"),
        TarotCard("Justice", "Fairness, truth, cause and effect, law", 
                "Inner balance, taking responsibility, cause and effect", 
                "https://i.imgur.com/OwmyIIP.png"),
        TarotCard("The Hanged Man", "Pause, surrender, letting go, new perspectives", 
                "New perspectives, personal growth, inner wisdom", 
                "https://i.imgur.com/WasMEnY.png"),
        TarotCard("Death", "Endings, change, transformation, transition", 
                "Resistance to change, personal transformation, new beginnings", 
                "https://i.imgur.com/FXTdIvq.png"),
        TarotCard("Temperance", "Balance, moderation, patience, purpose", 
                "Finding middle ground, aligning energies, personal alchemy", 
                "https://i.imgur.com/Dn5HIF9.png"),
        TarotCard("The Devil", "Shadow self, attachment, addiction, restriction", 
                "Releasing limiting beliefs, exploring dark side, reclaiming power", 
                "https://i.imgur.com/tNV3nDU.png"),
        TarotCard("The Tower", "Sudden change, upheaval, chaos, revelation, awakening", 
                "Avoiding disaster, breaking down structures, paradigm shift", 
                "https://i.imgur.com/ecONM3T.png"),
        TarotCard("The Star", "Hope, faith, purpose, renewal, spirituality", 
                "Rekindling hope, finding inspiration, inner trust", 
                "https://i.imgur.com/2CA6Ggw.png"),
        TarotCard("The Moon", "Illusion, fear, anxiety, subconscious, intuition", 
                "Releasing fears, uncovering illusions, subconscious exploration", 
                "https://i.imgur.com/jE25t7N.png"),
        TarotCard("The Sun", "Positivity, fun, warmth, success, vitality", 
                "Inner child, finding joy, enlightenment", 
                "https://i.imgur.com/VNPv10w.png"),
        TarotCard("Judgement", "Judgement, rebirth, inner calling, absolution", 
                "Self-reflection, inner transformation, forgiveness", 
                "https://i.imgur.com/WXioDet.png"),
        TarotCard("The World", "Completion, integration, accomplishment, travel", 
                "Seeking closure, acknowledging achievements, new cycles", 
                "https://i.imgur.com/lU1xl72.png"),
        TarotCard("Ace of Wands", "Inspiration, new opportunities, growth, potential", 
                "Inner fire, creative spark, enthusiasm", 
                "https://upload.wikimedia.org/wikipedia/commons/1/11/Wands01.jpg"),
        TarotCard("Two of Wands", "Future planning, progress, decisions, discovery", 
                "Personal power, making choices, inner alignment", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0f/Wands02.jpg"),
        TarotCard("Three of Wands", "Expansion, foresight, leadership, exploration", 
                "Opening horizons, preparing for the journey, inner vision", 
                "https://upload.wikimedia.org/wikipedia/commons/f/ff/Wands03.jpg"),
        TarotCard("Four of Wands", "Celebration, harmony, marriage, home, community", 
                "Personal celebrations, inner peace, foundational achievements", 
                "https://upload.wikimedia.org/wikipedia/commons/a/a4/Wands04.jpg"),
        TarotCard("Five of Wands", "Conflict, competition, rivalry, diversity", 
                "Inner conflicts, healthy competition, diversity in ideas", 
                "https://upload.wikimedia.org/wikipedia/commons/9/9d/Wands05.jpg"),
        TarotCard("Six of Wands", "Victory, success, public recognition, progress, self-confidence", 
                "Personal triumph, self-confidence, rising above", 
                "https://upload.wikimedia.org/wikipedia/commons/3/3b/Wands06.jpg"),
        TarotCard("Seven of Wands", "Challenge, competition, protection, perseverance", 
                "Inner conviction, holding your ground, perseverance", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e4/Wands07.jpg"),
        TarotCard("Eight of Wands", "Speed, action, air travel, movement, quick decisions", 
                "Aligning energy, inner momentum, swift changes", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6b/Wands08.jpg"),
        TarotCard("Nine of Wands", "Resilience, grit, last stand, persistence, test of faith", 
                "Inner strength, grit, preparing for the final push", 
                "https://upload.wikimedia.org/wikipedia/commons/4/4d/Tarot_Nine_of_Wands.jpg"),
        TarotCard("Ten of Wands", "Burden, extra responsibility, hard work, completion", 
                "Delegating, reassessing commitments, inner resolve", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0b/Wands10.jpg"),
        TarotCard("Page of Wands", "Exploration, excitement, freedom, adventure", 
                "Inner child, new perspectives, spark of passion", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6a/Wands11.jpg"),
        TarotCard("Knight of Wands", "Energy, passion, inspired action, adventure, impulsiveness", 
                "Inner fire, impulsiveness, adventure", 
                "https://upload.wikimedia.org/wikipedia/commons/1/16/Wands12.jpg"),
        TarotCard("Queen of Wands", "Courage, determination, joy, vibrancy, radiance", 
                "Inner radiance, self-assuredness, leading by example", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0d/Wands13.jpg"),
        TarotCard("King of Wands", "Natural-born leader, vision, entrepreneur, honour", 
                "Inner power, taking charge, inspiration to others", 
                "https://upload.wikimedia.org/wikipedia/commons/c/ce/Wands14.jpg"),
        TarotCard("Ace of Cups", "Love, new relationships, compassion, creativity", 
                "Self-love, intuition, new emotional beginnings", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e2/Cups01.jpg"),
        TarotCard("Two of Cups", "Unity, partnership, connection, attraction", 
                "Self-union, balancing relationships, mutual respect", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6f/Cups02.jpg"),
        TarotCard("Three of Cups", "Celebration, friendship, creativity, collaborations", 
                "Inner circle, community, shared happiness", 
                "https://upload.wikimedia.org/wikipedia/commons/0/02/Cups03.jpg"),
        TarotCard("Four of Cups", "Apathy, contemplation, disconnectedness, reevaluation", 
                "Inner world, revaluation, finding gratitude", 
                "https://upload.wikimedia.org/wikipedia/commons/5/5e/Cups04.jpg"),
        TarotCard("Five of Cups", "Loss, grief, self-pity, disappointment", 
                "Acceptance, finding the silver lining, moving forward", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0f/Cups05.jpg"),
        TarotCard("Six of Cups", "Revisiting the past, childhood memories, innocence, joy", 
                "Living in the present, inner child healing, forgiveness", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f3/Cups06.jpg"),
        TarotCard("Seven of Cups", "Opportunities, choices, wishful thinking, illusion", 
                "Fantasy vs. reality, prioritizing dreams, inner vision", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e4/Cups07.jpg"),
        TarotCard("Eight of Cups", "Disappointment, abandonment, withdrawal, escapism", 
                "Seeking deeper meaning, personal journey, inner quest", 
                "https://upload.wikimedia.org/wikipedia/commons/8/88/Cups08.jpg"),
        TarotCard("Nine of Cups", "Satisfaction, emotional stability, luxury, contentment", 
                "Inner happiness, appreciation, emotional stability", 
                "https://upload.wikimedia.org/wikipedia/commons/a/a0/Cups09.jpg"),
        TarotCard("Ten of Cups", "Divine love, blissful relationships, harmony, alignment", 
                "Inner peace, harmony in relationships, shared contentment", 
                "https://upload.wikimedia.org/wikipedia/commons/7/72/Cups10.jpg"),
        TarotCard("Page of Cups", "Creative opportunities, intuitive messages, curiosity, possibility", 
                "Inner voice, new feelings, emotional immaturity", 
                "https://upload.wikimedia.org/wikipedia/commons/8/81/Cups11.jpg"),
        TarotCard("Knight of Cups", "Creativity, romance, charm, imagination, beauty", 
                "Daydreaming, following the heart, idealism", 
                "https://upload.wikimedia.org/wikipedia/commons/8/80/Cups12.jpg"),
        TarotCard("Queen of Cups", "Compassion, calm, comfort, emotional stability, intuition", 
                "Emotional nurturing, intuition, inner feelings", 
                "https://upload.wikimedia.org/wikipedia/commons/4/4e/Cups13.jpg"),
        TarotCard("King of Cups", "Emotional balance, generosity, diplomacy, wisdom", 
                "Emotional wisdom, diplomacy, caring leadership", 
                "https://upload.wikimedia.org/wikipedia/commons/d/d8/Cups14.jpg"),
        TarotCard("Ace of Swords", "Clarity, clear vision, intellectual breakthroughs, truth", 
                "Inner clarity, new ideas, mental freshness", 
                "https://upload.wikimedia.org/wikipedia/commons/e/e7/Swords01.jpg"),
        TarotCard("Two of Swords", "Difficult decisions, weighing options, stalemate, denial", 
                "Inner conflict, truce, seeing both sides", 
                "https://upload.wikimedia.org/wikipedia/commons/3/32/Swords02.jpg"),
        TarotCard("Three of Swords", "Heartbreak, emotional pain, sorrow, grief, rejection", 
                "Healing, optimism, releasing pain", 
                "https://upload.wikimedia.org/wikipedia/commons/3/31/Swords03.jpg"),
        TarotCard("Four of Swords", "Rest, relaxation, meditation, contemplation, recuperation", 
                "Inner peace, healing, mental preparation", 
                "https://upload.wikimedia.org/wikipedia/commons/9/9d/Swords04.jpg"),
        TarotCard("Five of Swords", "Conflict, tension, loss, defeat, win at all costs", 
                "Inner conflicts, learning from defeat, reassessment", 
                "https://upload.wikimedia.org/wikipedia/commons/1/1d/Swords05.jpg"),
        TarotCard("Six of Swords", "Transition, change, rite of passage, releasing baggage", 
                "Internal transition, releasing baggage, gradual change", 
                "https://upload.wikimedia.org/wikipedia/commons/1/14/Swords06.jpg"),
        TarotCard("Seven of Swords", "Deception, trickery, stealth, strategy, resourcefulness", 
                "Reevaluation, redirecting energy, inner truth", 
                "https://upload.wikimedia.org/wikipedia/commons/0/0c/Swords07.jpg"),
        TarotCard("Eight of Swords", "Isolation, imprisonment, self-victimization, restriction", 
                "Self-imposed limitations, opening your eyes, inner freedom", 
                "https://upload.wikimedia.org/wikipedia/commons/6/61/Swords08.jpg"),
        TarotCard("Nine of Swords", "Anxiety, worry, fear, depression, nightmares", 
                "Facing fears, dark night of the soul, hope dawning", 
                "https://upload.wikimedia.org/wikipedia/commons/3/3d/Swords09.jpg"),
        TarotCard("Ten of Swords", "Painful endings, deep wounds, betrayal, loss, crisis", 
                "Recovery, rising from ashes, embracing change", 
                "https://upload.wikimedia.org/wikipedia/commons/6/61/Swords10.jpg"),
        TarotCard("Page of Swords", "New ideas, curiosity, thirst for knowledge, new ways of communicating", 
                "New ways of communicating, fresh perspectives, watchfulness", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f6/Swords11.jpg"),
        TarotCard("Knight of Swords", "Action, impulsiveness, defending beliefs, swift change", 
                "Inner truth, tempering haste, clear communication", 
                "https://upload.wikimedia.org/wikipedia/commons/7/73/Swords12.jpg"),
        TarotCard("Queen of Swords", "Sharp mind, unbiased judgment, clear communication, independence", 
                "Inner truth, perceptiveness, wisdom", 
                "https://upload.wikimedia.org/wikipedia/commons/2/2d/Swords13.jpg"),
        TarotCard("King of Swords", "Authority, intellectual power, truth, logic, clear thinking", 
                "Ethical leadership, clear thinking, inner authority", 
                "https://upload.wikimedia.org/wikipedia/commons/2/29/Swords14.jpg"),
        TarotCard("Ace of Pentacles", "New financial or career opportunity, manifestation, abundance", 
                "Inner wealth, potential for growth, seed of possibility", 
                "https://upload.wikimedia.org/wikipedia/commons/1/1f/Pentacles01.jpg"),
        TarotCard("Two of Pentacles", "Balancing decisions, priorities, adapting to change, juggling", 
                "Inner balance, juggling priorities, flexibility", 
                "https://upload.wikimedia.org/wikipedia/commons/7/7e/Pentacles02.jpg"),
        TarotCard("Three of Pentacles", "Teamwork, collaboration, learning, implementation", 
                "Mastering skills, quality work, self-improvement", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f9/Pentacles03.jpg"),
        TarotCard("Four of Pentacles", "Conservation, security, frugality, long-term investment", 
                "Redefining security, generosity, letting go", 
                "https://upload.wikimedia.org/wikipedia/commons/9/94/Pentacles04.jpg"),
        TarotCard("Five of Pentacles", "Financial loss, poverty, lack mindset, isolation, worry", 
                "Inner resources, spiritual growth, finding help", 
                "https://upload.wikimedia.org/wikipedia/commons/f/f6/Pentacles05.jpg"),
        TarotCard("Six of Pentacles", "Giving, receiving, sharing wealth, generosity, charity", 
                "Self-care, accepting help, inner abundance", 
                "https://upload.wikimedia.org/wikipedia/commons/d/d1/Pentacles06.jpg"),
        TarotCard("Seven of Pentacles", "Long-term view, sustained effort, perseverance, investment", 
                "Reassessment, redirecting energy, inner growth", 
                "https://upload.wikimedia.org/wikipedia/commons/0/03/Pentacles07.jpg"),
        TarotCard("Eight of Pentacles", "Apprenticeship, repetitive tasks, mastery, skill development", 
                "Inner mastery, refining skills, attention to detail", 
                "https://upload.wikimedia.org/wikipedia/commons/4/45/Pentacles08.jpg"),
        TarotCard("Nine of Pentacles", "Luxury, self-sufficiency, financial independence, rewards", 
                "Inner abundance, self-reliance, enjoying fruits of labor", 
                "https://upload.wikimedia.org/wikipedia/commons/5/5b/Pentacles09.jpg"),
        TarotCard("Ten of Pentacles", "Wealth, family, long-term success, inheritance, establishment", 
                "Inner wealth, family values, leaving a legacy", 
                "https://upload.wikimedia.org/wikipedia/commons/6/6d/Pentacles10.jpg"),
        TarotCard("Page of Pentacles", "Manifestation, financial opportunity, new career, scholarship", 
                "New skills, curiosity about material world, studentship", 
                "https://upload.wikimedia.org/wikipedia/commons/d/db/Pentacles11.jpg"),
        TarotCard("Knight of Pentacles", "Hard work, productivity, routine, conservatism, methodical", 
                "Rekindling purpose, breaking routine, measured changes", 
                "https://upload.wikimedia.org/wikipedia/commons/1/19/Pentacles12.jpg"),
        TarotCard("Queen of Pentacles", "Nurturing, practical, providing financially, luxury, comfort", 
                "Self-care, balancing work and home, abundance mindset", 
                "https://upload.wikimedia.org/wikipedia/commons/a/a8/Pentacles13.jpg"),
        TarotCard("King of Pentacles", "Abundance, prosperity, security, leadership, discipline", 
                "Generosity, financial wisdom, values-based decisions", 
                "https://upload.wikimedia.org/wikipedia/commons/7/70/Pentacles14.jpg")
        ]


    # Example: !test_card The Fool, !test_card Queen of Cups
    # Draw a specific tarot card for testing purposes. 
    @commands.command()
    async def test_card(self, ctx, *, card_name: str):
        """Draw a specific tarot card by name."""
        card = next((card for card in self.tarot_deck if card.name.lower() == card_name.lower()), None)
        
        if card:
            embed = discord.Embed(title=f"Test Card: {card.name}", color=0x7289DA)
            embed.set_image(url=card.image_url)
            embed.add_field(name="Upright Meaning", value=card.meaning_upright, inline=False)
            embed.add_field(name="Reversed Meaning", value=card.meaning_reversed, inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Card '{card_name}' not found. Please check the spelling and try again.")


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
