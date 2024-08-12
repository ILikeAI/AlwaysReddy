import time
import threading
from audio_recorder import AudioRecorder
from transcription_manager import TranscriptionManager
from input_apis.input_handler import get_input_handler
import tts_manager
from completion_manager import CompletionManager
from soundfx import play_sound_FX
from config_loader import config
import prompt
import os
import importlib
from actions.base_action import BaseAction
# Import actions

class AlwaysReddy:
    def __init__(self):
        """Initialize the AlwaysReddy instance with default settings and objects."""
        self.verbose = config.VERBOSE
        self.recorder = AudioRecorder(verbose=self.verbose)
        self.last_clipboard_text = None
        self.messages = prompt.build_initial_messages(config.ACTIVE_PROMPT)
        self.tts = tts_manager.TTSManager(parent_client=self, verbose=self.verbose)
        self.recording_timeout_timer = None
        self.transcription_manager = TranscriptionManager(verbose=self.verbose)
        self.completion_client = CompletionManager(verbose=self.verbose)
        self.action_thread = None
        self.stop_action = False
        self.input_handler = get_input_handler(verbose=self.verbose)
        self.input_handler.double_tap_threshold = config.DOUBLE_TAP_THRESHOLD
        self.last_action_time = 0
        self.current_recording_action = None

    def _start_recording(self, action=None):
        """
        Start the audio recording process and set a timeout for automatic stopping.
        
        Args:
            action (callable, optional): The action to be called when the recording times out.
        """
        if self.verbose:
            print(f"Starting recording... Action: {action.__name__ if action else 'None'}")
            
        play_sound_FX("start", volume=config.START_SOUND_VOLUME, verbose=self.verbose)
        self.recorder.start_recording()
        self.current_recording_action = action
        self.recording_timeout_timer = threading.Timer(config.MAX_RECORDING_DURATION, self._handle_recording_timeout)
        self.recording_timeout_timer.start()

    def _stop_recording(self):
        """Stop the current recording and return the filename."""
        self._cancel_recording_timeout_timer()
        if self.verbose:
            print("Stopping recording...")
        play_sound_FX("end", volume=config.END_SOUND_VOLUME, verbose=self.verbose)
        return self.recorder.stop_recording()

    def _handle_recording_timeout(self):
        """Handle the recording timeout by stopping the recording and calling the current recording action."""
        if self.verbose:
            print("Recording timeout reached.")

        if self.current_recording_action:
            if self.verbose:
                print(f"Attempting to run {self.current_recording_action.__name__}")
            self.execute_action_in_thread(self.current_recording_action)
        else:
            if self.verbose:
                print("No action set for recording timeout.")
        self.current_recording_action = None  # Clear the action after execution

    def _cancel_recording_timeout_timer(self):
        """Cancel the recording timeout timer if it is running."""
        if self.recording_timeout_timer and self.recording_timeout_timer.is_alive():
            self.recording_timeout_timer.cancel()

    def _cancel_recording(self):
        """Cancel the current recording."""
        if self.recorder.recording:
            if self.verbose:
                print("Cancelling recording...")
            self.recorder.stop_recording(cancel=True)
            if self.verbose:
                print("Recording cancelled.")

    def _cancel_tts(self):
        """Cancel the current TTS."""
        if self.verbose:
            print("Stopping text-to-speech...")
        self.tts.stop()
        if self.verbose:
            print("Text-to-speech cancelled.")

    def cancel_all(self, silent=False):
        """
        Cancel the current recording and TTS.
        This method runs outside the main action thread and can be called at any time to stop ongoing processes.
        
        Args:
            silent (bool): If True, don't play the cancel sound.
        """
        cancelled_something = False
        self._cancel_recording_timeout_timer()
        
        if self.action_thread is not None and self.action_thread.is_alive():
            self.stop_action = True
            cancelled_something = True

        if self.recorder.recording:
            self._cancel_recording()
            cancelled_something = True

        if self.tts.running_tts:
            self._cancel_tts()
            cancelled_something = True

        if cancelled_something and not silent:
            play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)

    def add_action_hotkey(self, hotkey, *, pressed=None, released=None, held=None, held_release=None, double_tap=None, run_in_action_thread=True):
        """
        Add a hotkey for an action with specified callbacks for different events.
        
        Args:
            hotkey (str): The hotkey combination.
            pressed (callable, optional): Callback for when the hotkey is pressed.
            released (callable, optional): Callback for when the hotkey is released.
            held (callable, optional): Callback for when the hotkey is held.
            held_release (callable, optional): Callback for when the hotkey is released after being held.
            double_tap (callable, optional): Callback for when the hotkey is double-tapped.
            run_in_action_thread (bool): If True, the action will run in the main thread. Default is True.
        """
        def wrap_for_action_thread(method):
            if method is None:
                return None
            def run_in_action_thread():
                self.execute_action_in_thread(method)
            return run_in_action_thread

        wrapped_kwargs = {}
        for event, method in [('pressed', pressed), ('released', released), ('held', held), 
                            ('held_release', held_release), ('double_tap', double_tap)]:
            if method is not None:
                wrapped_kwargs[event] = wrap_for_action_thread(method) if run_in_action_thread else method

        self.input_handler.add_hotkey(hotkey, **wrapped_kwargs)

    def toggle_recording(self, action=None):
        """
        Handle the hotkey press for starting or stopping recording.
        
        Args:
            action (callable, optional): The action to be called when the recording is stopped.
        
        Returns:
            str or None: The recording filename if stopped, None if started.
        """
        if self.recorder.recording:
            self.stop_action = False
            filename = self._stop_recording()
            return filename
        else:
            if config.ALWAYS_INCLUDE_CLIPBOARD:
                self.save_clipboard_text()
            self._start_recording(action)
            return None

    def execute_action_in_thread(self, action_to_run, *args, **kwargs):
        """
        Execute an action in a separate thread.
        
        Args:
            action_to_run (callable): The action to be executed.
            *args: Positional arguments for the action.
            **kwargs: Keyword arguments for the action.
        """
        current_time = time.time()
        if current_time - self.last_action_time < 0.1: # Delay between actions
            print("Action triggered too quickly. Please wait.")
            return

        self.last_action_time = current_time

        if self.action_thread is not None and self.action_thread.is_alive():
            self.cancel_all(silent=True)
            self.action_thread.join(timeout=2)  # Wait for up to 2 seconds
            if self.action_thread.is_alive():
                print("Warning: Previous action did not end properly.")

        if self.verbose:
            print(f"Running {action_to_run.__name__}...")
        self.stop_action = False
        self.action_thread = threading.Thread(target=action_to_run, args=args, kwargs=kwargs)
        self.action_thread.start()

    def discover_and_initialize_actions(self):
        actions_dir = 'actions'
        for filename in os.listdir(actions_dir):
            if filename.endswith('.py') and filename not in ['base_action.py', 'example_action.py']:
                module_name = f'actions.{filename[:-3]}'
                module = importlib.import_module(module_name)
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, BaseAction) and obj is not BaseAction:
                        print(f"\nInitalizing action: {obj.__name__}")
                        action_instance = obj(self)      

    def run(self):
        """Run the AlwaysReddy instance, setting up hotkeys and entering the main loop."""
        print("\n\nSetting up AlwaysReddy...\n")
        self.discover_and_initialize_actions()
        print("\nSystem actions:")
        
        # Add cancel_all as an action that doesn't run in the main thread
        self.add_action_hotkey(config.CANCEL_HOTKEY, pressed=self.cancel_all, run_in_action_thread=False)
        print(f"'{config.CANCEL_HOTKEY}': Cancel currently running action, recording, TTS or other")
        print("\nAlwaysReddy is reddy. Use any of the hotkeys above to get started.")
        try:
            self.input_handler.start(blocking=True)
        except KeyboardInterrupt:
            print("\nShutting down AlwaysReddy...")
        finally:
            self.cancel_all(silent=True)

if __name__ == "__main__":
    try:
        AlwaysReddy().run()
    except Exception as e:
        if config.VERBOSE:
            import traceback
            traceback.print_exc()
        else:
            print(f"Failed to start AlwaysReddy: {e}")