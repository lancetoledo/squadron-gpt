import os
import json
from datetime import datetime

FEEDBACK_DIR = 'data/feedback'  # Directory to store feedback files

def initialize_feedback_directory():
    # Create feedback directory if it doesn't exist
    if not os.path.exists(FEEDBACK_DIR):
        os.makedirs(FEEDBACK_DIR)
        print(f"Feedback directory created at: {FEEDBACK_DIR}")
    else:
        print(f"Feedback directory already exists at: {FEEDBACK_DIR}")

def save_feedback(user_input, discord_name):
    # Prepare feedback data with timestamp, user, and feedback content
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "user": discord_name,
        "feedback": user_input
    }
    # Ensure the feedback directory exists
    initialize_feedback_directory()
    # Save feedback to a JSON file named with current timestamp
    feedback_file = os.path.join(FEEDBACK_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_feedback.json")
    with open(feedback_file, "w") as file:
        json.dump(feedback_data, file, indent=4)
    print(f"Feedback saved to {feedback_file}")
