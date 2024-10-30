from utils import read_clipboard
from actions.base_action import BaseAction
from config_loader import config

class ReadClipboard(BaseAction):
    """Action for reading clipboard content aloud."""
    def setup(self):
        if config.READ_FROM_CLIPBOARD:
            self.AR.add_action_hotkey(config.READ_FROM_CLIPBOARD, pressed=self.read_aloud_clipboard)
            print(f"'{config.READ_FROM_CLIPBOARD}': To read the text in your clipboard aloud")

    def read_aloud_clipboard(self):
        """Read the content of the clipboard aloud."""
        clipboard_text = read_clipboard()
        if clipboard_text and clipboard_text["type"] == "text":
            self.AR.tts.run_tts(clipboard_text["content"])
        else:
            print("No text found in the clipboard.")