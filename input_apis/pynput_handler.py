from input_apis.input_handler import InputHandler
import pynput.keyboard as pynput_keyboard

class PynputHandler(InputHandler):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.hotkeys: list = []
        self.listener = pynput_keyboard.Listener(on_press=self.pressed, on_release=self.released)

    class HotKey(object):
        """Reimplementation of pynput's HotKey class.

        Adds on_release callback and return boolean whether hotkey was activated or deactivated.
        """

        def __init__(self, keys, on_press, on_release=None):
            self._state = set()
            self._keys = set(keys)
            self._on_press = on_press
            self._on_release = on_release
            self.pressed = False

        def combination_length(self):
            return len(self._keys)

        def press(self, key):
            if key in self._keys and key not in self._state:
                self._state.add(key)
                if self._state == self._keys:
                    self.pressed = True
                    if self._on_press:
                        self._on_press()
                    return True
            return False

        def release(self, key):
            if key in self._state:
                self._state.remove(key)
                if self.pressed:
                    self.pressed = False
                    if self._on_release:
                        self._on_release()
                    return True
            return False

    @staticmethod
    def convert_to_pynput_format(hotkey):
        """Convert a keyboard module style hotkey to a pynput style hotkey."""
        parts = hotkey.split('+')
        converted = []
        for part in parts:
            part = part.strip().lower()
            if part == 'win' or part == 'windows' or part == 'left windows':  # Handling Windows or Command key
                converted.append('<cmd>')  # Use <win> if <cmd> does not work
            if part == 'capslock':
                converted.append('<caps_lock>')
            elif len(part) > 1:
                converted.append(f'<{part}>')
            else:
                converted.append(part)
        return '+'.join(converted)

    def _add_hotkey(self, hotkey, press_callback, release_callback):
        converted_hotkey = PynputHandler.convert_to_pynput_format(hotkey)  # Convert hotkey to pynput format
        try:
            keys = [self.listener.canonical(key) for key in pynput_keyboard.HotKey.parse(converted_hotkey)]
            self.hotkeys.append(PynputHandler.HotKey(keys, press_callback, release_callback))
        except ValueError:
            print(f"\nERROR: hotkey '{hotkey}' is not supported by pynput library."
                  "\nTo set a new hotkey, run the 'hotkey_config_GUI.py' script or edit your 'config.py' file.\n")
            raise

    def add_hotkey(self, hotkey, callback):
        self._add_hotkey(hotkey, callback, None)

    def add_held_hotkey(self, hotkey, callback):
        """Callback must be a function that takes is_pressed as a boolean argument.
        """
        self._add_hotkey(hotkey, lambda: callback(is_pressed=True), lambda: callback(is_pressed=False))

    def pressed(self, key):
        # If a hotkey is already pressed, don't activate any other
        for hotkey in self.hotkeys:
            if hotkey.pressed:
                return

        key = self.listener.canonical(key)
        for hotkey in self.hotkeys:
            if hotkey.press(key):
                break

    def released(self, key):
        key = self.listener.canonical(key)
        for hotkey in self.hotkeys:
            hotkey.release(key)

    def start(self):
        try:
            # Sort hotkeys by number of keys in combination, so most complicated combinations are first
            # that way we can prioritize the most complex combination when there is a conflict
            self.hotkeys.sort(key=lambda hotkey: hotkey.combination_length(), reverse=True)

            with self.listener:
                self.listener.join()
        except KeyboardInterrupt:
            if self.verbose:
                print("Recorder stopped by user.")
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred: {e}")