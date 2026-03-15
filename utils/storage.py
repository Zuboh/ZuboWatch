import json
import os

FILE_PATH = "storage.json"

if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as f:
        try:
            user_data = json.load(f)
        except json.JSONDecodeError:
            user_data = {}
else:
    user_data = {}

def save():
    with open(FILE_PATH, "w") as f:
        json.dump(user_data, f, indent=4)

def get_user_selections(user_id: int, category: str) -> set:
    return set(user_data.get(str(user_id), {}).get(category, []))

def set_user_selection(user_id: int, category: str, selections: set):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {}
    user_data[uid][category] = list(selections)
    save()

def clear_user(user_id: int):
    uid = str(user_id)
    if uid in user_data:
        user_data[uid] = {}
        save()