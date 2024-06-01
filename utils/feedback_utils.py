import os
import json
from datetime import datetime

FEEDBACK_DIR = 'data/feedback'

def initialize_feedback_directory():
    if not os.path.exists(FEEDBACK_DIR):
        os.makedirs(FEEDBACK_DIR)

def write_feedback_to_file(feedback_data):
    initialize_feedback_directory()
    filename = f"{FEEDBACK_DIR}/feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(feedback_data, f, indent=4)

def detect_and_handle_feedback(message):
    # Placeholder function to detect feedback
    # Replace with actual feedback detection logic
    feedback_keywords = ['feedback', 'suggestion', 'issue']
    if any(keyword in message.content.lower() for keyword in feedback_keywords):
        feedback_data = {
            'user': message.author.name,
            'user_id': message.author.id,
            'message': message.content,
            'timestamp': str(datetime.now())
        }
        write_feedback_to_file(feedback_data)
        return True
    return False
