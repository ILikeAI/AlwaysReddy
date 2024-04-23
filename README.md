# Welcome to AlwaysReddy 🔊
Hey, I'm Josh, the creator of AlwaysReddy. I am still a noob when it comes to programming and I'm really trying to develop my skills over the next year, I'm treating this project as an attempt to better develop my skills, with that in mind I would really appreciate it if you could point out issues and bad practices in my code (of which I'm sure there will be plenty). I would also appreciate if you would make your own improvements to the project so I can learn from your changes.

**Pull Requests Welcome!**

## Meet AlwaysReddy 
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!
You interact with it entirely using hotkeys, it can easily read from or write to your clipboard.
Join the discord: https://discord.gg/v3Hb9za9B4

### Features:
You interact with AlwaysReddy entirely with hotkeys, it has the ability to:
- Voice chat with you via TTS and STT
- Read from your clipboard (with `Ctrl + Shift + Space + Space` rapidly double tapping space).
- Write text to your clipboard on request.

## Supported LLM servers:
- OpenAI
- Anthropic
- TogetherAI
- LM Studio (local)
See how to swap models below
## Use cases:
I often use AlwaysReddy for the following things:
- When I have just learned a new concept I will often explain the concept aloud to AlwaysReddy and have it save the concept (in roughly my words) into a note.
- "What is X called?" Often I know how to roughly describe something but cant remember what it is called, AlwaysReddy is handy for quickly giving me the answer without me having to open the browser.
- "Can you proof read the text in my clipboard before I send it?"
- "From the comments in my clipboard what do the r/LocalLLaMA users think of X?"
- Quick journal entries, I speedily list what I have done today and get it to write a journal entry to my clipboard before I shutdown the computer for the day.

## Known issues:
- Sometimes it will stop recording shortly after it starts recording without the hotkey being pressed. I need to investigate... 

### Setup: 
1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy` 
2. cd into the directory
3. Install reqs with `pip install -r requirements.txt`
4. Make a copy of the `config.py.example` file and rename the copy to `config.py`
5. Make a copy of the `.env.example` file and rename it as `.env` and place your OpenAI API key in the file. 
6. Run the assistant! `python main.py`
7. If you need ffmpeg installed run the `ffmpegsetup.bat` script as administrator in the scripts folder.

**Important note:** You must have an OpenAI API key in the .env file, at this point the only transcription option is via the OpenAI API, I hope to support local whisper soon

### How to use:
There are currently only main 2 actions:
Voice chat:
- Press `Ctrl + Shift + Space`  to start dictating, you can talk for as long as you want, then press `Ctrl + Shift + Space` again to stop recording, a few seconds later you will get a voice response from the AI.
Voice chat with context of your clipboard:
- Double tap `Ctrl + Shift + Space` (or just hold `Ctrl + Shift` and quickly press `Space` Twice) This will give the AI the content of your clipboard so you can ask it to reference it, rewrite it, answer questions from its contents... whatever you like! 
- Clear the assistants memory with `ctrl + alt + f12`.
- Cancel recording or TTS with `ctrl + alt + x`

All hotkeys can be edited in config.py

## How to swap servers or models
To swap models open the config.py file and uncomment the seconds for the API you want to use. For example this is how you would use Claude 3 sonnet, if you wanted to use LM studio you would comment out the Anthropic section and uncomment the LM studio section.
```python
### COMPLETIONS API SETTINGS ###

## LM Studio COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "lm_studio" 
# COMPLETION_MODEL = "local-model" #This stays as local-model no matter what model you are using

## ANTHROPIC COMPLETIONS API EXAMPLE ##
COMPLETIONS_API = "anthropic" 
COMPLETION_MODEL = "claude-3-sonnet-20240229" 

## TOGETHER COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "together"
# COMPLETION_MODEL = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT" 

## OPENAI COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "openai"
# COMPLETION_MODEL = "gpt-4-0125-preview"

```

### How to use local TTS
To use local TTS just open the config file and set `TTS_ENGINE="piper"`

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
