from input_apis.input_handler import InputHandler
import keyboard
import config
import threading
import time

class KeyboardLibraryHandler(InputHandler):
    """
    Handles keyboard input using the keyboard library.
    """

    def __init__(self, verbose=False):
        """
        Initialize the KeyboardLibraryHandler.

        :param verbose: If True, enable detailed logging.
        """
        super().__init__(verbose)
        self.running = False
        self.listener_thread = None

    def add_hotkey(self, hotkey, *, pressed=None, released=None, held=None, held_release=None, double_tap=None):
        """
        Adds a hotkey with specified callbacks for different events.

        :param hotkey: The hotkey combination (e.g., 'ctrl+alt+f').
        :param pressed: Callback for when the hotkey is initially pressed.
        :param released: Callback for when the hotkey is released (short press).
        :param held: Callback for when the hotkey is held down.
        :param held_release: Callback for when the hotkey is released after being held.
        :param double_tap: Callback for when the hotkey is double-tapped.
        """
        super().add_hotkey(
            hotkey,
            pressed=pressed,
            released=released,
            held=held,
            held_release=held_release,
            double_tap=double_tap
        )

        # Register the hotkey press event
        keyboard.add_hotkey(
            hotkey,
            lambda: self.process_key_event(hotkey, True),
            suppress=config.SUPPRESS_NATIVE_HOTKEYS
        )

        # Register the hotkey release event
        keys = hotkey.split('+')
        release_key = keys[-1]
        keyboard.on_release_key(
            release_key,
            lambda e: self.process_key_event(hotkey, False)
        )

    def start(self, blocking=False):
        """
        Starts the keyboard listener.

        :param blocking: If True, block execution until stopped.
                         If False, run the listener in a background thread.
        """
        self.running = True
        if blocking:
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Keyboard interrupt received. Stopping...")
            finally:
                self.stop()
        else:
            self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
            self.listener_thread.start()

    def _run_listener(self):
        """
        Internal method to keep the listener thread active.
        """
        try:
            while self.running:
                time.sleep(0.1)  # Keeps the thread alive
        except Exception as e:
            if self.verbose:
                print(f"An error occurred in KeyboardLibraryHandler listener thread: {e}")
            self.stop()

    def stop(self):
        """
        Stops the keyboard listener and cleans up.
        """
        if not self.running:
            return
        self.running = False
        keyboard.unhook_all_hotkeys()
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=0.5)
