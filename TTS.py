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
import utils

# Load .env file if present
load_dotenv()

class TTS:
    """
    Text-to-Speech (TTS) class for generating speech from text.
    """
    def __init__(self, parent_client):
        """
        Initialize the TTS class with the parent client and necessary attributes.
        
        """
        self.service = config.TTS_ENGINE
        self.audio_queue = queue.Queue()
        self.parent_client = parent_client
        self.queing = False
        self.temp_files = []
        self.play_audio_thread = threading.Thread(target=self.play_audio)
        self.completion_client = None
        self.running_tts = False
        self.last_sentence_spoken = ""
        if self.service == "openai":
            self.OpenAIClient = OpenAI()


        # Delete any leftover temp files if any
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
        # Set queuing flag to True
        self.queing = True
    
        # If the audio playback thread is not running, start it
        if not self.play_audio_thread.is_alive():
            self.play_audio_thread = threading.Thread(target=self.play_audio)
            self.play_audio_thread.start()
    
        # If the output directory does not exist, create it
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print(f"Error creating output directory {output_dir}: {e}")
                self.queing = False
                return
    
        try:
            # Create a temporary file in the output directory
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=".wav")
            temp_output_file = temp_file.name
            temp_file.close()
    
            # Run the TTS using the appropriate service
            if self.service == "openai":
                result = self.TTS_openai(sentence, temp_output_file)
            else:
                result = self.TTS_piper(sentence, temp_output_file)
            
            # If the TTS was successful, add the output file to the queue
            if result == "success":
                print(f"Running TTS: {sentence}")
                
                # If the stop flag is set, return early
                if self.parent_client.stop_response:
                    print("STOP TTS IS TRUE")
                    return
                
                self.temp_files.append(temp_output_file)
    
                print("Adding to queue")
                self.audio_queue.put((temp_output_file, sentence))
        except Exception as e:
            print(f"Error during TTS processing: {e}")
    
        # Set queuing flag to False
        self.queing = False


    def TTS_piper(self, text_to_speak, output_file):
        """
        Generate speech from text using the Piper TTS engine and save it to an output file.
        
        Args:
            text_to_speak (str): The text to be converted to speech.
            output_file (str): The file path where the audio will be saved.
        """
        # Sanitize the input text by removing unsuitable characters
        text_to_speak = utils.sanitize_text(text_to_speak)
        
        # If there is no text left after sanitization, return "failed"
        if not text_to_speak.strip():
            return "failed"

        # Get the file names for the voice model and configuration
        json_file_name = config.PIPER_VOICE_JSON
        onnx_file_name = config.PIPER_VOICE_ONNX

        # Define the paths for the Piper executable and voices directory
        exe_path = r"piper\piper.exe"
        voices_dir = r"piper_voices"

        # Ensure the voice model and configuration file names have the correct extensions
        json_file_name += ".json" if not json_file_name.endswith(".json") else ""
        onnx_file_name += ".onnx" if not onnx_file_name.endswith(".onnx") else ""

        # Construct the full paths for the voice model and configuration files
        onnx_file = os.path.join(voices_dir, onnx_file_name)
        json_file = os.path.join(voices_dir, json_file_name)

        # Check if the Piper executable and voice files exist
        if not all(map(os.path.exists, [exe_path, onnx_file, json_file])):
            print("One or more required files do not exist:")
            for file_path in [exe_path, onnx_file, json_file]:
                if not os.path.exists(file_path):
                    print(f"{file_path} does not exist")
            return "failed"
        
        # Try to run the Piper TTS command
        try:
            command = f'echo {text_to_speak} | {exe_path} -m {onnx_file} -c {json_file} -f {output_file}'
            subprocess.run(['cmd.exe', '/c', command], capture_output=True, text=True)
            return "success"
        except subprocess.CalledProcessError as e:
            # If the command fails, print the error and return "failed"
            print(f"Error running Piper TTS command: {e}")
            return "failed"
        
    def TTS_openai(self, text_to_speak, output_file, model="tts-1", format="opus"):
        """
        Generate speech from text using the OpenAI TTS engine and save it to an output file.
        
        Args:
            text (str): The text to be converted to speech.
            output_file (str): The file path where the audio will be saved.
            model (str): The model for TTS.
            format (str): The response format for the audio.
        """

        # Remove characters not suitable for TTS, including additional symbols
        text_to_speak = utils.sanitize_text(text_to_speak)
        
        #if there is no text after illegal characters are stripped
        if not text_to_speak.strip():
            return "failed"
        
        try:
            client = self.OpenAIClient
            voice = config.OPENAI_VOICE
            spoken_response = client.audio.speech.create(
                model=model,
                voice=voice,
                response_format=format,
                input=text_to_speak
                )

            with open(output_file, "wb") as f:
                for chunk in spoken_response.iter_bytes(chunk_size=4096):
                    f.write(chunk)

            return "success"
        except Exception as e:
            print(f"Error occurred while getting OpenAI TTS: {e}")
            return "failed"
        
    def play_audio(self):
        """
        Play the audio from the audio queue.
        """
        # While there are items in the queue or the queuing flag is set
        while self.queing or not self.audio_queue.empty(): 

            # If the stop response flag is set, break the loop
            if self.parent_client.stop_response == True:
                break

            # Set the running TTS flag to True
            self.running_tts = True
            try:
                # Try to get an item from the queue, with a timeout of 1 second
                file_path, sentence = self.audio_queue.get(timeout=1) 
                    
            except queue.Empty:
                # If the queue is empty, continue to the next iteration of the loop
                continue
                
            # Read the audio data from the file
            data, fs = sf.read(file_path, dtype='float32')

            # Play the audio
            sd.play(data, fs)

            # Print the sentence being spoken
            print(f"Playing audio: {sentence}")
            self.last_sentence_spoken = sentence
            # Wait for the audio to finish playing
            sd.wait()
            # Mark the task as done in the queue
            self.audio_queue.task_done()

            # If the audio file exists, remove it
            if os.path.exists(file_path):
                os.remove(file_path)
                # If the file path is in the temp_files list, remove it
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)

        # Set the running TTS flag to False
        self.running_tts = False

        # Delete any leftover temp files if any this is just to be safe and should not be needed
        for file in os.listdir(config.AUDIO_FILE_DIR):
            if file.endswith(".wav"):
                os.remove(f"{config.AUDIO_FILE_DIR}\\{file}")


    def stop(self):
        """
        Stop the TTS process and clean up any temporary files.
        """
        # Print a message indicating that the TTS process is stopping
        print("Stopping TTS")

        # Stop any currently playing audio
        sd.stop()

        # Attempt to clear the queue immediately to prevent any further processing
        while not self.audio_queue.empty():
            try:
                # Try to get an item from the queue without waiting
                self.audio_queue.get_nowait()
            except queue.Empty:
                # If the queue is empty, print a message and continue to the next iteration
                print("Queue is empty")
                continue
            # Mark the task as done in the queue
            self.audio_queue.task_done()

        # Start a new thread to handle file deletion
        file_deletion_thread = threading.Thread(target=self.delete_temp_files)
        file_deletion_thread.start()
        
        # If the audio playback thread is alive
        if self.play_audio_thread.is_alive():
            # Wait for the thread to finish
            self.play_audio_thread.join()

        # Wait for the file deletion thread to finish
        file_deletion_thread.join()

    def delete_temp_files(self):
        """
        Delete any temporary files.
        """
        # Iterate over a copy of the list of temporary files
        for temp_file in self.temp_files.copy():
            # If the file exists
            if os.path.exists(temp_file):
                try:
                    # Try to remove the file
                    os.remove(temp_file)
                    # If the file path is in the temp_files list, remove it
                    if temp_file in self.temp_files:
                        self.temp_files.remove(temp_file)
                except PermissionError as e:
                    # If a permission error occurs, print a message
                    print(f"Permission denied error when trying to delete {temp_file}: {e}")