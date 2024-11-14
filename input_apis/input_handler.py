import time
import threading
from config_loader import config
from typing import Callable, Optional, Dict

class HotkeyState:
    """
    Represents the state of a hotkey.
    """
    def __init__(self):
        self.last_press_time = 0
        self.press_start_time = 0
        self.is_pressed = False
        self.is_held = False
        self.hold_timer = None

class InputHandler:
    """
    Handles input events for hotkeys, managing different types of key presses and releases.
    """
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.hotkeys = {}
        self.hotkey_states = {}
        self.hold_threshold = 0.5      # seconds
        self.double_tap_threshold = 0.3  # seconds
        self.running = False

    def add_hotkey(
        self,
        hotkey: str,
        *,
        pressed: Optional[Callable] = None,
        released: Optional[Callable] = None,
        held: Optional[Callable] = None,
        held_release: Optional[Callable] = None,
        double_tap: Optional[Callable] = None
    ):
        """
        Adds a hotkey with specified callbacks for different events.

        :param hotkey: The hotkey combination (e.g., 'ctrl+a')
        :param pressed: Callback for when the hotkey is initially pressed
        :param released: Callback for when the hotkey is released (short press)
        :param held: Callback for when the hotkey is held down
        :param held_release: Callback for when the hotkey is released after being held
        :param double_tap: Callback for when the hotkey is double-tapped
        """
        if hotkey not in self.hotkeys:
            # Initialize the hotkey entry with all events set to None
            self.hotkeys[hotkey] = {
                'pressed': None,
                'released': None,
                'held': None,
                'held_release': None,
                'double_tap': None
            }
            self.hotkey_states[hotkey] = HotkeyState()
            if self.verbose:
                print(f"Registering new hotkey: {hotkey}")

        # Define a mapping of event names to their corresponding callbacks
        event_callbacks = {
            'pressed': pressed,
            'released': released,
            'held': held,
            'held_release': held_release,
            'double_tap': double_tap
        }

        for event, callback in event_callbacks.items():
            if callback is not None:
                if self.hotkeys[hotkey][event] is not None:
                    raise ValueError(
                        f"Conflict: {callback.__name__} Hotkey '{hotkey}' already has a '{event}' callback assigned by another action"
                    )
                self.hotkeys[hotkey][event] = callback
                if self.verbose:
                    print(f"Assigned '{event}' callback to hotkey '{hotkey}'.")

    def handle_event(self, hotkey, event_type):
        """
        Triggers the appropriate callback for a given hotkey and event type.
        """
        if hotkey in self.hotkeys and self.hotkeys[hotkey][event_type]:
            self.hotkeys[hotkey][event_type]()

    def process_key_event(self, hotkey, is_pressed):
        """
        Processes a key event (press or release) for a given hotkey.
        
        :param hotkey: The hotkey that triggered the event
        :param is_pressed: True if the key was pressed, False if released
        """
        state = self.hotkey_states[hotkey]
        current_time = time.time()

        if is_pressed:
            if not state.is_pressed:
                state.is_pressed = True
                state.press_start_time = current_time
                is_double_tap = (current_time - state.last_press_time < self.double_tap_threshold)
                
                if is_double_tap and self.hotkeys[hotkey]['double_tap']:
                    self.handle_event(hotkey, 'double_tap')
                else:
                    self.handle_event(hotkey, 'pressed')
                
                state.last_press_time = current_time

                # Set up a timer for the 'held' event
                if state.hold_timer:
                    state.hold_timer.cancel()
                state.hold_timer = threading.Timer(self.hold_threshold, self.trigger_held_event, args=[hotkey])
                state.hold_timer.start()
        else:
            if state.is_pressed:
                state.is_pressed = False
                if state.hold_timer:
                    state.hold_timer.cancel()
                
                if current_time - state.press_start_time >= self.hold_threshold:
                    self.handle_event(hotkey, 'held_release')
                else:
                    self.handle_event(hotkey, 'released')
                
                state.is_held = False

    def trigger_held_event(self, hotkey):
        """
        Triggers the 'held' event for a hotkey.
        """
        state = self.hotkey_states[hotkey]
        if state.is_pressed:
            state.is_held = True
            self.handle_event(hotkey, 'held')

    def start(self, blocking=False):
        """
        Starts the input handler.
        
        :param blocking: If True, the method will block until stop() is called.
                        If False, the method will return immediately and run in the background.
        """
        self.running = True
        if blocking:
            try:
                self._run()
            except KeyboardInterrupt:
                print("Keyboard interrupt received. Stopping...")
                self.stop()
        else:
            threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """
        Stops the input handler.
        """
        self.running = False

    def _run(self):
        """
        Internal method to run the input handler. To be implemented by subclasses.
        """
        raise NotImplementedError("_run method must be implemented in subclasses")

def get_input_handler(verbose=False):
    """
    Factory function to get the appropriate input handler based on the platform.
    """
    import platform
    if platform.system() == "Windows":
        if config.WINDOWS_INPUT_HANDLER == "autohotkey":
            from input_apis.autohotkey_handler import AutohotkeyHandler
            return AutohotkeyHandler(verbose)
        else:
            from input_apis.keyboard_library_handler import KeyboardLibraryHandler
            return KeyboardLibraryHandler(verbose)
    else:
        print("Using PynputHandler")
        from input_apis.pynput_handler import PynputHandler
        return PynputHandler(verbose)