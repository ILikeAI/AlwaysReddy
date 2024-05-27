from input_apis.input_handler import InputHandler
import keyboard
import config

class KeyboardLibraryHandler(InputHandler):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.held_hotkeys = {}

    def add_hotkey(self, hotkey, callback):
        keyboard.add_hotkey(hotkey, callback, suppress=config.SUPPRESS_NATIVE_HOTKEYS)

    def add_held_hotkey(self, hotkey, callback):
        self.held_hotkeys[hotkey] = False
        keyboard.add_hotkey(hotkey, lambda: self.handle_held_callback(hotkey, callback, is_pressed=True), suppress=config.SUPPRESS_NATIVE_HOTKEYS)
        keyboard.add_hotkey(hotkey, lambda: self.handle_held_callback(hotkey, callback, is_pressed=False), suppress=config.SUPPRESS_NATIVE_HOTKEYS, trigger_on_release=True)

    def handle_held_callback(self, hotkey, callback, is_pressed):
        if is_pressed != self.held_hotkeys[hotkey]:
            callback(is_pressed=is_pressed)
            self.held_hotkeys[hotkey] = is_pressed

    def start(self):
        try:
            while True:
                keyboard.wait()
        except KeyboardInterrupt:
            if self.verbose:
                print("Recorder stopped by user.")
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred: {e}")