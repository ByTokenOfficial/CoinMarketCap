import json

def load_json_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        json_data = json.load(f)
    
    return json_data

def save_json_file(file_path, data):
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)