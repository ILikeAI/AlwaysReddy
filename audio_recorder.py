import sounddevice as sd
import threading
import config
import time
import os
import numpy as np
from collections import deque
import soundfile as sf

class AudioRecorder:
    def __init__(self):
        self.filename = "temp_recording.wav"
        self.recording = False
        self.frames = deque()
        self.record_thread = None
        self.start_time = None

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.frames.clear()
            self.start_time = time.time()
            self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
            self.record_thread.start()
            print("Recording started...")

    @property
    def duration(self):
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def record_audio(self):
        with sd.InputStream(samplerate=config.FS, channels=2, dtype='float32', callback=self.callback):
            while self.recording:
                sd.sleep(100)

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        gain = 1.0  # Set to 1.0 to skip unnecessary gain multiplication
        self.frames.append(indata.copy() * gain)

    def stop_recording(self, cancel=False):
        if self.recording:
            self.recording = False
            self.record_thread.join()
            if not cancel:
                self.save_recording()


    def save_recording(self):
        if self.frames:
            recording = np.concatenate(self.frames)
            # Normalize if clipping occurred
            recording = np.clip(recording, -1, 1)

            directory = config.AUDIO_FILE_DIR
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            filename = os.path.join(directory, self.filename)

            sf.write(filename, recording, config.FS)
            print(f"Recording saved to {filename}")

