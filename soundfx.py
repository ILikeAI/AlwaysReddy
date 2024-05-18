import config
import threading
import os
import math
import time
import pyaudio
import wave
import numpy as np
import platform

def play_sound_file(file_name, volume, verbose=False):
    try:
        # Load the audio file using wave
        with wave.open(file_name, 'rb') as audio_file:
            # Create a PyAudio instance
            p = pyaudio.PyAudio()

            # Open a stream for playback
            stream = p.open(format=p.get_format_from_width(audio_file.getsampwidth()),
                            channels=audio_file.getnchannels(),
                            rate=audio_file.getframerate(),
                            output=True)

            # Adjust volume if volume != 1.0
            if volume != 1.0:
                # Read audio data into memory
                data = audio_file.readframes(audio_file.getnframes())
                audio = np.frombuffer(data, dtype=np.int16)
                
                # Adjust volume
                audio = np.multiply(audio, volume).astype(np.int16)

                # Write adjusted audio data to the stream
                stream.write(audio.tobytes())
            else:
                # Read audio data in chunks and write to the stream
                data = audio_file.readframes(1024)
                while data:
                    stream.write(data)
                    data = audio_file.readframes(1024)

            # Stop and close the stream
            stream.stop_stream()
            stream.close()

            # Terminate the PyAudio instance
            p.terminate()

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

        if platform.system() != "Windows":
            sound_thread.join()  # Wait for the thread to complete
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"An error occurred while attempting to play sound FX: {e}")