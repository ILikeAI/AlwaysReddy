import whisperx as wx# this gives me a warning but it works.
import os
import torch
import config 

class WhisperXClient:
    def __init__(self): 
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.batch_size = config.WHISPER_BATCH_SIZE
        self.compute_type = "int8"
        self.language = config.TRANSCRIPTION_LANGUAGE
        self.model = wx.load_model(config.WHISPER_MODEL, self.device, language=self.language, compute_type=self.compute_type, download_root=config.WHISPER_MODEL_PATH)
        print(f"Using WhisperX model: {config.WHISPER_MODEL} and device: {self.device}")

    def transcribe_audio_file(self, file_path):
        print(f"Transcribing audio file: {file_path}")
        try:
            transcript = ""
            result = self.model.transcribe(file_path, batch_size=self.batch_size)
            for segment in result['segments']:
                transcript += segment['text'] + " "

            return transcript
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The audio file {file_path} was not found.") from e
        except Exception as e:
            raise Exception(f"An error occurred during the transcription process: {e}") from e