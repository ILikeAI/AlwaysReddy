from utils import read_clipboard

class ReadClipboard:
    """Action for reading clipboard content aloud."""

    def __init__(self, AR):
        """
        Initialize the ReadClipboard action.
        
        Args:
            AR (AlwaysReddy): The AlwaysReddy instance.
        """
        self.AR = AR

    def read_aloud_clipboard(self):
        """Read the content of the clipboard aloud."""
        clipboard_text = read_clipboard()
        if clipboard_text:
            self.AR.tts.run_tts(clipboard_text)
        else:
            print("No text found in the clipboard.")