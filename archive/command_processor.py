from archive.dynamic_app_launcher import launch_app


COMMAND_KEYWORDS = ["open", "start", "launch"]

FILLER_WORDS = ["the", "a", "an", "my", "please"]


def process_command(user_input):

    user_input = user_input.lower()

    words = user_input.split()

    # remove filler words
    words = [word for word in words if word not in FILLER_WORDS]

    for keyword in COMMAND_KEYWORDS:

        if keyword in words:

            keyword_index = words.index(keyword)

            if keyword_index + 1 < len(words):

                app_name = words[keyword_index + 1]

                launch_app(app_name)

                return

    print("[VAP] Command not recognized.")