import json

def truncate_text(text, max_length=1500):
    # Truncate the text to the specified maximum length
    truncated_text = text[:max_length] if len(text) > max_length else text
    # print(f"Truncated text to {max_length} characters: {truncated_text[:50]}... (length: {len(truncated_text)})")
    return truncated_text

def summarize_context(context):
    # Convert the context dictionary to a JSON string and truncate it
    context_json = json.dumps(context)
    summarized_context = truncate_text(context_json, max_length=1500)
    # print(f"Summarized context: {summarized_context[:50]}... (length: {len(summarized_context)})")
    return summarized_context

def clean_text_for_tts(text):
    # List of characters to remove
    characters_to_remove = ['#', '*', '_', '~', '`', '^', '[', ']', '{', '}', '|', '\\']
    # List of characters to replace with a space
    characters_to_replace_with_space = ['@', '/', '>', '<']
    
    # Remove unwanted characters
    for char in characters_to_remove:
        text = text.replace(char, '')
    
    # Replace certain characters with a space
    for char in characters_to_replace_with_space:
        text = text.replace(char, ' ')
    
    # Replace double spaces with a single space
    text = text.replace('  ', ' ')
    
    # print(f"Cleaned text for TTS: {text[:50]}... (length: {len(text)})")
    return text
