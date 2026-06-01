import subprocess
from archive.app_registry import get_app_path


def launch_app(app_name):
    """Launch an application using its registry name"""


    path = get_app_path(app_name)

    if not path:
        print(f"[VAP] Application '{app_name}' not found in registry.")
        return

    try:
        subprocess.Popen(
            path,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        print(f"[VAP] Launching {app_name}...")

    except Exception as e:
        print(f"[VAP ERROR] Failed to launch {app_name}: {e}")