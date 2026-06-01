import psutil
import socket


# ------------------------
# THRESHOLDS
# ------------------------
RAM_THRESHOLD = 80   # % — warn above this
CPU_THRESHOLD = 40   # % — warn above this


# ------------------------
# CHECKS
# ------------------------
def get_ram_percent():
    return psutil.virtual_memory().percent


def get_cpu_percent():
    return psutil.cpu_percent(interval=0.5)


def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False


# ------------------------
# MAIN STATUS
# ------------------------
def get_system_context():
    ram = get_ram_percent()
    cpu = get_cpu_percent()
    internet = check_internet()

    warnings = []

    if ram >= RAM_THRESHOLD:
        warnings.append(f"RAM is at {ram}%")

    if cpu >= CPU_THRESHOLD:
        warnings.append(f"CPU is at {cpu}%")

    return {
        "ram": ram,
        "cpu": cpu,
        "internet": internet,
        "warnings": warnings,
        "is_high": len(warnings) > 0
    }