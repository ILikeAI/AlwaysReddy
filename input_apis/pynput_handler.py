from input_apis.input_handler import InputHandler
import pynput.keyboard as pynput_keyboard
import threading
import time

class PynputHandler(InputHandler):
    """
    Handles keyboard input using the pynput library.
    """

    def __init__(self, verbose=False):
        """
        Initialize the PynputHandler.

        :param verbose: If True, print detailed logging information.
        """
        super().__init__(verbose)
        self.listener = None
        self.current_keys = set()  # Set to track currently pressed keys
        self.hotkey_maps = {}  # Maps pynput key combinations to original hotkey strings
        self.listener_thread = None

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
        pynput_keys = frozenset(pynput_keyboard.HotKey.parse(self.convert_to_pynput_format(hotkey)))
        self.hotkey_maps[pynput_keys] = hotkey

    def on_press(self, key):
        """
        Handle key press events.

        :param key: The key that was pressed
        """
        try:
            canonical_key = self.listener.canonical(key)
            self.current_keys.add(canonical_key)
            
            for hotkey_combo, original_hotkey in self.hotkey_maps.items():
                if hotkey_combo.issubset(self.current_keys):
                    self.process_key_event(original_hotkey, True)
                    break
        except Exception as e:
            if self.verbose:
                print(f"Error in on_press: {e}")

    def on_release(self, key):
        """
        Handle key release events.

        :param key: The key that was released
        """
        try:
            canonical_key = self.listener.canonical(key)
            self.current_keys.discard(canonical_key)
            
            for hotkey_combo, original_hotkey in self.hotkey_maps.items():
                if canonical_key in hotkey_combo:
                    self.process_key_event(original_hotkey, False)
                    break
        except Exception as e:
            if self.verbose:
                print(f"Error in on_release: {e}")

    def start(self, blocking=False):
        """
        Start the pynput listener.

        :param blocking: If True, the method will block until stop() is called.
                         If False, the method will return immediately and run in the background.
        """
        super().start(blocking)

    def stop(self):
        """
        Stop the pynput listener and clean up.
        """
        super().stop()
        if self.listener:
            self.listener.stop()
        if self.listener_thread:
            self.listener_thread.join()

    def _run(self):
        """
        Internal method to run the pynput listener.
        """
        self.listener_thread = threading.Thread(target=self._run_listener)
        self.listener_thread.start()

        try:
            while self.running:
                time.sleep(0.1)  # Sleep to reduce CPU usage
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Stopping...")
        finally:
            self.stop()

    def _run_listener(self):
        """
        Internal method to run the actual pynput listener.
        """
        with pynput_keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()

    @staticmethod
    def convert_to_pynput_format(hotkey):
        """
        Convert a string hotkey to pynput format.

        :param hotkey: String representation of the hotkey
        :return: Pynput-formatted hotkey string
        """
        parts = hotkey.split('+')
        converted = []
        for part in parts:
            part = part.strip().lower()
            if part in ['win', 'windows', 'left windows']:
                converted.append('<cmd>')
            elif part == 'capslock':
                converted.append('<caps_lock>')
            elif len(part) > 1:
                converted.append(f'<{part}>')
            else:
                converted.append(part)
        return '+'.join(converted)