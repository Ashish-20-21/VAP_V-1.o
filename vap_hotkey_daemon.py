import threading
import ctypes
import keyboard
import subprocess
import sys
import os
import logging
import time
import psutil

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

PYTHON = sys.executable
PAUSE_FILE = r"C:\Users\Ashish\PycharmProjects\PythonProject\OFF.txt"

SCRIPTS = {
    "vap_main": r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py",
    "vap_inc":  r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_inc.py",
}

LOG_FILE = os.path.join(os.path.dirname(__file__), "vap_hotkey_daemon.log")

# ──────────────────────────────────────────────
# LOGGING SETUP
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("vap_hotkey_daemon")

# ──────────────────────────────────────────────
# ZOMBIE KILL — runs at very top before anything
# ──────────────────────────────────────────────

current_pid = os.getpid()

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = " ".join(proc.info['cmdline'] or [])
        if (
            "vap_hotkey_daemon.py" in cmdline
            and proc.info['pid'] != current_pid
        ):
            proc.kill()
            print(f"Killed stale daemon instance: PID {proc.info['pid']}")
            time.sleep(0.5)  # let OS clean up before continuing
    except:
        pass

# ──────────────────────────────────────────────
# LAUNCHER
# ──────────────────────────────────────────────

def launch_script(name: str):
    if os.path.exists(PAUSE_FILE):
        log.info(f"Daemon PAUSED: Hotkey for '{name}' ignored.")
        return

    path = SCRIPTS.get(name)

    if not path:
        log.error(f"No script registered under key: '{name}'")
        return

    if not os.path.isfile(path):
        log.error(f"Script not found: {path}")
        return

    log.info(f"Launching [{name}]  ->  {path}")

    try:
        subprocess.Popen(
            [PYTHON, path],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            close_fds=True,
            shell=False
        )
    except Exception as e:
        log.error(f"Failed to launch [{name}]: {e}")

# ──────────────────────────────────────────────
# HOTKEY HANDLERS
# ──────────────────────────────────────────────

def on_vap_main():
    log.info("Hotkey fired: Win+Alt+V")
    launch_script("vap_main")

def on_vap_inc():
    log.info("Hotkey fired: Win+Alt+I")
    launch_script("vap_inc")

# ──────────────────────────────────────────────
# WATCHDOG — re-registers hooks after sleep/wake
# ──────────────────────────────────────────────

def watchdog():
    while True:
        time.sleep(30)
        try:
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey("windows+alt+v", on_vap_main)
            keyboard.add_hotkey("windows+alt+i", on_vap_inc)
            log.info("Watchdog: hooks re-registered")
        except Exception as e:
            log.error(f"Watchdog error: {e}")

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    log.info("=" * 50)
    log.info("VAP Hotkey Daemon — STARTED")
    log.info(f"Python : {PYTHON}")
    log.info(f"Log    : {LOG_FILE}")
    log.info("Listening for:")
    log.info("  Win + Alt + V  ->  VAP Main")
    log.info("  Win + Alt + I  ->  VAP INC Mode")
    log.info(f"Daemon is PAUSED if '{PAUSE_FILE}' exists.")
    log.info("Press Ctrl+C to stop.")
    log.info("=" * 50)

    keyboard.add_hotkey("windows+alt+v", on_vap_main)
    keyboard.add_hotkey("windows+alt+i", on_vap_inc)

    # START WATCHDOG THREAD
    t = threading.Thread(target=watchdog, daemon=True)
    t.start()
    log.info("Watchdog thread started.")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Daemon stopped by user (Ctrl+C).")
    except Exception as e:
        log.critical(f"Daemon crashed: {e}", exc_info=True)
        sys.exit(1)

# """
# vap_hotkey_daemon.py
# --------------------
# VAP Background Daemon — Global Hotkey Listener
#
# Hotkeys:
#   Win + Alt + V  →  Launch VAP Main (main.py)
#   Win + Alt + I  →  Launch VAP INC Mode (vap_inc.py)
#
# --- TO "DISCONNECT" (PAUSE) THE DAEMON ---
# 1. In your project folder, create a new, empty text file named exactly "OFF.txt".
# 2. The daemon will keep running but will not launch anything.
# 3. When you're done editing your main scripts, simply DELETE "OFF.txt".
#    The hotkeys will work again instantly. No need to restart anything!
#
# Runs silently in background. No GUI. No fluff.
#
# Usage:
#   python vap_hotkey_daemon.py
#
# Dependencies:
#   pip install keyboard
#
# Note:
#   Must be run as Administrator for global hotkey access.
#   Add to Task Scheduler on login for auto-start.
# """
# import threading
# import ctypes
# import keyboard
# import subprocess
# import sys
# import os
# import logging
#
#
# # ──────────────────────────────────────────────
# # CONFIG
# # ──────────────────────────────────────────────
#
# # Uses same Python environment that runs this script
# PYTHON = sys.executable
#
# # *** CHANGE 1 OF 2: Define the path to your "kill switch" file ***
# # Path to your "kill switch" file
# PAUSE_FILE = r"C:\Users\Ashish\PycharmProjects\PythonProject\OFF.txt"
#
# SCRIPTS = {
#     "vap_main": r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py",      # Win+Alt+V
#     "vap_inc":  r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_inc.py",   # Win+Alt+I
# }
#
# LOG_FILE = os.path.join(os.path.dirname(__file__), "vap_hotkey_daemon.log")
#
# # ──────────────────────────────────────────────
# # LOGGING SETUP
# # ──────────────────────────────────────────────
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s  [%(levelname)s]  %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     handlers=[
#         logging.FileHandler(LOG_FILE, encoding="utf-8"),
#         logging.StreamHandler(sys.stdout),
#     ],
# )
# log = logging.getLogger("vap_hotkey_daemon")
#
# # ──────────────────────────────────────────────
# # LAUNCHER
# # ──────────────────────────────────────────────
#
# def launch_script(name: str):
#
#     """
#         Fire a script in a new detached console window.
#         Looks up path from SCRIPTS dict by key.
#         Logs error if key missing or file not found.
#         """
#     # *** CHANGE 2 OF 2: Add this block at the very start of the function ***
#     # This is the "gatekeeper". If it finds the OFF.txt file, it logs a message
#     # and immediately exits the function, preventing the scripts from launching.
#
#
#     # --- AUTO-DISCONNECT CHECK ---
#     if os.path.exists(PAUSE_FILE):
#         log.info(f"Daemon PAUSED: Hotkey for '{name}' ignored.")
#         return
#
#     path = SCRIPTS.get(name)
#
#     if not path:
#         log.error(f"No script registered under key: '{name}'")
#         return
#
#     if not os.path.isfile(path):
#         log.error(f"Script not found: {path}")
#         return
#
#     log.info(f"Launching [{name}]  ->  {path}")
#
#     try:
#         subprocess.Popen(
#             [PYTHON, path],
#             creationflags=subprocess.CREATE_NEW_CONSOLE,
#             close_fds=True,
#             shell=False
#         )
#     except Exception as e:
#         log.error(f"Failed to launch [{name}]: {e}")
#
#
#   # subprocess.Popen(
#         #     [PYTHON, path],
#         #     creationflags=subprocess.CREATE_NEW_CONSOLE,
#         # )
#
# # ──────────────────────────────────────────────
# # HOTKEY HANDLERS
# # ──────────────────────────────────────────────
#
# def on_vap_main():
#     """Triggered by Win+Alt+V"""
#     log.info("Hotkey fired: Win+Alt+V")
#     launch_script("vap_main")
#
#
# def on_vap_inc():
#     """Triggered by Win+Alt+I"""
#     log.info("Hotkey fired: Win+Alt+I")
#     launch_script("vap_inc")
#
#
# # ──────────────────────────────────────────────
# # MAIN
# # ──────────────────────────────────────────────
#
# def main():
#     log.info("=" * 50)
#     log.info("VAP Hotkey Daemon — STARTED")
#     log.info(f"Python : {PYTHON}")
#     log.info(f"Log    : {LOG_FILE}")
#     log.info("Listening for:")
#     log.info("  Win + Alt + V  ->  VAP Main")
#     log.info("  Win + Alt + I  ->  VAP INC Mode")
#     log.info(f"Daemon is PAUSED if '{PAUSE_FILE}' exists.")
#     log.info("Press Ctrl+C to stop.")
#     log.info("=" * 50)
#
#     keyboard.add_hotkey("windows+alt+v", on_vap_main)
#     keyboard.add_hotkey("windows+alt+i", on_vap_inc)
#
#     keyboard.wait()
#
#
#
# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         log.info("Daemon stopped by user (Ctrl+C).")
#     except Exception as e:
#         log.critical(f"Daemon crashed: {e}", exc_info=True)
#         sys.exit(1)
#
#
#
#
#
#
#
#
# #---------------------------PREVIOUS-CODE, ORIGINAL SIMPLE-----------------------------------------
# #
# # """
# # vap_hotkey_daemon.py
# # --------------------
# # VAP Background Daemon — Global Hotkey Listener
# #
# # Hotkeys:
# #   Win + Alt + V  →  Launch VAP Main (main.py)
# #   Win + Alt + I  →  Launch VAP INC Mode (vap_inc.py)
# #
# # Only job: catch those two combos and fire the right script.
# # Runs silently in background. No GUI. No fluff.
# #
# # Usage:
# #   python vap_hotkey_daemon.py
# #
# # Dependencies:
# #   pip install keyboard
# #
# # Note:
# #   Must be run as Administrator for global hotkey access.
# #   Add to Task Scheduler on login for auto-start.
# # """
# #
# # import keyboard
# # import subprocess
# # import sys
# # import os
# # import logging
# #
# # # ──────────────────────────────────────────────
# # # CONFIG
# # # ──────────────────────────────────────────────
# #
# # # Uses same Python environment that runs this script
# # PYTHON = sys.executable
# #
# # SCRIPTS = {
# #     "vap_main": r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py",      # Win+Alt+V
# #     "vap_inc":  r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_inc.py",   # Win+Alt+I
# # }
# #
# # LOG_FILE = os.path.join(os.path.dirname(__file__), "vap_hotkey_daemon.log")
# #
# # # ──────────────────────────────────────────────
# # # LOGGING SETUP
# # # ──────────────────────────────────────────────
# #
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s  [%(levelname)s]  %(message)s",
# #     datefmt="%Y-%m-%d %H:%M:%S",
# #     handlers=[
# #         logging.FileHandler(LOG_FILE, encoding="utf-8"),
# #         logging.StreamHandler(sys.stdout),
# #     ],
# # )
# # log = logging.getLogger("vap_hotkey_daemon")
# #
# # # ──────────────────────────────────────────────
# # # LAUNCHER
# # # ──────────────────────────────────────────────
# #
# # def launch_script(name: str):
# #     """
# #     Fire a script in a new detached console window.
# #     Looks up path from SCRIPTS dict by key.
# #     Logs error if key missing or file not found.
# #     """
# #     path = SCRIPTS.get(name)
# #
# #     if not path:
# #         log.error(f"No script registered under key: '{name}'")
# #         return
# #
# #     if not os.path.isfile(path):
# #         log.error(f"Script not found: {path}")
# #         return
# #
# #     log.info(f"Launching [{name}]  →  {path}")
# #
# #     try:
# #         subprocess.Popen(
# #             [PYTHON, path],
# #             creationflags=subprocess.CREATE_NEW_CONSOLE,  # opens fresh console window
# #         )
# #     except Exception as e:
# #         log.error(f"Failed to launch [{name}]: {e}")
# #
# #
# # # ──────────────────────────────────────────────
# # # HOTKEY HANDLERS
# # # ──────────────────────────────────────────────
# #
# # def on_vap_main():
# #     """Triggered by Win+Alt+V — launches VAP main pipeline."""
# #     log.info("Hotkey fired: Win+Alt+V  →  VAP Main")
# #     launch_script("vap_main")
# #
# #
# # def on_vap_inc():
# #     """Triggered by Win+Alt+I — launches VAP INC Mode."""
# #     log.info("Hotkey fired: Win+Alt+I  →  VAP INC Mode")
# #     launch_script("vap_inc")
# #
# #
# # # ──────────────────────────────────────────────
# # # MAIN
# # # ──────────────────────────────────────────────
# #
# # def main():
# #     log.info("=" * 50)
# #     log.info("VAP Hotkey Daemon — STARTED")
# #     log.info(f"Python : {PYTHON}")
# #     log.info(f"Log    : {LOG_FILE}")
# #     log.info("Listening for:")
# #     log.info("  Win + Alt + V  →  VAP Main")
# #     log.info("  Win + Alt + I  →  VAP INC Mode")
# #     log.info("Press Ctrl+C to stop.")
# #     log.info("=" * 50)
# #
# #     # Register global hotkeys — suppress=True prevents combo leaking to other apps
# #     keyboard.add_hotkey("windows+alt+v", on_vap_main)
# #     keyboard.add_hotkey("windows+alt+i", on_vap_inc)
# #
# #     # Block forever — daemon stays alive until killed or Ctrl+C
# #     keyboard.wait()
# #
# # if __name__ == "__main__":
# #     try:
# #         main()
# #     except KeyboardInterrupt:
# #         log.info("Daemon stopped by user (Ctrl+C).")
# #     except Exception as e:
# #         log.critical(f"Daemon crashed: {e}", exc_info=True)
# #         sys.exit(1)
