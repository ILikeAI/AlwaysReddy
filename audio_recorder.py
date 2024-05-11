import pyaudio
import threading
import config
import os
import numpy as np
from collections import deque
import wave
import time
import sys
from ctypes import *

class AudioRecorder:
    """A class to handle the recording of audio using the PyAudio library."""
    def __init__(self, verbose=False):
        """
        Initialize the AudioRecorder.

        :param verbose: If True, print detailed information during recording and saving.
        """
        self.filename = "temp_recording.wav"
        self.recording = False
        self.frames = deque()
        self.record_thread = None
        self.start_time = None
        self.verbose = verbose
        
        # Load ALSA library and set error handler for Linux
        if sys.platform.startswith('linux'):
            self.ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
            self.asound = cdll.LoadLibrary('libasound.so')
            self.c_error_handler = self.ERROR_HANDLER_FUNC(self.py_error_handler)
            self.asound.snd_lib_error_set_handler(self.c_error_handler)
        
        # Create PyAudio object and open the stream
        self.audio = pyaudio.PyAudio()
        self.stream = None
        try:
            self.stream = self.audio.open(format=pyaudio.paInt16, channels=1,
                                          rate=config.FS, input=True,
                                          frames_per_buffer=512, start=False)
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Failed to open audio stream: {e}")

    def py_error_handler(self, filename, line, function, err, fmt):
        """A custom error handler to suppress ALSA error messages."""
        pass

    def start_recording(self):
        """
        Start a new recording session.
        
        This method starts the recording thread and the audio stream.
        """
        if not self.recording and self.stream is not None:
            self.recording = True
            self.frames.clear()
            self.start_time = time.time()  # Set the start time when recording starts
            self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
            try:
                self.stream.start_stream()
                self.record_thread.start()
                if self.verbose:
                    print("Recording started...")
            except Exception as e:
                self.recording = False
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"Failed to start recording: {e}")

    @property
    def duration(self):
        """Calculate the duration of the current recording."""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def record_audio(self):
        """Record audio from the stream into the frames buffer."""
        try:
            while self.recording:
                data = self.stream.read(512)
                self.frames.append(np.frombuffer(data, dtype=np.int16))

        except Exception as e:
            self.recording = False
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error during recording: {e}")

    def stop_recording(self, cancel=False):
        """
        Stop the current recording session.
        
        :param cancel: If True, discard the recording without saving.
        """
        if self.recording:
            self.recording = False
            self.record_thread.join()
            if self.stream is not None:
                self.stream.stop_stream()
            if not cancel:
                self.save_recording()

    def save_recording(self):
        """Save the recorded audio to a WAV file."""
        if self.frames:
            recording = np.concatenate(self.frames)
            recording = np.clip(recording, -32768, 32767).astype(np.int16)
            directory = config.AUDIO_FILE_DIR
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                filename = os.path.join(directory, self.filename)
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(config.FS)
                    wf.writeframes(recording.tobytes())
                if self.verbose:
                    print(f"Recording saved to {filename}")

            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"Failed to save recording: {e}")

    def __del__(self):
        """Clean up resources when the AudioRecorder is deleted."""
        if self.stream is not None:
            self.stream.close()
        self.audio.terminate()
        if sys.platform.startswith('linux'):
            self.asound.snd_lib_error_set_handler(None)