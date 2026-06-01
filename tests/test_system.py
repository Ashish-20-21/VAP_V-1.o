from environment.system_monitor import SystemMonitor

status = SystemMonitor.system_status()

print("System Status:")
print(f"Internet: {'Connected' if status['internet'] else 'Not Connected'}")
print(f"CPU Usage: {status['cpu']}%")
print(f"RAM Usage: {status['ram']}%")