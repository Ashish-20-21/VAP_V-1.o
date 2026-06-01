import json
import os
import re

# ------------------------
# LOAD APP NAMES FROM REGISTRY
# Loaded once at startup — used for smart target matching
# ------------------------
def load_app_names():
    try:
        base_dir  = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "registry", "apps.json")
        with open(json_path, "r") as f:
            apps = json.load(f)
        return list(apps.keys())
    except Exception:
        return []

APP_NAMES = load_app_names()


# ------------------------
# HELPERS
# ------------------------

def split_targets(text):
    """
    Splits multi-app input by 'and' and commas.
    'open chrome and notepad' → ['chrome', 'notepad']
    """
    text = text.lower()
    text = re.sub(r'\band\b', ',', text)
    parts = [p.strip() for p in text.split(',')]
    return [p for p in parts if p]


def match_app(word):
    """
    Tries to match a word to a known app name.
    Three strategies: exact → part-word → fused-word
    Returns matched app name or None.
    """
    word = word.lower().strip()

    # skip very short words unless they exist exactly in registry
    if len(word) <= 2 and word not in APP_NAMES:
        return None

    # 1. Exact match
    if word in APP_NAMES:
        return word

    # 2. Word matches one part of multi-word app name
    # "file" → "file explorer", "wise" → "wise memory"
    for app in APP_NAMES:
        if word in app.split():
            return app

    # 3. Fused word match — handles "taskmanager" → "task manager"
    for app in APP_NAMES:
        if app.replace(" ", "") == word.replace(" ", ""):
            return app

    return None


def resolve_targets(parts):
    """
    Validates a list of word-parts against known app names.
    Returns only confirmed matches.
    """
    matched = []
    for word in parts:
        match = match_app(word)
        if match and match not in matched:
            matched.append(match)
    return matched


# ------------------------
# MAIN PARSER
# ------------------------
# At the top of parse() in intent_engine.py
# Strip wake word if it slipped through to parser
# vap_core handles it but this is a safety net

WAKE_WORD_PREFIX = "hey vap"

def parse(user_input):
    # safety strip — wake word guard in case it reaches parser
    WAKE_WORD_PREFIX = "hey vap"
    cleaned = user_input.lower().strip()
    if cleaned.startswith(WAKE_WORD_PREFIX):
        user_input = user_input[len(WAKE_WORD_PREFIX):].strip()

    # rest of existing parse() code unchanged below
    command = user_input.lower().strip()
    words = command.split()
    # ... existing code unchanged
    result = {
        "intent":      None,
        "targets":     [],
        "raw_input":   user_input,
        "raw_targets": [],      # everything user said as target, matched or not
        "content":     None     # inline content for notes, timer duration, search query
    }

    if not words:
        return result

    # ------------------------
    # CONFIRM
    # User accepting a suggestion
    # ------------------------
    if command in ["yes", "yeah", "yep", "sure", "open it", "do it"]:
        result["intent"] = "confirm"
        return result

    # ------------------------
    # NO ACTION
    # User explicitly rejecting — "no_action" not "reject"
    # DE holds last_suggestion for comparative learning
    # ------------------------
    if command in ["no", "nope", "nah"]:
        result["intent"] = "no_action"
        return result

    # ------------------------
    # STOP CONTENT
    # FIX #12 — user wants to exit joke/quote loop naturally
    # "done", "end", "stop it", "enough" → stop_content intent
    # DE clears last_content_intent on this
    # ------------------------
    if command in ["done", "end", "stop it", "enough", "that's enough", "ok enough"]:
        result["intent"] = "stop_content"
        return result

    # ------------------------
    # REPEAT LAST CONTENT
    # "once more" flow for joke/quote
    # ------------------------
    repeat_triggers = ["once more", "again", "another one", "one more"]
    if any(command == t or command.startswith(t) for t in repeat_triggers):
        result["intent"] = "repeat_last"
        return result

    # ------------------------
    # EXPLICIT SUGGEST REQUEST
    # ------------------------
    if "suggest" in command:
        result["intent"] = "suggest"
        return result

    # ------------------------
    # TAKE NOTE
    # Captures everything between trigger and stop word "end"
    # ------------------------
    note_triggers = ["take a note", "write a note", "note this", "take note"]
    for trigger in note_triggers:
        if command.startswith(trigger):
            raw_content = user_input[len(trigger):].strip()
            # strip stop word "end" from the tail
            if raw_content.lower().endswith(" end"):
                raw_content = raw_content[:-4].strip()
            elif raw_content.lower() == "end":
                raw_content = ""
            result["intent"]  = "take_note"
            result["content"] = raw_content if raw_content else None
            return result

    # ------------------------
    # OPEN NOTE
    # FIX #4 — added singular variants "show note", "my note"
    # ------------------------
    if command in ["open note", "open notes", "show notes", "show note",
                   "my notes", "my note"]:
        result["intent"] = "open_note"
        return result

    # ------------------------
    # TIMER
    # FIX #1 — solo "timer" with no number returns timer_no_input
    # so response_engine can give a clean usage hint
    # ------------------------
    timer_triggers = ["set timer", "set a timer", "remind me in"]
    if any(trigger in command for trigger in timer_triggers):
        result["intent"]  = "set_timer"
        result["content"] = user_input
        return result

    # "timer" alone as exact word — check if number present
    if "timer" in words:
        result["intent"]  = "set_timer"
        result["content"] = user_input   # plugin will extract number
        return result

    # ------------------------
    # SEARCH WEB
    # FIX #11 — solo "search" now returns search_no_query error
    # ------------------------
    if words[0] == "search":
        if len(words) > 1:
            query = " ".join(words[1:])
            result["intent"]  = "search_web"
            result["content"] = query
            result["targets"] = words[1:]
        else:
            # solo "search" with no query
            result["intent"] = "search_no_query"
        return result

    # ------------------------
    # CONTENT PLUGINS
    # Joke and quote — spoken content, supports "once more"
    # ------------------------
    joke_triggers = ["tell me a joke", "joke", "make me laugh", "say something funny"]
    if any(t in command for t in joke_triggers):
        result["intent"]  = "plugin"
        result["targets"] = ["joke"]
        return result

    quote_triggers = ["tell me a quote", "quote", "inspire me", "say a quote"]
    if any(t in command for t in quote_triggers):
        result["intent"]  = "plugin"
        result["targets"] = ["quote"]
        return result

    # ------------------------
    # SYSTEM INFO
    # ------------------------

    sysinfo_triggers = ["sysinfo", "system info", "system status"]

    if any(t in command for t in sysinfo_triggers):
        result["intent"] = "plugin"
        result["targets"] = ["system_info"]
        return result

    # ------------------------
    # SCREENSHOT
    # ------------------------
    screenshot_triggers = ["take screenshot", "screenshot", "capture screen",
                           "take a screenshot", "capture the screenshot"]
    if any(t in command for t in screenshot_triggers):
        result["intent"]  = "plugin"
        result["targets"] = ["screenshot"]
        return result

    # ------------------------
    # PLAYLIST
    # FIX #10 — added "play the playlist"
    # ------------------------
    playlist_triggers = ["play playlist", "hit my playlist", "play my songs",
                         "play my playlist", "play music", "play songs",
                         "play the playlist"]
    if any(t in command for t in playlist_triggers):
        result["intent"]  = "plugin"
        result["targets"] = ["playlist"]
        return result

    # ------------------------
    # SYSTEM CONTROL (volume / brightness / mute)
    # ------------------------
    system_control_triggers = ["volume", "vol", "brightness", "bright", "mute", "unmute"]

    if any(t in command for t in system_control_triggers):
        result["intent"] = "plugin"
        result["targets"] = ["system_control"]
        result["content"] = user_input  # full raw input — plugin needs it
        return result

    # ------------------------
    # WEATHER
    # ------------------------
    weather_triggers = ["weather", "how's the weather", "show weather",
                        "what's the weather", "check weather",
                        "tell me abt weather", "tell me about weather"]
    if any(t in command for t in weather_triggers):
        result["intent"]  = "plugin"
        result["targets"] = ["weather"]
        return result

    # ------------------------
    # APP OPEN / CLOSE INTENTS
    # ------------------------
    open_words  = ["open", "launch", "start", "run"]
    close_words = ["close", "stop", "quit"]

    if any(w in words for w in open_words):
        result["intent"] = "open_app"
    elif any(w in words for w in close_words):
        result["intent"] = "close_app"

    # ------------------------
    # TARGET EXTRACTION
    # Remove intent keywords, split by and/comma, match against registry
    # ------------------------
    cleaned      = [w for w in words if w not in open_words and w not in close_words]
    cleaned_text = " ".join(cleaned)
    parts        = split_targets(cleaned_text)
    matched      = resolve_targets(parts)

    result["targets"]     = matched   # registry-verified app names
    result["raw_targets"] = parts     # raw words — used by DE for app_not_found detection

    # ------------------------
    # FALLBACK — single unrecognised word
    # FIX #7 — only fires if match_app() confirms a registry match
    # No match → intent stays None → DE returns unknown_command
    # Prevents garbage words routing to app_not_found
    # ------------------------
    if not result["intent"] and len(words) == 1:
        single_match = match_app(words[0])
        if single_match:
            # confirmed registry match — treat as open_app
            result["intent"]  = "open_app"
            result["targets"] = [single_match]
        # else: intent stays None → unknown_command in DE

    return result









