import io
import os
import soundfile as sf
import sounddevice as sd
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
import subprocess
import threading
import queue
import config
import re
import tempfile
import threading
import time
# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

class TTS:
    def __init__(self,parent_client=None):
        self.service = config.TTS_ENGINE
        self.audio_queue = queue.Queue()
        self.running_tts = False
        self.stop_tts = False
        self.play_obj = None
        self.parent_client = parent_client 
        self.text_incoming = False 

        self.play_audio_thread = threading.Thread(target=self.play_audio, daemon=True)
        self.play_audio_thread.start()
        self.completion_client = None

        #delete any left over temp files
        for file in os.listdir(config.AUDIO_FILE_DIR):
            if file.endswith(".wav"):
                os.remove(f"{config.AUDIO_FILE_DIR}\\{file}")

        



    def split_text(self, text):
        split_sentences = re.split('!|\. |\?|\n', text)
        return [sentence for sentence in split_sentences if sentence]
        
    def wait(self):
        self.play_audio_thread.join()

    def run_tts(self, text_to_speak, output_dir=config.AUDIO_FILE_DIR):
        print(f"Running TTS: {text_to_speak}")
        self.running_tts = True  # Ensure this is set when starting to process new text
        if self.text_incoming:
            self.running_tts = True

        if self.running_tts:
            sentences = self.split_text(text_to_speak)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            for i, sentence in enumerate(sentences):
                temp_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=".wav")
                temp_output_file = temp_file.name
                temp_file.close()

                if self.service == "openai":
                    self.TTS_openai(sentence, temp_output_file)
                else:
                    self.TTS_piper(sentence, temp_output_file)

                print("Adding to queue")
                if self.running_tts:
                    self.audio_queue.put((temp_output_file, sentence))

            # Check if the play_audio thread is alive and restart it if necessary
            if not self.play_audio_thread.is_alive():
                self.play_audio_thread = threading.Thread(target=self.play_audio, daemon=True)
                self.play_audio_thread.start()




    def TTS_piper(self, text_to_speak, output_file ):
        
        #clear double quotes from text
        text_to_speak = text_to_speak.replace('"', '')
        
        json_file_name = config.PIPER_VOICE_JSON
        onnx_file_name = config.PIPER_VOICE_ONNX


        # Change voice_name to output_file
        exe_path = "piper\piper.exe"  
        voices_dir = "piper_voices"  

        #if the json file name does not end with .json, add it
        if not json_file_name.endswith(".json"):
            json_file_name += ".json"

        #if the onnx file name does not end with .onnx, add it
        if not onnx_file_name.endswith(".onnx"):
            onnx_file_name += ".onnx"

        onnx_file = f"{voices_dir}\\{onnx_file_name}"
        json_file = f"{voices_dir}\\{json_file_name}"


        if not all(map(os.path.exists, [exe_path, onnx_file, json_file])):
            #debug print files in the directory
            print("One or more required files do not exist.")

            #go through files 1 by 1 and show which are missing
            if not os.path.exists(exe_path):
                print(f"exe_path: {exe_path} does not exist")
            if not os.path.exists(onnx_file):
                print(f"onnx_file: {onnx_file} does not exist")
            if not os.path.exists(json_file):
                print(f"json_file: {json_file} does not exist")

            return

        command = f'echo {text_to_speak} | {exe_path} -m {onnx_file} -c {json_file} -f {output_file}'
        subprocess.run(['cmd.exe', '/c', command], capture_output=True, text=True)

    def TTS_openai(self, text, output_file, model="tts-1", format="opus"):
        
        try:
            client = OpenAI()

            voice = config.OPENAI_VOICE

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
            data = data * config.BASE_VOLUME

            with sf.SoundFile(output_file, 'w', samplerate=sound_file.samplerate, channels=sound_file.channels, subtype='PCM_16') as file:
                file.write(data)
        except Exception as e:
            print(f"Error occurred while using OpenAI API: {e}")
    
    def play_audio(self):
        while True:
            try:
                file_path, sentence = self.audio_queue.get(timeout=1)  # Extract both the file path and the text
                self.running_tts = True  # Indicate processing is active
            except queue.Empty:
                if not self.running_tts:
                    break
                continue

            if not os.path.exists(file_path):
                print(f"The file {file_path} does not exist.")
                self.audio_queue.task_done()
                continue
            if self.parent_client.waiting_for_tts:
                self.parent_client.waiting_for_tts = False
            data, fs = sf.read(file_path, dtype='float32')
            self.parent_client.how_long_to_speak_first_word(time.time())
            self.play_obj = sd.play(data, fs)
            print(f"Playing audio: {sentence}")
            self.last_played_sentence = sentence  # Store the last played sentence
            sd.wait()
            self.audio_queue.task_done()
            #check if file path exists and delete it
            if os.path.exists(file_path):
                os.remove(file_path)

            if self.audio_queue.empty():
                self.running_tts = False # No more items to process, can indicate the process is not active

    def stop(self):
        print("Stopping TTS")
        self.running_tts = False
        self.text_incoming = False
        self.completion_client.cancel = True
        self.waiting_for_tts = False
        sd.stop()  # This will stop any currently playing audio immediately

        # Clear the queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                continue
            self.audio_queue.task_done()




def play_sound_FX(name, volume=1.0):
    volume *= config.BASE_VOLUME
    def play():
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

    # Create a thread to play the sound asynchronously
    sound_thread = threading.Thread(target=play)
    sound_thread.start()

import unittest
from unittest.mock import Mock
from sound import TTS

class TestTTS(unittest.TestCase):
    def test_tts_queue_cancel(self):
        tts = TTS()
        tts.parent_client = Mock()
        tts.text_incoming = True
        tts.run_tts("This is the first test 1 2 3 4 5 6 7 8 9 10 11")
        tts.run_tts("This is the second test")
        
        #tts.stop()
        #print("Cancelling TTS")
        #self.assertTrue(tts.audio_queue.empty())
        #wait for the audio queue to empty
        tts.wait()

if __name__ == "__main__":
    unittest.main()