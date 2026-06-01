# import subprocess
# import sys
#
# PYTHON = r"C:\Program Files\Python310\python.exe"
# MAIN   = r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py"
# VAP_INC = r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_inc.py"
#
# print("\n  [I] Interactive Mode    [C] INC Mode    [Q] Quit\n")
#
# choice = input(">>> ").strip().lower()
#
# if choice == "i":
#     subprocess.run([PYTHON, MAIN])
# elif choice == "c":
#     subprocess.run([PYTHON, VAP_INC])
# elif choice == "q":
#     print("Bye!")
#     sys.exit()
# else:
#     print("Invalid option.")
#     input("Press Enter to exit...")

import subprocess
import sys

PYTHON = r"C:\Users\Ashish\AppData\Local\Programs\Python\Python310\python.exe"
MAIN   = r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py"
VAP_INC = r"C:\Users\Ashish\PycharmProjects\PythonProject\vap_inc.py"


# --- NEW: check for command line argument ---
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    if arg == "--inc" or arg == "-c":
        subprocess.run([PYTHON, VAP_INC])
        sys.exit(0)
    elif arg == "--interactive" or arg == "-i":
        subprocess.run([PYTHON, MAIN])
        sys.exit(0)
    elif arg == "--help":
        print("Usage: vap_launcher.py [--interactive | --inc]")
        sys.exit(0)
    # If unknown argument, fall through to normal menu

# --- Original interactive menu (only runs when no valid arg) ---
print("\n  [I] Interactive Mode    [C] INC Mode    [Q] Quit\n")
choice = input(">>> ").strip().lower()

if choice == "i":
    subprocess.run([PYTHON, MAIN])
elif choice == "c":
    subprocess.run([PYTHON, VAP_INC])
elif choice == "q":
    print("Bye!")
    sys.exit()
else:
    print("Invalid option.")
    input("Press Enter to exit...")



# import subprocess
# import sys
#
# PYTHON = r"C:\Program Files\Python310\python.exe"
# MAIN   = r"C:\Users\Ashish\PycharmProjects\PythonProject\main.py"
#
# print("\n  [N] Normal Mode    [I] INC Mode    [Q] Quit\n")
# choice = input(">>> ").strip().lower()
#
# if choice == "n":
#     subprocess.run([PYTHON, MAIN])
# elif choice == "i":
#     subprocess.run([PYTHON, MAIN, "--mode", "inc"])
# elif choice == "q":
#     print("Bye!")
#     sys.exit()
# else:
#     print("Invalid option.")
#     input("Press Enter to exit...")
