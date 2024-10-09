from utils import to_clipboard
from actions.base_action import BaseAction
from config_loader import config

class ExampleAction(BaseAction):
    """Action for transcribing audio to clipboard."""
    def setup(self):

        self.AR.add_action_hotkey("ctrl+alt+t", 
                            pressed=self.transcription_action,
                            held_release=self.transcription_action)

    def transcription_action(self):
        """Handle the transcription process."""
        recording_filename = self.AR.toggle_recording(self.transcription_action)
        if recording_filename: # If the recording has only just been started, recording_filename will be None
            transcript = self.AR.transcription_manager.transcribe_audio(recording_filename)
            to_clipboard(transcript)
            print("Transcription copied to clipboard.")