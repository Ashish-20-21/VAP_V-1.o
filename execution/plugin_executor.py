#💡 Key Feature of this code — it's infinitely expandable!
#Want new plugin? -> Just do this! >> Create plugins/spotify/plugin.py >>Add run() function inside >>No changes needed in execute_plugin >>It auto discovers! ✅
import importlib

def execute_plugin(plugin_name, command=None):   # ← added command=None
    try:
        module_path = f"plugins.{plugin_name}.plugin"
        plugin_module = importlib.import_module(module_path)

        if hasattr(plugin_module, "run"):
            result = plugin_module.run(command)   # ← passes command through
            return {"status": "success", "message": result}
        else:
            return {"status": "error", "message": f"Plugin '{plugin_name}' has no run() function"}

    except ModuleNotFoundError:
        return {"status": "error", "message": f"Plugin '{plugin_name}' not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Why importlib? To make it flexible ✅
# You don't know which plugin user will ask for!
# User could say "weather" or "calculator" or "news"
# → Can't hardcode all of them at top!
# → importlib loads whichever one is needed at that moment ✅

# ## Real Life Analogy:
# Think of it like an **App Store** 📱
# # importlib = App Store
# # plugin = App
# # run() = Open button

# User says "weather"
# → App Store finds weather app ✅
# → Checks if it has Open button ✅
# → Opens it ✅

### PREVIOUS code for REFERENCE

# import os
# import  JSON
# import importlib
#
#
# import os
#
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PLUGINS_FOLDER = os.path.join(BASE_DIR, "plugins")
#
#
# class PluginLoader:
#
#     def __init__(self):
#         self.plugins = self.load_plugins()
#
#     def load_plugins(self):
#         plugins = {}
#
#         for folder in os.listdir(PLUGINS_FOLDER):
#
#             plugin_path = os.path.join(PLUGINS_FOLDER, folder)
#
#             if os.path.isdir(plugin_path):
#
#                 config_path = os.path.join(plugin_path, "plugin.json")
#
#                 if os.path.exists(config_path):
#
#                     with open(config_path, "r") as f:
#                         config = json.load(f)
#
#                     trigger = config.get("trigger")
#
#                     try:
#                         module = importlib.import_module(
#                             f"plugins.{folder}.plugin"
#                         )
#
#                         plugins[trigger] = module
#
#                     except Exception as e:
#                         print(f"Failed to load plugin {folder}: {e}")
#
#         print(f"Loaded plugins: {list(plugins.keys())}")
#         return plugins
#
#     def execute(self, command):
#
#         command = command.lower()
#
#         for trigger in self.plugins:
#
#             if trigger in command:
#                 plugin = self.plugins[trigger]
#                 return plugin.run(command)
#
#         return None