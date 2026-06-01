import subprocess

# ------------------------
# CONFIG
# ------------------------
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE = "--profile-directory=Profile 3"
PLAYLIST_URL = "https://music.youtube.com"


# ------------------------
# MAIN
# ------------------------
def run(command=None):
    try:
        subprocess.Popen([CHROME_PATH, CHROME_PROFILE, PLAYLIST_URL])
        return "Your playlist is ready — enjoy the music A.P."

    except Exception as e:
        # fallback — default browser
        try:
            import webbrowser
            webbrowser.open(PLAYLIST_URL)
            return "Opening your playlist."
        except Exception as e2:
            return f"Playlist launch failed — {e2}"
