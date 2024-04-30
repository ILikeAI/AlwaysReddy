try:
    import whisperx as wx
except ModuleNotFoundError:
    print("The whisperx module is not found. Please run 'pip install -r local_whisper_requirements.txt' to install the required packages.")
    raise
import os
import torch
import config

class WhisperXClient:
    def __init__(self, verbose=False):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.batch_size = config.WHISPER_BATCH_SIZE
        self.compute_type = "int8"
        self.language = config.TRANSCRIPTION_LANGUAGE
        self.model = wx.load_model(config.WHISPER_MODEL, self.device, language=self.language, compute_type=self.compute_type, download_root=config.WHISPER_MODEL_PATH)
        self.verbose = verbose
        if self.verbose:
            print(f"Using WhisperX model: {config.WHISPER_MODEL} and device: {self.device}")

    def transcribe_audio_file(self, file_path):
        if self.verbose:
            print(f"Transcribing audio file: {file_path}")
        try:
            transcript = ""
            result = self.model.transcribe(file_path, batch_size=self.batch_size)
            for segment in result['segments']:
                transcript += segment['text'] + " "
            return transcript
        except FileNotFoundError as e:
            if self.verbose:
                print(f"The audio file {file_path} was not found.")
            raise FileNotFoundError(f"The audio file {file_path} was not found.") from e
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred during the transcription process: {e}")
            raise Exception(f"An error occurred during the transcription process: {e}") from e