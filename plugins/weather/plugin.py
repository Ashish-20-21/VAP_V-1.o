import subprocess

# ------------------------
# CONFIG
# ------------------------
WEATHER_UWP = "shell:AppsFolder\\Microsoft.BingWeather_8wekyb3d8bbwe!App"


# ------------------------
# MAIN
# ------------------------
def run(command=None):
    try:
        subprocess.Popen(f'start "" "{WEATHER_UWP}"', shell=True)
        return "On it — pulling up your weather dashboard."

    except Exception as e:
        # fallback — open in browser
        try:
            import webbrowser
            webbrowser.open("https://wttr.in")
            return "Opening weather in your browser."
        except Exception as e2:
            return f"Weather launch failed — {e2}"
