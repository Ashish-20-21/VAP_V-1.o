# dev_tools/usage_snapshot.py

import json
import os
import datetime


SNAPSHOT_FILE = "usage_snapshot.json"

# FOR GETTING PATH
# print("SNAPSHOT FILE PATH:", os.path.abspath(SNAPSHOT_FILE))

# ------------------------
# SAVE SNAPSHOT
# ------------------------
def save_snapshot(data):
    try:
        with open(SNAPSHOT_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"[DEV ERROR] Failed to save snapshot: {e}")


# ------------------------
# LOAD SNAPSHOT
# ------------------------

def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return None

    try:
        with open(SNAPSHOT_FILE, "r") as f:
            data = json.load(f)

        # 🔥 FIX: convert last_run back to datetime
        for app, info in data.items():
            last_run = info.get("last_run")
            if isinstance(last_run, str):
                try:
                    info["last_run"] = datetime.datetime.fromisoformat(last_run.replace(" ", "T"))
                except:
                    try:
                        info["last_run"] = datetime.strptime(last_run, "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        info["last_run"] = None

        return data

    except Exception:
        return None


# ------------------------
# CHECK IF SNAPSHOT EXISTS
# ------------------------
def snapshot_exists():
    return os.path.exists(SNAPSHOT_FILE)