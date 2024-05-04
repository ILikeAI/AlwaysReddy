import os
import soundfile as sf
import pyaudio
from dotenv import load_dotenv
import threading
import queue
import config
import tempfile
import time

# Load .env file if present
load_dotenv()

class TTS:
    """
    Text-to-Speech (TTS) class for generating speech from text.
    """
    def __init__(self, parent_client, verbose=False):
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
        self.verbose = verbose
        self.stop_playback = False

        if self.service == "openai":
            from TTS_apis.openai_api import OpenAITTSClient
            self.tts_client = OpenAITTSClient(verbose=self.verbose)
        elif self.service == "piper":
            from TTS_apis.piper_api import PiperTTSClient
            self.tts_client = PiperTTSClient(verbose=self.verbose)
        else:
            raise ValueError("Unsupported TTS engine configured")

        # Delete any leftover temp files if any
        for file in os.listdir(config.AUDIO_FILE_DIR):
            if file.endswith(".wav"):
                os.remove(os.path.join(config.AUDIO_FILE_DIR, file))

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
                if self.verbose:
                    print(f"Error creating output directory {output_dir}: {e}")
                self.queing = False
                return
    
        try:
            # Create a temporary file in the output directory
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=".wav")
            temp_output_file = temp_file.name
            temp_file.close()
    
            # Run the TTS using the appropriate service
            result = self.tts_client.tts(sentence, temp_output_file)
            
            # If the TTS was successful, add the output file to the queue
            if result == "success":
                if self.verbose:
                    print(f"Running TTS: {sentence}")
                
                # If the stop flag is set, return early
                if self.parent_client.stop_response:
                    return
                
                self.temp_files.append(temp_output_file)
    
                if self.verbose:
                    print("Adding to queue")
                self.audio_queue.put((temp_output_file, sentence))
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error during TTS processing: {e}")
    
        # Set queuing flag to False
        self.queing = False

    def play_audio(self):
        """
        Play the audio from the audio queue.
        """
        # While there are items in the queue or the queuing flag is set
        while self.queing or not self.audio_queue.empty():
            # If the stop response flag or stop_playback flag is set, break the loop
            if self.parent_client.stop_response or self.stop_playback:
                break

            # Set the running TTS flag to True
            self.running_tts = True
            try:
                # Try to get an item from the queue, with a timeout of 1 second
                file_path, sentence = self.audio_queue.get(timeout=1)
            except queue.Empty:
                # If the queue is empty, continue to the next iteration of the loop
                continue

            try:
                # Read the audio data from the file
                data, fs = sf.read(file_path, dtype='float32')
            except Exception as e:
                if self.verbose:
                    print(f"Error reading file {file_path}: {e}")
                continue

            try:
                # Play the audio using pyaudio
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paFloat32,
                                channels=1,
                                rate=fs,
                                output=True)
                
                # Write the audio data to the stream in chunks
                chunk_size = 1024
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i + chunk_size]
                    stream.write(chunk.tobytes())
                    
                    # Check if the stop_playback flag is set
                    if self.stop_playback:
                        break
                
                stream.stop_stream()
                stream.close()
                p.terminate()
            except Exception as e:
                if self.verbose:
                    print(f"Error playing audio: {e}")
                continue

            if self.verbose:
                print(f"Playing audio: {sentence}")
            self.last_sentence_spoken = sentence
            # Mark the task as done in the queue
            self.audio_queue.task_done()

            try:
                # If the audio file exists, remove it
                if os.path.exists(file_path):
                    os.remove(file_path)
                    # If the file path is in the temp_files list, remove it
                    if file_path in self.temp_files:
                        self.temp_files.remove(file_path)
            except Exception as e:
                if self.verbose:
                    print(f"Error deleting file {file_path}: {e}")

        # Set the running TTS flag to False
        self.running_tts = False

        # Delete any leftover temp files if any this is just to be safe and should not be needed
        try:
            for file in os.listdir(config.AUDIO_FILE_DIR):
                if file.endswith(".wav"):
                    os.remove(os.path.join(config.AUDIO_FILE_DIR, file))
        except Exception as e:
            if self.verbose:
                print(f"Error deleting leftover files: {e}")

    def stop(self):
        """
        Stop the TTS process and clean up any temporary files.
        """
        # Print a message indicating that the TTS process is stopping
        if self.verbose:
            print("Stopping TTS")

        # Stop any currently playing audio
        # Set the stop_playback flag to signal the play_audio thread to stop
        self.stop_playback = True
        
        # Wait for a short duration to allow the play_audio thread to stop
        time.sleep(0.2)

        # Attempt to clear the queue immediately to prevent any further processing
        while not self.audio_queue.empty():
            try:
                # Try to get an item from the queue without waiting
                self.audio_queue.get_nowait()
            except queue.Empty:
                # If the queue is empty, continue to the next iteration
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
        
        # Reset the stop_playback flag
        self.stop_playback = False

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
                    if self.verbose:
                        print(f"Permission denied error when trying to delete {temp_file}: {e}")