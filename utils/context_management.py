def update_history_with_extracted_info(history, user_message, brendan_response):
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": brendan_response})
    return truncate_history(history)

def truncate_history(history, max_tokens=8192):
    total_tokens = sum([len(item["content"].split()) for item in history])
    while (total_tokens > max_tokens) and history:
        history.pop(0)
        total_tokens = sum([len(item["content"].split()) for item in history])
    return history

def summarize_conversation(history):
    if len(history) > 5:
        summarized_history = "Summary of previous messages: " + " ".join([msg["content"] for msg in history[-5:]])
    else:
        summarized_history = " ".join([msg["content"] for msg in history])
    return summarized_history

# Function to split long messages into chunks within the limit
def split_message(message, max_length=2000):
    if len(message) <= max_length:
        return [message]
    else:
        return [message[i:i+max_length] for i in range(0, len(message), max_length)]