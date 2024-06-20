# Welcome to AlwaysReddy 🔊
Hey, I'm Josh, the creator of AlwaysReddy. I am still a little bit of a noob when it comes to programming and I'm really trying to develop my skills over the next year, I'm treating this project as an attempt to better develop my skills, with that in mind I would really appreciate it if you could point out issues and bad practices in my code (of which I'm sure there will be plenty). I would also appreciate if you would make your own improvements to the project so I can learn from your changes. Twitter: https://twitter.com/MindofMachine1

Contact me: joshlikesai@gmail.com

If you think this project is cool and you want to say thanks, feel free to buy me a coffee if you can afford it. I love coffee...

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/ilikeai)


**Pull Requests Welcome!**

## Sections
- [Meet AlwaysReddy](#meet-alwaysreddy)
- [Supported LLM servers](#supported-llm-servers)
- [Supported TTS systems](#supported-tts-systems)
- [Setup](#setup)
- [Known Issues](#known-issues)
- [Troubleshooting](#troubleshooting)
- [How to](#how-to)

## Meet AlwaysReddy 
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!
You interact with it entirely using hotkeys, it can easily read from or write to your clipboard.
It's like having voice ChatGPT running on your computer at all times, you just press a hotkey and it will listen to any questions you have, no need to swap windows or tabs, and if you want to give it context of some extra text, just copy the text and double tap the hotkey! 

Join the discord: https://discord.gg/su44drSBzb

**Here is a demo video of me using it with Llama3** https://www.reddit.com/r/LocalLLaMA/comments/1ca510h/voice_chatting_with_llama_3_8b/

### Features:
You interact with AlwaysReddy entirely with hotkeys, it has the ability to:
- Voice chat with you via TTS and STT
- Read from your clipboard (with `Ctrl + Alt + R + R` rapidly double tapping R).
- Write text to your clipboard on request.
- Can be run 100% locally!!!
- Supports Windows, Mac (experimental), linux (super duper experimental, see [Known Issues](#known-issues))

### Are you a linux wizard?
If you are and you're willing to help please consider look at the [Known Issues](#known-issues), I'm pretty stuck here!

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
- LM Studio (local) - [Setup Guide](https://youtu.be/b6MPdboJEfk)
- Ollama (local) - [Setup Guide](https://youtu.be/BMYwT58rtxw?si=LHTTm85XFEJ5bMUD)
- Perplexity

## Supported TTS systems:
- Piper TTS (local and fast) [See how to change voice model](#how-to-add-new-voices-for-piper-tts)
- OpenAI TTS API
- Default mac TTS

## Setup:

<details>
<summary>GPU Setup Instructions</summary>

## GPU Acceleration

To use GPU acceleration with the faster-whisper API, follow these steps:

1. Check if CUDA is already installed:
   - Open a terminal or command prompt.
   - Run the following command:
     ```
     nvcc --version
     ```
   - If CUDA is installed, you should see output similar to:
     ```
     nvcc: NVIDIA (R) Cuda compiler driver
     Copyright (c) 2005-2021 NVIDIA Corporation
     Built on Sun_Feb_14_21:12:58_PST_2021
     Cuda compilation tools, release 11.2, V11.2.152
     Build cuda_11.2.r11.2/compiler.29618528_0
     ```
   - Note down the CUDA version (e.g., 11.2 in the example above).

2. If CUDA is not installed or you want to install a different version:
   - Visit the official NVIDIA CUDA Toolkit website: [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
   - Download and install the appropriate CUDA Toolkit version for your system.

3. Install PyTorch with CUDA support based on your system and CUDA version. Follow the instructions on the official PyTorch website: [PyTorch Installation](https://pytorch.org/get-started/locally/)

   Example command for CUDA 11.6:
   ```
   pip install torch==1.12.0+cu116 -f https://download.pytorch.org/whl/torch_stable.html
   ```

4. In the `config.py` file, set `USE_GPU = True` to enable GPU acceleration.



</details>

### Setup for Windows, macOS, and Linux:
Note for MacOS: it is expected that you have Brew installed on your system, look [here](https://brew.sh/) for setup

1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy`
2. Navigate into the directory: `cd AlwaysReddy`
3. Run the setup script with `python setup.py` on windows or `python3 setup.py` on mac and linux.
4. Open the `config.py` and `.env` files and update them with your settings and API keys.

If you get `module 'requests' not found` run `pip install requests` or `pip3 install requests`

If you encounter any issues during the setup process, please refer to the [Troubleshooting](#troubleshooting) section below.

## How to Run
### Running on Windows:
- Double-click on the `run_AlwaysReddy.bat` file created during the setup process.

OR run `python main.py` from the command prompt or terminal.
- Activate the venv `venv\Scripts\activate` then run the main script directly `python main.py`.

### Running on macOS and Linux:
- Open a terminal, navigate to the AlwaysReddy directory, and run `./run_AlwaysReddy.sh`.

OR run `python3 main.py` from the command prompt or terminal.
- Activate the venv `source venv/bin/activate` then run the main script directly `python3 main.py`.

## Known Issues:
- On linux it only detects hotkey presses when the application is in foucs, this is a major issue as the whole point of the project is to have it run in the background, if you want to help out this would be a great place to start poking around! -- this may only be an issue with systems using wayland
- Using AlwaysReddy in the terminal on ubuntu does not work for me, when I press the hotkey it just prints the key in the terminal, running it in my IDE works. 

## Troubleshooting:
If you have issues try deleting the venv folder and starting again.
Set VERBOSE = True in the config to get more detailed logs and error traces

## How to:
### How to use AlwaysReddy:
There are currently only main 2 actions:

Voice chat:
- Press `Ctrl + Alt + R`  to start dictating, you can talk for as long as you want, then press `Ctrl + Alt + R` again to stop recording, a few seconds later you will get a voice response from the AI
- You can also hold `Ctrl + Alt + R` to record and release it when you're done to get the transcription.

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

### How to use local faster-whisper transcription:
1. Open the `config.py` file.
2. Locate the "Transcription API Settings" section.
3. Comment out the line `TRANSCRIPTION_API = "openai"` by adding a `#` at the beginning of the line.
4. Uncomment the line `TRANSCRIPTION_API = "faster-whisper"` by removing the `#` at the beginning of the line.
5. Adjust the `WHISPER_MODEL` and `TRANSCRIPTION_LANGUAGE` settings according to your preferences.
6. Save the `config.py` file.

Available models with faster-whisper: tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large-v1, large-v2, large-v3, large, distil-large-v2, distil-medium.en, distil-small.en, distil-large-v3

Here's an example of how your `config.py` file should look like for local whisper transcription:


```python
### Transcription API Settings ###

## OPENAI API TRANSCRIPTION EXAMPLE ##
# TRANSCRIPTION_API = "openai"  # this will use the hosted openai api

## Faster Whisper local transcription ###
TRANSCRIPTION_API = "FasterWhisper" # this will use the local whisper model

# Supported models: 
WHISPER_MODEL = "tiny.en" # If you prefer not to use english set it to "tiny", if the transcription quality is too low then set it to "base" but this will be a little slower

```

Note: The default whisper model is english only, try setting WHISPER_MODEL to 'tiny' or 'base' for other languages

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

### How to make a custom system prompt
1. Navigate to the *system_prompts* directory.
2. Make a copy of an existing prompt file.
3. Open the copy in a text or code editor and edit the prompt inside the two `'''` as you like.
4. Edit your config.py file by setting the `ACTIVE_PROMPT` option to the name of your new prompt file (without the .py extension) as a string.
   - For example, if your new prompt file is *custom_prompt.py*, then set in config.py: `ACTIVE_PROMPT = "custom_prompt"`

## How to add AlwaysReddy to Startup List (Windows)
To add AlwaysReddy to your startup list so it starts automatically on your computer startup, follow these steps:
1. run `venv\Scripts\activate`
2. Run `python setup.py`, follow the prompts, it will ask you if you want to add AlwaysReddy to the startup list, press Y the confrim

If you want to remove AlwaysReddy from the startup list you can follow the same steps again, only say no when asked if you want to add AlwaysReddy to the startup list and it will ask if you would like to remove it, press Y.
