# core/voice_io.py
# VAP — Voice I/O Module
# -------------------------------------------------------
# Owns: mic management, wake word detection, full command
#       capture, TTS output, mishear retry logic
# Does NOT own: pipeline logic, intent parsing, decisions
#
# Pattern confirmed working:
#   - Fresh Recognizer() per call
#   - No device_index (Windows default mic)
#   - No adjust_for_ambient_noise (broke recognition)
#   - r.listen(source, timeout=X)
#   - phrase_time_limit only for wake word (keeps it short)
#   - Wake phrase: "hey buddy" (reliable recognition)
# -------------------------------------------------------

import asyncio
import subprocess
import winsound
import os
import speech_recognition as sr
import edge_tts

# ── CONFIG ──────────────────────────────────────────────

VOICE       = "en-GB-RyanNeural"
AUDIO_FILE  = r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_response.mp3"
WAKE_PHRASE = "hey buddy"

# Mic tuning — MATCHED TO WORKING TEST
ENERGY_THRESHOLD        = 300
DYNAMIC_ENERGY          = False

# Listening beep tones
BEEP_LOW  = (700,  120)
BEEP_HIGH = (1050, 160)

# Listening timeouts
WAKE_LISTEN_TIMEOUT      = 5    # seconds to wait for sound
WAKE_PHRASE_DURATION     = 3    # max seconds for wake phrase
COMMAND_LISTEN_TIMEOUT   = 6    # seconds to wait for command
COMMAND_PHRASE_DURATION  = 8    # max seconds for full command

# Sentinel for network errors
NETWORK_ERROR = "__network_error__"


# ── BEEP ────────────────────────────────────────────────

def play_listen_beep():
    """Two-tone beep: signals VAP is ready for command."""
    winsound.Beep(BEEP_LOW[0],  BEEP_LOW[1])
    winsound.Beep(BEEP_HIGH[0], BEEP_HIGH[1])


# ── WAKE WORD LAYER (BACKGROUND) ────────────────────────

def listen_wake_word() -> bool:
    """
    Background listener for 'hey buddy'.
    Uses exact working mic pattern from test.
    phrase_time_limit keeps capture short for wake word efficiency.
    """
    try:
        r = sr.Recognizer()
        r.energy_threshold = ENERGY_THRESHOLD
        r.dynamic_energy_threshold = DYNAMIC_ENERGY

        with sr.Microphone() as source:
            # print("  [listening for wake word...]")
            audio = r.listen(
                source,
                timeout=WAKE_LISTEN_TIMEOUT,
                phrase_time_limit=WAKE_PHRASE_DURATION
            )

        text = r.recognize_google(audio).lower().strip()
        # print(f"  [heard: '{text}']")

        if "buddy" in text:
            return True
        return False

    except sr.WaitTimeoutError:
        return False
    except sr.UnknownValueError:
        return False
    except sr.RequestError:
        return False
    except Exception as e:
        print(f"  [wake error: {e}]")
        return False


# ── FULL COMMAND LAYER (ACTIVE) ──────────────────────────

def listen_full_command():
    """
    Full command capture after wake word.
    EXACT pattern from successful test — r.listen(source, timeout=X)
    NO phrase_time_limit so full command isn't cut off.
    """
    play_listen_beep()
    print("[VAP] Listening...")

    try:
        r = sr.Recognizer()
        r.energy_threshold = ENERGY_THRESHOLD
        r.dynamic_energy_threshold = DYNAMIC_ENERGY

        with sr.Microphone() as source:
            audio = r.listen(source, timeout=COMMAND_LISTEN_TIMEOUT)

        text = r.recognize_google(audio).strip()
        # print(f"[VAP] Heard: {text}")
        return text

    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return NETWORK_ERROR
    except Exception:
        return None


# ── TTS OUTPUT ───────────────────────────────────────────

async def _speak_async(text: str):
    """Internal async TTS using edge-tts."""
    clean = text.replace("[VAP]", "").strip()

    tts = edge_tts.Communicate(clean, VOICE, rate="+5%", volume="+10%")
    await tts.save(AUDIO_FILE)

    duration = max(3, len(clean) // 9)

    subprocess.run(
        [
            "powershell", "-c",
            "Add-Type -AssemblyName presentationCore; "
            "$player = New-Object system.windows.media.mediaplayer; "
            "$player.open([uri]'{}'); "
            "$player.play(); "
            "Start-Sleep {}".format(AUDIO_FILE, duration)
        ],
        capture_output=False
    )


def speak(text: str):
    """Public TTS — blocks until audio finishes."""
    if not text or not text.strip():
        return
    asyncio.run(_speak_async(text))


# ── STANDALONE TEST ──────────────────────────────────────

if __name__ == "__main__":

    print("=" * 45)
    print("  VAP voice_io.py — Standalone Test")
    print("=" * 45)

    # Step 1 — wake word test
    print("\nSay 'hey buddy' to trigger...\n")

    detected  = False
    attempts  = 0

    while not detected:
        attempts += 1
        detected = listen_wake_word()
        if not detected and attempts % 3 == 0:
            print(f"  [still waiting... attempt {attempts}]")

    print("\n✅ Wake word detected.")

    # Step 2 — command capture test
    print("\nNow say your command...")
    cmd = listen_full_command()

    if cmd == NETWORK_ERROR:
        print("❌ Network error — Google API unreachable.")
    elif cmd is None:
        print("⚠️  Mishear — nothing captured.")
    else:
        print(f"✅ Command captured: '{cmd}'")

        # Step 3 — TTS playback test
        print("\nPlaying back via TTS...")
        speak(f"Got it A.P. You said — {cmd}")
        print("✅ TTS complete.")

    print("\nTest finished.")