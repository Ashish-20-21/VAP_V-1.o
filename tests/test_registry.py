from registry.registry_manager import RegistryManager

rm = RegistryManager()

user_input = input("Enter app name: ")

app = rm.find_app(user_input)

if app:
    path = rm.get_app_path(app)
    print(f"Found: {app}")
    print(f"Path: {path}")
else:
    print("App not found.")