import os
import threading
import queue
from config_loader import config
import tempfile
import pyaudio
import wave
import re

class TTSManager:
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
        self._play_audio_thread = threading.Thread(target=self._play_audio)
        self.running_tts = False
        self.last_sentence_spoken = ""
        self.verbose = verbose
        self.stop_playback = False
        self.playback_stopped = threading.Event()
        self.sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)|\n'

        ## NOTE: For now all TTS services need to return wav files.
        if self.service == "openai":
            from TTS_apis.openai_tts_client import OpenAITTSClient
            self.tts_client = OpenAITTSClient(verbose=self.verbose)
        elif self.service == "piper":
            from TTS_apis.piper_tts_client import PiperTTSClient
            self.tts_client = PiperTTSClient(verbose=self.verbose)
        elif self.service == "mac":
            from TTS_apis.mac_tts_client import MacTTSClient
            self.tts_client = MacTTSClient(verbose=self.verbose)
        else:
            raise ValueError("Unsupported TTS engine configured")

        # Delete any leftover temp files if any
        for file in os.listdir(config.AUDIO_FILE_DIR):
            if file.endswith(".wav") or file.endswith(".mp3"):
                os.remove(os.path.join(config.AUDIO_FILE_DIR, file))

    def wait(self):
        """
        Wait for the _play_audio_thread to join.
        """
        self._play_audio_thread.join()

    def split_sentences(self, text):
        """
        Split the text into sentences and remove empty ones.
        """
        sentences = re.split(self.sentence_pattern, text)
        # Ensure sentences end with punctuation and remove empty sentences
        sentences = [s + '.' if not s.strip().endswith(('.', '!', '?')) else s for s in sentences if s.strip()]

        return sentences

    def run_tts(self, text, output_dir=config.AUDIO_FILE_DIR, split_sentences=True):
        """
        Run the TTS for the given text and output the audio to the specified directory.
        
        Args:
            text (str): The text to be converted to speech.
            output_dir (str): The directory where the audio files will be saved.
            split_sentences (bool): Whether to split the text into sentences. Default is True.
        """
        self.queing = True
    
        if not self._play_audio_thread.is_alive():
            self._play_audio_thread = threading.Thread(target=self._play_audio)
            self._play_audio_thread.start()
    
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                if self.verbose:
                    print(f"Error creating output directory {output_dir}: {e}")
                self.queing = False
                return
    
        texts_to_process = self.split_sentences(text) if split_sentences else [text]
    
    
        for current_text in texts_to_process:
            try:
                #if the text does not end with a punctuation mark, add a period
                if not current_text.endswith((".", "!", "?")):
                    current_text += "."
                    
                # Create a temporary file in the output directory
                temp_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=".wav")
                temp_output_file = temp_file.name
                temp_file.close()
    
                # Run the TTS using the appropriate service
                result = self.tts_client.tts(current_text, temp_output_file)
                
                # If the TTS was successful, add the output file to the queue
                if result == "success":                   
                    # If the stop flag is set, return early
                    if self.parent_client.stop_action:
                        return
                    
                    self.temp_files.append(temp_output_file)
                    self.audio_queue.put((temp_output_file, current_text))

            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"Error during TTS processing: {e}")
    
        # Set queuing flag to False
        self.queing = False

    def _play_audio(self): 
        """
        Play the audio from the audio queue.
        """
        # While there are items in the queue or the queuing flag is set
        while self.queing or not self.audio_queue.empty():
            # If the stop response flag or stop_playback flag is set, break the loop
            if self.parent_client.stop_action or self.stop_playback:
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
                
                if self.verbose:
                    print(f"Playing audio: {sentence}")
                # Load the audio file using wave
                with wave.open(file_path, 'rb') as audio_file:
                    # Create a PyAudio instance
                    p = pyaudio.PyAudio()

                    # Open a stream for playback
                    stream = p.open(format=p.get_format_from_width(audio_file.getsampwidth()),
                                    channels=audio_file.getnchannels(),
                                    rate=audio_file.getframerate(),
                                    output=True)

                    # Read audio data in chunks and write to the stream
                    data = audio_file.readframes(1024)
                    while data and not self.stop_playback:
                        stream.write(data)
                        data = audio_file.readframes(1024)

                    # Stop and close the stream
                    stream.stop_stream()
                    stream.close()

                    # Terminate the PyAudio instance
                    p.terminate()

                    if self.stop_playback:
                        self.playback_stopped.set()

            except Exception as e:
                if self.verbose:
                    print(f"Error playing audio: {e}")
                continue

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

        # Delete any leftover temp files if any (this is just to be safe and should not be needed)
        try:
            for file in os.listdir(config.AUDIO_FILE_DIR):
                if file.endswith(".wav") or file.endswith(".mp3"):
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

        # Set the stop_playback flag to signal the _play_audio thread to stop
        self.stop_playback = True

        # Wait for the playback to stop or for a timeout of 1 second
        self.playback_stopped.wait(timeout=0.01)

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
        file_deletion_thread = threading.Thread(target=self._delete_temp_files)
        file_deletion_thread.start()

        # If the audio playback thread is alive
        if self._play_audio_thread.is_alive():
            # Wait for the thread to finish
            self._play_audio_thread.join()

        # Wait for the file deletion thread to finish
        file_deletion_thread.join()
        
        # Reset the stop_playback flag and the playback_stopped event
        self.stop_playback = False
        self.playback_stopped.clear()

    def _delete_temp_files(self):
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
                    pass