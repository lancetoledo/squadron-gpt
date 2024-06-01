import json

def truncate_text(text, max_length=1500):
    # Truncate the given text to the specified maximum length
    # print(f"Truncating text to {max_length} characters")
    return text[:max_length] if len(text) > max_length else text

def summarize_context(context):
    # Convert the context dictionary to a JSON string and truncate it
    # print(f"Summarizing context: {context}")
    context_json = json.dumps(context)
    return truncate_text(context_json, max_length=1500)
