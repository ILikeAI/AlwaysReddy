from openai import OpenAI
from config_loader import config
import utils

class OpenAITTSClient:
    def __init__(self, verbose=False):
        """Initialize the OpenAI TTS client."""
        self.client = OpenAI()
        self.verbose = verbose

    def tts(self, text_to_speak, output_file, model="tts-1", format="wav"):
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
        
        # If there is no text after illegal characters are stripped
        if not text_to_speak.strip():
            if self.verbose:
                print("No text to speak after sanitization.")
            return "failed"
        
        try:
            voice = config.OPENAI_VOICE
            spoken_response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                response_format=format,
                input=text_to_speak
            )

            with open(output_file, "wb") as f:
                for chunk in spoken_response.iter_bytes(chunk_size=4096):
                    f.write(chunk)

            if self.verbose:
                print(f"OpenAI TTS completed successfully.")
            return "success"
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error occurred while getting OpenAI TTS: {e}")
            return "failed"