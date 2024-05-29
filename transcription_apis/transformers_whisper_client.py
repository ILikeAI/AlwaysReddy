import os
import wave
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from config_loader import config

class TransformersWhisperClient:
    def __init__(self, verbose=config.VERBOSE):
        self.processor = WhisperProcessor.from_pretrained(config.WHISPER_MODEL)
        self.model = WhisperForConditionalGeneration.from_pretrained(config.WHISPER_MODEL)
        self.verbose = verbose

    def transcribe_audio_file(self, file_path):
        if self.verbose:
            print(f"Transcribing audio file: {file_path}")

        try:
            # Read the WAV file and convert it to the format required by the model
            wf = wave.open(file_path, 'rb')
            waveform = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)
            wf.close()

            # Normalize the waveform
            waveform = waveform / np.iinfo(np.int16).max

            # Prepare input features
            input_features = self.processor(waveform, sampling_rate=wf.getframerate(), return_tensors="pt").input_features

            # Generate token IDs
            with torch.no_grad():
                predicted_ids = self.model.generate(input_features)

            # Decode the token IDs to text
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)

            if self.verbose:
                print(f"Transcription successful for file: {file_path}")

            return transcription[0].strip()

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
