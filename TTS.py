import io
import os
import soundfile as sf
import sounddevice as sd
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
import threading
import queue
import config
import re
import tempfile
import threading

# Load .env file if present
load_dotenv()

class TTS:
    def __init__(self,parent_client=None):
        self.service = config.TTS_ENGINE
        self.audio_queue = queue.Queue()
        self.running_tts = False
        self.stop_tts = False
        self.parent_client = parent_client 
        self.text_incoming = False  
        self.queing = False
        self.temp_files = []

        self.play_audio_thread = threading.Thread(target=self.play_audio)
        
        self.completion_client = None

        #delete any left over temp files
        for file in os.listdir(config.AUDIO_FILE_DIR):
            if file.endswith(".wav"):
                os.remove(f"{config.AUDIO_FILE_DIR}\\{file}")

        


    def split_text(self, text):

        split_sentences = re.split(r'!|\. |\?|\n', text)

        return [sentence for sentence in split_sentences if sentence]
        
    def wait(self):
        self.play_audio_thread.join()

    def run_tts(self, text_to_speak, output_dir=config.AUDIO_FILE_DIR):

        self.queing = True
        self.stop_tts = False   
        #if thread is not running, start it
        if not self.play_audio_thread.is_alive():
            self.play_audio_thread = threading.Thread(target=self.play_audio)
            self.play_audio_thread.start()

        print(f"Running TTS: {text_to_speak}")

        sentences = self.split_text(text_to_speak)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        sentences = [sentence for sentence in sentences if any(char.isalnum() for char in sentence)]

        for sentence in sentences:
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=".wav")
            temp_output_file = temp_file.name
            temp_file.close()

            # Add the temp file to the list
            self.temp_files.append(temp_output_file)

            if self.service == "openai":
                self.TTS_openai(sentence, temp_output_file)
            else:
                self.TTS_piper(sentence, temp_output_file)

            print("Adding to queue")
            if self.stop_tts:
                # Do not add audio to the que if the stop flag is set
                break

            self.audio_queue.put((temp_output_file, sentence))
            if self.parent_client.waiting_for_tts:
                self.parent_client.waiting_for_tts = False

        self.queing = False


    def TTS_piper(self, text_to_speak, output_file ):
        # Remove characters not suitable for TTS, including additional symbols
        disallowed_chars = '"<>[]{}|\\~`^*!@#$%()_+=;'
        text_to_speak = ''.join(filter(lambda x: x not in disallowed_chars, text_to_speak)).replace('&', ' and ')

        json_file_name = config.PIPER_VOICE_JSON
        onnx_file_name = config.PIPER_VOICE_ONNX

        # Change voice_name to output_file
        exe_path = r"piper\piper.exe"
        voices_dir = r"piper_voices"

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
        while self.queing or not self.audio_queue.empty(): 
            try:
                file_path, sentence = self.audio_queue.get(timeout=1) 
                self.running_tts = True
            except queue.Empty:
                continue

            data, fs = sf.read(file_path, dtype='float32')

            if self.stop_tts:
                self.stop_tts = False
                self.running_tts = False
                self.audio_queue.task_done()
                break
            sd.play(data, fs)

            print(f"Playing audio: {sentence}")
            sd.wait()
            self.audio_queue.task_done()

            if os.path.exists(file_path):
                os.remove(file_path)
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)

        self.running_tts = False 

    def stop(self):
        print("Stopping TTS")
        self.stop_tts = True  # Signal to stop the audio playback loop
        sd.stop()  # Stop any currently playing audio
        self.waiting_for_tts = False
        # Attempt to clear the queue immediately to prevent any further processing
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                continue
            self.audio_queue.task_done()
        
        for temp_file in self.temp_files.copy():
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    if temp_file in self.temp_files:
                        self.temp_files.remove(temp_file)

                except PermissionError as e:
                    print(f"Permission denied error when trying to delete {temp_file}: {e}")
        # Wait for the play_audio thread to acknowledge the stop signal and exit
        self.play_audio_thread.join()

        # Reset flags as necessary
        self.running_tts = False
        self.text_incoming = False


