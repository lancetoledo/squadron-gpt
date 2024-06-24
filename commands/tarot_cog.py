import discord
from discord.ext import commands
import random

class TarotCard:
    def __init__(self, name, meaning_upright, meaning_reversed):
        self.name = name
        self.meaning_upright = meaning_upright
        self.meaning_reversed = meaning_reversed

class TarotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tarot_deck = [
            TarotCard("The Fool", "New beginnings, innocence, free spirit", "Recklessness, risk-taking, foolishness"),
            TarotCard("The Magician", "Manifestation, resourcefulness, power", "Manipulation, poor planning, untapped talents"),
            TarotCard("The High Priestess", "Intuition, sacred knowledge, divine feminine", "Secrets, disconnected from intuition, withdrawal"),
            TarotCard("The Empress", "Femininity, beauty, nature", "Creative block, dependence on others"),
            TarotCard("The Emperor", "Authority, establishment, structure", "Domination, excessive control, lack of discipline"),
            TarotCard("The Hierophant", "Spiritual wisdom, religious beliefs, conformity", "Personal beliefs, freedom, challenging the status quo"),
            TarotCard("The Lovers", "Love, harmony, relationships", "Self-love, disharmony, imbalance"),
            TarotCard("The Chariot", "Control, willpower, success", "Lack of control, opposition, lack of direction"),
            TarotCard("Strength", "Courage, bravery, confidence", "Self-doubt, weakness, insecurity"),
            TarotCard("The Hermit", "Soul searching, introspection, being alone", "Isolation, loneliness, withdrawal"),
            TarotCard("Wheel of Fortune", "Good luck, karma, life cycles", "Bad luck, resistance to change, breaking cycles"),
            TarotCard("Justice", "Fairness, truth, law", "Unfairness, lack of accountability, dishonesty"),
            TarotCard("The Hanged Man", "Pause, surrender, letting go", "Delays, resistance, stalling"),
            TarotCard("Death", "Endings, change, transformation", "Resistance to change, personal transformation, inner purging"),
            TarotCard("Temperance", "Balance, moderation, patience", "Imbalance, excess, lack of long-term vision"),
            TarotCard("The Devil", "Shadow self, attachment, addiction", "Releasing limiting beliefs, exploring dark thoughts, detachment"),
            TarotCard("The Tower", "Sudden change, upheaval, chaos", "Avoidance of disaster, fear of change"),
            TarotCard("The Star", "Hope, faith, purpose", "Lack of faith, despair, discouragement"),
            TarotCard("The Moon", "Illusion, fear, anxiety", "Release of fear, repressed emotion, inner confusion"),
            TarotCard("The Sun", "Positivity, fun, success", "Inner child, feeling down, overly optimistic"),
            TarotCard("Judgement", "Judgement, rebirth, inner calling", "Self-doubt, inner critic, ignoring the call"),
            TarotCard("The World", "Completion, integration, accomplishment", "Seeking closure, short-cuts, delays"),
            TarotCard("Ace of Wands", "Inspiration, new opportunities, growth", "Lack of direction, delays, missed opportunity"),
            TarotCard("Two of Wands", "Future planning, progress, decisions", "Fear of unknown, lack of planning, staying put"),
            TarotCard("Three of Wands", "Expansion, foresight, overseas opportunities", "Obstacles, delays, frustration"),
            TarotCard("Four of Wands", "Celebration, harmony, homecoming", "Personal celebration, inner harmony, conflict with others"),
            TarotCard("Five of Wands", "Conflict, competition, tension", "Avoiding conflict, respecting differences"),
            TarotCard("Six of Wands", "Success, public recognition, progress", "Egotism, lack of recognition, fall from grace"),
            TarotCard("Seven of Wands", "Challenge, competition, protection", "Exhaustion, giving up, overwhelmed"),
            TarotCard("Eight of Wands", "Speed, action, movement", "Delays, frustration, resisting change"),
            TarotCard("Nine of Wands", "Resilience, courage, persistence", "Ongoing battle, weary, lack of fight"),
            TarotCard("Ten of Wands", "Burden, responsibility, hard work", "Avoiding responsibility, taking on too much, burnout"),
            TarotCard("Page of Wands", "Inspiration, ideas, discovery", "Lack of direction, procrastination, newly formed ideas"),
            TarotCard("Knight of Wands", "Energy, passion, inspired action", "Haste, scattered energy, delays"),
            TarotCard("Queen of Wands", "Courage, confidence, independence", "Self-respect, introverted, re-establish sense of self"),
            TarotCard("King of Wands", "Natural leader, vision, entrepreneur", "Impulsiveness, overbearing, unachievable expectations"),
            TarotCard("Ace of Cups", "Love, new relationships, compassion", "Self-love, intuition, repressed emotions"),
            TarotCard("Two of Cups", "Unified love, partnership, attraction", "Self-love, break-ups, disharmony"),
            TarotCard("Three of Cups", "Celebration, friendship, creativity", "Independence, alone time, hardcore partying"),
            TarotCard("Four of Cups", "Meditation, contemplation, apathy", "Retreat, withdrawal, checking in for alignment"),
            TarotCard("Five of Cups", "Regret, failure, disappointment", "Personal setbacks, self-forgiveness, moving on"),
            TarotCard("Six of Cups", "Revisiting the past, childhood memories, innocence", "Living in the past, forgiveness, lacking playfulness"),
            TarotCard("Seven of Cups", "Opportunities, choices, illusion", "Lack of purpose, diversion, confusion"),
            TarotCard("Eight of Cups", "Disappointment, abandonment, withdrawal", "Trying one more time, indecision, aimless drifting"),
            TarotCard("Nine of Cups", "Contentment, satisfaction, gratitude", "Inner happiness, materialism, dissatisfaction"),
            TarotCard("Ten of Cups", "Divine love, blissful relationships, harmony", "Disconnection, misaligned values, struggling relationships"),
            TarotCard("Page of Cups", "Creative opportunities, intuitive messages, curiosity", "New ideas, doubting intuition, creative blocks"),
            TarotCard("Knight of Cups", "Romantic proposals, offers, invitations", "Overactive imagination, unrealistic, jealous"),
            TarotCard("Queen of Cups", "Compassion, caring, emotionally stable", "Inner feelings, self-care, co-dependency"),
            TarotCard("King of Cups", "Emotional balance, control, generosity", "Emotional manipulation, moodiness, volatility"),
            TarotCard("Ace of Swords", "Breakthrough, clarity, sharp mind", "Confusion, miscommunication, hostility"),
            TarotCard("Two of Swords", "Difficult decisions, weighing up options, an impasse", "Indecision, confusion, information overload"),
            TarotCard("Three of Swords", "Heartbreak, emotional pain, sorrow", "Negative self-talk, releasing pain, optimism"),
            TarotCard("Four of Swords", "Rest, relaxation, contemplation", "Restlessness, burnout, stress"),
            TarotCard("Five of Swords", "Conflict, disagreements, competition", "Reconciliation, making amends, past resentment"),
            TarotCard("Six of Swords", "Transition, change, rite of passage", "Resistance to change, unfinished business"),
            TarotCard("Seven of Swords", "Betrayal, deception, getting away with something", "Imposter syndrome, keeping secrets, lying to oneself"),
            TarotCard("Eight of Swords", "Negative thoughts, self-imposed restriction, imprisonment", "Open to new perspectives, release, facing fears"),
            TarotCard("Nine of Swords", "Anxiety, worry, fear", "Inner turmoil, deep-seated fears, secrets"),
            TarotCard("Ten of Swords", "Painful endings, betrayal, loss", "Recovery, regeneration, resisting an inevitable end"),
            TarotCard("Page of Swords", "New ideas, curiosity, thirst for knowledge", "Self-expression, all talk and no action, haphazard action"),
            TarotCard("Knight of Swords", "Ambitious, action-oriented, driven", "Restless, unfocused, impulsive"),
            TarotCard("Queen of Swords", "Independent, unbiased judgment, clear boundaries", "Overly emotional, easily influenced, cold-hearted"),
            TarotCard("King of Swords", "Mental clarity, intellectual power, authority", "Manipulative, tyrannical, abusive"),
            TarotCard("Ace of Pentacles", "Manifestation, new financial opportunity, prosperity", "Lost opportunity, lack of planning, foresight"),
            TarotCard("Two of Pentacles", "Balance, adaptability, time management", "Disorganization, financial disarray, overcommitment"),
            TarotCard("Three of Pentacles", "Teamwork, collaboration, learning", "Disharmony, misalignment, working alone"),
            TarotCard("Four of Pentacles", "Saving money, security, conservatism", "Greed, materialism, self-protection"),
            TarotCard("Five of Pentacles", "Financial loss, poverty, isolation", "Recovery from loss, spiritual poverty"),
            TarotCard("Six of Pentacles", "Giving, receiving, sharing wealth", "Self-care, unpaid debts, one-sided charity"),
            TarotCard("Seven of Pentacles", "Long-term view, sustainable results, perseverance", "Lack of long-term vision, limited success or reward"),
            TarotCard("Eight of Pentacles", "Apprenticeship, repetitive tasks, mastery", "Self-development, perfectionism, misdirected activity"),
            TarotCard("Nine of Pentacles", "Abundance, luxury, self-sufficiency", "Self-worth, over-investment in work, hustling"),
            TarotCard("Ten of Pentacles", "Wealth, financial security, family", "Financial failure, loss, lack of stability"),
            TarotCard("Page of Pentacles", "Manifestation, financial opportunity, new job", "Lack of progress, procrastination, learn from failure"),
            TarotCard("Knight of Pentacles", "Hard work, productivity, routine", "Self-discipline, boredom, feeling 'stuck'"),
            TarotCard("Queen of Pentacles", "Practical, nurturing, providing financially", "Financial independence, self-care, work-home conflict"),
            TarotCard("King of Pentacles", "Wealth, business, leadership", "Financially inept, obsessed with wealth, stubborn")
        ]

    @commands.command()
    async def draw_card(self, ctx):
        card = random.choice(self.tarot_deck)
        is_upright = random.choice([True, False])
        
        embed = discord.Embed(title="Tarot Card Reading")
        embed.add_field(name="Card", value=card.name, inline=False)
        embed.add_field(name="Position", value="Upright" if is_upright else "Reversed", inline=False)
        embed.add_field(name="Meaning", value=card.meaning_upright if is_upright else card.meaning_reversed, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def timeline_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 3)
        positions = ["Past", "Present", "Future"]
        
        embed = discord.Embed(title="Three-Card Timeline Spread")
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed.add_field(name=f"{position}: {card.name}", value=f"{'Upright' if is_upright else 'Reversed'}\n{card.meaning_upright if is_upright else card.meaning_reversed}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def cross_spread(self, ctx):
        cards = random.sample(self.tarot_deck, 5)
        positions = ["Present", "Challenge", "Past", "Future", "Outcome"]
        
        embed = discord.Embed(title="Cross Spread")
        
        for card, position in zip(cards, positions):
            is_upright = random.choice([True, False])
            embed.add_field(name=f"{position}: {card.name}", value=f"{'Upright' if is_upright else 'Reversed'}\n{card.meaning_upright if is_upright else card.meaning_reversed}", inline=False)
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(TarotCog(bot))