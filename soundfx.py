import soundfile as sf
import sounddevice as sd
import numpy as np
import config
import scipy
import threading
from utils import resample

def play_sound_file(file_name, volume):
    """
    Play a sound file at a given volume, followed by a period of silence.

    Args:
        file_name (str): The path to the sound file to be played.
        volume (float): The volume at which to play the sound file.

    Raises:
        FileNotFoundError: If the sound file does not exist.
        Exception: If there is an error reading or playing the sound file.
    """
    try:
        with sf.SoundFile(file_name, 'r') as sound_file:
            data = sound_file.read(dtype='int16')
        
        # Resample the data to the desired sample rate
        resampled_data = scipy.signal.resample(data, int(len(data) * config.FS / sound_file.samplerate), axis=0)
        # Create a silence array of the same duration as one second of the resampled data
        silence = np.zeros((config.FS, resampled_data.shape[1]), dtype='int16')

        # Concatenate resampled data (scaled by volume) with silence
        # Note: Make sure to scale by volume correctly. Here assuming volume scales linearly
        combined_data = np.concatenate((resampled_data * volume, silence))

        # Play the combined data
        sd.play(combined_data, config.FS, device=config.OUT_DEVICE)
        sd.wait()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The sound file {file_name} was not found.") from e
    except Exception as e:
        raise Exception(f"An error occurred while playing the sound file: {e}") from e

def play_sound_FX(name, volume=1.0):
    """
    Play a sound effect with a specified name and volume.

    This function adjusts the volume based on a base volume setting and plays the sound
    asynchronously in a separate thread.

    Args:
        name (str): The name of the sound effect to be played.
        volume (float, optional): The volume at which to play the sound effect. Defaults to 1.0.
    """
    try:
        volume *= config.BASE_VOLUME
        sound_file_name = f"sounds/recording-{name}.mp3"
        
        # Create a thread to play the sound asynchronously
        sound_thread = threading.Thread(target=play_sound_file, args=(sound_file_name, volume))
        sound_thread.start()
    except Exception as e:
        print(f"An error occurred while attempting to play sound FX: {e}")
