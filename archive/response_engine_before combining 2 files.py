import random

# ------------------------
# CONTENT PLUGINS that get "once more" prompt
# ------------------------
REPEATABLE_PLUGINS = ["joke", "quote"]


def respond(result):

    # ------------------------
    # SUGGESTION
    # ------------------------
    if result.get("type") == "suggestion":
        options = result.get("options", [])
        return f"You usually open {options[0]} at this time. Want me to open it? Say yes or tell me what you need."

    # ------------------------
    # ERROR
    # ------------------------
    if result.get("type") == "error":
        error_type = result.get("error_type")

        error_map = {
            "unknown_command": "I didn't understand that A.P. Try something like — open chrome, or tell me a joke.",
            "missing_target": "Please tell me what to open A.P.",
            "nothing_to_confirm": "Nothing to confirm. What would you like to do?",
            "nothing_to_repeat": "Nothing to repeat A.P. Ask me a joke or a quote first.",
            "suggestion_cooldown": "Give me a moment before I suggest again.",
            "no_suggestions_available": "No suggestions right now. Tell me what you need.",
            "suggestion_rejected": "Alright, what would you like instead?",
            "unknown_execution_mode": "Something went wrong internally."
        }

        return error_map.get(error_type, "Something went wrong A.P.")

    # ------------------------
    # ACTION RESULT
    # ------------------------
    if result.get("type") == "action_result":
        results = result.get("results", [])

        if not results:
            return "Something went wrong."

        first = results[0]
        status = first.get("status")
        message = first.get("message", "")
        plugin_name = first.get("app", "")

        if status == "success":
            response = _format_success(message, plugin_name)

            # ------------------------
            # ONCE MORE PROMPT
            # for joke and quote only
            # ------------------------
            if plugin_name in REPEATABLE_PLUGINS:
                response += "\n\nWant to hear another one? Say — once more."

            return response

        else:
            return f"Sorry A.P., {message}"

    # ------------------------
    # FALLBACK
    # ------------------------
    return result.get("message", "Something went wrong.")


# ------------------------
# HELPERS
# ------------------------
def _format_success(message, plugin_name):

    # content plugins — speak the content directly with personality
    if plugin_name == "joke":
        intros = [
            f"Alright A.P., here's one — {message}",
            f"Got one for you — {message}",
            f"Sure buddy — {message}",
            f"Here we go — {message}"
        ]
        return random.choice(intros)

    if plugin_name == "quote":
        intros = [
            f"Sure A.P. — {message}",
            f"Here's one for you — {message}",
            f"Alright, listen to this — {message}",
            f"This one hits — {message}"
        ]
        return random.choice(intros)

    if plugin_name == "screenshot":
        return f"Done. {message}"

    if plugin_name == "timer":
        return message

    if plugin_name == "playlist":
        return message

    if plugin_name == "weather":
        return message

    if plugin_name == "take_note":
        return f"Got it. {message}"

    if plugin_name == "search":
        return message

    # generic success
    responses = [
        message,
        f"Done. {message}",
        f"Alright A.P., {message}",
        f"Got it. {message}"
    ]
    return random.choice(responses)
