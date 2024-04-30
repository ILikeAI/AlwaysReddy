import sys

if sys.platform.startswith('linux'):
    from pynput import keyboard
else:
    import keyboard

class KeyboardHandler:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def add_hotkey(self, hotkey, callback):
        raise NotImplementedError("add_hotkey method must be implemented in subclasses")

    def start(self):
        raise NotImplementedError("start method must be implemented in subclasses")

class KeyboardLibraryHandler(KeyboardHandler):
    def add_hotkey(self, hotkey, callback):
        keyboard.add_hotkey(hotkey, callback)

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

class PynputHandler(KeyboardHandler):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.hotkey_map = {}

    def add_hotkey(self, hotkey, callback):
        self.hotkey_map[hotkey] = callback

    def start(self):
        with keyboard.GlobalHotKeys(self.hotkey_map) as hotkey_listener:
            try:
                hotkey_listener.join()
            except KeyboardInterrupt:
                if self.verbose:
                    print("Recorder stopped by user.")
            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"An error occurred: {e}")

def get_keyboard_handler(verbose=False):
    if sys.platform.startswith('linux'):
        return PynputHandler(verbose)
    else:
        return KeyboardLibraryHandler(verbose)