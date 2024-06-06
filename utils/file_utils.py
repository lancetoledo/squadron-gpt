import json
import os
from docx import Document
from config import RELATIONSHIPS_DATA1, RELATIONSHIPS_DATA2, FRIEND_DATA1, FRIEND_DATA2

def load_json_files(directory):
    # Initialize data structure to hold friends and relationships data
    data = {"friends": [], "relationships": []}
    # List of JSON files to be loaded from environment variables
    json_files = [
        RELATIONSHIPS_DATA1,
        RELATIONSHIPS_DATA2,
        FRIEND_DATA1,
        FRIEND_DATA2
    ]
    # Iterate through each JSON file
    for file_name in json_files:
        file_path = os.path.join(directory, file_name)
        try:
            # Open and load JSON file data
            with open(file_path, "r") as file:
                file_data = json.load(file)
                # Extend friends and relationships data based on file content
                if "friends" in file_data:
                    data["friends"].extend(file_data.get("friends", []))
                if "relationships" in file_data:
                    data["relationships"].append(file_data)
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            print(f"Error decoding JSON from file {file_name}: {e}")
        except Exception as e:
            # Handle any other unexpected errors
            print(f"Unexpected error with file {file_name}: {e}")
    # Return the combined data from all JSON files
    return data

def parse_docx(file_path):
    # Open and read the content of a DOCX file
    print(f"Parsing DOCX file: {file_path}")
    doc = Document(file_path)
    data = {}
    current_key = None
    # Iterate through each paragraph in the DOCX file
    for para in doc.paragraphs:
        text = para.text.strip()
        # Check for key-value pairs separated by a colon
        if ":" in text:
            key, value = text.split(':', 1)
            data[key.strip()] = value.strip()
            current_key = key.strip()
        elif current_key:
            # Append text to the current key's value if no new key is found
            data[current_key] += f" {text}"
    # Return the parsed data
    return data

