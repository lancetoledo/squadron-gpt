import json

def truncate_text(text, max_length=1500):
    return text[:max_length] if len(text) > max_length else text

def summarize_context(context):
    context_json = json.dumps(context)
    return truncate_text(context_json, max_length=1500)

def clean_text_for_tts(text):
    characters_to_remove = ['#', '*', '_', '~', '`', '^', '[', ']', '{', '}', '|', '\\']
    characters_to_replace_with_space = ['@', '/', '>', '<']
    for char in characters_to_remove:
        text = text.replace(char, '')
    for char in characters_to_replace_with_space:
        text = text.replace(char, ' ')
    text = text.replace('  ', ' ')
    return text

