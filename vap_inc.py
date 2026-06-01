"""
vap_inc.py
----------
VAP — INC Mode (Instant Command)

Purpose: Execute commands as fast as possible.
No Decision Engine. No learning. No suggestions. No personality.
Just: input → identify → beep → execute.

Routing:
  search <query>   → Chrome search (Profile 3)
  <plugin name>    → plugin executor
  <anything else>  → app registry lookup → launch

Behaviour:
  - 2 minute fixed timer from launch → auto closes
  - Beep on every command received
  - Silent fail if app not found

Hotkey entry: Win+Alt+I via vap_hotkey_daemon.py
"""

import sys
import os
import time
import threading
import msvcrt  # built-in on Windows — no install needed

# ── Path fix ──────────────────────────────────
VAP_ROOT = r"C:\Users\Ashish\PycharmProjects\PythonProject"
os.chdir(VAP_ROOT)
if VAP_ROOT not in sys.path:
    sys.path.insert(0, VAP_ROOT)

from registry.registry_manager import get_app_config
from execution.app_launcher import launch_app
from execution.plugin_executor import execute_plugin

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

CHROME_PATH    = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE = "Profile 3"
BEEP_PATH      = os.path.join(VAP_ROOT, "assets", "beep.mp3")
AUTO_CLOSE_SEC = 120  # 2 minutes

SEARCH_KEYWORDS = ["search", "find", "google"]
EXIT_COMMANDS   = ["exit", "quit", "q"]

# ──────────────────────────────────────────────
# BEEP
# ──────────────────────────────────────────────

# def init_beep():
#     try:
#         import pygame
#         pygame.mixer.init()
#         if os.path.isfile(BEEP_PATH):
#             sound = pygame.mixer.Sound(BEEP_PATH)
#             return pygame, sound
#         return pygame, None
#     except Exception:
#         return None, None

def init_beep():
    try:
        import os
        import pygame
        # Suppress pygame's startup banner - MUST be set before mixer.init()
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        pygame.mixer.init()
        if os.path.isfile(BEEP_PATH):
            sound = pygame.mixer.Sound(BEEP_PATH)
            return pygame, sound
        return pygame, None
    except Exception:
        return None, None




def beep(pygame_ref, sound):
    if pygame_ref and sound:
        try:
            sound.stop()        # stop any previous instance immediately
            sound.play()
            time.sleep(0.3)     # just enough for the beep to be heard
            return
        except Exception:
            pass

    try:
        import winsound
        winsound.Beep(1000, 150)
    except Exception:
        pass

    # Last resort
    try:
        import winsound
        winsound.Beep(1000, 150)
    except Exception:
        pass


# ──────────────────────────────────────────────
# AUTO CLOSE TIMER
# ──────────────────────────────────────────────

# Shared flag — timer thread sets this, main loop watches it
_exit_flag = threading.Event()


def auto_close_timer():
    """
    Runs in background thread.
    Sleeps for AUTO_CLOSE_SEC then sets _exit_flag.
    Main loop checks this flag every 50ms via get_input().
    """
    time.sleep(AUTO_CLOSE_SEC)
    _exit_flag.set()


# ──────────────────────────────────────────────
# NON-BLOCKING INPUT
# ──────────────────────────────────────────────

def get_input(prompt):
    """
    Windows-only non-blocking input using msvcrt.
    Reads one character at a time — checks _exit_flag every 50ms.

    Why not input():
      input() blocks forever waiting for Enter.
      Timer fires, flag sets, but loop is frozen — can't check flag.
      msvcrt.kbhit() polls for keystrokes without blocking.

    Returns:
      string — what user typed when they pressed Enter
      None   — timer fired while waiting (exit signal)
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()

    chars = []

    while not _exit_flag.is_set():
        if msvcrt.kbhit():  # key available in buffer?
            ch = msvcrt.getwche()  # read one char and echo it

            if ch in ('\r', '\n'):  # Enter pressed — command complete
                sys.stdout.write('\n')
                return ''.join(chars)

            elif ch == '\x08':  # Backspace — remove last char
                if chars:
                    chars.pop()

            elif ch == '\x03':  # Ctrl+C — treat as exit
                raise KeyboardInterrupt

            else:
                chars.append(ch)  # normal character — accumulate

        else:
            time.sleep(0.05)  # no key yet — wait 50ms before checking again

    # _exit_flag was set while waiting — timer fired
    return None


# ──────────────────────────────────────────────
# ROUTING
# ──────────────────────────────────────────────

def is_search(command: str) -> bool:
    """True if first word is a search keyword."""
    return command.split()[0].lower() in SEARCH_KEYWORDS


def is_plugin(command: str) -> bool:
    """True if a plugin folder exists for this command's first word."""
    plugin_name = command.split()[0].lower()
    plugin_path = os.path.join(VAP_ROOT, "plugins", plugin_name, "plugin.py")
    return os.path.isfile(plugin_path)


# ──────────────────────────────────────────────
# EXECUTORS
# ──────────────────────────────────────────────

def run_search(command: str):
    """Strip search keyword, open Chrome Profile 3 with Google search URL."""
    parts = command.split(maxsplit=1)
    query = parts[1] if len(parts) > 1 else ""
    if not query:
        return
    import subprocess
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    subprocess.Popen(
        [CHROME_PATH, f"--profile-directory={CHROME_PROFILE}", url],
        shell=False
    )


def run_plugin(command: str):
    """Route first word to plugin executor."""
    plugin_name = command.split()[0].lower()
    execute_plugin(plugin_name)


def run_app(command: str):
    """
    Registry lookup → launch.
    Silent fail if app not found — user notices and retypes.
    """
    config = get_app_config(command.strip().lower())
    if not config:
        return
    launch_app(config)


# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────

def start():
    pygame_ref, sound = init_beep()
    # print(f"[DEBUG] pygame init result: {pygame}")  # add this temporarily

    # Start 2 min countdown in background — daemon so it dies with main process
    timer = threading.Thread(target=auto_close_timer, daemon=True)
    timer.start()

    print("INC MODE  —  2 min session  |  exit to close")
    print("-" * 42)

    while not _exit_flag.is_set():
        try:
            # get_input() polls every 50ms — won't block when timer fires
            user_input = get_input("INC >> ")

        except KeyboardInterrupt:
            break

        # None means timer fired while waiting at prompt — exit cleanly
        if user_input is None:
            break

        user_input = user_input.strip()

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            break

        # beep first — confirms command received, then route
        beep(pygame_ref, sound)

        if is_search(user_input):
            run_search(user_input)
        elif is_plugin(user_input):
            run_plugin(user_input)
        else:
            run_app(user_input)

    print("\n[INC] Session closed.")


if __name__ == "__main__":
    start()
