import subprocess
import os

def launch_app(config):
    method = config.get("method")
    command = config.get("command")

    try:
        if method == "exe":
            subprocess.Popen(
                command,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        elif method == "system":
            subprocess.Popen(
                f'start "" {command}',
                shell=True
            )

        elif method == "uwp":
            subprocess.Popen(
                f'start "" {command}',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

        elif method == "system":
            subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

        elif method == "web":
            subprocess.Popen(
                f'start "" {command}',
                shell=True
            )

        elif method == "file":
            os.startfile(command)

        elif method == "plugin":
            return {"status": "error", "message": "plugins route through command_handler"}

        else:
            return {"status": "error", "message": f"Unknown method: {method}"}

        return {"status": "success", "message": f"Opening"}

    except Exception as e:
        return {"status": "error", "message": str(e)}