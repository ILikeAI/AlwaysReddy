import os
import shutil
import subprocess
import sys

def is_linux():
    return sys.platform.startswith('linux')

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
    if is_linux():
        with open('run_AlwaysReddy.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('source venv/bin/activate\n')
            f.write('python3 main.py\n')
        os.chmod('run_noroot.sh', 0o755)
        print("Created run files")
    else:
        with open('run_AlwaysReddy.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('venv\\Scripts\\activate\n')
            f.write('python main.py\n')
        print("Created run file")


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


if __name__ == "__main__":
    main()