import random

# ------------------------
# CONTENT PLUGINS that get "once more" prompt
# ------------------------
REPEATABLE_PLUGINS = ["joke", "quote"]

# ------------------------
# KNOWN PLUGINS — handled separately from app launches
# ------------------------
_KNOWN_PLUGINS = [
    "joke", "quote", "screenshot", "timer",
    "playlist", "weather", "take_note", "search",
    "system_control"
]

# ------------------------
# RESPONSE VARIANTS
# ------------------------
OPEN_SUCCESS = [
    "Alright A.P., opening {app} for you.",
    "Launching {app} now.",
    "Sure A.P., starting {app}.",
    "{app} coming right up.",
    "On it — opening {app}.",
    "Got it A.P., firing up {app}.",
]

OPEN_MULTI_SUCCESS = [
    "Alright A.P., opening {apps} for you.",
    "Launching {apps} now.",
    "On it — starting {apps}.",
    "Got it A.P., firing up {apps}.",
]

# ================================================================
# ✅ FIX 1 — CLOSE SUCCESS RESPONSES (NEW)
# ================================================================
CLOSE_SUCCESS = [
    "Closed {app} A.P.",
    "Done — {app} is shut down.",
    "Got it A.P., {app} is closed.",
    "{app} closed.",
]

SUGGESTION_PROMPTS = [
    "Hey A.P., you usually open {app} now. Say openit or something else?",
    "A.P., {app} feels right for now. Open it, or tell me what to open?",
    "Based on your habits, {app} is your go-to. Say Open it or pick another.",
    "You tend to open {app} around now. Yes to launch, or something different?",
]
ERROR_MAP = {
    "unknown_command": "Didn't catch that A.P. Try saying something like 'open youtube' or 'tell me a joke'.",
    "close_not_supported": "Close feature coming soon A.P. — use Task Manager for now.",
    "missing_target": "What do you want to open A.P.? Try 'open chrome' or 'open pycharm'.",
    "nothing_to_confirm": "Nothing to confirm A.P. — what would you like to open?",
    "nothing_to_repeat": "Nothing to repeat A.P. — ask me a joke or a quote first.",
    "suggestion_cooldown": "Just suggested that a moment ago A.P. — want me to open it?",
    "no_suggestions_available": "Not sure what to suggest right now A.P. Tell me what you need.",
    "no_action": "Okay A.P., let me know what you need.",
    "suggestion_rejected": "Okay A.P., what would you like to open?",
    "unknown_execution_mode": "Something went wrong on my end A.P. Try again.",
    "app_not_found": "Couldn't find that one A.P. Is it in the registry?",
    "search_no_query": "What do you want to search for A.P.? Try — search quantum computing.",
    "timer_seconds_unsupported": "Only minute timers for now A.P. Try — timer 5.",
    "close_app_web": "That app runs in the browser A.P. — press Ctrl+W to close the tab.",
    "missing_close_target": "What do you want to close A.P.? Try — close chrome or close notepad.",
}


# ------------------------
# MAIN RESPONDER
# ------------------------
def respond(result):
    if result.get("type") == "error" and result.get("error_type") == "suggestion_cooldown":
        app = result.get("context", {}).get("last_suggestion", "that app")
        return f"Just suggested {app} a moment ago A.P. — want me to open it?"

    if result.get("type") == "error" and result.get("error_type") == "app_not_found":
        app = result.get("context", {}).get("attempted_target", "that app")
        return f"Couldn't find '{app}' A.P. — not in the registry. Try adding it."

    if result.get("type") == "system_warning":
        return result.get("message", "System load is high A.P.")

    if result.get("type") == "suggestion":
        options = result.get("options", [])
        if not options:
            return "Not sure what to suggest right now A.P."

        top = options[0]
        response = random.choice(SUGGESTION_PROMPTS).format(app=top)

        if len(options) > 1:
            others = ", ".join(options[1:])
            response += f" (Also available: {others})"

        return response

    if result.get("type") == "error":
        error_type = result.get("error_type", "")
        return ERROR_MAP.get(error_type, "Something went wrong A.P. Try again.")

    # ------------------------
    # ACTION RESULT
    # ------------------------
    if result.get("type") == "action_result":
        results = result.get("results", [])

        # ------------------------
        # CLOSE RESULT
        # ------------------------
        if result.get("intent") == "close_app":
            success_apps = [r["app"] for r in results if r["status"] == "success"]
            info_results = [r for r in results if r["status"] == "info"]
            failed_apps = [r for r in results if r["status"] not in ("success", "info")]

            if info_results:
                return info_results[0]["message"]
            if success_apps:
                return random.choice(CLOSE_SUCCESS).format(app=success_apps[0])
            if failed_apps:
                return f"Couldn't close '{failed_apps[0]['app']}' A.P. — {failed_apps[0]['message']}"
            return "Something went wrong A.P."


        if not results:
            return "Something went wrong A.P."

        first = results[0]
        message = first.get("message", "")

        # ------------------------
        # PLUGIN RESULT
        # ------------------------
        if first.get("app") in _KNOWN_PLUGINS:
            if first.get("status") == "success":
                if message.startswith("NEEDS_INPUT:"):
                    return message.replace("NEEDS_INPUT:", "").strip()

                response = _format_plugin(message, first.get("app"))

                if first.get("app") in REPEATABLE_PLUGINS:
                    response += "\n\nWant to hear another one? Say — once more."

                return response
            else:
                return f"Sorry A.P., {message}"

        # ------------------------
        # APP RESULT
        # ------------------------
        success_apps = [r["app"] for r in results if r["status"] == "success"]
        info_results = [r for r in results if r["status"] == "info"]
        failed_apps = [r["app"] for r in results if r["status"] not in ("success", "info")]

        response_lines = []

        # ================================================================
        # ✅ FIX 1 — DETECT CLOSE INTENT (NEW)
        # We infer close by checking message content
        # ================================================================
        is_close_action = any(
            "close" in (r.get("message", "") or "").lower()
            for r in results
        )

        if success_apps:
            if len(success_apps) == 1:
                if is_close_action:
                    response_lines.append(
                        random.choice(CLOSE_SUCCESS).format(app=success_apps[0])
                    )
                else:
                    response_lines.append(
                        random.choice(OPEN_SUCCESS).format(app=success_apps[0])
                    )
            else:
                apps_str = ", ".join(success_apps[:-1]) + " and " + success_apps[-1]
                if is_close_action:
                    response_lines.append(
                        f"Closed {apps_str} A.P."
                    )
                else:
                    response_lines.append(
                        random.choice(OPEN_MULTI_SUCCESS).format(apps=apps_str)
                    )

        if info_results:
            return info_results[0]["message"]

        if failed_apps:
            for app in failed_apps:
                response_lines.append(
                    f"Couldn't find '{app}' A.P. — not in the registry."
                )

        system_warning = result.get("system_warning", [])
        normal_response = " ".join(response_lines) if response_lines else "Something went wrong A.P."

        if system_warning:
            warning = " and ".join(system_warning)
            return f"Heads up A.P. — {warning}. {normal_response} Using Wise memory suggested "

        return normal_response

    return result.get("message", "Something went wrong A.P.")


# ------------------------
# PLUGIN RESPONSE FORMATTER
# ------------------------
def _format_plugin(message, plugin_name):
    if plugin_name.replace(" ", "_") == "system_info":
        return ""

    if plugin_name == "joke":
        return random.choice([
            f"Alright A.P., here's one — {message}",
            f"Got one for you — {message}",
            f"Sure buddy — {message}",
            f"Here we go — {message}"
        ])

    if plugin_name == "quote":
        return random.choice([
            f"Sure A.P. — {message}",
            f"Here's one for you — {message}",
            f"Alright, listen to this — {message}",
            f"This one hits — {message}"
        ])

    if plugin_name == "screenshot":
        return f"Done. {message}"

    if plugin_name == "take_note":
        return f"Got it. {message}"

    return message






