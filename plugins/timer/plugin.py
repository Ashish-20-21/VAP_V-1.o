import subprocess
import re

# ------------------------
# CONFIG
# ------------------------
CHROME_PATH    = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE = "--profile-directory=Profile 3"


# ------------------------
# HELPERS
# ------------------------
def extract_duration(raw):
    """
    Extracts number from timer command string.
    Handles: "timer 5", "set timer 10 minutes", "remind me in 3"
    Returns (number, unit) or (None, None)
    """
    if not raw:
        return None, None

    raw = str(raw).lower()

    # detect seconds — Chrome timer only supports minutes
    # FIX #5 — catch sec/second/seconds and return unit="sec"
    has_seconds = bool(re.search(r'\b(sec|secs|second|seconds)\b', raw))

    # extract first number
    match = re.search(r'\b(\d+)\b', raw)
    if match:
        return int(match.group(1)), "sec" if has_seconds else "min"

    return None, None


# ------------------------
# MAIN
# ------------------------
def run(input_data=None):

    duration, unit = extract_duration(input_data)

    # FIX #5 — seconds not supported via Chrome URL — give honest message
    if unit == "sec":
        return "Only minute timers for now A.P. Try — timer 5."

    # FIX #1 — no two-step flow. If no number found, give usage hint directly.
    # "timer" alone → clean usage message, no NEEDS_INPUT state machine.
    if not duration:
        return "Say it like — timer 5 or set timer 10 minutes A.P."

    url = f"https://www.google.com/search?q={duration}+minute+timer"

    try:
        subprocess.Popen([CHROME_PATH, CHROME_PROFILE, url])
        return f"{duration} minute timer started — check Chrome."

    except Exception:
        # fallback — try default browser
        try:
            import webbrowser
            webbrowser.open(url)
            return f"{duration} minute timer started."
        except Exception as e:
            return f"Timer failed — {e}"





# import subprocess
# import re
#
# # ------------------------
# # CONFIG
# # ------------------------
# CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
# CHROME_PROFILE = "--profile-directory=Profile 3"
#
# # ------------------------
# # HELPERS
# # ------------------------
# def extract_duration(input_data):
#     """
#     Extracts number from timer command.
#     Handles: "5", "5 minutes", "set timer 5", "10-minute timer"
#     """
#     if isinstance(input_data, dict):
#         raw = input_data.get("raw_input", "")
#     else:
#         raw = str(input_data)
#
#     # find first number in the string
#     match = re.search(r'\b(\d+)\b', raw)
#     if match:
#         return int(match.group(1))
#     return None
#
#
# # ------------------------
# # MAIN
# # ------------------------
# def run(input_data=None):
#     duration = extract_duration(input_data) if input_data else None
#
#     if not duration:
#         # default fallback — ask VAP to prompt user
#         return "NEEDS_INPUT:How many minutes for the timer, A.P.?"
#
#     url = f"https://www.google.com/search?q={duration}+minute+timer"
#
#     try:
#         subprocess.Popen([CHROME_PATH, PROFILE, url])
#         return f"{duration} minute timer started — check Chrome."
#
#     except Exception as e:
#         # fallback — try default browser
#         try:
#             import webbrowser
#             webbrowser.open(url)
#             return f"{duration} minute timer started."
#         except Exception as e2:
#             return f"Timer failed — {e2}"
