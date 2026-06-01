import subprocess
import os


# UWP apps that run under ApplicationFrameHost — can't close individually
_SHARED_HOST_PROCESS = "ApplicationFrameHost"


def _get_process_name(method, command, config):
    """
    Returns (process_name, kill_method) tuple.
    Priority: explicit "process" field in config → extract from command path.
    kill_method: "taskkill" | "powershell" | "web" | "shared_host"
    """

    # ------------------------
    # EXPLICIT PROCESS FIELD (UWP apps with own process)
    # Set directly in apps.json — most reliable
    # ------------------------
    explicit = config.get("process")
    if explicit:
        if explicit == _SHARED_HOST_PROCESS:
            return explicit, "shared_host"
        if method == "uwp":
            return explicit, "powershell"
        return explicit, "taskkill"

    # ------------------------
    # WEB — URL entries, no process to kill
    # ------------------------
    if method == "web":
        return None, "web"

    # ------------------------
    # SYSTEM — command IS the process name directly
    # e.g. notepad.exe, cmd.exe, taskmgr.exe
    # ------------------------
    if method == "system":
        return command.strip(), "taskkill"
    # ------------------------
    # EXE — extract filename from full path (don't split on spaces)
    # e.g. C:\Program Files\...\pycharm64.exe → pycharm64.exe
    # ------------------------
    if method == "exe":
        clean = command.strip().strip('"')
        return os.path.basename(clean), "taskkill"

    # ------------------------
    # FILE — .lnk shortcuts, may have arguments
    # e.g. "C:\...\shortcut.lnk" → shortcut.lnk
    # ------------------------
    if method == "file":
        clean = command.strip().strip('"').split()[0]
        return os.path.basename(clean), "taskkill"


def _kill_by_taskkill(process_name):
    try:
        # print(f"DEBUG TASKKILL: running -> taskkill /f /im {process_name}")  # ← ADD
        result = subprocess.run(
            ["taskkill", "/f", "/im", process_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return {"status": "success", "message": f"Closed successfully"}
        if result.returncode == 128 or "not found" in result.stderr.lower():
            return {"status": "error", "message": "App is not running"}
        return {"status": "error", "message": f"Could not close — {result.stderr.strip()}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _kill_by_powershell(process_name):
    try:
        result = subprocess.run(
            ["powershell", "-c",
             f"Stop-Process -Name '{process_name}' -Force -ErrorAction Stop"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return {"status": "success", "message": f"Closed successfully"}
        if "cannot find" in result.stderr.lower():
            return {"status": "error", "message": "App is not running"}
        return {"status": "error", "message": f"Could not close — {result.stderr.strip()}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ------------------------
# MAIN ENTRY
# ------------------------


def close_app(app_name, config):
    method  = config.get("method")
    command = config.get("command", "")

    process_name, kill_method = _get_process_name(method, command, config)

    # ------------------------
    # HARD BLOCK — Windows shell protection
    # explorer.exe IS the desktop — killing it destroys taskbar + UI
    # ------------------------
    PROTECTED = ["explorer.exe", "explorer"]
    if process_name and process_name.lower() in PROTECTED:
        return {
            "status": "info",
            "message": "Can't close File Explorer A.P. — it's the Windows shell. Use the X button instead."
        }

    # rest of function unchanged...

    # Web entries — friendly reminder
    if kill_method == "web":
        return {
            "status": "info",
            "message": f"{app_name.title()} runs in Chrome A.P. — press Ctrl+W to close the tab or close Chrome directly."
        }

    # Shared host UWP — can't target individually
    if kill_method == "shared_host":
        return {
            "status": "info",
            "message": f"Can't close {app_name.title()} individually A.P. — use the X button or Alt+F4."
        }

    # No process resolved
    if kill_method == "unknown" or not process_name:
        return {
            "status": "error",
            "message": f"Don't know how to close '{app_name}' A.P."
        }

    if kill_method == "taskkill":
        return _kill_by_taskkill(process_name)

    if kill_method == "powershell":
        return _kill_by_powershell(process_name)

    return {
        "status": "error",
        "message": f"Could not close '{app_name}' A.P."
    }