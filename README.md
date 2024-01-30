### Notice:
1. AlwaysReddy is still very much a work in progress!
2. I have only tested this on Windows so I'm unsure if it works on Linux or macOS

## Meet AlwaysReddy
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!

### How to use:
There are currently only main 2 actions:
- Voice chat:
    - Press `Ctrl + Shift + Space`  to start dictating, you can talk for as long as you want, then press `Ctrl + Shift + Space` again to stop recording, a few seconds later you will get a voice response from the AI.
- Voice chat with context of your clipboard:
    - Double tap `Ctrl + Shift + Space` (or just hold `Ctrl + Shift` and quickly press `Space` Twice) This will give the AI the content of your clipboard so you can ask it to reference it, rewrite it, answer questions from its contents... whatever you like! 
- Clear the assistants memory with `ctrl + alt + f12`.
- Cancel recording without getting a response from the AI with `ctrl + alt + x`

All hotkeys can be edited in config.py

### Features:
You interact with AlwaysReddy entirely with hotkeys, it has the ability to:
- Voice chat with you via TTS and STT
- Read from your clipboard (with `Ctrl + Shift + Space` by default )
- Write text to your clipboard on request.
- Support for togetherAI API

### Setup:
1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy`
2. cd into the directory
3. Install reqs with `pip install -r requirements.txt`
4. make a copy of the `.env.example` file and rename it as `.env` and place your OpenAI API key in the file.
5. Run the assistant! `python main.py`

## How to add AlwaysReddy to Startup List
To add AlwaysReddy to your startup list so it starts automatically on your computer startup, follow these steps:
1. Press Windows key + R to open the "Run" dialog.
2. Type "shell:startup" and press Enter. This will open the Startup folder.
3. Copy the `startup_script.bat` from the `scripts` folder in the repo to into this folder.
4. Right click the file and select edit, replace `DIR_TO_ALWAYSREDDY_REPO` with the directory to the main folder of the AlwaysReddy Repo

The file should end up looking something like this:
```cmd
cd C:\Users\Josh\Documents\GitHub\AlwaysReddy\
python main.py
pause
```

### Improvements:
If you want to improve on this system here are some places to start:
- The prompt could do with a lot of work
- Faster STT
- Possible issues around the hotkey that need to be fixed?
- Streaming TTS

Please feel free to improve this repo and make forks of it as you like!