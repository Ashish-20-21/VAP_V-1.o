import json
import re


class AppRegistry:

    def __init__(self):

        with open("old_apps.json", "r") as f:
            self.apps = json.load(f)

    def find_apps_in_command(self, command):

        # remove punctuation
        command = re.sub(r"[^\w\s]", " ", command)

        command_words = command.lower().split()

        detected_apps = set()


        for word in command_words:

            if word in self.apps:
                detected_apps.add(word)

        return list(detected_apps)