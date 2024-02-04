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
import simpleaudio as sa
import glob
import time
import re


# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

class TTS:
    def __init__(self):
        self.service = config.TTS_ENGINE
        self.audio_queue = queue.Queue()
        self.stop_tts = False
        self.play_obj = None  

        self.play_audio_thread = threading.Thread(target=self.play_audio, daemon=True)
        self.play_audio_thread.start()



    def split_text(self, text):
        split_sentences = re.split('!|\.|\?|\n', text)
        return [sentence for sentence in split_sentences if sentence]
        
    def wait(self):
        self.play_audio_thread.join()

    def run_tts(self, text_to_speak, output_file="tts_outputs\\response"):

        self.stop_tts = False

        sentences = self.split_text(text_to_speak)

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i, sentence in enumerate(sentences):
            # Stop adding sentences if the TTS is cancelled
            if self.stop_tts:
                break

            # Append a timestamp to the filename to ensure it's unique
            timestamp = int(time.time())
            unique_output_file = f"{output_file}_{timestamp}_{i}.wav"

            if self.service == "openai":
                self.TTS_openai(sentence, unique_output_file)
            else:
                self.TTS_piper(sentence, unique_output_file)

            self.audio_queue.put(unique_output_file)


    def TTS_piper(self, text_to_speak, output_file ):
        

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
                file_path = self.audio_queue.get(timeout=1) 
            except queue.Empty:
                if self.stop_tts:
                    break
                continue

            if not os.path.exists(file_path):
                print(f"The file {file_path} does not exist.")
                continue
            
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            self.play_obj = wave_obj.play()
            self.play_obj.wait_done()
            self.audio_queue.task_done()

            # Delete the audio file after it has been played
            os.remove(file_path)

    def stop(self):
        self.stop_tts = True
        if self.play_obj:
            self.play_obj.stop()
        # Delete any remaining audio files in the queue
        while not self.audio_queue.empty():
            file_path = self.audio_queue.get()
            if os.path.exists(file_path):
                os.remove(file_path)
        self.audio_queue.join()

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
    tts = TTS()
    print("Running TTS")
    tts.run_tts("This is the first test")
    tts.run_tts("This is the second test")
    tts.wait()
    print("TTS finished")
    tts.stop()  # Stop the text-to-speech process

if __name__ == "__main__":
    main()

