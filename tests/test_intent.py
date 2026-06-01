from brain.intent_engine import IntentEngine

engine = IntentEngine()

command = input("Enter command: ")

intent, target = engine.detect_intent(command)

print("Intent:", intent)
print("Target:", target)