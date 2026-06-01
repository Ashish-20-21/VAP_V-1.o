import os
import datetime
import subprocess

# ------------------------
# CONFIG
# ------------------------
NOTES_FILE = r"C:\Users\Ashish\VAP\data\notes.txt"


# ------------------------
# HELPERS
# ------------------------
def ensure_notes_file():
    folder = os.path.dirname(NOTES_FILE)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            f.write("VAP Notes\n" + "=" * 40 + "\n\n")


# ------------------------
# MAIN
# ------------------------
def run(note_content=None):
    ensure_notes_file()

    if not note_content or not note_content.strip():
        return "NEEDS_INPUT:What should I note down, A.P.?"

    # build timestamped entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}]\n{note_content.strip()}\n\n"

    try:
        # write to file — Python saves it, no Ctrl+S needed
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

        # open in Notepad to show the user
        subprocess.Popen(["notepad.exe", NOTES_FILE])
        return f"Note saved — '{note_content.strip()}'"

    except Exception as e:
        return f"Failed to save note — {e}"


# ------------------------
# OPEN NOTE (separate entry for "open note" command)
# ------------------------
def open_note():
    ensure_notes_file()
    try:
        subprocess.Popen(["notepad.exe", NOTES_FILE])
        return "Opening your notes A.P."
    except Exception as e:
        return f"Failed to open notes — {e}"
