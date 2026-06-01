import datetime

from brain.usage_engine import get_usage_data
from brain.suggestion_engine import get_suggestion_scores
from brain.learning_engine import update_acceptance, update_comparative
from environment.system_monitor import get_system_context


class DecisionEngine:

    def __init__(self):
        self.last_suggestion      = None    # last suggested app — held for comparative learning
        self.last_suggestion_time = None    # timestamp — used for cooldown check
        self.last_content_intent  = None    # last joke/quote — used for "once more"

    # ------------------------
    # STARTUP / IDLE TRIGGER
    # Called by vap_core at boot and by idle_watcher thread
    # FIX #9 — bypass_cooldown=True so idle watcher is never
    # blocked by the 120s cooldown that user-triggered suggestions use
    # ------------------------
    def trigger_suggestion(self):
        now        = datetime.datetime.now()
        usage_data = get_usage_data()
        scores     = get_suggestion_scores(usage_data)
        return self._handle_suggestion(scores, now, bypass_cooldown=True)

    # ------------------------
    # MAIN ENTRY
    # Receives parsed input from intent_engine
    # Returns structured decision output for command_handler
    # ------------------------
    def process(self, parsed):

        intent    = parsed.get("intent")
        targets   = parsed.get("targets", [])
        raw_input = parsed.get("raw_input")
        content   = parsed.get("content")
        now       = datetime.datetime.now()

        # ------------------------
        # CONFIRM
        # User said yes to a suggestion
        # ------------------------
        if intent == "confirm":
            return self._handle_confirm(now)

        # ------------------------
        # NO ACTION
        # User explicitly said no — clear suggestion state
        # ------------------------
        if intent == "no_action":
            self.last_suggestion      = None
            self.last_suggestion_time = None
            return {
                "type":       "error",
                "error_type": "no_action",
                "context":    {}
            }

        # ------------------------
        # STOP CONTENT
        # FIX #12 — user said "done", "end", "enough" to exit joke/quote loop
        # Clears last_content_intent so "once more" returns nothing_to_repeat
        # ------------------------
        if intent == "stop_content":
            self.last_content_intent = None
            return {
                "type":       "error",
                "error_type": "no_action",
                "context":    {}
            }

        # ------------------------
        # CLOSE APP
        # Not wired yet — friendly error
        # ------------------------
        if intent == "close_app":
            if intent == "close_app":
                    if not targets:
                        return self._error("missing_close_target", raw_input, intent, None)  # ← CHANGE THIS
                    return {
                        "type":    "action",
                        "intent":  "close_app",
                        "targets": targets,
                        "execution": {
                            "mode": "close",
                            "data": {"targets": targets}
                        },
                        "system_warning": []
                    }

        # ------------------------
        # EXPLICIT SUGGEST REQUEST
        # ------------------------
        if intent == "suggest":
            usage_data = get_usage_data()
            scores     = get_suggestion_scores(usage_data)
            return self._handle_suggestion(scores, now)

        # ------------------------
        # REPEAT LAST CONTENT
        # "once more" → re-run last joke or quote
        # ------------------------
        if intent == "repeat_last":
            return self._handle_repeat()

        # ------------------------
        # SEARCH NO QUERY
        # FIX #11 — user typed "search" alone
        # ------------------------
        if intent == "search_no_query":
            return {
                "type":       "error",
                "error_type": "search_no_query",
                "context":    {}
            }

        # ------------------------
        # TAKE NOTE
        # ------------------------
        if intent == "take_note":
            return {
                "type":    "action",
                "intent":  "take_note",
                "targets": [],
                "execution": {
                    "mode": "plugin_note",
                    "data": {
                        "plugin":  "take_note",
                        "content": content
                    }
                },
                "system_warning": []
            }

        # ------------------------
        # OPEN NOTE
        # ------------------------
        if intent == "open_note":
            return {
                "type":    "action",
                "intent":  "open_note",
                "targets": [],
                "execution": {
                    "mode": "plugin_open_note",
                    "data": {"plugin": "take_note"}
                },
                "system_warning": []
            }

        # ------------------------
        # TIMER
        # ------------------------
        if intent == "set_timer":
            return {
                "type":    "action",
                "intent":  "set_timer",
                "targets": [],
                "execution": {
                    "mode": "plugin_timer",
                    "data": {
                        "plugin":  "timer",
                        "content": content
                    }
                },
                "system_warning": []
            }

        # ------------------------
        # SEARCH WEB
        # ------------------------
        if intent == "search_web":
            return {
                "type":    "action",
                "intent":  "search_web",
                "targets": [],
                "execution": {
                    "mode": "search",
                    "data": {"query": content}
                },
                "system_warning": []
            }

        # ------------------------
        # DIRECT PLUGIN
        # joke, quote, screenshot, playlist, weather
        # FIX #3 — clear last_content_intent when a NON-content
        # intent fires (open_app, search, timer etc.) so "once more"
        # doesn't leak across unrelated commands
        # Content plugins set it, everything else clears it below
        # ------------------------
        if intent == "plugin":
            plugin_name = targets[0] if targets else None

            if not plugin_name:
                return self._error("missing_target", raw_input, intent, None)

            # track content plugins for "once more"
            if plugin_name in ["joke", "quote"]:
                self.last_content_intent = plugin_name
            else:
                # non-content plugin (screenshot, playlist, weather)
                # clear content session — "once more" should not work after these
                self.last_content_intent = None

            return {
                "type": "action",
                "intent": "plugin",
                "targets": targets,
                "execution": {
                    "mode": "plugin",
                    "data": {
                        "plugin": plugin_name,
                        "content": content  # ← this line — already extracted at top of process()
                    }
                },
                "system_warning": []
            }

        # ------------------------
        # VALIDATION
        # Nothing matched — unknown command
        # ------------------------
        if not intent:
            return self._error("unknown_command", raw_input, intent, None)

        # ------------------------
        # VAGUE OPEN COMMAND — no targets
        # Distinguish genuinely vague vs app not found
        # ------------------------
        if intent == "open_app" and not targets:
            raw_targets = parsed.get("raw_targets", [])
            vague_words = {"app", "something", "anything", "stuff", "it", "this", "that"}

            if raw_targets and not all(w in vague_words for w in raw_targets):
                return self._error("app_not_found", raw_input, intent, raw_targets[0])

            usage_data = get_usage_data()
            scores     = get_suggestion_scores(usage_data)
            return self._handle_suggestion(scores, now)

        # ------------------------
        # COMPARATIVE LEARNING
        # Implicit reject — new command while suggestion pending
        # ------------------------
        if self.last_suggestion and targets:
            update_comparative(self.last_suggestion, targets[0])
            self.last_suggestion      = None
            self.last_suggestion_time = None

        # ------------------------
        # FIX #3 — clear content session on any direct app action
        # "once more" after "open chrome" should return nothing_to_repeat
        # ------------------------
        self.last_content_intent = None

        # ------------------------
        # SYSTEM CONTEXT CHECK
        # ------------------------
        system = get_system_context()

        # ------------------------
        # DIRECT ACTION
        # ------------------------
        return {
            "type":    "action",
            "intent":  intent,
            "targets": targets,
            "execution": {
                "mode": "app",
                "data": {"targets": targets}
            },
            "system_warning": system["warnings"] if system["is_high"] else []
        }

    # ------------------------
    # REPEAT LAST CONTENT
    # ------------------------
    def _handle_repeat(self):
        if not self.last_content_intent:
            return {
                "type":       "error",
                "error_type": "nothing_to_repeat",
                "context":    {}
            }

        plugin_name = self.last_content_intent

        return {
            "type":    "action",
            "intent":  "plugin",
            "targets": [plugin_name],
            "execution": {
                "mode": "plugin",
                "data": {"plugin": plugin_name}
            },
            "system_warning": []
        }

    # ------------------------
    # SUGGESTION HANDLER
    # FIX #9 — bypass_cooldown param added
    # idle_watcher and startup use bypass=True
    # user-triggered suggestions still respect 120s cooldown
    # ------------------------
    def _handle_suggestion(self, scores, now, bypass_cooldown=False):

        if not bypass_cooldown and self.last_suggestion_time:
            delta = (now - self.last_suggestion_time).total_seconds()
            if delta < 120:
                return {
                    "type":       "error",
                    "error_type": "suggestion_cooldown",
                    "context":    {"last_suggestion": self.last_suggestion}
                }

        if not scores:
            return {
                "type":       "error",
                "error_type": "no_suggestions_available",
                "context":    {}
            }

        options = list(scores.keys())[:3]

        self.last_suggestion      = options[0]
        self.last_suggestion_time = now

        return {
            "type":    "suggestion",
            "options": options
        }

    # ------------------------
    # CONFIRM HANDLER
    # ------------------------
    def _handle_confirm(self, now):

        if not self.last_suggestion:
            return {
                "type":       "error",
                "error_type": "nothing_to_confirm",
                "context":    {}
            }

        app = self.last_suggestion
        update_acceptance(app)

        self.last_suggestion      = None
        self.last_suggestion_time = None

        return {
            "type":    "action",
            "intent":  "open_app",
            "targets": [app],
            "execution": {
                "mode": "app",
                "data": {"targets": [app]}
            },
            "system_warning": []
        }

    # ------------------------
    # ERROR BUILDER
    # ------------------------
    def _error(self, error_type, raw_input, intent, target):
        return {
            "type":       "error",
            "error_type": error_type,
            "context": {
                "raw_input":        raw_input,
                "intent":           intent,
                "attempted_target": target
            }
        }




















