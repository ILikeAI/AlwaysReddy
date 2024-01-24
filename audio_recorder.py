import sounddevice as sd
import threading
import config
import wave
import time
import os
import numpy as np

class AudioRecorder:
    def __init__(self):
        self.filename = "recording.wav"
        self.recording = False
        self.frames = []
        self.record_thread = None
        self.start_time = None
        

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.frames = []
            self.start_time = time.time()
            self.record_thread = threading.Thread(target=self.record_audio)
            self.record_thread.start()
            print("Recording started...")

    @property
    def duration(self):
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def record_audio(self):
        with sd.InputStream(samplerate=config.FS, channels=2, dtype='int16', callback=self.callback):
            while self.recording:
                sd.sleep(1000)

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        gain = 3.0  # Increase this for more gain
        indata = indata * gain
        self.frames.append(indata.copy())



    def stop_recording(self):
        if self.recording:
            print("Stopping recording...")
            self.recording = False
            self.record_thread.join()
            self.save_recording()


    def save_recording(self):
        if self.frames:
            recording = np.concatenate(self.frames)
            # Ensure that the data is within the correct range 
            recording = np.clip(recording, -32768, 32767)
            
            # Create a subdirectory if it doesn't exist
            directory = config.AUDIO_FILE_DIR
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Save the file in the subdirectory
            filename = os.path.join(directory, "recording.wav")
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(config.FS)
                wf.writeframes(recording.astype('int16').tobytes())
            print(f"Recording saved to {filename}")
            