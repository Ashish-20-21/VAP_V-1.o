import datetime
import math
from brain.learning_engine import get_learning_data


# ------------------------
# CONFIG (tunable)
# ------------------------
WEIGHTS = {
    "usage": 0.4,
    "recency": 0.2,
    "learning": 0.35
}

MAX_LEARNING_IMPACT = 10


# ------------------------
# HELPERS
# ------------------------
def normalize(value, max_value):
    if max_value == 0:
        return 0
    return (value / max_value) * 10


def get_time_bucket(now):
    hour = now.hour

    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 22:
        return "evening"
    else:
        return "night"


def recency_score(last_run, now):
    if not last_run:
        return 0

    delta_hours = (now - last_run).total_seconds() / 3600

    if delta_hours < 1:
        return 10
    elif delta_hours < 6:
        return 7
    elif delta_hours < 24:
        return 5
    elif delta_hours < 72:
        return 2
    return 0


def decay(days):
    return math.exp(-0.05 * days)


# ------------------------
# MAIN FUNCTION
# ------------------------
def get_suggestion_scores(usage_data):
    scores = {}
    now = datetime.datetime.now()
    learning_data = get_learning_data()
    time_bucket = get_time_bucket(now)

    if not usage_data:
        return scores

    # normalization base
    max_count = max([data.get("count", 0) for data in usage_data.values()])

    for app, data in usage_data.items():
        count = data.get("count", 0)
        last_run = data.get("last_run")

        # ------------------------
        # 1. Usage
        # ------------------------
        usage = normalize(count, max_count)

        # ------------------------
        # 2. Recency
        # ------------------------
        recency = recency_score(last_run, now)

        # ------------------------
        # 3. Learning (with decay)
        # ------------------------
        learning = 0
        learn_data = learning_data.get(app, {})

        boost = learn_data.get("boost", 0)
        last_learned = learn_data.get("last_learned")

        if last_learned:
            try:
                last_dt = datetime.datetime.fromisoformat(last_learned)
                days = (now - last_dt).days
                learning = boost * decay(days)
            except ValueError:
                learning = boost
        else:
            learning = boost

        # clamp learning (stability)
        learning = max(min(learning, MAX_LEARNING_IMPACT), -MAX_LEARNING_IMPACT)

        # ------------------------
        # 4. Time Bonus (basic V1)
        # ------------------------
        time_bonus = 0
        if time_bucket == "morning" and app in ["chrome", "edge"]:
            time_bonus = 2
        elif time_bucket == "night" and app in ["pycharm", "vscode"]:
            time_bonus = 2

        # ------------------------
        # FINAL SCORE
        # ------------------------
        total = (
            (usage * WEIGHTS["usage"]) +
            (recency * WEIGHTS["recency"]) +
            (learning * WEIGHTS["learning"]) +
            time_bonus
        )

        scores[app] = round(total, 2)

    # return sorted scores (high → low)
    # print(scores)
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

