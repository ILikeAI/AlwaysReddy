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
            to_clipboard(transcript)
            pyautogui.hotkey('ctrl', 'v') 
            print("Transcription copied to clipboard.")