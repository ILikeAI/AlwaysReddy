
import simpleaudio as sa
from pydub import AudioSegment
from pydub.playback import play
import config
import threading
import os
import math

def play_sound_file(file_name, volume, verbose=False):
    try:
        if file_name.lower().endswith(".wav"):
            # Load and play WAV file using simpleaudio
            wave_obj = sa.WaveObject.from_wave_file(file_name)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        elif file_name.lower().endswith(".mp3"):
            # Load and play MP3 file using pydub
            audio = AudioSegment.from_file(file_name, format="mp3")
            # Adjust volume
            if volume != 1.0:
                decibels = 10 * math.log10(volume)
                audio = audio + decibels
            play(audio)
        else:
            raise ValueError(f"Unsupported audio file format: {file_name}")
    except FileNotFoundError as e:
        if verbose:
            print(f"The sound file {file_name} was not found.")
        raise FileNotFoundError(f"The sound file {file_name} was not found.") from e
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"An error occurred while playing the sound file: {e}")
        raise Exception(f"An error occurred while playing the sound file: {e}") from e

def play_sound_FX(name, volume=1.0, verbose=False):
    try:
        volume *= config.BASE_VOLUME
        sound_file_name = f"sounds/recording-{name}"
        if verbose:
            print(f"Playing sound FX: {sound_file_name}")
        if os.path.exists(sound_file_name + ".wav"):
            sound_file_name += ".wav"
        elif os.path.exists(sound_file_name + ".mp3"):
            sound_file_name += ".mp3"
        else:
            raise FileNotFoundError(f"No sound file found for {name}")
        sound_thread = threading.Thread(target=play_sound_file, args=(sound_file_name, volume, verbose))
        sound_thread.start()
        sound_thread.join()  # Wait for the thread to complete
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"An error occurred while attempting to play sound FX: {e}")
