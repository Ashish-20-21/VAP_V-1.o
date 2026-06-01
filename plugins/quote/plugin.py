import random
import sys
import os

# ------------------------
# PATH FIX
# ------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from data.data_loader import get_quotes


# ------------------------
# MAIN
# ------------------------
def run(command=None):
    quotes = get_quotes()

    if not quotes:
        return "Sorry A.P., I couldn't find any quotes right now."

    quote = random.choice(quotes)
    return f'"{quote}"'
