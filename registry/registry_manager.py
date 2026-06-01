# Key Takeaway — 3 improvements in one change:

# Performance → JSON loads once not every call
# Simplicity → One function instead of whole class
# Single source of truth → Only registry touches apps.json

# Load apps.json once (global)
import os
import json
from difflib import get_close_matches

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "apps.json")
try:
    with open(JSON_PATH, "r") as f:
        APPS = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load apps.json: {e}")
    APPS = {}


def get_app_config(app_name):
    app_name = app_name.lower()

    # ------------------------
    # 1. Exact match
    # ------------------------
    if app_name in APPS:
        app_config = APPS[app_name]

    else:
        app_config = None

        # ------------------------
        # 2. Partial match (safe)
        # ------------------------
        for key in APPS:
            if app_name in key:
                app_config = APPS[key]
                break

        # ------------------------
        # 3. Fuzzy match (fallback only)
        # ------------------------
        if not app_config:
            matches = get_close_matches(app_name, APPS.keys(), n=1, cutoff=0.75)
            if matches:
                app_config = APPS[matches[0]]

    # ------------------------
    # 4. Not found
    # ------------------------
    if not app_config:
        return None

    # ------------------------
    # 5. Validate config
    # ------------------------
    method = app_config.get("method")
    command = app_config.get("command")

    if not method or not command:
        return None

    # ------------------------
    # 6. Return clean config
    # ------------------------
    result = {
        "method": method,
        "command": command
    }
    if app_config.get("process"):
        result["process"] = app_config["process"]
    return result
# SSD Disk~0.5-1ms❌ Old way — reading file
# RAM~0.001ms✅ New way — already loaded

# ANALOGY :

# ❌ Old way = Every time you cook
# you go to SUPERMARKET to buy ingredients
# → takes 30 minutes every meal!

# ✅ New way = Buy all ingredients ONCE
# store them in your KITCHEN (RAM)
# → cook instantly whenever needed! ⚡

# apps.json typical size = 2KB - 5KB
# RAM on your PC        = 8GB - 16GB
#
# That's like asking:
# "Will one grain of sand fill a swimming pool?" 🏊

# -------------------------------
# Previous code before phase5.5


# import json
# import os
#
# REGISTRY_FILE = os.path.join(
#     os.path.dirname(__file__),
#     "apps.json"
# )
#
# class RegistryManager:
#
#     def __init__(self):
#         self.apps = self.load_registry()
#
#     def load_registry(self):
#         if not os.path.exists(REGISTRY_FILE):
#             print("Registry file not found!")
#             return {}
#
#         with open(REGISTRY_FILE, "r") as f:
#             data = json.load(f)
#             print(f"Loaded {len(data)} apps")  # 👈 ADD THIS
#             return data
#
#     def find_app(self, user_input):
#         user_input = user_input.lower().strip()  # 🔥 FIX 1
#
#         matches = []
#
#         for app_name in self.apps:
#             app_name_clean = app_name.lower().strip()  # 🔥 FIX 2
#
#             if user_input in app_name_clean:
#                 matches.append(app_name)
#
#         if len(matches) == 0:
#             return None
#
#         return matches[0]
#
#     def get_app_path(self, app_name):
#         return self.apps.get(app_name, None)