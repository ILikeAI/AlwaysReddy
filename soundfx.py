import soundfile as sf
import sounddevice as sd
import numpy as np
import threading
import config
import threading


def play_sound_file(file_name, volume):
    with sf.SoundFile(file_name, 'r') as sound_file:
        data = sound_file.read(dtype='int16')
    silence = np.zeros((sound_file.samplerate, data.shape[1]), dtype='int16')
    sd.play(np.concatenate((data * volume, silence)), sound_file.samplerate)
    sd.wait()

def play_sound_FX(name, volume=1.0):
    volume *= config.BASE_VOLUME
    sound_file_name = f"sounds/recording-{name}.mp3"
    
    # Create a thread to play the sound asynchronously
    sound_thread = threading.Thread(target=play_sound_file, args=(sound_file_name, volume))
    sound_thread.start()