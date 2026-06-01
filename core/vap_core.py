# core/vap_core.py
# VAP — Pipeline Orchestrator
# -------------------------------------------------------
# Role: stateless loop — calls modules in order, zero logic
# Voice mode: default True (Phase 7)
# Toggle: Ctrl+Alt+T switches voice ↔ text at runtime
# -------------------------------------------------------
# States:
#   ACTIVE     — VAP awake, accepts full command
#   BACKGROUND — VAP silent, listening for wake word only
#   DEAD       — 10 min idle, process exits
#
# STARTUP_SUGGESTION flag:
#   True  — VAP just showed a suggestion at startup
#           next input goes straight to pipeline (no mishear auto-drop)
#   False — normal command flow with mishear handling
# -------------------------------------------------------

import time
import threading

from brain.intent_engine   import parse
from brain.decision_engine import DecisionEngine
from brain.command_handler import handle_command
from brain.response_engine import respond
from core.voice_io         import listen_wake_word, listen_full_command, speak, NETWORK_ERROR

# ── STATE CONSTANTS ──────────────────────────────────────

STATE_ACTIVE     = "active"
STATE_BACKGROUND = "background"
STATE_DEAD       = "dead"

WAKE_WORD        = "hey buddy"
IDLE_TIMEOUT_SEC = 600


def start():

    decision_engine = DecisionEngine()

    # mutable state — lists so threads can read/write
    state                = [STATE_ACTIVE]
    last_wake_time       = [time.time()]
    mishear_count        = [0]
    stop_flag            = [False]
    voice_mode           = [True]
    toggle_fired         = [False]
    awaiting_suggestion  = [False]   # True = next input is suggestion response

    # ── Ctrl+Alt+T TOGGLE ────────────────────────────────

    def setup_toggle():
        try:
            import keyboard

            def on_toggle():
                if stop_flag[0]:
                    return

                voice_mode[0] = not voice_mode[0]
                mishear_count[0] = 0
                toggle_fired[0] = True

                if voice_mode[0]:
                    state[0] = STATE_BACKGROUND  # voice mode needs wake word
                    print("\n[VAP] Voice mode restored. Say 'hey buddy' to activate.")
                else:
                    state[0] = STATE_ACTIVE  # text mode goes straight to prompt
                    print("\n[VAP] Text mode — type your command below.\n")

            keyboard.add_hotkey("ctrl+alt+t", on_toggle, suppress=True)

        except ImportError:
            print("[VAP] WARNING: 'keyboard' not installed — toggle unavailable.")
        except Exception as e:
            print(f"[VAP] WARNING: Toggle setup failed — {e}")

    toggle_thread = threading.Thread(target=setup_toggle, daemon=True)
    toggle_thread.start()
    time.sleep(0.15)

    # ── STARTUP SUGGESTION ───────────────────────────────
    # Fires once, stays ACTIVE so user can respond
    # Sets awaiting_suggestion = True so mishear logic is bypassed
    # for this first response only

    startup_decision = decision_engine.trigger_suggestion()

    if startup_decision and startup_decision.get("type") != "error":
        response = respond(startup_decision)
        print(response)
        if voice_mode[0]:
            speak(response)
        state[0]               = STATE_ACTIVE
        awaiting_suggestion[0] = True    # next input = suggestion response

    else:
        # no suggestion — go straight to background
        state[0] = STATE_BACKGROUND

    # ── 10 MIN IDLE KILL THREAD ──────────────────────────

    def idle_killer():
        while not stop_flag[0]:
            time.sleep(30)
            if stop_flag[0]:
                break
            if state[0] == STATE_BACKGROUND:
                elapsed = time.time() - last_wake_time[0]
                if elapsed >= IDLE_TIMEOUT_SEC:
                    farewell = "No activity for 10 minutes. Shutting down. Later A.P."
                    print(f"\n[VAP] {farewell}")
                    if voice_mode[0]:
                        speak(farewell)
                    state[0]     = STATE_DEAD
                    stop_flag[0] = True
                    break

    killer = threading.Thread(target=idle_killer, daemon=True)
    killer.start()

    # ── MAIN LOOP ────────────────────────────────────────

    while state[0] != STATE_DEAD:

        toggle_fired[0] = False

        # ── BACKGROUND STATE ─────────────────────────────

        if state[0] == STATE_BACKGROUND:

            if voice_mode[0]:
                heard_wake = listen_wake_word()

                if heard_wake:
                    state[0]          = STATE_ACTIVE
                    last_wake_time[0] = time.time()
                    mishear_count[0]  = 0
                    print("[VAP] Ready.")

            # else:
            #     try:
            #         raw = input(">> ").strip().lower()
            #     except (EOFError, KeyboardInterrupt):
            #         break
            #
            #     if toggle_fired[0]:
            #         continue
            #
            #     if not raw:
            #         continue
            #
            #     if WAKE_WORD in raw:
            #         state[0]          = STATE_ACTIVE
            #         last_wake_time[0] = time.time()
            #         mishear_count[0]  = 0
            #         print("[VAP] Ready.")

            continue

        # ── ACTIVE STATE ─────────────────────────────────

        if state[0] == STATE_ACTIVE:

            # ── GET INPUT ────────────────────────────────

            if voice_mode[0]:
                user_input = listen_full_command()

                if user_input == NETWORK_ERROR:
                    msg = "Can't reach Google right now. Switching to text."
                    print(f"[VAP] {msg}")
                    speak(msg)
                    voice_mode[0]       = False
                    mishear_count[0]    = 0
                    awaiting_suggestion[0] = False
                    print("[VAP] Text mode — Ctrl+Alt+T to switch back.\n")
                    state[0] = STATE_ACTIVE
                    continue

                if user_input is None:
                    # ── MISHEAR LOGIC ─────────────────────
                    # If awaiting suggestion response → single retry only
                    # no auto-drop to text — user just needs to respond yes/no
                    if awaiting_suggestion[0]:
                        speak("Didn't catch that A.P. — say yes, or tell me what to open.")
                        continue    # stay ACTIVE, retry

                    # normal command mishear — 2 strike rule
                    mishear_count[0] += 1

                    if mishear_count[0] == 1:
                        speak("Didn't catch that A.P.")
                        continue

                    else:
                        speak("Still didn't catch that — switching to text.")
                        mishear_count[0]       = 0
                        voice_mode[0]          = False
                        awaiting_suggestion[0] = False
                        print("[VAP] Text mode — Ctrl+Alt+T to switch back.\n")
                        state[0] = STATE_ACTIVE
                        continue

            else:
                # ── TEXT INPUT ───────────────────────────
                try:
                    user_input = input(">> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if toggle_fired[0]:
                    continue

                if not user_input:
                    continue

            # ── GOOD INPUT — reset counters ───────────────
            mishear_count[0]  = 0

            # ── EXIT ─────────────────────────────────────
            if user_input.lower().startswith(("exit", "quit")):
                farewell = "Shutting down VAP. Later A.P."
                print(f"[VAP] {farewell}")
                if voice_mode[0]:
                    speak(farewell)
                stop_flag[0] = True
                break

            # ── STRIP WAKE WORD IF IN SENTENCE ───────────
            lower_input = user_input.lower()
            if lower_input.startswith(WAKE_WORD):
                user_input = user_input[len(WAKE_WORD):].strip()
                if not user_input:
                    print("[VAP] Ready.")
                    continue

            # ── PIPELINE ─────────────────────────────────
            parsed   = parse(user_input)
            decision = decision_engine.process(parsed)
            result   = handle_command(decision)
            response = respond(result)

            print(response)
            if voice_mode[0]:
                speak(response)

            # ── STATE TRANSITION ─────────────────────────
            decision_type = decision.get("type")

            # clear suggestion flag after first response regardless
            awaiting_suggestion[0] = False

            if decision_type not in ["suggestion", "error"]:
                # action completed
                if voice_mode[0]:
                    state[0] = STATE_BACKGROUND  # voice: go sleep, wait for wake word
                # else: text mode stays ACTIVE — keeps the prompt live
                last_wake_time[0] = time.time()
            # suggestion/error — stay ACTIVE for follow-up
            # (user says yes/no or retries)



# # core/vap_core.py
# # VAP — Pipeline Orchestrator
# # -------------------------------------------------------
# # Role: stateless loop — calls modules in order, zero logic
# # Voice mode: hardcoded True for Phase 7
# #             Ctrl+Alt+T toggle → added later
# # -------------------------------------------------------
# # States:
# #   ACTIVE     — VAP awake, accepts full command
# #   BACKGROUND — VAP silent, listening for wake word only
# #   DEAD       — 10 min idle, process exits
# # -------------------------------------------------------
#
# import time
# import threading
#
# from brain.intent_engine   import parse
# from brain.decision_engine import DecisionEngine
# from brain.command_handler import handle_command
# from brain.response_engine import respond
# from core.voice_io         import listen_wake_word, listen_full_command, speak, NETWORK_ERROR
#
# # ── STATE CONSTANTS ──────────────────────────────────────
#
# STATE_ACTIVE     = "active"
# STATE_BACKGROUND = "background"
# STATE_DEAD       = "dead"
#
# WAKE_WORD        = "hey buddy"     # matches voice_io.py WAKE_PHRASE
# IDLE_TIMEOUT_SEC = 600             # 10 minutes
#
# # ── VOICE MODE ───────────────────────────────────────────
#
# VOICE_MODE = True   # hardcoded for Phase 7
#                     # Ctrl+Alt+T toggle wired in next pass
#
#
# def start():
#
#     decision_engine = DecisionEngine()
#
#     # mutable state — list so threads can read/write
#     state           = [STATE_ACTIVE]
#     last_wake_time  = [time.time()]
#     mishear_count   = [0]
#     stop_flag       = [False]
#
#     # ── STARTUP SUGGESTION ───────────────────────────────
#     # Fires once at launch — proactive suggestion
#     startup_decision = decision_engine.trigger_suggestion()
#
#     if startup_decision and startup_decision.get("type") != "error":
#         response = respond(startup_decision)
#         print(response)
#         if VOICE_MODE:
#             speak(response)
#
#     # ── 10 MIN IDLE KILL THREAD ──────────────────────────
#     # Checks every 30s — kills process if no wake word in 10 min
#     def idle_killer():
#         while not stop_flag[0]:
#             time.sleep(30)
#             if stop_flag[0]:
#                 break
#             if state[0] == STATE_BACKGROUND:
#                 elapsed = time.time() - last_wake_time[0]
#                 if elapsed >= IDLE_TIMEOUT_SEC:
#                     farewell = "No activity for 10 minutes. Shutting down. Later A.P."
#                     print(f"\n[VAP] {farewell}")
#                     if VOICE_MODE:
#                         speak(farewell)
#                     state[0]    = STATE_DEAD
#                     stop_flag[0] = True
#                     break
#
#     killer = threading.Thread(target=idle_killer, daemon=True)
#     killer.start()
#
#     # ── MAIN LOOP ────────────────────────────────────────
#
#     while state[0] != STATE_DEAD:
#
#         # ── BACKGROUND STATE ─────────────────────────────
#         # Voice: listen for wake word in a loop — silent on miss
#         # Text:  wait for typed input, check for wake word string
#
#         if state[0] == STATE_BACKGROUND:
#
#             if VOICE_MODE:
#                 heard_wake = listen_wake_word()
#
#                 if heard_wake:
#                     state[0]          = STATE_ACTIVE
#                     last_wake_time[0] = time.time()
#                     mishear_count[0]  = 0
#                     print("[VAP] Ready.")
#                 # else: silence — loop continues, nothing printed
#
#             else:
#                 # text mode background — wait for typed wake word
#                 try:
#                     raw = input("").strip().lower()
#                 except (EOFError, KeyboardInterrupt):
#                     break
#
#                 if WAKE_WORD in raw:
#                     state[0]          = STATE_ACTIVE
#                     last_wake_time[0] = time.time()
#                     mishear_count[0]  = 0
#                     print("[VAP] Ready.")
#
#             continue   # always continue after background check
#
#         # ── ACTIVE STATE ─────────────────────────────────
#
#         if state[0] == STATE_ACTIVE:
#
#             # ── GET INPUT ────────────────────────────────
#
#             if VOICE_MODE:
#                 user_input = listen_full_command()
#
#                 # ── NETWORK ERROR ────────────────────────
#                 if user_input == NETWORK_ERROR:
#                     msg = "Can't reach Google right now. Switching to text."
#                     print(f"[VAP] {msg}")
#                     speak(msg)
#                     print("[VAP] Text mode — Ctrl+Alt+T to switch back.")
#                     # drop to text mode for this session
#                     # full toggle wired in next pass
#                     state[0] = STATE_BACKGROUND
#                     continue
#
#                 # ── MISHEAR ──────────────────────────────
#                 if user_input is None:
#                     mishear_count[0] += 1
#
#                     if mishear_count[0] == 1:
#                         # first miss — gentle retry
#                         speak("Didn't catch that A.P.")
#                         # stay ACTIVE — listen again immediately
#                         continue
#
#                     else:
#                         # second miss — suggest text
#                         speak("Still didn't catch that — switching to text.")
#                         mishear_count[0] = 0
#                         print("[VAP] Text mode — Ctrl+Alt+T to switch back.")
#                         state[0] = STATE_BACKGROUND
#                         continue
#
#             else:
#                 # text mode active — standard prompt
#                 try:
#                     user_input = input(">> ").strip()
#                 except (EOFError, KeyboardInterrupt):
#                     break
#
#                 if not user_input:
#                     continue
#
#             # ── SUCCESSFUL INPUT — reset mishear count ───
#             mishear_count[0] = 0
#
#             # ── EXIT CHECK ───────────────────────────────
#             if user_input.lower().startswith(("exit", "quit")):
#                 farewell = "Shutting down VAP. Later A.P."
#                 print(f"[VAP] {farewell}")
#                 if VOICE_MODE:
#                     speak(farewell)
#                 stop_flag[0] = True
#                 break
#
#             # ── STRIP WAKE WORD IF PRESENT ───────────────
#             # handles "hey buddy open chrome" in one sentence
#             lower_input = user_input.lower()
#             if lower_input.startswith(WAKE_WORD):
#                 user_input = user_input[len(WAKE_WORD):].strip()
#                 if not user_input:
#                     print("[VAP] Ready.")
#                     continue
#
#             # ── PIPELINE ─────────────────────────────────
#             parsed   = parse(user_input)
#             decision = decision_engine.process(parsed)
#             result   = handle_command(decision)
#             response = respond(result)
#
#             print(response)
#
#             if VOICE_MODE:
#                 speak(response)
#
#             # ── STATE TRANSITION ─────────────────────────
#             # suggestion/error shown → stay ACTIVE (need yes/no)
#             # any completed action   → go BACKGROUND silently
#             decision_type = decision.get("type")
#
#             if decision_type not in ["suggestion", "error"]:
#                 state[0]          = STATE_BACKGROUND
#                 last_wake_time[0] = time.time()
#


# import time
# import threading
#
# from brain.intent_engine import parse
# from brain.decision_engine import DecisionEngine
# from brain.command_handler import handle_command
# from brain.response_engine import respond
#
#
# def start():
#
#     decision_engine = DecisionEngine()
#
#     # ------------------------
#     # STARTUP SUGGESTION
#     # Fires once when VAP launches — proactive suggestion based on habits
#     # bypass_cooldown=True so startup is never blocked
#     # ------------------------
#     startup_decision = decision_engine.trigger_suggestion()
#     if startup_decision and startup_decision.get("type") != "error":
#         print(respond(startup_decision))
#
#     # ------------------------
#     # IDLE SUGGESTION — background thread
#     # If no input for 120s → auto suggest once
#     # Uses list so thread can mutate the value (Python closure behaviour)
#     # bypass_cooldown=True so idle is never blocked by user-triggered cooldown
#     # ------------------------
#     last_input_time = [time.time()]
#     stop_flag       = [False]
#
#     def idle_watcher():
#         while not stop_flag[0]:
#             time.sleep(10)
#
#             if stop_flag[0]:
#                 break
#
#             elapsed = time.time() - last_input_time[0]
#
#             if elapsed >= 120:
#                 # skip if suggestion already pending — don't stack
#                 if decision_engine.last_suggestion:
#                     last_input_time[0] = time.time()
#                     continue
#
#                 idle_decision = decision_engine.trigger_suggestion()
#
#                 if idle_decision and idle_decision.get("type") != "error":
#                     print("\n" + respond(idle_decision))
#                     print(">> ", end="", flush=True)
#
#                 # always reset timer after check
#                 last_input_time[0] = time.time()
#
#     watcher = threading.Thread(target=idle_watcher, daemon=True)
#     watcher.start()
#
#     # ------------------------
#     # MAIN LOOP
#     # Pure pipeline — parse → decide → handle → respond
#     # Zero intelligence here, just coordination
#     # ------------------------
#     while True:
#         user_input = input(">> ").strip()
#
#         if not user_input:
#             continue
#
#         # reset idle timer on every input
#         last_input_time[0] = time.time()
#
#         # FIX #8 — "exit vap", "exit please" etc all work now
#         # startswith covers all exit variations naturally
#         if user_input.lower().startswith("exit") or user_input.lower().startswith("quit"):
#             stop_flag[0] = True
#             print("Shutting down VAP. Later A.P. 👋")
#             break
#
#         parsed   = parse(user_input)
#         decision = decision_engine.process(parsed)
#         result   = handle_command(decision)
#         response = respond(result)
#
#         print(response)
#
#
#
