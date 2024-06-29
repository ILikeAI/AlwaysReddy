import time
import threading
from enum import Enum, auto
from audio_recorder import AudioRecorder
from transcription_manager import TranscriptionManager
from input_apis.input_handler import get_input_handler
import tts_manager
from completion_manager import CompletionManager
from soundfx import play_sound_FX
from utils import read_clipboard, to_clipboard
from config_loader import config
import prompt

class HandlerType(Enum):
    """
    Enum for different types of recording handlers.
    This allows for easy extension of functionality by adding new handler types.
    """
    STANDARD = auto()
    TRANSCRIBE = auto()

class RecordingHandler:
    """
    Base class for recording handlers.
    Provides a common interface for different recording behaviors.
    """
    def __init__(self, always_reddy):
        self.always_reddy = always_reddy

    def start_recording(self):
        """Start the recording process."""
        self.always_reddy.recorder.start_recording()

    def stop_recording(self):
        """Stop the recording process."""
        self.always_reddy.recorder.stop_recording()

    def process_recording(self, audio_file):
        """
        Process the recorded audio file.
        This method should be implemented by subclasses to define specific behavior.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

class StandardRecordingHandler(RecordingHandler):
    """Handler for standard recording and response generation."""
    def process_recording(self, audio_file):
        transcript = self.always_reddy.transcription_manager.transcribe_audio(audio_file)
        # Only process if we have a transcript and haven't been told to stop
        if transcript and not self.always_reddy.stop_response:
            self.always_reddy.handle_response(transcript)

class TranscribeToClipboardHandler(RecordingHandler):
    """Handler for transcribing and copying to clipboard."""
    def process_recording(self, audio_file):
        transcript = self.always_reddy.transcription_manager.transcribe_audio(audio_file)
        if transcript:
            to_clipboard(transcript)
            # Provide audible feedback that the operation is complete
            self.always_reddy.tts.run_tts("Copied.")

class AlwaysReddy:
    """
    Main class for the AlwaysReddy application.
    Manages recording, transcription, and response generation.
    """
    def __init__(self):
        """Initialize AlwaysReddy with default settings and objects."""
        self.verbose = config.VERBOSE
        self.recorder = AudioRecorder(verbose=self.verbose)
        self.clipboard_text = None
        self.messages = prompt.get_initial_prompt(config.ACTIVE_PROMPT)
        self.last_press_time = 0
        self.tts = tts_manager.TTSManager(parent_client=self, verbose=self.verbose)
        self.recording_timeout_timer = None
        self.transcription_manager = TranscriptionManager(verbose=self.verbose)
        self.completion_client = CompletionManager(TTS_client=self.tts, parent_client=self, verbose=self.verbose)
        self.tts.completion_client = self.completion_client
        self.recording_stop_time = None
        self.main_thread = None
        self.stop_response = False
        self.last_message_was_cut_off = False

        # Initialize different recording handlers
        self.recording_handlers = {
            HandlerType.STANDARD: StandardRecordingHandler(self),
            HandlerType.TRANSCRIBE: TranscribeToClipboardHandler(self)
        }
        self.current_handler = None

    def clear_messages(self):
        """Clear the message history to start a fresh conversation."""
        print("Clearing messages...")
        self.messages = prompt.get_initial_prompt(config.ACTIVE_PROMPT)
        self.last_message_was_cut_off = False

    def start_recording(self):
        """Start the audio recording process and set a timeout for automatic stopping."""
        if self.verbose:
            print("Starting recording...")
        self.current_handler.start_recording()
        play_sound_FX("start", volume=config.START_SOUND_VOLUME, verbose=self.verbose)
        # Set a timer to automatically stop recording after a set duration
        self.recording_timeout_timer = threading.Timer(config.MAX_RECORDING_DURATION, self.stop_recording)
        self.recording_timeout_timer.start()

    def cancel_recording_timeout_timer(self):
        """Cancel the recording timeout timer if it's running."""
        if self.recording_timeout_timer and self.recording_timeout_timer.is_alive():
            self.recording_timeout_timer.cancel()
            
    def stop_recording(self):
        """Stop the audio recording process and handle the recorded audio."""
        print("Stopping recording...")
        self.cancel_recording_timeout_timer()
        
        if self.recorder.recording:
            if self.verbose:
                print("Stopping recording...")
            play_sound_FX("end", volume=config.END_SOUND_VOLUME, verbose=self.verbose)
            self.current_handler.stop_recording()
            self.recording_stop_time = time.time()

            # Ignore recordings that are too short
            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                if self.verbose:
                    print("Recording is too short or file does not exist, ignoring...")
                return

            try:
                self.current_handler.process_recording(self.recorder.filename)
            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"An error occurred during processing: {e}")

    def cancel_recording(self):
        """Cancel the current recording."""
        if self.recorder.recording:
            if self.verbose:
                print("Cancelling recording...")
            self.recorder.stop_recording(cancel=True)
            if self.verbose:
                print("Recording cancelled.")

    def cancel_tts(self):
        """Cancel the current text-to-speech playback."""
        if self.verbose:
            print("Stopping text-to-speech...")
        self.tts.stop()
        if self.verbose:
            print("Text-to-speech cancelled.")

    def cancel_all(self, silent=False):
        """
        Cancel all ongoing operations (recording, TTS, response generation).
        Used when starting a new recording or explicitly cancelling.
        """
        played_cancel_sfx = False
        self.cancel_recording_timeout_timer()

        # Stop the main thread if it's running
        if self.main_thread is not None and self.main_thread.is_alive():
            if not silent:
                play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
                played_cancel_sfx = True
            self.stop_response = True

        # Stop recording if it's ongoing
        if self.recorder.recording:
            if not silent and not played_cancel_sfx:
                play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
                played_cancel_sfx = True
            self.cancel_recording()

        # Stop TTS if it's running
        if self.tts.running_tts:
            if not silent and not played_cancel_sfx:
                play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
            self.cancel_tts()

    def handle_response(self, transcript):
        """
        Handle the response from the transcription and generate a completion.
        This method manages the conversation flow and response generation.
        """
        try:
            # Indicate if the previous assistant message was cut off
            if self.last_message_was_cut_off:
                transcript = "--> USER CUT THE ASSISTANTS LAST MESSAGE SHORT <--\n" + transcript

            # Include clipboard content if available
            if self.clipboard_text:
                self.messages.append({"role": "user", "content": transcript + f"\n\nCLIPBOARD CONTENT (ignore if user doesn't mention it):\n```{self.clipboard_text}```"})
                self.clipboard_text = None
                print("\nUsing the text in your clipboard...")
            else:
                self.messages.append({"role": "user", "content": transcript})

            print("\nTranscription:\n", transcript)

            # Stop if the user has cancelled the response
            if self.stop_response:
                return

            response = self.completion_client.get_completion(self.messages, model=config.COMPLETION_MODEL)

            # Wait for any ongoing TTS to finish
            while self.tts.running_tts:
                time.sleep(0.001)

            if not response:
                if self.verbose:
                    print("No response generated.")
                self.messages = self.messages[:-1]
                return

            self.last_message_was_cut_off = False

            # Handle case where response was interrupted
            if self.stop_response:
                index = response.rfind(self.tts.last_sentence_spoken)
                if index != -1:
                    response = response[:index + len(self.tts.last_sentence_spoken)]
                    self.last_message_was_cut_off = True

            self.messages.append({"role": "assistant", "content": response})

            print("\nResponse:\n", response)

        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred while handling the response: {e}")

    def toggle_recording(self, handler_type: HandlerType):
        """
        Handle the hotkey press for starting or stopping recording.
        This method switches between recording states and updates the current handler.
        """
        if self.recorder.recording:
            self.stop_response = False
            # Update the current handler based on which hotkey was used to stop recording
            self.current_handler = self.recording_handlers[handler_type]
            self.stop_recording()
        else:
            self.current_handler = self.recording_handlers[handler_type]
            self.start_recording()

    def start_main_thread(self, handler_type: HandlerType):
        """
        Start the main thread for recording.
        This method ensures only one recording thread is active at a time.
        """
        if self.main_thread is not None and self.main_thread.is_alive():
            self.cancel_all(silent=True)
        
        self.main_thread = threading.Thread(target=self.toggle_recording, args=(handler_type,))
        self.main_thread.start()

    def handle_record_hotkey(self, is_pressed):
        """
        Handle the record hotkey press.
        This method manages the behavior for starting/stopping standard recording.
        """
        within_delay = time.time() - self.last_press_time < config.RECORD_HOTKEY_DELAY
        if is_pressed:
            self.last_press_time = time.time()

            # Handle clipboard inclusion based on configuration and timing
            if config.ALWAYS_INCLUDE_CLIPBOARD:
                self.clipboard_text = read_clipboard()
            elif self.recorder.recording and within_delay:
                self.clipboard_text = read_clipboard()
                if self.verbose:
                    print("Using clipboard...")
                return

            self.start_main_thread(HandlerType.STANDARD)
        else:
            if self.recorder.recording and not within_delay:
                self.start_main_thread(HandlerType.STANDARD)

    def handle_transcribe_hotkey(self, is_pressed):
        """
        Handle the transcribe hotkey press.
        This method manages the behavior for starting/stopping transcribe-to-clipboard functionality.
        """
        within_delay = time.time() - self.last_press_time < config.RECORD_HOTKEY_DELAY
        if is_pressed:
            self.last_press_time = time.time()
            self.start_main_thread(HandlerType.TRANSCRIBE)
        else:
            if self.recorder.recording and not within_delay:
                self.start_main_thread(HandlerType.TRANSCRIBE)

    def run(self):
        """
        Run the AlwaysReddy application.
        This method sets up hotkeys and starts the main input handler loop.
        """
        input_handler = get_input_handler(verbose=self.verbose)

        print()
        if config.RECORD_HOTKEY:
            input_handler.add_held_hotkey(config.RECORD_HOTKEY, self.handle_record_hotkey)
            print(f"Press '{config.RECORD_HOTKEY}' to start recording, press again to stop and transcribe."
                  f"\n\tAlternatively hold it down to record until you release.")

            if "+" in config.RECORD_HOTKEY:
                hotkey_start, hotkey_end = config.RECORD_HOTKEY.rsplit("+", 1)
                print(f"\tHold down '{hotkey_start}' and double tap '{hotkey_end}' to give AlwaysReddy the content currently copied in your clipboard.")
            else:
                print(f"\tDouble tap '{config.RECORD_HOTKEY}' to give AlwaysReddy the content currently copied in your clipboard.")

        if config.CANCEL_HOTKEY:
            input_handler.add_hotkey(config.CANCEL_HOTKEY, self.cancel_all)
            print(f"Press '{config.CANCEL_HOTKEY}' to cancel recording.")

        if config.CLEAR_HISTORY_HOTKEY:
            input_handler.add_hotkey(config.CLEAR_HISTORY_HOTKEY, self.clear_messages)
            print(f"Press '{config.CLEAR_HISTORY_HOTKEY}' to clear the chat history.")

        if config.TRANSCRIBE_CLIPBOARD_HOTKEY:
            input_handler.add_held_hotkey(config.TRANSCRIBE_CLIPBOARD_HOTKEY, self.handle_transcribe_hotkey)
            print(f"Press '{config.TRANSCRIBE_CLIPBOARD_HOTKEY}'to transcribe what you say and write it to the clipboard."
                    f"\n\tAlternatively hold it down to record until you release.")

        input_handler.start()

if __name__ == "__main__":
    try:
        AlwaysReddy().run()
    except Exception as e:
        if config.VERBOSE:
            import traceback
            traceback.print_exc()
        else:
            print(f"Failed to start the recorder: {e}")