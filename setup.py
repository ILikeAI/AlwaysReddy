import os
import shutil
import subprocess
import sys
import platform
from scripts.installpipertts import setup_piper_tts

def is_windows():
    return sys.platform == 'win32'

def is_macos():
    return sys.platform == 'darwin'

def create_virtualenv(force_create=False):
    if not os.path.isdir('venv') or force_create:
        if force_create and os.path.isdir('venv'):
            print("[!] Removing existing virtual environment...")
            shutil.rmtree('venv')
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
        print("[+] Virtual environment created.")
    else:
        print("[!] Virtual environment already exists.")

def install_dependencies(requirements_file):
    venv_python = os.path.join('venv', 'bin', 'python') if not is_windows() else os.path.join('venv', 'Scripts', 'python')
    command = [venv_python, "-m", "pip", "install", "-r", os.path.join("requirements", requirements_file)]

    try:
        subprocess.check_call(command)
        print(f"[+] Successfully installed dependencies from {requirements_file}.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error installing dependencies from {requirements_file}: {e}")
        sys.exit(1)

def install_linux_dependencies():
    try:
        subprocess.check_call(['sudo', 'apt-get', 'update'])
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'libasound-dev', 'portaudio19-dev', 'libportaudio2', 'libportaudiocpp0', 'ffmpeg'])
        print("[+] Successfully installed Linux dependencies.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error installing Linux dependencies: {e}")
        sys.exit(1)

def install_macos_dependencies():
    try:
        subprocess.check_call(['brew', 'install', 'xclip', 'ffmpeg', 'portaudio'])
        print("[+] Successfully installed dependencies using Homebrew")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error installing dependencies using Homebrew: {e}")
        print("[-] Please make sure Homebrew is installed and try again.")
        sys.exit(1)

def copy_file(src, dest):
    if os.path.exists(dest):
        should_overwrite = input(f"[?] {dest} already exists. Do you want to overwrite it? (y/n): ")
        if should_overwrite.lower() != 'y':
            print(f"[!] Skipping {dest}")
            return
    shutil.copy(src, dest)
    print(f"[+] Copied {src} to {dest}")

def create_run_files():
    if is_windows():
        with open('run_AlwaysReddy.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('call venv\\Scripts\\activate.bat\n')
            f.write('python main.py\n')
            f.write('pause\n')
        print("[+] Created run file for Windows")
    else:
        with open('run_AlwaysReddy.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('source venv/bin/activate\n')
            f.write('python3 main.py\n')
        os.chmod('run_AlwaysReddy.sh', 0o755)
        print("[+] Created run file for Linux/macOS")

def add_to_startup(run_file):
    if is_windows():
        confirm = input("[?] Are you sure you want to add AlwaysReddy to startup? (y/n): ")
        if confirm.lower() != 'y':
            print("[!] Skipping adding AlwaysReddy to startup.")
            return False

        startup_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        os.makedirs(startup_dir, exist_ok=True)
        startup_file = os.path.join(startup_dir, "AlwaysReddy.bat")
        with open(startup_file, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"cd /d \"{os.path.dirname(os.path.abspath(__file__))}\"\n")
            f.write(f"start cmd /k \"{run_file}\"\n")
        print(f"[+] Added {run_file} to startup")

        return True
    else:
        print("[!] Startup setup is only available for Windows.")
        return False

def main():
    print("===== AlwaysReddy Setup =====")
    print()

    if os.path.isdir('venv'):
        user_input = input("[?] A virtual environment already exists. Do you want to create a new one? (y/n): ")
        if user_input.lower() == 'y':
            create_virtualenv(force_create=True)
        else:
            print("[!] Using existing virtual environment.")
    else:
        create_virtualenv()

    # Check if the system is Linux or macOS and install dependencies if necessary
    if is_macos():
        install_macos_dependencies()
    elif not is_windows():
        install_linux_dependencies()

    # Install the main requirements
    install_dependencies("requirements.txt")

    # Ask if the user wants to install extra libraries for faster whisper or transformer whisper
    print("[?] Do you want to install extra libraries for:")
    print("    1. Faster Whisper (local Transcription)")
    print("    2. Transformer Whisper (local Transcription)")
    print("    3. Skip")
    choice = input("[>] Enter your choice (1/2/3): ")

    if choice == "1":
        install_dependencies("faster_whisper_requirements.txt")
    elif choice == "2":
        install_dependencies("transformer_whisper_requirements.txt")
    elif choice == "3":
        print("[!] Skipping installation of extra libraries.")
    else:
        print("[!] Invalid choice. Skipping installation of extra libraries.")

    # Copy config_default.py to config.py
    copy_file('config_default.py', 'config.py')

    # Copy .env.example to .env
    copy_file('.env.example', '.env')
    print("[!] Please open .env and enter your API keys")

    # Ask if the user wants to install Piper TTS
    install_piper = input("[?] Do you want to install Piper local TTS? (y/n): ")
    if install_piper.lower() == 'y':
        setup_piper_tts()

    create_run_files()

    if is_windows():
        # Ask if the user wants to add the project to startup
        add_to_startup_prompt = input("[?] Do you want to add AlwaysReddy to startup? (y/n): ")
        if add_to_startup_prompt.lower() == 'y':
            run_file = 'run_AlwaysReddy.bat'
            add_to_startup(run_file)
        else:
            print("[!] Skipping adding AlwaysReddy to startup.")

    print()
    print("===== Setup Complete =====")

if __name__ == "__main__":
    main()
