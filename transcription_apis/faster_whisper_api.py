try:
    from faster_whisper import WhisperModel
except ModuleNotFoundError:
    print("The faster_whisper module is not found. Please run 'pip install -r faster_whisper_requirements.txt' to install the required packages.")
    raise

import os
import config
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE" # This is a workaround for a bug 


class FasterWhisperClient:
    def __init__(self, verbose=False):
        self.device = "cuda" if config.USE_GPU else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = WhisperModel(
            config.WHISPER_MODEL,
            device=self.device,
            compute_type=self.compute_type
        )
        self.beam_size = config.BEAM_SIZE
        self.verbose = verbose

        if self.verbose:
            print(f"Using faster-whisper model: {config.WHISPER_MODEL} and device: {self.device}")

    def transcribe_audio_file(self, file_path):
        if self.verbose:
            print(f"Transcribing audio file: {file_path}")

        try:
            segments, info = self.model.transcribe(
                file_path,
                beam_size=self.beam_size
            )

            transcript = ""
            for segment in segments:
                print(segment.text)
                transcript += segment.text + " "

            if self.verbose:
                print(f"Detected language: {info.language} with probability {info.language_probability:.2f}")

            return transcript.strip()

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

