import importlib
import subprocess
import webbrowser

from registry.registry_manager import get_app_config
from execution.app_launcher import launch_app
from execution.plugin_executor import execute_plugin
from execution.app_closer import close_app as close_app_exec



def handle_command(decision):

    decision_type = decision.get("type")

    # ------------------------
    # PASS THROUGH
    # Errors and suggestions go straight to response_engine
    # Command handler has zero intelligence — only routes
    # ------------------------
    if decision_type in ["error", "suggestion"]:
        return decision

    # ------------------------
    # SYSTEM WARNING PREP
    # Check if first target is a plugin — system warning suppressed for plugins
    # ------------------------
    targets        = decision.get("targets", [])
    system_warning = decision.get("system_warning", [])
    config_check   = get_app_config(targets[0]) if targets else None
    is_plugin      = config_check and config_check.get("method") == "plugin"

    execution = decision.get("execution", {})
    mode      = execution.get("mode")
    data      = execution.get("data", {})

    # ------------------------
    # APP EXECUTION
    # Standard app launch — also handles registry-registered plugins
    # ------------------------
    if mode == "app":
        targets = data.get("targets", [])
        results = []

        for app in targets:
            config = get_app_config(app)

            if not config:
                results.append({
                    "app":     app,
                    "status":  "error",
                    "message": "not found"
                })
                continue

            # ------------------------
            # REGISTRY PLUGIN ROUTE
            # Apps registered as method=plugin in apps.json
            # e.g. system_info, sysinfo
            # ------------------------
            if config.get("method") == "plugin":
                plugin_name = config.get("command")
                result      = execute_plugin(plugin_name)
                results.append({
                    "app":     app,
                    "status":  result.get("status"),
                    "message": result.get("message")
                })
                continue

            # ------------------------
            # NORMAL APP LAUNCH
            # ------------------------
            result = launch_app(config)
            results.append({
                "app":     app,
                "status":  result.get("status"),
                "message": result.get("message")
            })

        return {
            "type":           "action_result",
            "results":        results,
            "system_warning": system_warning if not is_plugin else []
        }

    # ------------------------
    # DIRECT PLUGIN MODE
    # joke, quote, screenshot, playlist, weather
    # These come directly from intent — not via registry
    # ------------------------
    if mode == "plugin":
        plugin_name = data.get("plugin")
        content = data.get("content")  # ← add this
        result = execute_plugin(plugin_name, content)  # ← pass it
        return {
            "type": "action_result",
            "results": [{
                "app":     plugin_name,
                "status":  result.get("status"),
                "message": result.get("message")
            }],
            "system_warning": []
        }

    # ------------------------
    # TIMER PLUGIN
    # Needs content (raw input) passed to plugin for duration extraction
    # ------------------------
    if mode == "plugin_timer":
        plugin_name = data.get("plugin")
        content     = data.get("content")
        result      = _execute_plugin_with_input(plugin_name, content)
        return {
            "type": "action_result",
            "results": [{
                "app":     plugin_name,
                "status":  result.get("status"),
                "message": result.get("message")
            }],
            "system_warning": []
        }

    # ------------------------
    # TAKE NOTE PLUGIN
    # Needs note content passed to plugin
    # ------------------------
    if mode == "plugin_note":
        plugin_name = data.get("plugin")
        content     = data.get("content")
        result      = _execute_plugin_with_input(plugin_name, content)
        return {
            "type": "action_result",
            "results": [{
                "app":     plugin_name,
                "status":  result.get("status"),
                "message": result.get("message")
            }],
            "system_warning": []
        }

    # ------------------------
    # OPEN NOTE
    # Opens notes.txt in Notepad via plugin's open_note()
    # ------------------------
    if mode == "plugin_open_note":
        from plugins.take_note.plugin import open_note
        message = open_note()
        return {
            "type": "action_result",
            "results": [{
                "app":     "take_note",
                "status":  "success",
                "message": message
            }],
            "system_warning": []
        }

    # ------------------------
    # SEARCH WEB
    # Opens Chrome with Google search URL in Profile 3
    # ------------------------
    if mode == "search":
        query  = data.get("query", "")
        result = _execute_search(query)
        return {
            "type": "action_result",
            "results": [{
                "app":     "search",
                "status":  result.get("status"),
                "message": result.get("message")
            }],
            "system_warning": []
        }
    # ------------------------
    # CLOSE APP
    # ------------------------
    if mode == "close":
        targets = data.get("targets", [])
        results = []

        for app in targets:
            config = get_app_config(app)
            # print(f"DEBUG CLOSE: app={app}, config={config}")  # ← ADD THIS

            if not config:
                results.append({
                    "app":     app,
                    "status":  "error",
                    "intent": "close_app",
                    "message": "not found"
                })
                continue

            result = close_app_exec(app, config)
            # print(f"DEBUG CLOSE RESULT: {result}")  # ← ADD THIS
            results.append({
                "app":     app,
                "status":  result.get("status"),
                "message": result.get("message")
            })

        return {
            "type": "action_result",
            "intent": "close_app",  # ← ADD HERE (top level)
            "results": results,
            "system_warning": []
        }


    # ------------------------
    # UNKNOWN MODE FALLBACK
    # ------------------------
    return {
        "type":       "error",
        "error_type": "unknown_execution_mode",
        "context":    {}
    }


# ========================
# PRIVATE HELPERS
# ========================

def _execute_plugin_with_input(plugin_name, input_data):
    """
    For plugins that need input data passed to run().
    Used by timer (duration) and take_note (note content).
    """
    try:
        module = importlib.import_module(f"plugins.{plugin_name}.plugin")

        if hasattr(module, "run"):
            result = module.run(input_data)
            return {"status": "success", "message": result}
        else:
            return {"status": "error", "message": f"Plugin {plugin_name} has no run()"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def _execute_search(query):
    """
    Opens Chrome with a Google search URL.
    Uses Profile 3 (AP's profile). Falls back to default browser.
    """
    CHROME_PATH    = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    CHROME_PROFILE = "--profile-directory=Profile 3"

    if not query:
        return {"status": "error", "message": "No search query provided."}

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    try:
        subprocess.Popen([CHROME_PATH, CHROME_PROFILE, search_url])
        return {"status": "success", "message": f"Searching for — {query}"}
    except Exception:
        try:
            webbrowser.open(search_url)
            return {"status": "success", "message": f"Searching for — {query}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}




