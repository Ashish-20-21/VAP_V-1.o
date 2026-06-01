import logging

LOG_FILE = r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_debug.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("=== VAP WELCOME STARTED ===")

# from playsound import playsound
import edge_tts
import sys
import asyncio
import subprocess
import winsound
import time
import os
import psutil
import socket
import datetime
import random



# ── CONFIG ───────────────────────────────────────────────────────────────

VOICE      = "en-GB-RyanNeural"
AUDIO_FILE = r"C:\Users\Ashish\PycharmProjects\PythonProject\welcome_audio.mp3"
PYTHON     = sys.executable
LAUNCHER   = r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_launcher.py"

CHIME_TONES = [
    (523, 110),
    (659, 110),
    (784, 160),
]

BRIGHTNESS_BOOST = 80
FADE_STEP        = 7
FADE_DELAY       = 0.018

# ── BRIGHTNESS ───────────────────────────────────────────────────────────
logging.info("Starting brightness boost")
def get_current_brightness():
    try:
        result = subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
            capture_output=True, text=True
        )
        return int(result.stdout.strip())
    except Exception:
        return 50

def set_brightness(value):
    subprocess.run(
        ["powershell", "-WindowStyle", "Hidden", "-Command",
         f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{int(value)})"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def fade_brightness(start, end):
    if start == end:
        return
    step = FADE_STEP if end > start else -FADE_STEP
    current = start
    while True:
        current += step
        if step > 0 and current >= end:
            break
        if step < 0 and current <= end:
            break
        set_brightness(current)
        time.sleep(FADE_DELAY)
    set_brightness(end)

# ── CHIME ─────────────────────────────────────────────────────────────────
logging.info("Playing chime")
def play_chime():
    for freq, duration in CHIME_TONES:
        winsound.Beep(freq, duration)
        time.sleep(0.03)

# ── SYSTEM SNAPSHOT ───────────────────────────────────────────────────────
def get_startup_snapshot():
    battery = psutil.sensors_battery()
    if battery:
        percent = int(battery.percent)
        charging = battery.power_plugged
    else:
        percent = None
        charging = None

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        internet = True
    except OSError:
        internet = False

    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    elif 17 <= hour < 21:
        period = "evening"
    else:
        period = "late night"

    return {
        "battery_percent": percent,
        "charging": charging,
        "internet": internet,
        "period": period,
    }

# ── BUILD MESSAGE ─────────────────────────────────────────────────────────
logging.info("Building message")
def build_welcome_message(snap):
    period   = snap["period"]
    internet = snap["internet"]
    pct      = snap["battery_percent"]
    charging = snap["charging"]

    greetings = {
        "morning":    "Shuubh praabhaat!",
        "afternoon":  "Working afternoon!",
        "evening":    "Evening vibes!",
        "late night": "Hey, still up?",
    }
    greeting = greetings[period]

    if internet:
        net = random.choice(["internet's up", "WiFi's connected", "we're online", "connection's good"])
    else:
        net = "feeling disconnected — local mode on"

    if pct is None:
        bat = "can't read battery right now"
    elif charging:
        bat = f"you're at {pct}% and charging"
    elif pct > 90:
        bat = f"you're almost fully charged at {pct}%"
    elif pct > 80:
        bat = f"{pct}% battery, solid"
    elif pct > 50:
        bat = f"{pct}% battery, decent"
    else:
        bat = random.choice([
            f"only {pct}% left — plug in soon, AP",
            f"{pct}% battery, that's low — charger time",
        ])

    templates = [
        f"VAP welcomes you, AP. {net}, {bat}. {greeting}",
        f"VAP's online, AP. {greeting} {net}, {bat}.",
        f"Good to go, AP. {bat}, {net}. {greeting}",
    ]

    return random.choice(templates)

# ── SPEAK (FIXED — NO CUT-OFF) ────────────────────────────────────────────
logging.info("Starting TTS")



from playsound import playsound

async def speak(text):
    try:
        logging.info("TTS generation started")
        tts = edge_tts.Communicate(text, VOICE, rate="-11%", volume="+11%")
        await tts.save(AUDIO_FILE)

        logging.info("Audio file saved")

        playsound(AUDIO_FILE)

        logging.info("Audio playback completed")

    except Exception as e:
        logging.error(f"TTS ERROR: {e}")

# ── MAIN ──────────────────────────────────────────────────────────────────

async def main():
    original = get_current_brightness()
    boosted = min(120, original + BRIGHTNESS_BOOST)
    try:
        logging.info("Main started")


        try:
            # 1. Brightness UP
            fade_brightness(original, boosted)
            time.sleep(0.08)

            # 2. Chime
            play_chime()
            time.sleep(0.3)

            # 3. Build message
            snap    = get_startup_snapshot()
            message = build_welcome_message(snap)

            # 🔥 Combined smooth speech
            final_message = message + ". Initiating VAP."

            print(f"\n[VAP Welcome] {final_message}\n")

            # 4. Speak (fully synced)
            await speak(final_message)

            # 5. Brightness DOWN
            fade_brightness(boosted, original)

        except Exception as e:
            print(f"[VAP Welcome] Error: {e}")
            try:
                set_brightness(original)
            except Exception:
                pass

        logging.info("Launching CMD with full path")
        # 6. Launch VAP

        subprocess.Popen(
            [r"C:\Windows\System32\cmd.exe", "/k", PYTHON, LAUNCHER],
            creationflags=subprocess.CREATE_NEW_CONSOLE

        )
        logging.info("Launcher started successfully")

    except Exception as e:
        logging.error(f"MAIN ERROR: {e}")


asyncio.run(main()) 

# import edge_tts
# import asyncio
# import subprocess
# import winsound-
# import time
# import os
# import psutil
# import socket
# import datetime
# import random
# import sys
#
# # ── CONFIG ───────────────────────────────────────────────────────────────
#
# VOICE      = "en-GB-RyanNeural"
# AUDIO_FILE = r"C:\Users\Ashish\PycharmProjects\PythonProject\welcome_audio.mp3"
# PYTHON     = sys.executable
# LAUNCHER   = r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_launcher.py"
#
# CHIME_TONES = [
#     (523, 110),
#     (659, 110),
#     (784, 160),
# ]
#
# BRIGHTNESS_BOOST = 80
# FADE_STEP        = 7
# FADE_DELAY       = 0.018
#
# # ── BRIGHTNESS ───────────────────────────────────────────────────────────
#
# def get_current_brightness():
#     try:
#         result = subprocess.run(
#             ["powershell", "-WindowStyle", "Hidden", "-Command",
#              "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
#             capture_output=True, text=True
#         )
#         return int(result.stdout.strip())
#     except Exception:
#         return 50
#
# def set_brightness(value):
#     subprocess.run(
#         ["powershell", "-WindowStyle", "Hidden", "-Command",
#          f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{int(value)})"],
#         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
#     )
#
# def fade_brightness(start, end):
#     if start == end:
#         return
#     step = FADE_STEP if end > start else -FADE_STEP
#     current = start
#     while True:
#         current += step
#         if step > 0 and current >= end:
#             break
#         if step < 0 and current <= end:
#             break
#         set_brightness(current)
#         time.sleep(FADE_DELAY)
#     set_brightness(end)
#
# # ── CHIME ─────────────────────────────────────────────────────────────────
#
# def play_chime():
#     for freq, duration in CHIME_TONES:
#         winsound.Beep(freq, duration)
#         time.sleep(0.03)
#
# # ── SYSTEM SNAPSHOT ───────────────────────────────────────────────────────
#
# def get_startup_snapshot():
#     battery = psutil.sensors_battery()
#     if battery:
#         percent = int(battery.percent)
#         charging = battery.power_plugged
#     else:
#         percent = None
#         charging = None
#
#     try:
#         socket.create_connection(("8.8.8.8", 53), timeout=2)
#         internet = True
#     except OSError:
#         internet = False
#
#     hour = datetime.datetime.now().hour
#     if 5 <= hour < 12:
#         period = "morning"
#     elif 12 <= hour < 17:
#         period = "afternoon"
#     elif 17 <= hour < 21:
#         period = "evening"
#     else:
#         period = "late night"
#
#     return {
#         "battery_percent": percent,
#         "charging": charging,
#         "internet": internet,
#         "period": period,
#     }
#
# # ── BUILD MESSAGE ─────────────────────────────────────────────────────────
#
# def build_welcome_message(snap):
#     period   = snap["period"]
#     internet = snap["internet"]
#     pct      = snap["battery_percent"]
#     charging = snap["charging"]
#
#     greetings = {
#         "morning":    "Shubh prabhat!",
#         "afternoon":  "Working afternoon!",
#         "evening":    "Evening vibes!",
#         "late night": "Hey, still up?",
#     }
#     greeting = greetings[period]
#
#     if internet:
#         net = random.choice(["WiFi's connected", "we're online", "connection's good"])
#     else:
#         net = "feeling disconnected — local mode on"
#
#     if pct is None:
#         bat = "can't read battery right now"
#     elif charging:
#         bat = f"you're at {pct}% and charging"
#     elif pct > 90:
#         bat = f"you're almost fully charged at {pct}%"
#     elif pct > 80:
#         bat = f"{pct}% battery, solid"
#     elif pct > 50:
#         bat = f"{pct}% battery, decent"
#     else:
#         bat = f"{pct}% battery, that's low — charger time"
#
#     templates = [
#         f"VAP welcomes you, AP. {net}, {bat}. {greeting}",
#         f"Good to go, AP. {bat}, {net}. {greeting}",
#     ]
#
#     return random.choice(templates)
#
# # ── SPEAK ─────────────────────────────────────────────────────────────────
#
# async def speak(text):
#     tts = edge_tts.Communicate(text, VOICE, rate="-11%", volume="+11%")
#     await tts.save(AUDIO_FILE)
#
#     subprocess.run(
#         ["powershell", "-WindowStyle", "Hidden", "-c",
#          f"""
#     Add-Type -AssemblyName presentationCore
#     $player = New-Object system.windows.media.mediaplayer
#     $player.open([uri]'{AUDIO_FILE}')
#     $player.Play()
#
#     while ($player.NaturalDuration.HasTimeSpan -eq $false) {{
#         Start-Sleep -Milliseconds 100
#     }}
#
#     $duration = $player.NaturalDuration.TimeSpan.TotalSeconds
#     Start-Sleep -Seconds $duration
#     """
#          ],
#         capture_output=False,
#         # creationflags=subprocess.CREATE_NO_WINDOW
#     )
#
# # ── LAUNCH WITH RETRY ─────────────────────────────────────────────────────
#
# def launch_vap():
#     try:
#         subprocess.Popen(
#             [sys.executable, LAUNCHER, "--interactive"],   # ← added argument
#             creationflags=subprocess.CREATE_NEW_CONSOLE
#         )
#     except Exception as e:
#         print(f"[VAP Launch Failed] {e}")
#
# # ── MAIN ──────────────────────────────────────────────────────────────────
#
# async def main():
#     original = get_current_brightness()
#     boosted  = min(120, original + BRIGHTNESS_BOOST)
#
#     try:
#         # Brightness UP
#         fade_brightness(original, boosted)
#         time.sleep(0.08)
#
#         # Chime
#         play_chime()
#         time.sleep(0.3)
#
#         # Message
#         snap    = get_startup_snapshot()
#         message = build_welcome_message(snap)
#         final_message = message + ". Initiating VAP."
#
#         print(f"\n[VAP Welcome] {final_message}\n")
#
#         # Speak
#         await speak(final_message)
#
#         # ⚠️ TASKKILL REMOVED HERE
#
#
#
#         # Brightness DOWN
#         fade_brightness(boosted, original)
#
#     except Exception as e:
#         print(f"[VAP Welcome] Error: {e}")
#         try:
#             set_brightness(original)
#         except Exception:
#             pass
#
#     # Delay before launch
#     time.sleep(0.5)
#
#     # Launch VAP
#     launch_vap()
#
# # ── RUN ───────────────────────────────────────────────────────────────────
#
# asyncio.run(main())