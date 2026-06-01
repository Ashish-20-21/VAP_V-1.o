# Auto Discovery Engine
import os
import json
import win32com.client

START_MENU_PATHS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    os.path.expanduser(
        r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
    )
]

REGISTRY_FILE = "registry/apps.json"


def resolve_shortcut(path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(path)
    return shortcut.Targetpath


def clean_app_name(name):
    name = name.lower()
    name = name.replace(".lnk", "")
    return name.strip()


def scan_start_menu():

    apps = {}

    for base_path in START_MENU_PATHS:

        for root, dirs, files in os.walk(base_path):

            for file in files:

                if file.endswith(".lnk"):

                    shortcut_path = os.path.join(root, file)

                    try:
                        target = resolve_shortcut(shortcut_path)

                        if target and target.endswith(".exe") and os.path.exists(target):

                            app_name = clean_app_name(file)

                            apps[app_name] = target

                    except Exception:
                        pass

    return apps


def save_registry(apps):

    os.makedirs("registry", exist_ok=True)

    with open(REGISTRY_FILE, "w") as f:
        json.dump(apps, f, indent=4)


def build_registry():

    print("Scanning Start Menu for applications...")

    apps = scan_start_menu()

    save_registry(apps)

    print(f"Discovered {len(apps)} applications.")
    print("Registry created successfully.")


if __name__ == "__main__":
    build_registry()