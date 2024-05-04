# Welcome to AlwaysReddy 🔊
Hey, I'm Josh, the creator of AlwaysReddy. I am still a little bit of a noob when it comes to programming and I'm really trying to develop my skills over the next year, I'm treating this project as an attempt to better develop my skills, with that in mind I would really appreciate it if you could point out issues and bad practices in my code (of which I'm sure there will be plenty). I would also appreciate if you would make your own improvements to the project so I can learn from your changes. Twitter: https://twitter.com/MindofMachine1

Contact me: joshlikesai@gmail.com

If you think this project is cool and you want to say thanks, feel free to buy me a coffee if you can afford it. I love coffee...

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/ilikeai)


**Pull Requests Welcome!**

## Meet AlwaysReddy 
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!
You interact with it entirely using hotkeys, it can easily read from or write to your clipboard.
It's like having voice ChatGPT running on your computer at all times, you just press a hotkey and it will listen to any questions you have, no need to swap windows or tabs, and if you want to give it context of some extra text, just copy the text and double tap the hotkey! 
Join the discord: https://discord.gg/v3Hb9za9B4

**Here is a demo video of me using it with Llama3** https://www.reddit.com/r/LocalLLaMA/comments/1ca510h/voice_chatting_with_llama_3_8b/

### Features:
You interact with AlwaysReddy entirely with hotkeys, it has the ability to:
- Voice chat with you via TTS and STT
- Read from your clipboard (with `Ctrl + Alt + R + R` rapidly double tapping R). NOTE: Linux has a different hotkey!
- Write text to your clipboard on request.
- Can be run 100% locally!!!

### Use cases:
I often use AlwaysReddy for the following things:
- When I have just learned a new concept I will often explain the concept aloud to AlwaysReddy and have it save the concept (in roughly my words) into a note.
- "What is X called?" Often I know how to roughly describe something but cant remember what it is called, AlwaysReddy is handy for quickly giving me the answer without me having to open the browser.
- "Can you proof read the text in my clipboard before I send it?"
- "From the comments in my clipboard what do the r/LocalLLaMA users think of X?"
- Quick journal entries, I speedily list what I have done today and get it to write a journal entry to my clipboard before I shutdown the computer for the day.

## Supported LLM servers:
- OpenAI
- Anthropic
- TogetherAI
- LM Studio (local) - [Setup Guide](https://youtu.be/3aXDOCibJV0?si=2LTMmaaFbBiTFcnT)
- Ollama (local) - [Setup Guide](https://youtu.be/BMYwT58rtxw?si=LHTTm85XFEJ5bMUD)

## Supported TTS systems:
- Piper TTS (local and fast) [See how to change voice model](#how-to-add-new-voices-for-piper-tts)
- OpenAI TTS API

## Setup:

### Setup for Windows:

1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy`
2. cd into the directory `cd AlwaysReddy`
3. Create a virtual environment with `python -m venv venv`-- This step is imortant, make sure to name it exactly `venv`
4. Activate the virtual environment: `venv\Scripts\activate`
5. Install requirements with `pip install -r requirements.txt`. Also run `pip install -r local_whisper_requirements.txt` if you want to run whisper locally. - check the setup steps here if you have troubles using local whisper https://github.com/m-bain/whisperX
6. Run the setup script with `python setup.py`. This will also create a run file `run_AlwaysReddy.bat`.
7. Open the `config.py` and `.env` files and update them with your settings and API key.
8. Run the assistant with `run_AlwaysReddy.bat` or `python main.py`. The run file will automatically activate the virtual environment.

If you get an error saying you need to install ffmpeg, try the steps here: https://github.com/openai/whisper#setup

### Setup for Linux:
Linux support is super experimental but its working for me, contact me if you have any trouble.

1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy`
2. cd into the directory `cd AlwaysReddy`
3. Create a virtual environment with `python3 -m venv venv`-- This step is imortant, make sure to name it exactly `venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install requirements with `pip install -r requirements.txt`. Also run `pip install -r local_whisper_requirements.txt` if you want to run whisper locally. - check the setup steps here if you have troubles using local whisper https://github.com/m-bain/whisperX
6. Run the setup script with `python3 setup.py`. This will also create a run file `run_AlwaysReddy.sh`.
7. Open the `config.py` and `.env` files and update them with your settings and API key.
8. Run the assistant with `./run_AlwaysReddy.sh` or `python3 main.py`. The run file will automatically activate the virtual environment.

Please note that on linux we are using the pynput library which does not let us use space or tab in our hotkeys.

If you get an error saying you need to install ffmpeg, try the steps here: https://github.com/openai/whisper#setup

## Known Issues:
- For me it crashes if I spam the record hotkey, I havent worked out why just yet.

## Troubleshooting:
If you have issues try deleting the venv folder and starting again.
Set VERBOSE = True in the config to get more detailed logs and error traces

## How to:
### How to use AlwaysReddy:
There are currently only main 2 actions:

Voice chat:
- Press `Ctrl + Alt + R`  to start dictating, you can talk for as long as you want, then press `Ctrl + Alt + R` again to stop recording, a few seconds later you will get a voice response from the AIal

Voice chat with context of your clipboard:
- Double tap `Ctrl + Alt + R` (or just hold `Ctrl + Alt` and quickly press `R` Twice) This will give the AI the content of your clipboard so you can ask it to reference it, rewrite it, answer questions from its contents... whatever you like! 
- Clear the assistants memory with `Ctrl + Alt + W`.
- Cancel recording or TTS with `Ctrl + Alt + E`

**Please let me know if you think of better hotkey defaults!**

All hotkeys can be edited in config.py


### How to add new voices for Piper TTS:
1. Go to https://huggingface.co/rhasspy/piper-voices/tree/main and navigate to your desired language.
2. Click on the name of the voice you want to try. There are different sized models available; I suggest using the medium size as it's pretty fast but still sounds great (for a locally run model).
3. Listen to the sample in the "sample" folder to ensure you like the voice.
4. Download the `.onnx` and `.json` files for the chosen voice.
5. Create a new folder in the `piper_tts\voices` directory and give it a descriptive name. You will need to enter the name of this folder into the `config.py` file. For example: `PIPER_VOICE = "default_female_voice"`.
6. Move the two downloaded files (`.onnx` and `.json`) into your newly created folder within the `piper_tts\voices` directory.

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

### How to swap servers or models
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

## How to add AlwaysReddy to Startup List (Windows)
To add AlwaysReddy to your startup list so it starts automatically on your computer startup, follow these steps:
1. run `venv\Scripts\activate`
2. Run `python setup.py`, follow the prompts, it will ask you if you want to add AlwaysReddy to the startup list, press Y the confrim

If you want to remove AlwaysReddy from the startup list you can follow the same steps again, only say no when asked if you want to add AlwaysReddy to the startup list and it will ask if you would like to remove it, press Y.