import sounddevice as sd
import threading
import config
import time
import os
import numpy as np
from collections import deque
import soundfile as sf

class AudioRecorder:
    """A class to handle the recording of audio using the sounddevice library."""
    def __init__(self, verbose=False):
        """Initializes the audio recorder with default settings."""
        self.filename = "temp_recording.wav"
        self.recording = False
        self.frames = deque()
        self.record_thread = None
        self.start_time = None
        self.verbose = verbose

    def start_recording(self):
        """Starts a new recording session."""
        if not self.recording:
            self.recording = True
            self.frames.clear()
            self.start_time = time.time()
            self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
            try:
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
        """Calculates the duration of the current recording."""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def record_audio(self):
        """Records audio from the default input device."""
        try:
            with sd.InputStream(samplerate=config.FS, channels=1, dtype='float32', callback=self.callback):
                while self.recording:
                    sd.sleep(100)
        except Exception as e:
            self.recording = False
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error during recording: {e}")

    def callback(self, indata, frames, time, status):
        """Callback function for the sounddevice input stream."""
        if status:
            if self.verbose:
                print(f"Error in audio input stream: {status}")
        gain = 1.0  # Set to 1.0 to skip unnecessary gain multiplication
        self.frames.append(indata.copy() * gain)

    def stop_recording(self, cancel=False):
        """Stops the current recording session, optionally cancelling the save."""
        if self.recording:
            self.recording = False
            self.record_thread.join()
            if not cancel:
                self.save_recording()

    def save_recording(self):
        """Saves the recorded audio to a file."""
        if self.frames:
            recording = np.concatenate(self.frames)
            # Normalize if clipping occurred
            recording = np.clip(recording, -1, 1)
            directory = config.AUDIO_FILE_DIR
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                filename = os.path.join(directory, self.filename)
                sf.write(filename, recording, config.FS)
                if self.verbose:
                    print(f"Recording saved to {filename}")
            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"Failed to save recording: {e}")