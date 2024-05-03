import time
import threading
from audio_recorder import AudioRecorder
from transcriber import TranscriptionManager
from keyboard_handler import get_keyboard_handler
import TTS
from chat_completions import CompletionManager
from soundfx import play_sound_FX
from utils import read_clipboard, count_tokens, trim_messages
import config
from prompt import prompts

class AlwaysReddy:
    def __init__(self):
        """Initialize the Recorder with default settings and objects."""
        self.verbose = config.VERBOSE
        self.recorder = AudioRecorder(verbose=self.verbose)
        self.is_recording = False
        self.clipboard_text = None
        self.messages = prompts[config.ACTIVE_PROMPT]["messages"].copy()
        self.last_press_time = 0
        self.tts = TTS.TTS(parent_client=self, verbose=self.verbose)
        self.recording_timeout_timer = None
        self.transcription_manager = TranscriptionManager(verbose=self.verbose)
        self.completion_client = CompletionManager(TTS_client=self.tts, parent_client=self, verbose=self.verbose)
        self.tts.completion_client = self.completion_client
        self.recording_stop_time = None
        self.timer = None
        self.main_thread = None
        self.stop_response = False
        self.last_message_was_cut_off = False

    def clear_messages(self):
        """Clear the message history."""
        # TODO Eventually i would like to keep track of conversations and be able to switch between them
        if self.verbose:
            print("Clearing messages...")
        self.messages = prompts[config.ACTIVE_PROMPT]["messages"].copy()

    def was_double_tapped(self, threshold=0.2):
        """
        Check if the hotkey was double tapped within a given threshold.

        Args:
            threshold (float): The time threshold for double tapping.

        Returns:
            bool: True if double tapped, False otherwise.
        """
        current_time = time.time()
        double_tapped = current_time - self.last_press_time < threshold
        self.last_press_time = current_time
        return double_tapped

    def start_recording(self):
        """Start the audio recording process and set a timeout for automatic stopping."""
        if self.verbose:
            print("Starting recording...")
        self.is_recording = True
        self.recorder.start_recording()

        play_sound_FX("start", volume=config.START_SOUND_VOLUME, verbose=self.verbose)

        # This just starts a timer for the recording to stop after a certain amount of time, just to make sure you dont leave it recording forever!
        self.recording_timeout_timer = threading.Timer(config.MAX_RECORDING_DURATION, self.stop_recording)
        self.recording_timeout_timer.start()

    def stop_recording(self):
        """Stop the audio recording process and handle the recorded audio."""
        if self.recording_timeout_timer and self.recording_timeout_timer.is_alive():
            self.recording_timeout_timer.cancel()

        if self.is_recording:
            if self.verbose:
                print("Stopping recording...")
            play_sound_FX("end", volume=config.END_SOUND_VOLUME, verbose=self.verbose)
            self.is_recording = False
            self.recorder.stop_recording()
            self.recording_stop_time = time.time()

            # If the recording is too short, ignore it
            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                if self.verbose:
                    print("Recording is too short or file does not exist, ignoring...")
                return

            try:
                transcript = self.transcription_manager.transcribe_audio(self.recorder.filename)

                # If the user has tried to cut off the response, we need to make sure we dont process it
                if not self.stop_response and transcript:
                    # Handle response is where the magic happens
                    self.handle_response(transcript)

            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"An error occurred during transcription: {e}")

    def how_long_to_speak_first_word(self, first_word_time):
        """
        Calculate and print the delay between the end of recording and the first word spoken by TTS.
        This is really just for testing purposes.

        Args:
            first_word_time (float): The timestamp of the first word spoken by TTS.
        """
        if self.recording_stop_time:
            if self.verbose:
                print(f"Response delay for first word: {first_word_time - self.recording_stop_time} seconds")
            self.recording_stop_time = None

    def cancel_recording(self):
        """Cancel the current recording."""
        if self.is_recording:
            if self.verbose:
                print("Cancelling recording...")
            self.recorder.stop_recording(cancel=True)
            if self.verbose:
                print("Recording cancelled.")
            self.is_recording = False

    def cancel_tts(self):
        """Cancel the current TTS."""
        if self.verbose:
            print("Stopping text-to-speech...")
        self.tts.stop()
        if self.verbose:
            print("Text-to-speech cancelled.")

    def cancel_all(self, silent=False):
        """Cancel the current recording and TTS."""
        played_cancel_sfx = False

        if self.main_thread is not None and self.main_thread.is_alive():
            if not silent:
                # Track if the cancel sound has been played so it doesn't play twice
                play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
                played_cancel_sfx = True
            self.stop_response = True

        elif self.is_recording:
            if not silent:
                # Track if the cancel sound has been played so it doesn't play twice
                play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
                played_cancel_sfx = True
            self.cancel_recording()

        if self.tts.running_tts:
            # Seems like the wrong way to do this but I want to ensure I only play the sound once
            if not played_cancel_sfx:
                if not silent:
                    play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
                    played_cancel_sfx = True
            self.cancel_tts()

    def handle_response(self, transcript):
        """
        Handle the response from the transcription and generate a completion.

        Args:
            transcript (str): The transcribed text from the audio recording.
        """
        try:
            # If the user has cut off the assistant's last message, add a message to indicate this
            if self.last_message_was_cut_off:
                transcript = "--> USER CUT THE ASSISTANTS LAST MESSAGE SHORT <--\n" + transcript

            # If the user wants to use the clipboard text, append it to the message
            if self.clipboard_text:
                self.messages.append({"role": "user", "content": transcript + f"\n\nTHE USER HAS THIS TEXT COPIED TO THEIR CLIPBOARD:\n```{self.clipboard_text}```"})
                self.clipboard_text = None
            else:
                self.messages.append({"role": "user", "content": transcript})

            # Make sure token count is within limits
            if count_tokens(self.messages) > config.MAX_TOKENS:
                self.messages = trim_messages(self.messages, config.MAX_TOKENS)


            print("Transcription:\n", transcript)

            # Make sure the user hasn't cut off the response
            if self.stop_response:
                return

            # Get the response from the AI
            response = self.completion_client.get_completion(self.messages, model=config.COMPLETION_MODEL)

            while self.tts.running_tts:
                # Waiting for the TTS to finish before processing it this way we can tell if the user has cut off the TTS before saving it to the messages
                # Doing it this way feels like its probably not optimal though
                time.sleep(0.001)

            if not response:
                if self.verbose:
                    print("No response generated.")
                # If the response is empty, remove the last message
                self.messages = self.messages[:-1]
                return

            # Reset the flag indicating the last message was cut off
            self.last_message_was_cut_off = False

            if self.stop_response:
                # If the assistant was cut off while speaking, find the last sentence spoken and cut off the response there
                index = response.rfind(self.tts.last_sentence_spoken)

                # If the last sentence spoken was found, cut off the response there
                if index != -1:
                    # Add a message to indicate the user cut off the response
                    response = response[:index + len(self.tts.last_sentence_spoken)]
                    self.last_message_was_cut_off = True

            self.messages.append({"role": "assistant", "content": response})

            print("Response:\n", response)

        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred while handling the response: {e}")

    def handle_hotkey(self):
        """Handle the hotkey press for starting or stopping recording."""
        if self.tts.running_tts:
            if self.verbose:
                print("TTS is running, stopping...")
            self.tts.stop()

        if self.is_recording:
            self.stop_response = False
            self.stop_recording()
        else:
            self.start_recording()

    def start_main_thread(self):
        """This starts the main thread and keeps a reference to it."""
        self.timer = None

        if self.main_thread is not None and self.main_thread.is_alive():
            # If the thread is already running, cancel (without playing cancel sound) and start a new one
            self.cancel_all(silent=True)  # the silence is just so you dont hear cancel sound immediately followed by the start sound
            self.main_thread.join()

            self.main_thread = threading.Thread(target=self.handle_hotkey)
            self.main_thread.start()

        else:
            self.main_thread = threading.Thread(target=self.handle_hotkey)
            self.main_thread.start()

    def handle_hotkey_wrapper(self):
        """
        Wrapper for the hotkey handler to include double tap detection for clipboard usage.
        """
        use_clipboard = self.was_double_tapped()
        if self.verbose:
            print("use_clipboard:", use_clipboard)
        if use_clipboard:
            try:
                self.clipboard_text = read_clipboard()
            except Exception as e:
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"Failed to read from clipboard: {e}")

        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
            self.start_main_thread()
        else:
            self.timer = threading.Timer(0.2, self.start_main_thread)
            self.timer.start()

    def run(self):
        """Run the recorder, setting up hotkeys and entering the main loop."""
        keyboard_handler = get_keyboard_handler(verbose=self.verbose)
        keyboard_handler.add_hotkey(config.RECORD_HOTKEY, self.handle_hotkey_wrapper)
        keyboard_handler.add_hotkey(config.CANCEL_HOTKEY, self.cancel_all)
        keyboard_handler.add_hotkey(config.CLEAR_HISTORY_HOTKEY, self.clear_messages)

        print(f"\n\nPress '{config.RECORD_HOTKEY}' to start recording, press again to stop and transcribe.\nDouble tap to give the AI access to read your clipboard (I suggest holding all but the last key down then quickly double tapping the last key).\nPress '{config.CANCEL_HOTKEY}' to cancel recording.\nPress '{config.CLEAR_HISTORY_HOTKEY}' to clear the chat history.")

        keyboard_handler.start()

if __name__ == "__main__":
    try:
        AlwaysReddy().run()
    except Exception as e:
        if config.VERBOSE:
            import traceback
            traceback.print_exc()
        else:
            print(f"Failed to start the recorder: {e}")