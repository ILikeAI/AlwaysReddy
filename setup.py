import os
import shutil
import subprocess
import sys
import platform

def is_windows():
    return sys.platform == 'win32'

def install_linux_dependencies():
    try:
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'xclip', 'ffmpeg', 'portaudio19-dev'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing Linux dependencies: {e}")
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
    if is_windows():
        with open('run_AlwaysReddy.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('if not defined VIRTUAL_ENV (\n')
            f.write(' call venv\\Scripts\\activate.bat\n')
            f.write(')\n')
            f.write('python main.py\n')
            f.write('pause\n')
        print("Created run file")

def add_to_startup(run_file):
    if is_windows():
        print("Adding AlwaysReddy to startup may trigger antivirus alerts.")
        print("Please ensure that your antivirus software allows the necessary permissions.")
        print("If you encounter any issues, you can remove AlwaysReddy from startup using the provided option.")
        confirm = input("Are you sure you want to add AlwaysReddy to startup? (y/n): ")
        if confirm.lower() != 'y':
            print("Skipping adding AlwaysReddy to startup.")
            return False

        startup_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        os.makedirs(startup_dir, exist_ok=True)
        startup_file = os.path.join(startup_dir, "AlwaysReddy.bat")
        with open(startup_file, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"cd /d \"{os.path.dirname(os.path.abspath(__file__))}\"\n")
            f.write(f"start cmd /k \"{run_file}\"\n")
        print(f"Added {run_file} to startup")

        print("To remove AlwaysReddy from startup, run this script again and choose the 'Remove from startup' option.")
        return True
    else:
        print("Startup setup is only available for Windows.")
        return False

def remove_from_startup():
    if is_windows():
        startup_file = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "AlwaysReddy.bat")
        if os.path.exists(startup_file):
            os.remove(startup_file)
            print("Removed AlwaysReddy from startup")
        else:
            print("AlwaysReddy not found in startup")
    else:
        print("Startup setup is only available for Windows.")

def main():
    # Check if the system is Linux and install dependencies if necessary
    if not is_windows():
        install_linux_dependencies()

    # Copy config.py.example to config.py
    copy_file('EXAMPLE.config', 'config.py')

    # Copy .env.example to .env
    copy_file('.env.example', '.env')
    print("Please open .env and enter your API keys")

    # Ask if the user wants to install Piper TTS
    install_piper = input("Do you want to install Piper local TTS? (y/n): ")
    if install_piper.lower() == 'y':
        subprocess.run(['python', 'scripts/installpipertts.py'])

    create_run_files()

    if is_windows():
        # Ask if the user wants to add the project to startup
        added_to_startup = False
        add_to_startup_prompt = input("Do you want to add AlwaysReddy to startup? (y/n): ")
        if add_to_startup_prompt.lower() == 'y':
            run_file = 'run_AlwaysReddy.bat'
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