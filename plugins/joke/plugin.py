import random
import sys
import os

# ------------------------
# PATH FIX
# ------------------------
# Ensures data/ folder is accessible from plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from data.data_loader import get_jokes


# ------------------------
# MAIN
# ------------------------
def run(command=None):
    jokes = get_jokes()

    if not jokes:
        return "Sorry A.P., I couldn't find any jokes right now."

    joke = random.choice(jokes)
    return joke
