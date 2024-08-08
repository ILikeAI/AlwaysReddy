from utils import to_clipboard
from actions.base_action import BaseAction

class TranscribeToClipboard(BaseAction):
    """Action for transcribing audio to clipboard."""

    def __init__(self, AR):
        """
        Initialize the TranscribeToClipboard action.
        
        Args:
            AR (AlwaysReddy): The AlwaysReddy instance.
        """
        self.AR = AR

    def transcription_action(self):
        """Handle the transcription process."""
        recording_filename = self.AR.toggle_recording(self.transcription_action)
        if recording_filename:
            transcript = self.AR.transcription_manager.transcribe_audio(recording_filename)
            to_clipboard(transcript)
            print("Transcription copied to clipboard.")