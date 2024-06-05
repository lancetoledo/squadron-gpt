import json
from text_processing.spacy_setup import nlp
from utils.file_utils import load_json_files
from config import STATIC_FRIEND_DATA


friend_data_json = load_json_files("data")

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

    friend_data_json = load_json_files("data")
    for friend in friend_data_json.get("friends", []):
        if friend.get("name").lower() == friend_name.lower():
            return friend

    return {}

# Function to find relationships for a specific person and target
def find_relationships(person_name, target_friend_name):
    print(f"Finding relationship for {person_name} and {target_friend_name}")
    relationships_info = {}

    friend_data_json = load_json_files("data")
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
def handle_friend_inquiry(user_input, user_name, known_friend_names, nickname_to_full_name):
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
def handle_relationship_inquiry(user_input, friend_name, primary_person, known_friend_names):
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