import config
import platform

operating_system = platform.system()
if operating_system == "Windows":
    import keyboard

else:
    from pynput import keyboard as pynput_keyboard

    

def convert_to_pynput_format(hotkey):
    """Convert a keyboard module style hotkey to a pynput style hotkey."""
    parts = hotkey.split('+')
    converted = []
    for part in parts:
        part = part.strip().lower()
        if part == 'ctrl':
            converted.append('<ctrl>')
        elif part == 'shift':
            converted.append('<shift>')
        elif part == 'alt':
            converted.append('<alt>')
        elif part == 'windows' or part == 'cmd' or part == 'left windows':  # Handling Windows or Command key
            converted.append('<cmd>')  # Use <win> if <cmd> does not work
        else:
            converted.append(part)
    return '+'.join(converted)


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
        # Convert hotkey to pynput format
        pynput_hotkey = convert_to_pynput_format(hotkey)
        self.hotkey_map[pynput_hotkey] = callback

    def start(self):
        with pynput_keyboard.GlobalHotKeys(self.hotkey_map) as hotkey_listener:
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
    if operating_system == "Windows":
        return KeyboardLibraryHandler(verbose)
    else:
        return PynputHandler(verbose)




