import os
import json
from datetime import datetime

FEEDBACK_DIR = 'data/feedback'

def initialize_feedback_directory():
    if not os.path.exists(FEEDBACK_DIR):
        os.makedirs(FEEDBACK_DIR)

def save_feedback(user_input, discord_name):
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "user": discord_name,
        "feedback": user_input
    }
    feedback_dir = "feedback"
    if not os.path.exists(feedback_dir):
        os.makedirs(feedback_dir)
    feedback_file = os.path.join(feedback_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_feedback.json")
    with open(feedback_file, "w") as file:
        json.dump(feedback_data, file, indent=4)
    print(f"Feedback saved to {feedback_file}")
    
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
