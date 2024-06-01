import json

def truncate_text(text, max_length=1500):
    return text[:max_length] if len(text) > max_length else text

def summarize_context(context):
    context_json = json.dumps(context)
    return truncate_text(context_json, max_length=1500)
