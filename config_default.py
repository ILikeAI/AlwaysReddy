
## MAKE A COPY OF THIS CALLED config.py
VERBOSE = True
USE_GPU = False  # Set to True to use GPU acceleration. Refer to the README for instructions on installing PyTorch with CUDA support.


### COMPLETIONS API SETTINGS  ###
# Just uncomment the ONE api you want to use

### LOCAL OPTIONS ###

## OLLAMA COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "ollama"
# COMPLETION_MODEL = "llama3"
# OLLAMA_API_BASE_URL = "http://localhost:11434" #This should be the defualt

## LM Studio COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "lm_studio" 
# COMPLETION_MODEL = "local-model" # You dont need to update this
# LM_STUDIO_API_BASE_URL = "http://localhost:1234/v1" #This should be the defualt


### Hosted APIS ###

## ANTHROPIC COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "anthropic" 
# COMPLETION_MODEL = "claude-3-sonnet-20240229" 

## TOGETHER COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "together"
# COMPLETION_MODEL = "meta-llama/Llama-3-8b-chat-hf" 

## OPENAI COMPLETIONS API EXAMPLE ##
COMPLETIONS_API = "openai"
COMPLETION_MODEL = "gpt-4-0125-preview"

## PERPLEXITY COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "perplexity"
# COMPLETION_MODEL = "llama-3-sonar-small-32k-online"

## OPENROUTER COMPLETIONS API EXAMPLE ##
# COMPLETIONS_API = "openrouter"
# COMPLETION_MODEL = "openai/gpt-3.5-turbo"

### Transcription API Settings ###

## Faster Whisper local transcription ###
# TRANSCRIPTION_API = "FasterWhisper" # this will use the local whisper model
# WHISPER_MODEL = "tiny.en" # If you prefer not to use english set it to "tiny", if the transcription quality is too low then set it to "base" but this will be a little slower
# BEAM_SIZE = 5


## Transformers Whisper local transcription ###
# TRANSCRIPTION_API = "TransformersWhisper"
# WHISPER_MODEL = "openai/whisper-tiny.en"

## OPENAI Hosted Transcription ###
TRANSCRIPTION_API = "openai" # this will use the hosted openai api



### TTS SETTINGS ###
TTS_ENGINE="openai" # 'piper' or 'openai' or 'mac'(mac is only for macos)

PIPER_VOICE = "default_female_voice"
OPENAI_VOICE = "nova"

### PROMPTS ###
ACTIVE_PROMPT = "default_prompt" #Right now there is only 1 prompt

### HOTKEYS ###
# Hotkeys can be set to None to disable them
CANCEL_HOTKEY = 'alt+ctrl+e'
CLEAR_HISTORY_HOTKEY = 'alt+ctrl+w'
RECORD_HOTKEY = 'alt+ctrl+r' # Press to start, press again to stop, or hold and release. Double tap to include clipboard

RECORD_HOTKEY_DELAY = 0.2 # Seconds to wait for RECORD_HOTKEY double tap before starting recording
SUPPRESS_NATIVE_HOTKEYS = True # Suppress the native system functionality of the defined hotkeys above (Windows only)


### MISC ###
AUDIO_FILE_DIR = "audio_files"
MAX_TOKENS = 8000 #Max tokens allowed in memory at once
START_SEQ = "-CLIPSTART-" #the model is instructed to place any text for the clipboard between the start and end seq
END_SEQ = "-CLIPEND-" #the model is instructed to place any text for the clipboard between the start and end seq


### AUDIO SETTINGS ###
BASE_VOLUME = 1 
START_SOUND_VOLUME = 0.05
END_SOUND_VOLUME = 0.05
CANCEL_SOUND_VOLUME = 0.09
MIN_RECORDING_DURATION = 0.3
MAX_RECORDING_DURATION= 600 # If you record for more than 10 minutes, the recording will stop automatically

