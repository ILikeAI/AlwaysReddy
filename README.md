## Meet AlwaysReddy
AlwaysReddy is a simple LLM assistant with the perfect amount of UI... None!

There are currently only 2 actions:
- Voice chat:
	- Press `Ctrl + Space` to start dictating, you can talk for as long as you want, then press `Ctrl + Space` again to stop recording, a few seconds later you will get a voice response from the AI.
- Voice chat with context of your clipboard:
	- `Ctrl + Shift + Space` This will use the contents of your clipboard as added context for the AI, you can get it to summarize.


Note: AlwaysReddy is still very much a work in progress!
### How to use:
- Press `Ctrl + Space` to start dictating, you can talk for as long as you want, then press `Ctrl + Space` again to stop recording, a few seconds later you will get a voice response from the AI.

### Features:
You interact with AlwaysReddy entirely with hotkeys, it has the ability to:
- Voice chat with you via TTS and STT
- Read from your clipboard (with ctrl + shift + space by default )
- Write text to your clipboard on request.
- Support for togetherAI API

### Setup:
1. Clone this repo with `git clone https://github.com/ILikeAI/AlwaysReddy`
2. cd into the directory
3. Install reqs with `pip install -r requirements.txt`
4. make a copy of the `.env.example` file and rename it as `.env` and place your OpenAI API key in the file.
5. Run the assistant! `python main.py`

### Improvements: 
If you want to improve on this system here are some places to start:
- The prompt could do with a lot of work
- Faster STT
- Possible issues around the hotkey that need to be fixed?
- Streaming TTS



Please feel free to improve this repo and make forks of it as you like!
