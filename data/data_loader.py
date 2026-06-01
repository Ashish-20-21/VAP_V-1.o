import json
import os

# ------------------------
# BASE PATH
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------
# CORE LOADER
# ------------------------
def load(filename):
    """
    Load any JSON file from the data/ folder.
    Usage: load("jokes") → returns full dict
    """
    file_path = os.path.join(BASE_DIR, f"{filename}.json")

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[data_loader] Failed to load {filename}.json: {e}")
        return None


# ------------------------
# SPECIFIC GETTERS
# ------------------------
def get_jokes():
    data = load("jokes")
    if not data:
        return []
    return data.get("jokes", [])


def get_quotes():
    data = load("quotes")
    if not data:
        return []
    return data.get("quotes", [])


# ------------------------
# FUTURE GETTERS (ready to add)
# ------------------------
# def get_facts():
#     data = load("facts")
#     return data.get("facts", []) if data else []

# def get_news():
#     data = load("news")
#     return data.get("news", []) if data else []
