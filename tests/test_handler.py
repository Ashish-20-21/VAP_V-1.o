from brain.intent_engine import IntentEngine
from brain.command_handler import CommandHandler
from archive.app_registry import AppRegistry
from archive.recovery_engine import RecoveryEngine

intent_engine = IntentEngine()
handler = CommandHandler()
registry = AppRegistry()
recovery = RecoveryEngine()

command = input("Command: ")

intent, _ = intent_engine.detect_intent(command)
targets = registry.find_apps_in_command(command)

print("Intent:", intent)
print("Targets:", targets)

# recovery check
if not recovery.handle(intent, targets):
    exit()

for target in targets:
    handler.handle(intent, target)