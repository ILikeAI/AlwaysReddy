from utils import to_clipboard
from actions.base_action import BaseAction
from config_loader import config
import pyautogui
import time

class TranscribeAndPaste(BaseAction):
    """Action for transcribing audio to clipboard and pasting it."""
    def setup(self):
        if config.TRANSCRIBE_RECORDING:
            self.AR.add_action_hotkey(config.TRANSCRIBE_RECORDING, 
                                pressed=self.transcription_action,
                                held_release=self.transcription_action)
            print(f"'{config.TRANSCRIBE_RECORDING}': Transcribe to clipboard (press to toggle on and off, or hold and release)")

    def transcription_action(self):
        """Handle the transcription process."""
        recording_filename = self.AR.toggle_recording(self.transcription_action)
        if recording_filename:
            transcript = self.AR.transcription_manager.transcribe_audio(recording_filename)
            
            # Send transcript to language model for error correction
            messages = [
                {"role": "system", "content": "You are a helpful assistant that corrects transcription errors. Please fix any errors in the following transcription, maintaining the original meaning and style."},
                {"role": "user", "content": transcript}
            ]
            corrected_transcript = self.AR.completion_client.get_completion(messages, config.COMPLETION_MODEL)
            
            to_clipboard(corrected_transcript)
            pyautogui.hotkey('ctrl', 'v')
            print("Corrected transcription copied to clipboard and pasted.")
