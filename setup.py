import os
import shutil
import subprocess
import sys
import platform

def is_linux():
    return sys.platform.startswith('linux')

def is_windows():
    return sys.platform == 'win32'

def is_macos():
    return sys.platform == 'darwin'

def install_xclip():
    try:
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'xclip'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing xclip: {e}")
        sys.exit(1)

def copy_file(src, dest):
    """
    Copies a file from the source path to the destination path.
    If the destination file already exists, it prompts the user for confirmation to overwrite.
    """
    if os.path.exists(dest):
        if dest == "config.py":
            should_overwrite = input(f"{dest} already exists. Do you want to overwrite it? This may be required after an update as new contents are added to the config file often.(y/n): ")
        else:
            should_overwrite = input(f"{dest} already exists. Do you want to overwrite it? (y/n): ")
        if should_overwrite.lower() != 'y':
            print(f"Skipping {dest}")
            return
    shutil.copy(src, dest)
    print(f"Copied {src} to {dest}")

def create_run_files():
    if is_linux() or is_macos():
        with open('run_AlwaysReddy.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('cd "$(dirname "$0")"\n')
            f.write('if [[ -z "$VIRTUAL_ENV" ]]; then\n')
            f.write(' source venv/bin/activate\n')
            f.write('fi\n')
            f.write('python3 main.py\n')
        os.chmod('run_AlwaysReddy.sh', 0o755)
        print("Created run files")
    elif is_windows():
        with open('run_AlwaysReddy.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('if not defined VIRTUAL_ENV (\n')
            f.write(' call venv\\Scripts\\activate.bat\n')
            f.write(')\n')
            f.write('python main.py\n')
        print("Created run file")

def add_to_startup(run_file):
    print("Adding AlwaysReddy to startup may trigger antivirus alerts.")
    print("Please ensure that your antivirus software allows the necessary permissions.")
    print("If you encounter any issues, you can remove AlwaysReddy from startup using the provided option.")
    confirm = input("Are you sure you want to add AlwaysReddy to startup? (y/n): ")
    if confirm.lower() != 'y':
        print("Skipping adding AlwaysReddy to startup.")
        return False

    if is_linux():
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_file = os.path.join(autostart_dir, "AlwaysReddy.desktop")
        with open(desktop_file, 'w') as f:
            f.write("[Desktop Entry]\n")
            f.write("Type=Application\n")
            f.write(f"Exec=bash -c 'cd \"{os.path.dirname(os.path.abspath(__file__))}\" && ./\"{run_file}\"'\n")
            f.write("Hidden=false\n")
            f.write("NoDisplay=false\n")
            f.write("X-GNOME-Autostart-enabled=true\n")
            f.write("Name=AlwaysReddy\n")
        print(f"Added {run_file} to startup")
    elif is_windows():
        startup_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        os.makedirs(startup_dir, exist_ok=True)
        startup_file = os.path.join(startup_dir, "AlwaysReddy.bat")
        with open(startup_file, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"cd /d \"{os.path.dirname(os.path.abspath(__file__))}\"\n")
            f.write(f"call \"{run_file}\"\n")
        print(f"Added {run_file} to startup")
    elif is_macos():
        plist_file = os.path.expanduser("~/Library/LaunchAgents/com.AlwaysReddy.plist")
        with open(plist_file, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            f.write('<plist version="1.0">\n')
            f.write('<dict>\n')
            f.write('    <key>Label</key>\n')
            f.write('    <string>com.AlwaysReddy</string>\n')
            f.write('    <key>ProgramArguments</key>\n')
            f.write('    <array>\n')
            f.write('        <string>/bin/bash</string>\n')
            f.write('        <string>-c</string>\n')
            f.write(f'        <string>cd "{os.path.dirname(os.path.abspath(__file__))}" &amp;&amp; ./{run_file}</string>\n')
            f.write('    </array>\n')
            f.write('    <key>RunAtLoad</key>\n')
            f.write('    <true/>\n')
            f.write('</dict>\n')
            f.write('</plist>\n')
        print(f"Added {run_file} to startup")

    print("To remove AlwaysReddy from startup, run this script again and choose the 'Remove from startup' option.")
    return True

def remove_from_startup():
    if is_linux():
        desktop_file = os.path.expanduser("~/.config/autostart/AlwaysReddy.desktop")
        if os.path.exists(desktop_file):
            os.remove(desktop_file)
            print("Removed AlwaysReddy from startup")
        else:
            print("AlwaysReddy not found in startup")
    elif is_windows():
        startup_file = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "AlwaysReddy.bat")
        if os.path.exists(startup_file):
            os.remove(startup_file)
            print("Removed AlwaysReddy from startup")
        else:
            print("AlwaysReddy not found in startup")
    elif is_macos():
        plist_file = os.path.expanduser("~/Library/LaunchAgents/com.AlwaysReddy.plist")
        if os.path.exists(plist_file):
            os.remove(plist_file)
            print("Removed AlwaysReddy from startup")
        else:
            print("AlwaysReddy not found in startup")

def main():
    # Check if the system is Linux and install xclip if necessary
    if is_linux():
        install_xclip()

    # Copy config.py.example to config.py
    copy_file('EXAMPLE.config', 'config.py')

    # Copy .env.example to .env
    copy_file('.env.example', '.env')
    print("Please open .env and enter your OpenAI API key.")

    # Ask if the user wants to install Piper TTS
    install_piper = input("Do you want to install Piper local TTS? (y/n): ")
    if install_piper.lower() == 'y':
        subprocess.run(['python', 'scripts/installpipertts.py'])

    create_run_files()

    # Ask if the user wants to add the project to startup
    added_to_startup = False
    add_to_startup_prompt = input("Do you want to add AlwaysReddy to startup? (y/n): ")
    if add_to_startup_prompt.lower() == 'y':
        run_file = 'run_AlwaysReddy.sh' if is_linux() or is_macos() else 'run_AlwaysReddy.bat'
        added_to_startup = add_to_startup(run_file)
    else:
        print("Skipping adding AlwaysReddy to startup.")

    # Ask if the user wants to remove the project from startup
    if not added_to_startup:
        remove_from_startup_prompt = input("Do you want to remove AlwaysReddy from startup? (y/n): ")
        if remove_from_startup_prompt.lower() == 'y':
            remove_from_startup()
        else:
            print("Skipping removing AlwaysReddy from startup.")

if __name__ == "__main__":
    main()