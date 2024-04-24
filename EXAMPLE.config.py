## MAKE A COPY OF THIS CALLED config.py

### COMPLETIONS API SETTINGS  ###
# Just uncomment the ONE api you want to use

### LOCAL OPTIONS ###

## OLLAMA COMPLETIONS API EXAMPLE ##
COMPLETIONS_API = "ollama"
COMPLETION_MODEL = "llama3:8b-instruct-fp16"
OLLAMA_API_BASE_URL = "http://localhost:11434" #This should be the defualt

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
# COMPLETIONS_API = "openai"
# COMPLETION_MODEL = "gpt-4-0125-preview"


### Transcription API Settings ###

## Whisper X local transcription API EXAMPLE ##
TRANSCRIPTION_API = "whisperx" #local transcription!
WHISPER_MODEL = "tiny" # (tiny, base, small, medium, large) Turn this up to "base" if the transcription is too bad
TRANSCRIPTION_LANGUAGE = "en" 
WHISPER_BATCH_SIZE = 16
WHISPER_MODEL_PATH = None # you can point this to an existing model or leave it set to none

### Transcription API Settings ###
# TRANSCRIPTION_API = "openai" # this will use the hosted openai api



### VOICE SETTINGS ###
PIPER_VOICE_JSON="en_en_US_amy_medium_en_US-amy-medium.onnx.json" #These are located in the piper_voices folder
PIPER_VOICE_ONNX="en_US-amy-medium.onnx"
TTS_ENGINE="piper" # 'piper' or 'openai' piper is local and fast but openai is better sounding
OPENAI_VOICE = "nova"

### PROMPTS ###
ACTIVE_PROMPT = "default_prompt" #Right now there is only 1 prompt

### HOTKEYS ###
CANCEL_HOTKEY = 'ctrl + alt + x'
CLEAR_HISTORY_HOTKEY = 'ctrl + alt + f12'
RECORD_HOTKEY = 'ctrl + shift + space'

### MISC ###
HOTKEY_DELAY = 0.5
AUDIO_FILE_DIR = "audio_files"
MAX_TOKENS = 8000 #Max tokens allowed in memory at once
START_SEQ = "-CLIPSTART-" #the model is instructed to place any text for the clipboard between the start and end seq
END_SEQ = "-CLIPEND-" #the model is instructed to place any text for the clipboard between the start and end seq


### AUDIO SETTINGS ###
BASE_VOLUME = 1 
FS = 48000 # 48000 #44100
# see sounddevice.query_devices()
OUT_DEVICE = "HD-Audio Generic: ALC1220 Analog (hw:2,0)"# 6 # 6 HD-Audio Generic: ALC1220 Analog (hw:2,0), ALSA (2 in, 2 out)
IN_DEVICE = "KLIM Talk: USB Audio (hw:3,0)" # 8 KLIM Talk: USB Audio (hw:3,0), ALSA (1 in, 0 out)
START_SOUND_VOLUME = 0.000003
END_SOUND_VOLUME = 0.000003
CANCEL_SOUND_VOLUME = 0.000009
MIN_RECORDING_DURATION = 0.3
MAX_RECORDING_DURATION= 600 # If you record for more than 10 minutes, the recording will stop automatically
