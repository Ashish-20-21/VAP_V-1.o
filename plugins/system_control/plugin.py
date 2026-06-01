# # plugins/system_control/plugin.py
import subprocess
import re
import time

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False


# ------------------------
# VOLUME CONTROL
# ------------------------

def _press_key(code, times):
    for _ in range(times):
        subprocess.run(
            ["powershell", "-c",
             f"(New-Object -ComObject WScript.Shell).SendKeys([char]{code})"],
            capture_output=True
        )
        time.sleep(0.01)


def set_volume(level):
    level = max(0, min(100, level))
    try:
        _press_key(174, 50)          # hammer down to 0
        steps = int(level / 2)       # ~2% per keypress
        _press_key(175, steps)
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Failed to set volume — {e}"


def mute():
    _press_key(173, 1)
    return "Muted"


def unmute():
    _press_key(173, 1)
    return "Unmuted"


# ------------------------
# BRIGHTNESS CONTROL
# ------------------------

def set_brightness(level):
    if not SBC_AVAILABLE:
        return "screen_brightness_control not installed — run: pip install screen-brightness-control"
    level = max(0, min(100, level))
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Brightness control failed — {e}"


def brightness_max():
    return set_brightness(100)


def brightness_low():
    return set_brightness(20)


# ------------------------
# MAIN ENTRY
# ------------------------

def run(command=None):
    if not command:
        return "What should I control A.P.? Try — mute, volume 70, brightness max."

    cmd = command.lower().strip()

    # -------- VOLUME --------
    if "unmute" in cmd:
        return unmute()

    if "mute" in cmd:
        return mute()

    if "volume" in cmd or "vol" in cmd:
        match = re.search(r'\b(\d+)\b', cmd)
        if match:
            return set_volume(int(match.group()))
        return "Tell me a level A.P. — like: set volume to 70"

    # -------- BRIGHTNESS --------
    if "brightness" in cmd or "bright" in cmd:
        if "max" in cmd:
            return brightness_max()
        if "low" in cmd or "min" in cmd:
            return brightness_low()
        match = re.search(r'\b(\d+)\b', cmd)
        if match:
            return set_brightness(int(match.group()))
        return "Tell me a level A.P. — like: brightness 50, brightness max, brightness low"  # ← add this

    return "Didn't catch that — try: mute, volume 80, brightness max"



# import subprocess
# import re
# import time
# import screen_brightness_control as sbc
#
# # ------------------------
# # VOLUME CONTROL (Deterministic)
# # ------------------------
# def _press_key(code, times):
#     for _ in range(times):
#         subprocess.run(
#             ["powershell", "-c",
#              f"(New-Object -ComObject WScript.Shell).SendKeys([char]{code})"],
#             capture_output=True
#         )
#         time.sleep(0.01)
#
#
# def set_volume(level):
#     level = max(0, min(100, level))
#
#     try:
#         # Step 1: Force volume to 0
#         _press_key(174, 50)   # volume down many times
#
#         # Step 2: Increase to target
#         steps = int(level / 2)  # approx: each press ~2%
#         _press_key(175, steps)
#
#         return f"Volume set to {level}%"
#     except Exception as e:
#         return f"Failed to set volume — {e}"
#
#
# def mute():
#     _press_key(173, 1)
#     return "Volume muted"
#
#
# def unmute():
#     _press_key(173, 1)
#     return "Volume unmuted"
#
#
# # ------------------------
# # BRIGHTNESS CONTROL
# # ------------------------
# def set_brightness(level):
#     level = max(0, min(100, level))
#     try:
#         sbc.set_brightness(level)
#         return f"Brightness set to {level}%"
#     except:
#         return "Brightness control not supported"
#
#
# def brightness_max():
#     return set_brightness(100)
#
#
# def brightness_low():
#     return set_brightness(20)
#
#
# # ------------------------
# # MAIN ENTRY
# # ------------------------
# def run(command=None):
#
#     if not command:
#         return "What should I control A.P.? Try volume or brightness."
#
#     cmd = command.lower()
#
#     # -------- Volume --------
#     if "mute" in cmd:
#         return mute()
#
#     if "unmute" in cmd:
#         return unmute()
#
#     if "volume" in cmd:
#         match = re.search(r'\d+', cmd)
#         if match:
#             return set_volume(int(match.group()))
#         return "Tell me a number like — set volume to 70"
#
#     # -------- Brightness --------
#     if "brightness" in cmd:
#
#         if "max" in cmd:
#             return brightness_max()
#
#         if "low" in cmd:
#             return brightness_low()
#
#         match = re.search(r'\d+', cmd)
#         if match:
#             return set_brightness(int(match.group()))
#         return "Tell me a number like — set brightness to 50"
#
#     return "Command not recognized for system control"