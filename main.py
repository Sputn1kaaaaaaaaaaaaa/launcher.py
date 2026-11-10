#  _                        _                           
# | | __ _ _   _ _ __   ___| |__   ___ _ __ _ __  _   _ 
# | |/ _` | | | | '_ \ / __| '_ \ / _ \ '__| '_ \| | | |
# | | (_| | |_| | | | | (__| | | |  __/ | _| |_) | |_| |
# |_|\__,_|\__,_|_| |_|\___|_| |_|\___|_|(_) .__/ \__, |
#                                          |_|    |___/ 

# ------------------
# strings of apps
# ------------------

# to do that look impossible but probably possible with some magic:
# - we need to get the list of apps from the system
# - somehow put that into the class apps in the code
#   - we might be able to do that with a literal writing thing that goes "app_name": "app_path" 
#     and writes it into the file
#   - that solution might break the code but it might be worth it

# random note typing quirks:
#   =====> head title (ex: "====> launcher.py, a simple launcher for your apps")
#   ====> parent title (ex: "===> launching firefox...")
#   ==> child title (ex: "==> located at /usr/bin/firefox...")
#   ===> end title (ex: "===> launched firefox!")

import os
import subprocess
import sys
import termios
import tty

# apps are saved here so they're still there next time you run launcher.py
# (when built with pyinstaller, __file__ is a temp folder, so use the binary's folder instead)
if getattr(sys, "frozen", False):
    APPS_DIR = os.path.dirname(sys.executable)
else:
    APPS_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_FILE = os.path.join(APPS_DIR, "apps.txt")

class apps:
    # list of apps and their paths
    apps = {
        # example: "app_name": "app_path"
        # in action example: "firefox": "/usr/bin/firefox"

    }

def load_apps():
    # reads apps.txt, which looks like:
    # firefox {
    #   path = "/usr/bin/firefox"
    # }
    if not os.path.exists(APPS_FILE):
        return
    app_name = None
    with open(APPS_FILE) as f:
        for line in f:
            line = line.strip()
            if line.endswith("{"):
                app_name = line[:-1].strip()
            elif line.startswith("path") and app_name is not None:
                apps.apps[app_name] = line.split("=", 1)[1].strip().strip('"')
            elif line == "}":
                app_name = None

def save_apps():
    with open(APPS_FILE, "w") as f:
        for app_name, app_path in apps.apps.items():
            f.write(f"{app_name} {{\n")
            f.write(f'  path = "{app_path}"\n')
            f.write("}\n\n")
    
class options:
    options = {
        # example: "option_name": "option_description"
        "Add an app": "add a new app to the list",
        "Remove an app": "remove an app from the list",
        "List all apps": "show every app in the list",
        "Quit": "exit launcher.py",
        "Launch an app": "start an app from the list",
        "Edit an app": "change an app's name or path",
    }

def get_key():
    # reads one keypress without needing enter (arrow keys come in as 3 chars)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":
            key += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def select_option():
    names = list(options.options)
    selected = 0
    while True:
        for i, name in enumerate(names):
            if i == selected:
                print(f"\033[K\033[7m> {name}\033[0m")
            else:
                print(f"\033[K  {name}")
        key = get_key()
        if key == "\x1b[A":
            selected = (selected - 1) % len(names)
        elif key == "\x1b[B":
            selected = (selected + 1) % len(names)
        elif key in ("\r", "\n"):
            return names[selected]
        elif key == "\x03":
            raise KeyboardInterrupt
        # move the cursor back up so the menu redraws in place
        print(f"\033[{len(names)}A", end="")

def logo_figlet():
    print(r" _                        _                           ")
    print(r"| | __ _ _   _ _ __   ___| |__   ___ _ __ _ __  _   _ ")
    print(r"| |/ _` | | | | '_ \ / __| '_ \ / _ \ '__| '_ \| | | |")
    print(r"| | (_| | |_| | | | | (__| | | |  __/ | _| |_) | |_| |")
    print(r"|_|\__,_|\__,_|_| |_|\___|_| |_|\___|_|(_) .__/ \__, |")
    print(r"                                         |_|    |___/ ")
    print("---------------------------------------------------------")

def main():
    logo_figlet()
    print("=====> launcher.py, a simple launcher for your apps")
    load_apps()

    # need while true loop to keep the program running until the user quits
    while True:
        choice = select_option()
        print(f"====> selected {choice}")
        if choice == "Quit":
            print("====> bye!")
            break
        elif choice == "Add an app":
            print("====> adding an app")
            app_name = input("===> enter the name of the app: ")
            app_path = input("===> enter the path of the app (CASE SENSITIVE): ")
            apps.apps[app_name] = app_path
            save_apps()
        elif choice == "Remove an app":
            print("====> removing an app")
            app_name = input("====> enter the name of the app to remove: ")
            if app_name in apps.apps:
                del apps.apps[app_name]
                save_apps()
            else:
                print("====> app not found")
        elif choice == "Launch an app":
            print("====> launching an app")
            app_name = input("===> enter the name of the app to launch: ")
            if app_name in apps.apps:
                # Popen so the launcher doesn't freeze until the app is closed
                try:
                    subprocess.Popen([apps.apps[app_name]], start_new_session=True)
                    print(f"===> launched {app_name}!")
                except OSError as e:
                    print(f"====> couldn't launch {app_name}: {e}")
            else:
                print("====> app not found")
        elif choice == "Edit an app":
            print("====> editing an app")
            app_name = input("===> enter the name of the app to edit: ")
            if app_name in apps.apps:
                app_path = input("===> enter the new path of the app (CASE SENSITIVE): ")
                apps.apps[app_name] = app_path
                save_apps()
            else:
                print("====> app not found")
        elif choice == "List all apps":
            print("====> listing all apps")
            for app_name, app_path in apps.apps.items():
                print(f"===> {app_name}: {app_path}")

main()