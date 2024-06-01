import json
import os
from docx import Document

def load_json_files(file_pattern):
    data = {"friends": [], "lance_relationships": []}
    json_files = [
        "Lance_Relationships_Detailed.json",
        "Navi_Relationships_Detailed.json",
        "squadron1.json",
        "squadron2.json"
    ]
    for file_name in json_files:
        try:
            with open(file_name, "r") as file:
                file_data = json.load(file)
                if "friends" in file_data:
                    data["friends"].extend(file_data.get("friends", []))
                if "relationships" in file_data:
                    data["lance_relationships"].append(file_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {file_name}: {e}")
        except Exception as e:
            print(f"Unexpected error with file {file_name}: {e}")
    return data

def parse_docx(file_path):
    doc = Document(file_path)
    data = {}
    current_key = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if ":" in text:
            key, value = text.split(':', 1)
            data[key.strip()] = value.strip()
            current_key = key.strip()
        elif current_key:
            data[current_key] += f" {text}"
    return data
