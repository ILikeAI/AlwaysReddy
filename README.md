# Welcome to AlwaysReddy 🔊
Hey, I'm Josh, the creator of AlwaysReddy. I am still a noob when it comes to programming and I'm really trying to develop my skills over the next year, I'm treating this project as an attempt to better develop my skills, with that in mind I would really appreciate it if you could point out issues and bad practices in my code (of which I'm sure there will be plenty). I would also appreciate if you would make your own improvements to the project so I can learn from your changes. Twitter: https://twitter.com/MindofMachine1

**Pull Requests Welcome!**

## Meet AlwaysReddy 
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!
You interact with it entirely using hotkeys, it can easily read from or write to your clipboard.
Join the discord: https://discord.gg/v3Hb9za9B4

**Here is a demo video of me using it with Llama3** https://www.reddit.com/r/LocalLLaMA/comments/1ca510h/voice_chatting_with_llama_3_8b/

### Features:
You interact with AlwaysReddy entirely with hotkeys, it has the ability to:
- Voice chat with you via TTS and STT
- Read from your clipboard (with `Ctrl + Shift + Space + Space` rapidly double tapping space). NOTE: Linux has a different hotkey!
- Write text to your clipboard on request.
- Can be run 100% locally!!!

## Supported LLM servers:
- OpenAI
- Anthropic
- TogetherAI
- LM Studio (local) Guide: https://youtu.be/3aXDOCibJV0?si=2LTMmaaFbBiTFcnT
- Ollama (local) Guide: https://youtu.be/BMYwT58rtxw?si=LHTTm85XFEJ5bMUD

See how to swap models below

## Use cases:
I often use AlwaysReddy for the following things:
- When I have just learned a new concept I will often explain the concept aloud to AlwaysReddy and have it save the concept (in roughly my words) into a note.
- "What is X called?" Often I know how to roughly describe something but cant remember what it is called, AlwaysReddy is handy for quickly giving me the answer without me having to open the browser.
- "Can you proof read the text in my clipboard before I send it?"
- "From the comments in my clipboard what do the r/LocalLLaMA users think of X?"
- Quick journal entries, I speedily list what I have done today and get it to write a journal entry to my clipboard before I shutdown the computer for the day.

### Setup: 
Please Note that I have only tested on Windows so far, although some users have it running on linux.

Here is a video guide of the setup process: https://youtu.be/14wXj2ypLGU?si=zp13P1Krkt0Vxflo

1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy` 
2. cd into the directory `cd AlwaysReddy`
3. Create a virtual environment with `python -m venv venv`
4. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
5. Install reqs with `pip install -r requirements.txt` also run `pip install -r local_whisper_requirements.txt` if you want to run whisper locally. - check the setup steps here if you have troubles using local whisper https://github.com/m-bain/whisperX
6. Make a copy of the `config.py.example` file and rename the copy to `config.py`
7. Make a copy of the `.env.example` file and rename it as `.env` and place your OpenAI API key in the file. 
8. Run the assistant! `python main.py`
9. If you need ffmpeg installed run the `ffmpegsetup.bat` script as administrator in the scripts folder. If you have troubles with this, try the steps steps here: https://github.com/openai/whisper#setup

<details>
<summary>Known issues</summary>

- Sometimes it will stop recording shortly after it starts recording without the hotkey being pressed. I need to investigate...
- Some users are reporting compatibility issues with Mac and Linux, but some have managed to get it working. We're working on improving cross-platform compatibility. 
</details>

### Linux Support and Considerations

AlwaysReddy now has improved support for Linux users. However, there are a few things to keep in mind:

1. **Running as Root**: Some Linux users, particularly those using the Wayland display protocol, may need to run AlwaysReddy with root privileges to allow the system to capture global hotkeys when the application is running in the background. To do this, use the following command:

   ```
   sudo python main.py
   ```

   Please note that running the application with root privileges should be done with caution and understanding of the potential security implications.

2. **Updated Hotkeys**: For Linux users, the default hotkeys have been updated to avoid conflicts with system shortcuts. The new default hotkeys are:

   - Start/Stop Recording: `Ctrl + Alt + R`
   - Cancel Recording/TTS: `Ctrl + Alt + X`
   - Clear Assistant's Memory: `Ctrl + Alt + C`

   You can still customize these hotkeys in the `config.py` file if desired.

3. **Known Issues**: Some people are hitting sample rate issues with the existing sound FX, there are fixes for that on their way.

If you hit any problems running AlwaysReddy on Linux, please let me know by opening an issue it hitting me up on discord.

### How to use local whisper transcription:
1. Open the `config.py` file.
2. Locate the "Transcription API Settings" section.
3. Comment out the line `TRANSCRIPTION_API = "openai"` by adding a `#` at the beginning of the line.
4. Uncomment the line `TRANSCRIPTION_API = "whisperx"` by removing the `#` at the beginning of the line.
5. Adjust the `WHISPER_MODEL` and `TRANSCRIPTION_LANGUAGE` settings according to your preferences.
6. Save the `config.py` file.

Here's an example of how your `config.py` file should look like for local whisper transcription:

```python
### Transcription API Settings ###

## OPENAI API TRANSCRIPTION EXAMPLE ##
# TRANSCRIPTION_API = "openai"  # this will use the hosted openai api

## Whisper X local transcription API EXAMPLE ##
TRANSCRIPTION_API = "whisperx"  # local transcription!
WHISPER_MODEL = "tiny"  # (tiny, base, small, medium, large) Turn this up to "base" if the transcription is too bad
TRANSCRIPTION_LANGUAGE = "en"
WHISPER_BATCH_SIZE = 16
WHISPER_MODEL_PATH = None  # you can point this to an existing model or leave it set to none
```

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
To swap models open the config.py file and uncomment the sections for the API you want to use. For example this is how you would use Claude 3 sonnet, if you wanted to use LM studio you would comment out the Anthropic section and uncomment the LM studio section.

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