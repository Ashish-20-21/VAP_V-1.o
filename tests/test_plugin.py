from execution.plugin_executor import PluginLoader

pl = PluginLoader()

while True:
    cmd = input("Enter command: ")

    result = pl.execute(cmd)

    if result:
        print(result)
    else:
        print("No plugin handled this command.")