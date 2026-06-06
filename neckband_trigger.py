from pynput import keyboard as pynput_keyboard
import time
import asyncio
import subprocess
import winsound
import edge_tts

# ─── Config ───────────────────────────────────────────
VOICE = "en-GB-RyanNeural"
AUDIO_FILE = r"C:\Users\Ashish\VAP\welcome_audio.mp3"
PYTHON = r"C:\Users\Ashish\AppData\Local\Programs\Python\Python310\python.exe"
MAIN = r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py"

TAP_WINDOW = 5.0        # was 0.8 — more breathing room
REQUIRED_TAPS = 3
# ──────────────────────────────────────────────────────

tap_times = []

async def speak(text):
    tts = edge_tts.Communicate(text, VOICE, rate="-10%", volume="+10%")
    await tts.save(AUDIO_FILE)
    subprocess.run(["powershell", "-c",
        "Add-Type -AssemblyName presentationCore; "
        "$player = New-Object system.windows.media.mediaplayer; "
        "$player.open([uri]'{}'); $player.play(); Start-Sleep 5".format(AUDIO_FILE)],
        capture_output=False)

async def run_welcome():
    winsound.MessageBeep(winsound.MB_ICONASTERISK)
    time.sleep(1.5)
    await speak("Senapati welcomes you, AP. All systems ready.")
    await speak("Master, would you like to activate VAP?")
    print("\n  [Y] Yes    [N] No\n")
    choice = input(">>> ").strip().lower()
    if choice == "y":
        await speak("Activating VAP. Stand by.")
        subprocess.Popen(["start", "cmd", "/k", PYTHON, MAIN], shell=True)
    elif choice == "n":
        await speak("Gotcha buddy. Have a good one.")
    else:
        await speak("Invalid input. Shutting down.")

def on_press(key):
    global tap_times

    if key == pynput_keyboard.Key.media_play_pause:
        now = time.time()

        # Clean taps outside the window
        tap_times = [t for t in tap_times if now - t <= TAP_WINDOW]
        tap_times.append(now)

        print(f"  Tap detected — count: {len(tap_times)}")

        if len(tap_times) >= REQUIRED_TAPS:
            tap_times = []  # reset
            print("  3x detected! Triggering VAP welcome...")
            asyncio.run(run_welcome())

# ─── Main ─────────────────────────────────────────────
print("Neckband trigger active. Press play/pause 3x to wake VAP.")
print("Close this window to stop.\n")

with pynput_keyboard.Listener(on_press=on_press) as listener:
    listener.join()

print(f"  Tap detected — count: {len(tap_times)} | times: {[round(t % 100, 2) for t in tap_times]}")