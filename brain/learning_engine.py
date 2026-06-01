import json
import os
import datetime
from brain.usage_engine import apply_merge

FILE_PATH = "learning_data.json"


def load_data():
    if not os.path.exists(FILE_PATH):
        return {}

    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_data(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def ensure_schema(data, app):
    if app not in data:
        data[app] = {
            "boost": 0,
            "last_learned": None
        }
    else:
        data[app].setdefault("boost", 0)
        data[app].setdefault("last_learned", None)


def update_acceptance(app):
    # ✅ Normalize app name BEFORE storing (prevents duplicates like youtube/YouTube/yt)
    app = apply_merge(app)

    data = load_data()

    ensure_schema(data, app)

    data[app]["boost"] += 1
    data[app]["last_learned"] = datetime.datetime.now().isoformat()

    save_data(data)


def update_comparative(suggested, actual):
    # ✅ Normalize both apps BEFORE storing
    suggested = apply_merge(suggested)
    actual = apply_merge(actual)

    if suggested == actual:
        return  # avoid useless update

    data = load_data()

    for app in [suggested, actual]:
        ensure_schema(data, app)

    data[suggested]["boost"] -= 1
    data[actual]["boost"] += 1

    now = datetime.datetime.now().isoformat()
    data[suggested]["last_learned"] = now
    data[actual]["last_learned"] = now

    save_data(data)


def get_learning_data():
    raw_data = load_data()
    clean_data = {}

    for app, info in raw_data.items():
        # ✅ Normalize key (youtube / yt / YouTube → YouTube)
        normalized = apply_merge(app)

        if normalized not in clean_data:
            clean_data[normalized] = info.copy()
        else:
            # ✅ Merge boost values
            clean_data[normalized]["boost"] += info.get("boost", 0)

            # ✅ Keep MOST RECENT last_learned (critical for decay logic)
            existing = clean_data[normalized].get("last_learned")
            incoming = info.get("last_learned")

            if incoming and existing:
                # ISO format → safe string comparison
                if incoming > existing:
                    clean_data[normalized]["last_learned"] = incoming
            elif incoming:
                clean_data[normalized]["last_learned"] = incoming

    return clean_data
# 1/5 - date for keeping track when changes have been done

