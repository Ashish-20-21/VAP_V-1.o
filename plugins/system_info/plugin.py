import psutil
import socket
import datetime
import random
import asyncio
import edge_tts
import subprocess

VOICE = "en-GB-RyanNeural"
AUDIO_FILE = r"C:\Users\Ashish\PycharmProjects\PythonProject\sysinfo_audio.mp3"


# ------------------------
# DATA FETCH
# ------------------------
def get_system_snapshot():
    cpu = int(psutil.cpu_percent(interval=1))

    ram = psutil.virtual_memory()
    ram_percent = int(ram.percent)

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        internet = True
    except OSError:
        internet = False

    now = datetime.datetime.now()

    return {
        "cpu": cpu,
        "ram_percent": ram_percent,
        "internet": internet,
        "time": now,
    }


# ------------------------
# TIME PHRASE
# ------------------------
def get_time_phrase(now):
    hour = now.hour
    minute = now.minute

    if 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    elif 17 <= hour < 21:
        period = "evening"
    else:
        period = "late night"

    if minute == 0:
        clock = f"{now.strftime('%I %p').lstrip('0').strip()}"
    elif minute < 10:
        clock = f"just past {now.strftime('%I').lstrip('0')} {now.strftime('%p')}"
    elif minute < 20:
        clock = f"quarter past {now.strftime('%I').lstrip('0')} {now.strftime('%p')}"
    elif minute < 35:
        clock = f"half past {now.strftime('%I').lstrip('0')} {now.strftime('%p')}"
    elif minute < 50:
        clock = f"quarter to {(now + datetime.timedelta(hours=1)).strftime('%I').lstrip('0')} {now.strftime('%p')}"
    else:
        clock = f"almost {(now + datetime.timedelta(hours=1)).strftime('%I %p').lstrip('0').strip()}"

    return clock, period


# ------------------------
# CPU PHRASE
# ------------------------
def get_cpu_phrase(cpu):
    if cpu < 20:
        return random.choice([
            f"CPU's barely doing anything at {cpu}%",
            f"CPU's super chill, only {cpu}%",
            f"CPU's at {cpu}%, totally relaxed",
        ])
    elif cpu < 50:
        return random.choice([
            f"CPU's at {cpu}%, nothing crazy",
            f"CPU's cruising at {cpu}%",
            f"running smooth at {cpu}% CPU",
        ])
    elif cpu < 80:
        return random.choice([
            f"CPU's working at {cpu}%, keeping up",
            f"CPU's at {cpu}%, bit busy but fine",
            f"CPU's pushing {cpu}%, holding steady",
        ])
    else:
        return random.choice([
            f"CPU's sweating at {cpu}% — might want to close a few things",
            f"CPU's pretty loaded, {cpu}% — heads up",
            f"CPU's at {cpu}%, running hot",
        ])


# ------------------------
# RAM PHRASE
# ------------------------
def get_ram_phrase(ram_percent):
    if ram_percent < 50:
        return random.choice([
            f"RAM's sitting easy at {ram_percent}%",
            f"RAM's comfortable, {ram_percent}%",
            f"plenty of RAM left at {ram_percent}%",
        ])
    elif ram_percent < 75:
        return random.choice([
            f"RAM's at {ram_percent}%, decent",
            f"RAM's at {ram_percent}%, all good",
        ])
    elif ram_percent < 90:
        return random.choice([
            f"RAM's getting full at {ram_percent}%",
            f"RAM's a bit tight, {ram_percent}%",
            f"RAM's at {ram_percent}%, could wrap up some tabs",
        ])
    else:
        return random.choice([
            f"RAM's almost maxed at {ram_percent}% — close something if you can",
            f"RAM's at {ram_percent}%, getting rough",
        ])


# ------------------------
# SPEAK
# ------------------------
async def speak_async(text):
    tts = edge_tts.Communicate(text, VOICE, rate="+11%", volume="+10%")
    await tts.save(AUDIO_FILE)
    subprocess.run(
        ["powershell", "-c",
         "Add-Type -AssemblyName presentationCore; "
         "$player = New-Object system.windows.media.mediaplayer; "
         "$player.open([uri]'{}'); "
         "$player.play(); "
         "Start-Sleep 12".format(AUDIO_FILE)],
        capture_output=False
    )


# ------------------------
# MAIN RUN (plugin interface)
# ------------------------
def run(command=None):
    snapshot = get_system_snapshot()
    clock, period = get_time_phrase(snapshot["time"])
    cpu_phrase = get_cpu_phrase(snapshot["cpu"])
    ram_phrase = get_ram_phrase(snapshot["ram_percent"])

    templates = [
        f"{cpu_phrase}, {ram_phrase}, and it's {clock} — {period}",
        f"It's {clock}. {cpu_phrase}, and {ram_phrase}",
        f"Quick check — {cpu_phrase}, {ram_phrase}. It's {clock}",
    ]

    message = random.choice(templates)

    print(f"\n[Sysinfo] {message}\n")

    asyncio.run(speak_async(message))

    return message






# import psutil
# import socket
# import datetime
# import random
# import asyncio
# import edge_tts
# import subprocess
#
# # ------------------------
# # DATA FETCH
# # ------------------------
# def get_system_snapshot():
#     cpu = int(psutil.cpu_percent(interval=1))
#     ram = psutil.virtual_memory()
#     ram_percent = int(ram.percent)
#     ram_used = round(ram.used / (1024 ** 3), 1)
#     ram_total = round(ram.total / (1024 ** 3), 1)
#
#     try:
#         socket.create_connection(("8.8.8.8", 53), timeout=2)
#         internet = True
#     except OSError:
#         internet = False
#
#     now = datetime.datetime.now()
#
#     return {
#         "cpu": cpu,
#         "ram_percent": ram_percent,
#         "ram_used": ram_used,
#         "ram_total": ram_total,
#         "internet": internet,
#         "time": now,
#     }
#
#
# # ------------------------
# # TIME PHRASE
# # ------------------------
# def get_time_phrase(now):
#     hour = now.hour
#     minute = now.minute
#
#     # time of day label
#     if 5 <= hour < 12:
#         period = "morning"
#     elif 12 <= hour < 17:
#         period = "afternoon"
#     elif 17 <= hour < 21:
#         period = "evening"
#     else:
#         period = "late night"
#
#     # natural clock phrase
#     if minute == 0:
#         clock = f"{now.strftime('%I %p').lstrip('0').strip()}"
#     elif minute < 10:
#         clock = f"just past {now.strftime('%I').lstrip('0')} {now.strftime('%p')}"
#     elif minute < 20:
#         clock = f"quarter past {now.strftime('%I').lstrip('0')} {now.strftime('%p')}"
#     elif minute < 35:
#         clock = f"half past {now.strftime('%I').lstrip('0')} {now.strftime('%p')}"
#     elif minute < 50:
#         clock = f"quarter to {(now + datetime.timedelta(hours=1)).strftime('%I').lstrip('0')} {now.strftime('%p')}"
#     else:
#         clock = f"almost {(now + datetime.timedelta(hours=1)).strftime('%I %p').lstrip('0').strip()}"
#
#     return clock, period
#
#
# # ------------------------
# # CPU PHRASE
# # ------------------------
# def get_cpu_phrase(cpu):
#     if cpu < 20:
#         options = [
#             f"CPU's barely doing anything at {cpu}%",
#             f"CPU's super chill, only {cpu}%",
#             f"CPU's at {cpu}%, totally relaxed",
#         ]
#     elif cpu < 50:
#         options = [
#             f"CPU's at {cpu}%, nothing crazy",
#             f"CPU's cruising at {cpu}%",
#             f"running smooth at {cpu}% CPU",
#         ]
#     elif cpu < 80:
#         options = [
#             f"CPU's working at {cpu}%, keeping up",
#             f"CPU's at {cpu}%, bit busy but fine",
#             f"CPU's pushing {cpu}%, holding steady",
#         ]
#     else:
#         options = [
#             f"CPU's sweating at {cpu}% — might want to close a few things",
#             f"CPU's pretty loaded, {cpu}% — heads up",
#             f"CPU's at {cpu}%, running hot",
#         ]
#     return random.choice(options)
#
#
# # ------------------------
# # RAM PHRASE
# # ------------------------
# def get_ram_phrase(ram_percent):
#     if ram_percent < 50:
#         options = [
#             f"RAM's sitting easy at {ram_percent}%",
#             f"RAM's comfortable, {ram_percent}%",
#             f"plenty of RAM left at {ram_percent}%",
#         ]
#     elif ram_percent < 75:
#         options = [
#             f"RAM's at {ram_percent}%, decent",
#             f"RAM's moderately loaded at {ram_percent}%",
#             f"RAM's at {ram_percent}%, all good",
#         ]
#     elif ram_percent < 90:
#         options = [
#             f"RAM's getting full at {ram_percent}%",
#             f"RAM's a bit tight, {ram_percent}%",
#             f"RAM's at {ram_percent}%, could wrap up some tabs",
#         ]
#     else:
#         options = [
#             f"RAM's almost maxed at {ram_percent}% — close something if you can",
#             f"RAM's at {ram_percent}%, getting rough",
#             f"RAM's overloaded at {ram_percent}%, watch out",
#         ]
#     return random.choice(options)
#
#
# # ------------------------
# # BUILD SYSINFO MESSAGE
# # ------------------------
# def build_sysinfo_message(snapshot):
#     clock, period = get_time_phrase(snapshot["time"])
#     cpu_phrase = get_cpu_phrase(snapshot["cpu"])
#     ram_phrase = get_ram_phrase(snapshot["ram_percent"])
#
#     templates = [
#         f"{cpu_phrase}, {ram_phrase}, and it's {clock} — {period}.",
#         f"It's {clock}. {cpu_phrase}, and {ram_phrase}.",
#         f"{clock} {period}. {cpu_phrase}, {ram_phrase}.",
#         f"Quick check — {cpu_phrase}, {ram_phrase}. It's {clock}.",
#     ]
#
#     return random.choice(templates)
#
#
# # ------------------------
# # SPEAK
# # ------------------------
# VOICE = "en-GB-RyanNeural"
# AUDIO_FILE = r"C:\Users\Ashish\VAP\test_sysinfo_output.mp3"
#
# async def speak(text):
#     tts = edge_tts.Communicate(text, VOICE, rate="+11%", volume="+10%")
#     await tts.save(AUDIO_FILE)
#     subprocess.run(
#         ["powershell", "-c",
#          "Add-Type -AssemblyName presentationCore; "
#          "$player = New-Object system.windows.media.mediaplayer; "
#          "$player.open([uri]'{}'); "
#          "$player.play(); "
#          "Start-Sleep 12".format(AUDIO_FILE)],
#         capture_output=False
#     )
#
# async def main():
#     snapshot = get_system_snapshot()
#     message = build_sysinfo_message(snapshot)
#
#     print(f"\n[VAP Sysinfo] {message}\n")
#     print(f"  Raw → CPU: {snapshot['cpu']}%  RAM: {snapshot['ram_percent']}%  "
#           f"Internet: {'Yes' if snapshot['internet'] else 'No'}  "
#           f"Time: {snapshot['time'].strftime('%I:%M %p')}")
#
#     await speak(message)
#
# asyncio.run(main())
#
# # ------------------------
# # RUN
# # ------------------------
# if __name__ == "__main__":
#     snapshot = get_system_snapshot()
#     message = build_sysinfo_message(snapshot)
#
#     print(f"\n[VAP Sysinfo] {message}\n")
#     print(f"  Raw → CPU: {snapshot['cpu']}%  RAM: {snapshot['ram_percent']}%  "
#           f"Internet: {'Yes' if snapshot['internet'] else 'No'}  "
#           f"Time: {snapshot['time'].strftime('%I:%M %p')}")


# import psutil
# import socket
# import datetime
#
#
# def run():
#     # ------------------------
#     # CPU
#     # ------------------------
#     cpu = psutil.cpu_percent(interval=1)
#
#     # ------------------------
#     # RAM
#     # ------------------------
#     ram = psutil.virtual_memory()
#     ram_used = round(ram.used / (1024 ** 3), 1)
#     ram_total = round(ram.total / (1024 ** 3), 1)
#     ram_percent = ram.percent
#
#     # ------------------------
#     # INTERNET
#     # ------------------------
#     try:
#         socket.create_connection(("8.8.8.8", 53), timeout=2)
#         internet = "Connected"
#     except OSError:
#         internet = "Not connected"
#
#     # ------------------------
#     # TIME
#     # ------------------------
#     now = datetime.datetime.now().strftime("%I:%M %p, %d %b %Y")
#
#     return (
#         f"System Status — {now}\n"
#         f"  CPU     : {cpu}%\n"
#         f"  RAM     : {ram_used}GB / {ram_total}GB ({ram_percent}%)\n"
#         f"  Internet: {internet}"
#     )