import os
import shutil
import subprocess

def copy_file(src, dest):
    if os.path.exists(dest):
        should_overwrite = input(f"{dest} already exists. Do you want to overwrite it? (y/n): ")
        if should_overwrite.lower() != 'y':
            print(f"Skipping {dest}")
            return
    shutil.copy(src, dest)
    print(f"Copied {src} to {dest}")

def main():
    # Copy config.py.example to config.py
    copy_file('config.py.example', 'config.py')

    # Copy .env.example to .env
    copy_file('.env.example', '.env')

    print("Please open .env and enter your OpenAI API key.")

    # Ask if they want to install Piper TTS
    install_piper = input("Do you want to install Piper local TTS? (y/n): ")
    if install_piper.lower() == 'y':
        subprocess.run(['python', 'scripts/installpipertts.py'])

if __name__ == "__main__":
    main()