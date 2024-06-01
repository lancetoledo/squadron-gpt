import json
import discord
import openai
import os
import asyncio
from config import OPENAI_API_KEY, STATIC_FRIEND_DATA, DISCORD_TO_REAL_NAME
from utils.feedback_utils import save_feedback
from text_processing.text_utils import truncate_text
from text_processing.relationship_detection import is_relationship_inquiry, is_friend_inquiry, is_feedback, is_general_inquiry
from utils.file_utils import load_json_files
from utils.context_management import update_history_with_extracted_info, truncate_history, summarize_conversation, split_message
from tts.elevenlabs_tts import generate_custom_tts
from text_processing.spacy_setup import nlp

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Load JSON data from the data directory
# Change 'data' to 'sample_data' after you added your personal data to the json files.
friend_data_json = load_json_files("data")

# Initialize dictionaries for session histories and contexts
session_histories = {}
session_contexts = {}

# Placeholder examples for static friend data and discord to real name mapping
# Users should replace these with their actual data in the .env file

# Static friend data is for uncommon names or cultural names that aren't being detected by NER like "Fabriccio" or "Pragg"
# STATIC_FRIEND_DATA = [
#     {"name": "Christian"},
#     {"name": "Justine"},
#     {"name": "Bob"}
# ]

# This is used so the bot can recognize discord users to their real names so the bot can search it's data set for them.
# DISCORD_TO_REAL_NAME = {
#     "noobmaster69": "Korg",
#     "thechosenone": "Neo",
# }

# Function to extract friend names from JSON files and static data
def extract_friend_names():
    friend_names = set()
    nickname_to_full_name = {}

    for friend in STATIC_FRIEND_DATA:
        name = friend.get("name", "").lower()
        if name:
            friend_names.add(name)

    for friend in friend_data_json.get("friends", []):
        name = friend.get("name", "").lower()
        nickname = friend.get("nickname", "").lower()
        if name:
            friend_names.add(name)
        if nickname:
            friend_names.add(nickname)
            nickname_to_full_name[nickname] = name

    for relationship_data in friend_data_json.get("relationships", []):
        for relationship in relationship_data.get("relationships", []):
            name = relationship.get("name", "").lower()
            nickname = relationship.get("nickname", "").lower()
            if name:
                friend_names.add(name)
            if nickname:
                friend_names.add(nickname)
                nickname_to_full_name[nickname] = name

    return list(friend_names), nickname_to_full_name

# Load the combined list of friend names
known_friend_names, nickname_to_full_name = extract_friend_names()

# Function to replace nicknames with full names in user input
def replace_nicknames(user_input):
    words = user_input.split()
    replaced_words = []
    for word in words:
        clean_word = word.strip(".,!?").lower()
        if clean_word.endswith("'s"):
            clean_word = clean_word[:-2]  # Remove 's from the word
        replaced_word = nickname_to_full_name.get(clean_word, word)
        replaced_words.append(replaced_word)
    return " ".join(replaced_words)

# Function to retrieve data for a specific friend from JSON files and static data
def get_friend_data(friend_name):
    for friend in STATIC_FRIEND_DATA:
        if friend.get("name").lower() == friend_name.lower():
            return friend

    for friend in friend_data_json.get("friends", []):
        if friend.get("name").lower() == friend_name.lower():
            return friend

    return {}

# Function to find relationships for a specific person and target
def find_relationships(person_name, target_friend_name):

    print(f"Finding relationship for {person_name} and {target_friend_name}")
    relationships_info = {}

    # Extract relationships from friends section
    for friend in friend_data_json.get("friends", []):
        if friend["name"].lower() == person_name.lower():
            if "relationships" in friend:
                for close_friend in friend["relationships"].get("closeFriends", []):
                    if close_friend["name"].lower() == target_friend_name.lower():
                        relationships_info["primary"] = close_friend
                        break

    # Extract detailed relationships from relationships section
    for relationship_data in friend_data_json.get("relationships", []):
        if relationship_data["name"].lower() == person_name.lower():
            for rel in relationship_data.get("relationships", []):
                if rel["name"].lower() == target_friend_name.lower():
                    relationships_info["detailed"] = rel
                    break

    if "primary" in relationships_info and "detailed" in relationships_info:
        return relationships_info
    elif "primary" in relationships_info:
        return {"primary": relationships_info["primary"]}
    elif "detailed" in relationships_info:
        return {"detailed": relationships_info["detailed"]}
    else:
        return f"No information found for relationship between {person_name} and {target_friend_name}"

# Function to extract relevant friend data
def handle_friend_inquiry(user_input, user_name):
    doc = nlp(user_input)

    # Collect friend data for all recognized entities
    friend_data_list = []
    detected_friends = set()

    # Handle "me" explicitly
    if "me" in user_input.lower():
        detected_friends.add(user_name.lower())
        friend_data = get_friend_data(user_name.lower())
        if friend_data:
            friend_data_list.append(friend_data)

    # Collect friend data for recognized entities
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.text.lower() in known_friend_names:
            detected_friends.add(ent.text.lower())
            friend_data = get_friend_data(ent.text.lower())
            if friend_data:
                friend_data_list.append(friend_data)

    # Fallback to keyword matching for additional names
    for word in user_input.lower().split():
        clean_word = word.strip(".,!?").lower()
        if clean_word.endswith("'s"):
            clean_word = clean_word[:-2]  # Remove 's from the word
        if clean_word in known_friend_names and clean_word not in detected_friends:
            detected_friends.add(clean_word)
            friend_data = get_friend_data(clean_word)
            if friend_data:
                friend_data_list.append(friend_data)

    if friend_data_list:
        return friend_data_list
    else:
        return None

# Function to handle relationship inquiry
def handle_relationship_inquiry(user_input, friend_name, primary_person=None):
    doc = nlp(user_input)
    detected_names = [ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON"]
    print(f"Detected names using NER: {detected_names}")

    if not detected_names:
        # Fallback to check known friend names
        words = user_input.lower().split()
        for word in words:
            clean_word = word.strip(".,!?").lower()
            if clean_word.endswith("'s"):
                clean_word = clean_word[:-2]  # Remove 's from the word
            if clean_word in known_friend_names:
                detected_names.append(clean_word)

    if len(detected_names) == 1:
        # Check for additional names in the user input
        words = user_input.lower().split()
        additional_names = []
        for word in words:
            clean_word = word.strip(".,!?").lower()
            if clean_word.endswith("'s"):
                clean_word = clean_word[:-2]  # Remove 's from the word
            if clean_word in known_friend_names and clean_word != detected_names[0]:
                additional_names.append(clean_word)
        
        if additional_names:
            primary_person = detected_names[0]
            target_names = additional_names
        else:
            primary_person = friend_name.lower()
            target_names = detected_names
    else:
        primary_person = detected_names[0] if detected_names else friend_name.lower()
        target_names = detected_names[1:] if len(detected_names) > 1 else []

    relationships_info = {}
    for target_name in target_names:
        relationships_info[target_name] = find_relationships(primary_person, target_name)

    if relationships_info:
        return relationships_info
    else:
        return f"No information found for relationship between {primary_person} and the detected friends."


# Guardrails for sensitive topics specific to Lance and Jenny
def check_sensitive_topics(context, user_input):
    sensitive_phrases = [
        "ex-girlfriend", "new boyfriend", "broke up", "started dating", "romantic feelings",
        "anniversary", "Steve", "hospitalized", "car accident", "then, came 2021—the year things got real dramatic",
        "front and center, even calling her mom to break the news"
    ]
    
    if "lance" in user_input.lower() and "jenny" in user_input.lower():
        if "dating history" not in user_input.lower():
            for phrase in sensitive_phrases:
                context = context.replace(phrase, "[redacted]")
            context = context.replace("ex-girlfriend, now friends", "friends")
            context = context.replace("ex-girlfriend", "friend")
            context = context.replace("new boyfriend", "friend")
            context = context.replace("broke up", "had a disagreement")
            context = context.replace("started dating", "became closer friends")
            context = context.replace("romantic feelings", "strong feelings")
    
    return context

# Event triggered when a message is received
async def on_message(bot, message):
    print(f"on_message triggered by: {message.author.name}, content: {message.content}")

    if message.author == bot.user or not message.content.startswith('!talk'):
        print("Message is from bot or does not start with '!talk'")
        await bot.process_commands(message)
        return

    async with message.channel.typing():
        user_input = message.content[5:].strip()
        print(f"User input after trimming '!talk': {user_input}")

        discord_name = message.author.name
        channel_id = message.channel.id
        session_id = str(channel_id)  # Use channel ID as session ID

        print(f"Discord name: {discord_name}, Channel ID: {channel_id}, Session ID: {session_id}")

        friend_name = DISCORD_TO_REAL_NAME.get(discord_name, discord_name)  # Use Discord username if real name is not found
        primary_person = friend_name.lower()
        print(f"Friend name: {friend_name}, Primary person: {primary_person}")

        user_input = replace_nicknames(user_input)
        print(f"User input after replacing nicknames: {user_input}")

        if session_id not in session_histories:
            session_histories[session_id] = []
            session_contexts[session_id] = {}
            print(f"Initialized session history and context for session ID: {session_id}")

        messages_to_send = []
        audio_path = None

        try:
            if is_feedback(user_input):
                print("Detected feedback in user input")
                save_feedback(user_input, discord_name)
                await message.channel.send("Thank you for the feedback. It has been noted.")
                return

            if is_relationship_inquiry(user_input):
                print("Detected relationship inquiry in user input")
                relationship_info = handle_relationship_inquiry(user_input, friend_name, primary_person)

                if relationship_info is None:
                    response_context = f"Sorry, I don't understand the request."
                    print("Relationship inquiry resulted in no information")
                elif isinstance(relationship_info, dict):
                    response_context = relationship_info
                    session_contexts[session_id] = {
                        "last_inquiry": "relationship",
                        "primary_person": primary_person
                    }
                    print(f"Relationship JSON retrieved: {response_context}")
                else:
                    response_context = relationship_info
                    print(f"Relationship inquiry response: {response_context}")
            elif is_friend_inquiry(user_input, known_friend_names):
                print("Detected friend inquiry in user input")
                friend_data = handle_friend_inquiry(user_input, friend_name)

                if friend_data is None:
                    response_context = f"Sorry, I don't understand the request."
                    print("Friend inquiry resulted in no information")
                else:
                    response_context = friend_data
                    print(f"Friend data for {friend_name}: {response_context}")
            elif is_general_inquiry(user_input):
                print("Detected general inquiry in user input")
                user_data = get_friend_data(friend_name)
                response_context = user_data
                print(f"General inquiry response for {friend_name}: {response_context}")
            else:
                response_context = f"Sorry, I don't understand the request."
                print("User input did not match any inquiry type")

            # Apply guardrails for sensitive topics
            response_context = check_sensitive_topics(json.dumps(response_context, indent=2), user_input)
            # print(f"Response context after applying sensitive topic guardrails: {response_context}")

            # Summarize conversation history to maintain context
            session_histories[session_id] = update_history_with_extracted_info(session_histories[session_id], user_input, response_context)
            conversation_history = session_histories[session_id]
            conversation_history.append({"role": "system", "content": summarize_conversation(session_histories[session_id])})
            conversation_history = truncate_history(conversation_history)
            # print(f"Conversation history: {conversation_history}")

            # Custom GPT simulation context for Brendan with expanded detail
            brendan_context = f"""
            Brendan is designed as a sassy, sarcastic chatbot, engaging users with a playful, sharp-witted manner that adapts to the personalities and interests of the user's friends.
            Brendan tailors each conversation to the friend's likes, personalities, and goals.
            This session is with {friend_name}.
            Context: {truncate_text(json.dumps(response_context, indent=2))}
            """

            if friend_name == "Fabio":
                brendan_context = f"""
                Brendan is not friendly, more reluctant, more sarcastic, sassy but still performs its usual functionality when talking to Fabio. Using its sharp-witted manner that adapts to the personalities and interests of the user's friends.
                Brendan tailors each conversation to the friend's likes, personalities, and goals.
                This session is with {friend_name}.
                Context: {truncate_text(json.dumps(response_context, indent=2))}
                """

            # print(f"Brendan context: {brendan_context}")

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=conversation_history + [{"role": "system", "content": brendan_context}, {"role": "user", "content": user_input}]
            )
            # print(f"OpenAI response: {response}")

            session_histories[session_id].append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            # Ensure response is within the character limit for Discord
            messages_to_send = split_message(response['choices'][0]['message']['content'])
            # print(f"Messages to send: {messages_to_send}")

            # Generate TTS audio concurrently within the typing context
            audio_path = await generate_custom_tts(response['choices'][0]['message']['content'])
            print(f"Audio path: {audio_path}")

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Sorry, I couldn't process your request at the moment.")
            return
        
    # Send text and play TTS simultaneously after the typing indicator stops
    async def send_text_and_play_tts():
        print("Sending text and playing TTS")
        for msg in messages_to_send:
            await message.channel.send(msg)
        if audio_path and message.guild.voice_client:
            voice_client = message.guild.voice_client
            voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=audio_path), after=lambda e: print('done', e))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            os.remove(audio_path)
            print("Audio played and file removed")
        elif not message.guild.voice_client:
            await message.channel.send("I need to be in a voice channel to speak!")
            print("Bot not in voice channel")

    # Run the text sending and TTS playback concurrently
    await asyncio.gather(send_text_and_play_tts())
