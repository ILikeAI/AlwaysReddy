import os
import subprocess
from config_loader import config
import utils
import platform

class PiperTTSClient:
    def __init__(self, verbose=False):
        """Initialize the Piper TTS client."""
        self.verbose = verbose

    def tts(self, text_to_speak, output_file, voice_folder=config.PIPER_VOICE):
        """
        This function uses the Piper TTS engine to convert text to speech.
        
        Args:
            text_to_speak (str): The text to be converted to speech.
            output_file (str): The path where the output audio file will be saved.
            voice_folder (str): The folder containing the voice files for the TTS engine.
            
        Returns:
            str: "success" if the TTS process was successful, "failed" otherwise.
        """
        # Sanitize the text to be spoken
        text_to_speak = utils.sanitize_text(text_to_speak)

        # If there's no text left after sanitization, return "failed"
        if not text_to_speak.strip():
            if self.verbose:
                print("No text to speak after sanitization.")
            return "failed"

        # Determine the operating system
        operating_system = platform.system()
        if operating_system == "Windows":
            piper_binary = os.path.join("piper_tts", "piper.exe")
        else:
            piper_binary = os.path.join("piper_tts", "piper")

        # Construct the path to the voice files
        voice_path = os.path.join("piper_tts", "voices", voice_folder)

        # If the voice folder doesn't exist, return "failed"
        if not os.path.exists(voice_path):
            if self.verbose:
                print(f"Voice folder '{voice_folder}' does not exist.")
            return "failed"

        # Find the model and JSON files in the voice folder
        files = os.listdir(voice_path)
        model_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.onnx')), None)
        json_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.json')), None)

        # If either the model or JSON file is missing, return "failed"
        if not model_path or not json_path:
            if self.verbose:
                print("Required voice files not found.")
            return "failed"

        try:
            # Construct and execute the Piper TTS command
            command = [
                piper_binary,
                "-m", model_path,
                "-c", json_path,
                "-f", output_file,
                "-s", str(config.PIPER_VOICE_INDEX),
                "--length_scale", str(1/config.PIPER_VOICE_SPEED)
            ]
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            process.communicate(text_to_speak.encode("utf-8"))
            process.wait()
            return "success"

        except subprocess.CalledProcessError as e:
            # If the command fails, print an error message and return "failed"
            if self.verbose:
                print(f"Error running Piper TTS command: {e}")
            return "failed"