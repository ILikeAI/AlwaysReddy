import subprocess
import utils

class MacTTSClient:
    def __init__(self, verbose=False):
        """Initialize the Mac TTS client."""
        self.verbose = verbose

    def tts(self, text_to_speak, output_file, voice="Alex"):
        """
        Generate speech from text using the macOS `say` command and save it to an output file.
        
        Args:
            text_to_speak (str): The text to be converted to speech.
            output_file (str): The file path where the audio will be saved.
            voice (str): The voice to use for TTS.
        """

        # Remove characters not suitable for TTS, including additional symbols
        text_to_speak = utils.sanitize_text(text_to_speak)
        
        # If there is no text after illegal characters are stripped
        if not text_to_speak.strip():
            if self.verbose:
                print("No text to speak after sanitization.")
            return "failed"
        
        try:
            command = ['say', '-v', voice, '-o', output_file, '--data-format=LEF32@22050', text_to_speak]
            subprocess.call(command)
            
            if self.verbose:
                print(f"Mac TTS completed successfully.")
            return "success"
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error occurred while getting Mac TTS: {e}")
            return "failed"
