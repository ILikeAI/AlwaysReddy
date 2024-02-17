# Meet AlwaysReddy (Now with Piper TTS!)
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!
You interact with it entirely using hotkeys, it can easily read from or write to your clipboard.
Join the discord: https://discord.gg/v3Hb9za9B4

### How to use:
There are currently only main 2 actions:
Voice chat:
- Press `Ctrl + Shift + Space`  to start dictating, you can talk for as long as you want, then press `Ctrl + Shift + Space` again to stop recording, a few seconds later you will get a voice response from the AI.
Voice chat with context of your clipboard:
- Double tap `Ctrl + Shift + Space` (or just hold `Ctrl + Shift` and quickly press `Space` Twice) This will give the AI the content of your clipboard so you can ask it to reference it, rewrite it, answer questions from its contents... whatever you like! 
- Clear the assistants memory with `ctrl + alt + f12`.
- Cancel recording or TTS with `ctrl + alt + x`

All hotkeys can be edited in config.py

### How to use local TTS or Together API models (easy!)
To use local TTS just open the config file and set `TTS_ENGINE="piper"`

To use Together AI API (allowing for mixtral), open the config file and set `USE_TOGETHER_API = True`
Make sure your TOGETHER_API_KEY is in the .env or in your env vars.

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
5.1 If you need fmmpeg installed run the `fmmpegsetup.bat`script as administrator in the scripts folder

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

Please feel free to improve this repo and make forks of it as you like!