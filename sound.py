import io
import os
import soundfile as sf
import sounddevice as sd
from openai import OpenAI
import config
from dotenv import load_dotenv
import numpy as np
import time


# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY') or os.environ['OPENAI_API_KEY']

def TTS(text, model="tts-1", voice="nova", format="opus"):
    client = OpenAI()

    spoken_response = client.audio.speech.create(
        model=model,
        voice=voice,
        response_format=format,
        input=text
        )

    buffer = io.BytesIO()
    for chunk in spoken_response.iter_bytes(chunk_size=4096):
        buffer.write(chunk)
    buffer.seek(0)

    with sf.SoundFile(buffer, 'r') as sound_file:
        data = sound_file.read(dtype='int16')
    data = data * config.BASE_VOLUME  # Apply BASE_VOLUME multiplier
    sd.play(data, sound_file.samplerate)
    sd.wait()
    
def play_sound(name, volume=1.0):
    volume *= config.BASE_VOLUME
    if name == "start":
        with sf.SoundFile(f"sounds/recording-start.mp3", 'r') as sound_file:
            data = sound_file.read(dtype='int16')
        silence = np.zeros((sound_file.samplerate, data.shape[1]), dtype='int16')
        sd.play(np.concatenate((data * volume, silence)), sound_file.samplerate)
        sd.wait()

    elif name == "end":
        with sf.SoundFile(f"sounds/recording-end.mp3", 'r') as sound_file:
            data = sound_file.read(dtype='int16')
        silence = np.zeros((sound_file.samplerate, data.shape[1]), dtype='int16')
        sd.play(np.concatenate((data * volume, silence)), sound_file.samplerate)
        sd.wait()
    
    elif name == "cancel":
        with sf.SoundFile(f"sounds/recording-cancel.mp3", 'r') as sound_file:
            data = sound_file.read(dtype='int16')
        silence = np.zeros((sound_file.samplerate, data.shape[1]), dtype='int16')
        sd.play(np.concatenate((data * volume, silence)), sound_file.samplerate)
        sd.wait()


def main():
    #play start and end sounds
    # play_sound("start", volume=0.000003)
    # play_sound("end", volume=0.000003)
    TTS("Hello, I'm an AI.", model="tts-1", voice="nova")
    pass


if __name__ == "__main__":
    main()


