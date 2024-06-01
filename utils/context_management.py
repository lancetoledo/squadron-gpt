def update_history_with_extracted_info(history, user_message, brendan_response):
    # Add the user's message and Brendan's response to the conversation history
    print("Updating history with user message and Brendan's response")
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": brendan_response})
    return truncate_history(history)

def truncate_history(history, max_tokens=8192):
    # Ensure the total token count in the history does not exceed the maximum allowed
    print("Truncating history to fit within token limits")
    total_tokens = sum([len(item["content"].split()) for item in history])
    while (total_tokens > max_tokens) and history:
        print(f"Total tokens: {total_tokens} exceeds max tokens: {max_tokens}, removing oldest message")
        history.pop(0)
        total_tokens = sum([len(item["content"].split()) for item in history])
    return history

def summarize_conversation(history):
    # Summarize the last few messages in the conversation history
    print("Summarizing conversation history")
    if len(history) > 5:
        summarized_history = "Summary of previous messages: " + " ".join([msg["content"] for msg in history[-5:]])
    else:
        summarized_history = " ".join([msg["content"] for msg in history])
    # print(f"Summarized history: {summarized_history}")
    return summarized_history

# Function to split long messages into chunks within the limit
def split_message(message, max_length=2000):
    # Split a long message into smaller chunks if it exceeds the maximum length
    print(f"Splitting message into chunks with max length {max_length}")
    if len(message) <= max_length:
        return [message]
    else:
        return [message[i:i+max_length] for i in range(0, len(message), max_length)]
