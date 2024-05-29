import os
from dotenv import load_dotenv
from config import AUDIO_FILE_DIR
from config_loader import config

# Load .env file if present
load_dotenv()

class TranscriptionManager:
    def __init__(self, verbose=config.VERBOSE):
        self.client = None
        self.verbose = verbose
        self._setup_client()

    def _setup_client(self):
        """Instantiates the appropriate transcription client based on configuration file."""
        if config.TRANSCRIPTION_API == "openai":
            from transcription_apis.openai_client import OpenAIClient
            self.client = OpenAIClient(verbose=self.verbose)
        elif config.TRANSCRIPTION_API == "FasterWhisper":
            from transcription_apis.faster_whisper_client import FasterWhisperClient
            self.client = FasterWhisperClient(verbose=self.verbose)
        elif config.TRANSCRIPTION_API == "TransformersWhisper":
            from transcription_apis.transformers_whisper_client import TransformersWhisperClient
            self.client = TransformersWhisperClient(verbose=self.verbose)
        else:
            raise ValueError("Unsupported transcription API service configured")

    def transcribe_audio(self, file_path):
        """
        Transcribes the audio from a given file path.

        Args:
            file_path (str): The path to the audio file to be transcribed.

        Returns:
            str: The transcribed text of the audio file.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            Exception: If there is an error during the transcription process.
        """
        try:
            full_path = os.path.join(AUDIO_FILE_DIR, file_path)
            transcript = self.client.transcribe_audio_file(full_path)
            
            # Delete the audio file
            os.remove(full_path)
            
            return transcript
        
        except FileNotFoundError as e:
            if self.verbose:
                print(f"The audio file {file_path} was not found.")
            raise FileNotFoundError(f"The audio file {file_path} was not found.") from e
        
        except Exception as e:
            if self.verbose:
                print(f"An error occurred during the transcription process: {e}")
            raise Exception(f"An error occurred during the transcription process: {e}") from e
