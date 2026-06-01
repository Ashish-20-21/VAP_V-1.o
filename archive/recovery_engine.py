def handle_failure(intent_data):
        intent = intent_data.get("intent")
        target = intent_data.get("target")

        if intent is None:
            return {
                "status": "error",
                "message": "I didn't understand that command. Try saying something like 'open chrome'."
            }

        if target is None:
            return {
                "status": "error",
                "message": "Please specify what you want to open. For example, 'open notepad'."
            }

        return {
            "status": "error",
            "message": f"I couldn't handle '{intent}' for '{target}'."
        }

# # ❌ Old — not helpful
# return False
# # What failed? Why? No idea!
#
# # ✅ New — descriptive
# return {"status": "error", "message": "No target specified."}
# # Exactly what failed and why! ✅
#               OR

#ANALOGY :
## Real Life Analogy:
# ❌ Old way = carrying groceries by hand
# 🥛 milk in one hand
# 🍞 bread in other hand
# 🥚 eggs under arm
# → messy, hard to manage!
#
# # ✅ New way = groceries in one bag 📦
# → everything in one place
# → clean and easy to carry!



### PREVIOUS Code for REFERENCE below ###


# class RecoveryEngine:      #(hard-coded)
#
#     def handle(self, intent, targets):
#
#         if intent is None:
#             print("I couldn't understand the command.")
#             print("Try saying something like: open calculator")
#
#             return False
#
#         if intent == "OPEN_APP" and len(targets) == 0:
#             print("I couldn't find any supported apps in that command.")
#
#             return False
#
#         return True