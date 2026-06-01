import os
import datetime

# ------------------------
# CONFIG
# ------------------------
SCREENSHOT_DIR = r"C:\Users\Ashish\Desktop\VAP-SS"


# ------------------------
# MAIN
# ------------------------
def run(command=None):
    try:
        import pyautogui
    except ImportError:
        return "Screenshot failed — pyautogui not installed. Run: pip install pyautogui"

    # create folder if not exists
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

    # build filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"VAP_screenshot_{timestamp}.png"
    full_path = os.path.join(SCREENSHOT_DIR, filename)

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(full_path)
        return f"Screenshot saved — {filename}"

    except Exception as e:
        return f"Screenshot failed — {e}"
