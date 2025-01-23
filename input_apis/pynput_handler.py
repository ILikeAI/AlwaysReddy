import pynput.keyboard as pynput_keyboard
import threading
import time
import platform

from input_apis.input_handler import InputHandler

#
# EXTENSIVE (BUT NOT TRULY EXHAUSTIVE) LIST OF SYSTEM-LEVEL SHORTCUTS
# Note: Some combos might not be captured at all if the OS intercepts them first.
#       Others may vary by user or DE. This is a best-effort list of "common" defaults.
#
SYSTEM_SHORTCUTS = {
    "Windows": [
        # App switching / system UI
        "alt+tab",
        "win+tab",
        "alt+esc",
        # Closing/minimizing
        "alt+f4",
        "win+m",         # Minimize all
        "win+d",         # Show desktop
        # Lock, run, search, etc.
        "win+l",
        "win+r",
        "win+e",         # Explorer
        "win+x",         # Quick link menu
        "win+i",         # Settings
        # Task manager (some OS versions might not deliver this)
        "ctrl+shift+esc",
        # Virtual desktops
        "win+ctrl+d",
        "win+ctrl+f4",   # Close active virtual desktop
        # Arrow-based shortcuts
        "win+up",
        "win+down",
        "win+left",
        "win+right",
        # Some SHIFT combos
        "shift+win+up",
        "shift+win+down",
        "shift+win+left",
        "shift+win+right",
        # Possibly: "ctrl+alt+delete" won't be caught by typical userland apps, so we omit
    ],
    "Darwin": [  # macOS
        # App switching / system UI
        "cmd+tab",
        "cmd+space",         # Spotlight
        "cmd+shift+space",   # Might be used for Siri or multiple input sources
        "cmd+option+esc",    # Force quit
        # Mission Control
        "ctrl+up",           # Traditional mission control (some setups)
        "ctrl+down",         # App expose
        "ctrl+left",
        "ctrl+right",
        # Fullscreen & Window management
        "ctrl+cmd+f",        # Toggle fullscreen in many apps
        # Launchpad
        "thumb+shift+a",     # Not universal, some set "thumb" = "cmd"? This is user-based
        # Screenshot combos (the system often intercepts them):
        "cmd+shift+3",
        "cmd+shift+4",
        "cmd+shift+5",
    ],
    "Linux": [
        # Common combos in many DEs (GNOME, KDE, etc.)
        "alt+tab",       # Switch apps
        "alt+f2",        # Run prompt
        "super+tab",     # Some distros use "super" for switching
        "super+space",   # Some use this for launcher
        # TTY switching (if you're on a virtual console):
        "ctrl+alt+f1",
        "ctrl+alt+f2",
        "ctrl+alt+f3",
        "ctrl+alt+f4",
        "ctrl+alt+f5",
        "ctrl+alt+f6",
        # Lock screen / show desktop (varies by distro):
        "super+l",       # GNOME, etc.
        "ctrl+alt+l",    # Some distros
        # Window actions:
        "alt+f4",        # Close window in many DEs
    ]
}


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
        self.hotkey_maps = {}      # Maps pynput key combinations to original hotkey strings
        self.listener_thread = None

        # Identify platform and parse known system shortcuts
        self.platform_system = platform.system()
        self.known_system_shortcuts = self._parse_system_shortcuts()

    def _parse_system_shortcuts(self):
        """
        Convert known system shortcuts for this OS into frozensets of keys
        in pynput-friendly format.
        """
        raw_shortcuts = SYSTEM_SHORTCUTS.get(self.platform_system, [])
        parsed = []
        for combo_str in raw_shortcuts:
            combo_keys = frozenset(
                pynput_keyboard.HotKey.parse(
                    self.convert_to_pynput_format(combo_str)
                )
            )
            parsed.append(combo_keys)
        return parsed

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
        # Register callbacks in the base class (InputHandler)
        super().add_hotkey(
            hotkey,
            pressed=pressed,
            released=released,
            held=held,
            held_release=held_release,
            double_tap=double_tap
        )

        # Convert the hotkey string to a pynput-friendly format
        pynput_keys = frozenset(
            pynput_keyboard.HotKey.parse(self.convert_to_pynput_format(hotkey))
        )
        # Store in a map: frozenset(...) -> original hotkey string
        self.hotkey_maps[pynput_keys] = hotkey

    def on_press(self, key):
        """
        Handle key press events.

        :param key: The key that was pressed
        """
        try:
            if not self.listener:
                return  # If the listener isn't active, do nothing

            # Convert to a canonical form so shift-l vs. shift-r doesn't break logic
            canonical_key = self.listener.canonical(key)

            # 1) Copy old state
            old_keys = set(self.current_keys)

            # 2) Add the newly pressed key
            self.current_keys.add(canonical_key)

            # 3) If no change in the set of pressed keys, ignore (prevents duplicates)
            if self.current_keys == old_keys:
                return

            # 4) Check combos from largest to smallest
            for hotkey_combo, original_hotkey in sorted(
                self.hotkey_maps.items(),
                key=lambda x: len(x[0]),
                reverse=True
            ):
                if hotkey_combo.issubset(self.current_keys):
                    self.process_key_event(original_hotkey, True)
                    break

            # 5) Check if we just pressed a known system-level shortcut
            for sys_combo in self.known_system_shortcuts:
                if sys_combo.issubset(self.current_keys):
                    # We suspect the OS may swallow release events for this combo
                    self.reset_all_keys()
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
            if not self.listener:
                return

            canonical_key = self.listener.canonical(key)

            # 1) Copy old state
            old_keys = set(self.current_keys)

            # 2) Remove this key if present
            if canonical_key in self.current_keys:
                self.current_keys.remove(canonical_key)
            else:
                # If it's not in current_keys, the set didn't change, so ignore
                return

            # 3) Check combos from largest to smallest
            for hotkey_combo, original_hotkey in sorted(
                self.hotkey_maps.items(),
                key=lambda x: len(x[0]),
                reverse=True
            ):
                if hotkey_combo.issubset(old_keys):
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

    def reset_all_keys(self):
        """
        Clears the current_keys state and cancels any ongoing 'held' timers,
        effectively resetting any stuck keys.
        """
        # 1) For each hotkey that might be considered 'pressed',
        #    we trigger a release event so we don't remain stuck.
        old_keys = set(self.current_keys)
        self.current_keys.clear()

        # Sort from largest to smallest, in case some combos overlap
        for hotkey_combo, original_hotkey in sorted(
            self.hotkey_maps.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            if hotkey_combo.issubset(old_keys):
                self.process_key_event(original_hotkey, False)

        # Also cancel hold timers in the base InputHandler:
        for hotkey in self.hotkey_states:
            state = self.hotkey_states[hotkey]
            if state.hold_timer:
                state.hold_timer.cancel()

    @staticmethod
    def convert_to_pynput_format(hotkey):
        """
        Convert a string hotkey (e.g., 'ctrl+alt+e') to pynput format (e.g., 'ctrl+alt+e').
        For longer keys like 'windows' or 'capslock', wrap them in <...>.
        Also handle 'cmd' as <cmd> for macOS.
        """
        parts = hotkey.split('+')
        converted = []
        for part in parts:
            part = part.strip().lower()
            if part in ['win', 'windows', 'left windows']:
                converted.append('<cmd>')
            elif part in ['cmd', 'command']:
                converted.append('<cmd>')  # Mac command key
            elif part == 'capslock':
                converted.append('<caps_lock>')
            elif part == 'super':
                converted.append('<cmd>')  # On many Linux DEs, 'super' is Windows key
            elif len(part) > 1:
                converted.append(f'<{part}>')
            else:
                # Single-character keys stay as is (e.g., 'w', 'a', etc.)
                converted.append(part)
        return '+'.join(converted)
