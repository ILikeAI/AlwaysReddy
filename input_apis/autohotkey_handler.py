from input_apis.input_handler import InputHandler
from ahk import AHK
import threading
import time

class AutohotkeyHandler(InputHandler):
    """
    Handles keyboard input using AutoHotkey via the ahk library.
    """

    def __init__(self, verbose=False):
        """
        Initialize the AutohotkeyHandler.

        :param verbose: If True, print detailed logging information.
        """
        super().__init__(verbose)
        self.ahk = AHK()
        self.ahk_thread = None

    def add_hotkey(self, hotkey, *, pressed=None, released=None, held=None, held_release=None, double_tap=None):
        """
        Add a hotkey with its associated callbacks.

        :param hotkey: String representation of the hotkey (e.g., 'ctrl+shift+a')
        :param pressed: Callback for when the hotkey is pressed
        :param released: Callback for when the hotkey is released
        :param held: Callback for when the hotkey is held
        :param held_release: Callback for when the hotkey is released after being held
        :param double_tap: Callback for when the hotkey is double-tapped
        """
        super().add_hotkey(hotkey, pressed=pressed, released=released, held=held, held_release=held_release, double_tap=double_tap)
        converted_hotkey = self.convert_to_autohotkey_format(hotkey)
        self.ahk.add_hotkey(converted_hotkey, lambda: self.process_key_event(hotkey, True))
        self.ahk.add_hotkey(f"{converted_hotkey} up", lambda: self.process_key_event(hotkey, False))

    def start(self, blocking=False):
        """
        Start the AutoHotkey handler.

        :param blocking: If True, the method will block until stop() is called.
                         If False, the method will return immediately and run in the background.
        """
        self.running = True
        self.ahk_thread = threading.Thread(target=self._run_ahk)
        self.ahk_thread.start()

        if blocking:
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Keyboard interrupt received. Stopping...")
            finally:
                self.stop()

    def stop(self):
        """
        Stop the AutoHotkey handler.
        """
        self.running = False
        if self.ahk_thread:
            self.ahk_thread.join(timeout=0.5)  # Wait for up to 0.5 seconds
        self._stop_ahk()

    def _run_ahk(self):
        """
        Internal method to run AutoHotkey in a separate thread.
        """
        self.ahk.start_hotkeys()
        while self.running:
            time.sleep(0.1)

    def _stop_ahk(self):
        """
        Internal method to stop AutoHotkey.
        """
        try:
            self.ahk.stop_hotkeys()
        except Exception as e:
            if self.verbose:
                print(f"Error stopping AutoHotkey: {e}")

    @staticmethod
    def convert_to_autohotkey_format(hotkey):
        """
        Convert a string hotkey to AutoHotkey format.

        :param hotkey: String representation of the hotkey
        :return: AutoHotkey-formatted hotkey string
        """
        pynput_modifier_remap = {
            'shift': '+',
            'ctrl': '^',
            'alt': '!',
            'win': '#',
            'cmd': '#',
        }

        parts = hotkey.lower().split('+')
        modifiers = [pynput_modifier_remap.get(part, part) for part in parts if part in pynput_modifier_remap]
        non_modifiers = [part for part in parts if part not in pynput_modifier_remap]

        if len(non_modifiers) > 1:
            raise ValueError(f"Too many non-modifiers in hotkey: {hotkey}. More than one non-modifier is not supported.")

        return ''.join(modifiers + non_modifiers)