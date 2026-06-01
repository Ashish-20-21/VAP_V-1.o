# FOR PAST 7 DAYS SYSTEM FILE COUNT

# from usage_engine import get_usage_data
#
# data = get_usage_data(days=7)
#
# for app, info in data.items():
#     print(app, info)

#--------------------------

#List of the top 5 apps
#
# from brain.usage_engine import get_top_apps
#
# top_apps = get_top_apps(n=5)
#
# print("Top Apps:", top_apps)

#------------testing beepsound working-----------------
# import pygame
# pygame.mixer.init()
# pygame.mixer.music.load(r"C:\Users\Ashish\PycharmProjects\PythonProject\assets\beep.mp3")
# pygame.mixer.music.play()
# import time
# time.sleep(2)

# command = "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"
# part = command.split("\\")[-1]    # → 5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App
# part = part.split("!")[0]          # → 5319275A.WhatsAppDesktop_cv1g1gvanyjgm
# part = part.split("_")[0]          # → 5319275A.WhatsAppDesktop
# part = part.split(".")[-1]         # → WhatsAppDesktop
# print(part)  # should print: WhatsAppDesktop


# from brain.intent_engine import parse
# print(parse("close whatsapp"))
# print(parse("close chrome"))
# print(parse("close notepad"))

# from registry.registry_manager import get_app_config
# config = get_app_config("pycharm")
# print(config)


#-----------------------MIC TEST---------------------------------------------
# mic_test.py — run this standalone, paste output back

# import speech_recognition as sr
#
# r = sr.Recognizer()
#
# # List all available mics
# print("Available microphones:")
# for i, name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f"  [{i}] {name}")
#
# print()
#
# # Test with longer calibration + manual energy floor
# with sr.Microphone() as source:
#     print("Calibrating for 3 seconds — stay silent...")
#     r.adjust_for_ambient_noise(source, duration=3)
#     print(f"Energy threshold after calibration: {int(r.energy_threshold)}")
#
#     # Force a minimum floor — 183 is too low
#     if r.energy_threshold < 300:
#         r.energy_threshold = 300
#         print(f"Threshold too low — manually set to: 300")
#
#     print()
#     print("Now say ANYTHING clearly into your mic...")
#     print("Listening for 5 seconds...")
#
#     try:
#         audio = r.listen(source, timeout=5, phrase_time_limit=5)
#         print("Audio captured — sending to Google...")
#
#         text = r.recognize_google(audio)
#         print(f"Google heard: '{text}'")
#
#     except sr.WaitTimeoutError:
#         print("TIMEOUT — mic did not detect any sound above threshold")
#         print("Either mic is wrong device, or threshold still too low")
#
#     except sr.UnknownValueError:
#         print("Audio captured but Google couldn't parse it")
#         print("Mic is working — speech quality issue")
#
#     except sr.RequestError as e:
#         print(f"Google API error: {e}")
#         print("Internet or API key issue")


# mic_device_test.py
# Tests specific mic devices to find which one captures voice correctly

# import speech_recognition as sr
#
# r = sr.Recognizer()
# r.energy_threshold = 500        # force a sane floor
# r.dynamic_energy_threshold = True
#
# # Candidates — your actual input devices
# CANDIDATES = {
#     1:  "Microphone Array (AMD Audio Device)",
#     5:  "Microphone Array (AMD Audio Device) - alt",
#     9:  "Microphone Array (AMD Audio Device) - alt2",
#     13: "Microphone (Realtek HD Audio Mic input)",   # ← most likely correct
#     18: "Microphone Array 1 (AMDAfdInstall)",
#     19: "Microphone Array 2 (AMDAfdInstall)",
# }
#
# print("Testing mic devices one by one.")
# print("For each — say 'hey vap open chrome' clearly when prompted.\n")
#
# for index, label in CANDIDATES.items():
#     print(f"─" * 50)
#     print(f"Testing [{index}] {label}")
#
#     try:
#         with sr.Microphone(device_index=index) as source:
#             print("  Calibrating 2s — stay silent...")
#             r.adjust_for_ambient_noise(source, duration=2)
#             print(f"  Threshold: {int(r.energy_threshold)}")
#
#             print("  >> Say something now (5 seconds)...")
#             audio = r.listen(source, timeout=5, phrase_time_limit=5)
#
#         print("  Sending to Google...")
#         text = r.recognize_google(audio)
#         print(f"  ✅ RESULT: '{text}'")
#         print(f"\n  *** WORKING DEVICE FOUND: index={index} ***\n")
#
#     except sr.WaitTimeoutError:
#         print("  ⏱ Timeout — no sound detected above threshold")
#
#     except sr.UnknownValueError:
#         print("  ⚠️  Audio captured but Google couldn't parse")
#
#     except sr.RequestError as e:
#         print(f"  ❌ Google API error: {e}")
#
#     except Exception as e:
#         print(f"  ❌ Device error: {e}")
#
#     print()
#
# print("Done. Note which index printed ✅ RESULT.")


# live_mic_test.py
# Simple loop — listens, transcribes, prints, repeats
# Press Ctrl+C to stop

# live_mic_test_v2.py
# Testing different energy thresholds
# Press 1/2/3 to switch sensitivity levels, Ctrl+C to stop

# import speech_recognition as sr
#
# # Three sensitivity levels to test
# LEVELS = {
#     "1": {"name": "High Sensitivity", "threshold": 100},
#     "2": {"name": "Medium (current)", "threshold": 300},
#     "3": {"name": "Low Sensitivity", "threshold": 600},
# }
#
# current_level = "1"
# LISTEN_TIMEOUT = 5
#
# print("=" * 55)
# print("  Live Mic Test — Sensitivity Tester")
# print("=" * 55)
# print("  Press 1 = High sensitivity (100)")
# print("  Press 2 = Medium (300) — current")
# print("  Press 3 = Low sensitivity (600)")
# print("  Ctrl+C to stop")
# print("=" * 55)
# print()
#
# while True:
#     try:
#         level_info = LEVELS[current_level]
#
#         r = sr.Recognizer()
#         r.energy_threshold = level_info["threshold"]
#         r.dynamic_energy_threshold = False
#
#         with sr.Microphone() as source:
#             print(f"🎤 [{level_info['name']}] Listening...")
#             audio = r.listen(source, timeout=LISTEN_TIMEOUT)
#
#         text = r.recognize_google(audio).strip()
#         print(f"✅ Heard: \"{text}\"")
#         print()
#
#     except sr.WaitTimeoutError:
#         print("⏰ Timeout — no speech detected")
#         print()
#
#     except sr.UnknownValueError:
#         print("❓ Heard something but couldn't understand")
#         print("   Try: speak louder, or press 1 for higher sensitivity")
#         print()
#
#     except sr.RequestError:
#         print("🌐 Network error — check internet")
#         print()
#
#     except KeyboardInterrupt:
#         print("\n👋 Stopped.")
#         break
#
#     except Exception as e:
#         # Check if it's a number key press (we're hijacking the loop)
#         if hasattr(e, 'args') and len(e.args) > 0:
#             arg = str(e.args[0])
#             if arg in LEVELS:
#                 current_level = arg
#                 print(f"\n🔧 Switched to: {LEVELS[current_level]['name']}")
#                 print()
#                 continue
#         print(f"⚠️  Error: {e}")
#         print()

import pygame
pygame.mixer.init()
print("OK")