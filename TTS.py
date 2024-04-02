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
import tempfile

# Load .env file if present
load_dotenv()

class TTS:
    """
    Text-to-Speech (TTS) class for generating speech from text.
    """
    def __init__(self):
        """
        Initialize the TTS class with the parent client and necessary attributes.
        
        """
        self.service = config.TTS_ENGINE
        self.audio_queue = queue.Queue()
        self.stop_tts = False
        self.queing = False
        self.temp_files = []
        self.play_audio_thread = threading.Thread(target=self.play_audio)
        self.completion_client = None
        self.running_tts = False

        # Delete any leftover temp files
        for file in os.listdir(config.AUDIO_FILE_DIR):
            if file.endswith(".wav"):
                os.remove(f"{config.AUDIO_FILE_DIR}\\{file}")
        
    def wait(self):
        """
        Wait for the play_audio_thread to join.
        """
        self.play_audio_thread.join()

    def run_tts(self, sentence, output_dir=config.AUDIO_FILE_DIR):
        """
        Run the TTS for the given sentence and output the audio to the specified directory.
        
        Args:
            sentence (str): The text to be converted to speech.
            output_dir (str): The directory where the audio file will be saved.
        """
        self.queing = True

        # If thread is not running, start it
        if not self.play_audio_thread.is_alive():
            self.play_audio_thread = threading.Thread(target=self.play_audio)
            self.play_audio_thread.start()

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print(f"Error creating output directory {output_dir}: {e}")
                self.queing = False
                return

        try:
            print(f"Running TTS: {sentence}")
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=".wav")
            temp_output_file = temp_file.name
            temp_file.close()


            if self.service == "openai":
                self.TTS_openai(sentence, temp_output_file)
            else:
                self.TTS_piper(sentence, temp_output_file)

            self.temp_files.append(temp_output_file)
            if self.stop_tts:
                print("STOP TTS IS TRUE")
                return
            
            print("Adding to queue")

            self.audio_queue.put((temp_output_file, sentence))

        except Exception as e:
            print(f"Error during TTS processing: {e}")

        self.queing = False

    def TTS_piper(self, text_to_speak, output_file):
        """
        Generate speech from text using the Piper TTS engine and save it to an output file.
        
        Args:
            text_to_speak (str): The text to be converted to speech.
            output_file (str): The file path where the audio will be saved.
        """
        # Remove characters not suitable for TTS, including additional symbols
        disallowed_chars = '"<>[]{}|\\~`^*!@#$%()_+=;'
        text_to_speak = ''.join(filter(lambda x: x not in disallowed_chars, text_to_speak)).replace('&', ' and ')

        json_file_name = config.PIPER_VOICE_JSON
        onnx_file_name = config.PIPER_VOICE_ONNX

        exe_path = r"piper\piper.exe"
        voices_dir = r"piper_voices"

        # Ensure file names have the correct extensions
        json_file_name += ".json" if not json_file_name.endswith(".json") else ""
        onnx_file_name += ".onnx" if not onnx_file_name.endswith(".onnx") else ""

        onnx_file = os.path.join(voices_dir, onnx_file_name)
        json_file = os.path.join(voices_dir, json_file_name)

        # Check if required files exist
        if not all(map(os.path.exists, [exe_path, onnx_file, json_file])):
            print("One or more required files do not exist:")
            for file_path in [exe_path, onnx_file, json_file]:
                if not os.path.exists(file_path):
                    print(f"{file_path} does not exist")
            return
        try:
            command = f'echo {text_to_speak} | {exe_path} -m {onnx_file} -c {json_file} -f {output_file}'
            subprocess.run(['cmd.exe', '/c', command], capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running Piper TTS command: {e}")

    def TTS_openai(self, text, output_file, model="tts-1", format="opus"):
        """
        Generate speech from text using the OpenAI TTS engine and save it to an output file.
        
        Args:
            text (str): The text to be converted to speech.
            output_file (str): The file path where the audio will be saved.
            model (str): The model for TTS.
            format (str): The response format for the audio.
        """
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
            print(f"Error occurred while getting OpenAI TTS: {e}")
    
    def play_audio(self):
        """
        Play the audio from the audio queue.
        """
        while self.queing or not self.audio_queue.empty(): 
            self.running_tts = True
            try:
                file_path, sentence = self.audio_queue.get(timeout=1) 
                
            except queue.Empty:
                continue
            
            data, fs = sf.read(file_path, dtype='float32')
            if self.stop_tts:

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
        """
        Stop the TTS process and clean up any temporary files.
        """
        print("Stopping TTS")
        self.stop_tts = True  # Signal to stop the audio playback loop
        sd.stop()  # Stop any currently playing audio
        # Attempt to clear the queue immediately to prevent any further processing
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                print("Queue is empty")
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


        
        if self.play_audio_thread.is_alive():
            self.play_audio_thread.join()
