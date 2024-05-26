import platform

class InputHandler:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def add_hotkey(self, hotkey, callback):
        raise NotImplementedError("add_hotkey method must be implemented in subclasses")

    def add_held_hotkey(self, hotkey, callback):
        raise NotImplementedError("add_held_hotkey method must be implemented in subclasses")

    def start(self):
        raise NotImplementedError("start method must be implemented in subclasses")

def get_input_handler(verbose=False):
    if platform.system() == "Windows":
        from input_apis.keyboard_library_handler import KeyboardLibraryHandler
        return KeyboardLibraryHandler(verbose)
    else:
        from input_apis.pynput_handler import PynputHandler
        return PynputHandler(verbose)




