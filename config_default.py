
## MAKE A COPY OF THIS CALLED config.py
VERBOSE = True
USE_GPU = False  # Set to True to use GPU acceleration. Refer to the README for instructions on installing PyTorch with CUDA support.

### HOTKEY BINDINGS ###
# Hotkeys can be set to None to disable them
# On Mac/Linux, a hotkey cannot overlap another (e.g. cmd+e and cmd+shift+e)
CANCEL_HOTKEY = 'alt+ctrl+e'
NEW_CHAT_HOTKEY = 'alt+ctrl+w'
RECORD_HOTKEY = 'alt+ctrl+r' # Press to start, press again to stop, or hold and release. Double tap to include clipboard
READ_FROM_CLIPBOARD = "ctrl+alt+c"
TRANSCRIBE_RECORDING = "ctrl+alt+t"

### COMPLETIONS API SETTINGS  ###
# Just uncomment the ONE api you want to use

### LOCAL OPTIONS ###

## OLLAMA COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "ollama"
# COMPLETION_MODEL = "llama3"
# OLLAMA_API_BASE_URL = "http://localhost:11434" #This should be the defualt
# OLLAMA_KEEP_ALIVE = "-1" # The duration that models stay loaded in memory. Examples: "20m", "24h". Set to "-1" to keep models loaded indefinitely

## LM Studio COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "lm_studio" 
# COMPLETION_MODEL = "local-model" # You dont need to update this
# LM_STUDIO_API_BASE_URL = "http://localhost:1234/v1" #This should be the defualt

# TabbyAPI COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "tabby_api"
# COMPLETION_MODEL = "llama3-7b-instruct-4.0bpw-exl2"
# TABBY_API_BASE_URL = "http://localhost:5000/v1"


### Hosted APIS ###

## ANTHROPIC COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "anthropic" 
# COMPLETION_MODEL = "claude-3-5-sonnet-20240620" 

## TOGETHER COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "together"
# COMPLETION_MODEL = "meta-llama/Llama-3-8b-chat-hf" 

## OPENAI COMPLETIONS API EXAMPLE ##
COMPLETIONS_API = "openai"
COMPLETION_MODEL = "gpt-4o"

## PERPLEXITY COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "perplexity"
# COMPLETION_MODEL = "llama-3-sonar-small-32k-online"

## OPENROUTER COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "openrouter"
# COMPLETION_MODEL = "openai/gpt-3.5-turbo"

## GROQ COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "groq"
# COMPLETION_MODEL = "llama3-70b-8192"

## GOOGLE GEMINI COMPLETIONS EXAMPLE ##
# COMPLETIONS_API = "google"
# COMPLETION_MODEL = "gemini-1.5-flash"


### COMPLETIONS API PARAMETERS ###
# Allows you to override the default parameters for the completions API
# The available parameters depend on which completions API you are using, so should be looked up in the API documentation online
COMPLETION_PARAMS = {"temperature": 0.7, "max_tokens": 2048}

### TRANSCRIPTION API SETTINGS ###

## Faster Whisper local transcription ###
TRANSCRIPTION_API = "FasterWhisper" # this will use the local whisper model
WHISPER_MODEL = "tiny.en" # If you prefer not to use english set it to "tiny", if the transcription quality is too low then set it to "base" but this will be a little slower
BEAM_SIZE = 5

## Transformers Whisper local transcription ###
# TRANSCRIPTION_API = "TransformersWhisper"
# WHISPER_MODEL = "openai/whisper-tiny.en"

## OPENAI Hosted Transcription ###
# TRANSCRIPTION_API = "openai" # this will use the hosted openai api


### Piper TTS SETTINGS ###
TTS_ENGINE="piper" 
PIPER_VOICE = "default_female_voice" # You can add more voices to the piper_tts/voices folder
PIPER_VOICE_INDEX = 0 # For multi-voice models, select the index of the voice you want to use
PIPER_VOICE_SPEED = 1.0 # Speed of the TTS, 1.0 is normal speed, 2.0 is double speed, 0.5 is half speed

### OPENAI TTS SETTINGS ###
# TTS_ENGINE="openai" 
# OPENAI_VOICE = "nova"

### PROMPTS ###
# Options:
# - "default_prompt": Straight to the point assistant.
# - "chat_prompt": Friendly back-and-forth chat.
# - None: No system prompt, for the raw out-of-the-box model behavior.
# Or create your own prompt in the "system_prompts" folder, then put the name of the file here.
ACTIVE_PROMPT = "default_prompt"

# Options:
# - "clipboard": Allow the assistant to write to the clipboard when requested
# - "time": Add the current time to the system prompt
# - "window_title": Add the current window title to the system prompt
# Or create your own module in the "system_prompts\modules" folder, then add the name of the file here.
ACTIVE_PROMPT_MODULES = ["clipboard", "time", "window_title"]

### MISC ###
AUDIO_FILE_DIR = "audio_files"
MAX_TOKENS = 8000 #Max tokens allowed in memory at once
CLIPBOARD_TEXT_START_SEQ = "[CLIPSTART]" #the model is instructed to place any text for the clipboard between the start and end seq
CLIPBOARD_TEXT_END_SEQ = "[CLIPEND]" #the model is instructed to place any text for the clipboard between the start and end seq
TIMESTAMP_MESSAGES = True # If this is true a timestamp will be added to the end of each of your messages
WINDOWS_INPUT_HANDLER = "keyboard" # "autohotkey" or "keyboard" #  On windows there are 2 options for input handler libraries, the the default is the 'keyboard' library, however some users may prefer to use "autohotkey"


DOUBLE_TAP_THRESHOLD = 0.4 # The time window in which a second press must occur to be considered a double tap
SUPPRESS_NATIVE_HOTKEYS = True # Suppress the native system functionality of the defined hotkeys above (Windows only)
ALWAYS_INCLUDE_CLIPBOARD = False # Always include the clipboard content without having to double tap the record hotkey


### AUDIO SETTINGS ###
BASE_VOLUME = 1 
START_SOUND_VOLUME = 0.05
END_SOUND_VOLUME = 0.05
CANCEL_SOUND_VOLUME = 0.09
MAX_RECORDING_DURATION= 600 # If you record for more than 10 minutes, the recording will stop automatically

