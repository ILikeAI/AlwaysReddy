import time
import threading
from audio_recorder import AudioRecorder
from transcription_manager import TranscriptionManager
from input_apis.input_handler import get_input_handler
import tts_manager
from completion_manager import CompletionManager
from soundfx import play_sound_FX
from utils import read_clipboard, to_clipboard
from config_loader import config
import prompt

class AlwaysReddy:
    def __init__(self):
        """Initialize the Recorder with default settings and objects."""
        self.verbose = config.VERBOSE
        self.recorder = AudioRecorder(verbose=self.verbose)
        self.clipboard_text = None
        self.last_clipboard_text = None # This is used to check if the clipboard text has changed
        self.messages = prompt.build_initial_messages(config.ACTIVE_PROMPT)
        self.tts = tts_manager.TTSManager(parent_client=self, verbose=self.verbose)
        self.recording_timeout_timer = None
        self.transcription_manager = TranscriptionManager(verbose=self.verbose)
        self.completion_client = CompletionManager(verbose=self.verbose)
        self.main_thread = None
        self.stop_response = False
        self.last_message_was_cut_off = False

    def new_chat(self):
        """Clear the message history."""
        # TODO Eventually i would like to keep track of conversations and be able to switch between them
        print("Clearing messages...")
        self.messages = prompt.build_initial_messages(config.ACTIVE_PROMPT)
        self.last_message_was_cut_off = False
        self.last_clipboard_text = None

    def start_recording(self):
        """Start the audio recording process and set a timeout for automatic stopping."""
        if self.verbose:
            print("Starting recording...")
        self.recorder.start_recording()

        play_sound_FX("start", volume=config.START_SOUND_VOLUME, verbose=self.verbose)

        # This just starts a timer for the recording to stop after a certain amount of time, just to make sure you dont leave it recording forever!
        self.recording_timeout_timer = threading.Timer(config.MAX_RECORDING_DURATION, self.stop_recording)
        self.recording_timeout_timer.start()
    
    def cancel_recording_timeout_timer(self):
        """Cancel the recording timeout timer if it is running."""
        if self.recording_timeout_timer and self.recording_timeout_timer.is_alive():
            self.recording_timeout_timer.cancel()

    def stop_recording(self):
        """Stop the audio recording process and handle the recorded audio."""
        self.cancel_recording_timeout_timer()
        if self.recorder.recording:
            if self.verbose:
                print("Stopping recording...")
            play_sound_FX("end", volume=config.END_SOUND_VOLUME, verbose=self.verbose)
            recording_filename = self.recorder.stop_recording()

            # If the recording is too short, ignore it
            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                if self.verbose:
                    print("Recording is too short or file does not exist, ignoring...")
                return

            try:
                transcript = self.transcription_manager.transcribe_audio(recording_filename)

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

    def cancel_recording(self):
        """Cancel the current recording."""
        if self.recorder.recording:
            if self.verbose:
                print("Cancelling recording...")
            self.recorder.stop_recording(cancel=True)
            if self.verbose:
                print("Recording cancelled.")

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
        self.cancel_recording_timeout_timer()
        if self.main_thread is not None and self.main_thread.is_alive():
            if not silent:
                # Track if the cancel sound has been played so it doesn't play twice
                play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME, verbose=self.verbose)
                played_cancel_sfx = True
            self.stop_response = True

        elif self.recorder.recording:
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

    def handle_response_stream(self, stream, run_tts=True):
        """
        This recieves a generator that yields tuples of the type of content and the content itself.
        The type may be "sentence", "clipboard_text" or "full_response", sentence is spoken by the TTS and clipboard_text is copied to the clipboard.

        Args:
            stream (generator): A generator that yields tuples of the type of content and the content itself.
        """
        response = None
        for type, content in stream:
            # If stop stream is set to True, break the loop
            if self.stop_response:
                break

            if type == "sentence" and run_tts:
                self.tts.run_tts(content)

            elif type == "clipboard_text":
                to_clipboard(content)

            elif type == "full_response":
                response = content

        return response
    
    def handle_response(self, transcript):
        """
        Handle the response from the transcription and generate a completion.

        Args:
            transcript (str): The transcribed text from the audio recording.
        """
        try:
            # Refresh system prompt. For system prompts that contain variables like date and time
            if len(self.messages) > 0 and self.messages[0]["role"] == "system":
                self.messages[0]["content"] = prompt.get_system_prompt_message(config.ACTIVE_PROMPT)

            # If the user has cut off the assistant's last message, add a message to indicate this
            if self.last_message_was_cut_off:
                transcript = "--> USER CUT THE ASSISTANTS LAST MESSAGE SHORT <--\n" + transcript

            # If the user wants to use the clipboard text, append it to the message
            if self.clipboard_text and self.clipboard_text != self.last_clipboard_text:
                self.messages.append({"role": "user", "content": transcript + f"\n\nTHIS IS THE USERS CLIPBOARD CONTENT (ignore if user doesn't mention it):\n```{self.clipboard_text}```"})
                self.last_clipboard_text = self.clipboard_text
                self.clipboard_text = None
            else:
                self.messages.append({"role": "user", "content": transcript})

            if config.TIMESTAMP_MESSAGES:
                #add timestamp to end of message on new line
                self.messages[-1]["content"] += f"\n\nMESSAGE TIMESTAMP:{time.strftime('%I:%M %p')} {time.strftime('%Y-%m-%d (%A)')} "
            print("\nTranscription:\n", transcript)

            # Make sure the user hasn't cut off the response
            if self.stop_response:
                return

            #Get the completion stream
            stream = self.completion_client.get_completion(self.messages, model=config.COMPLETION_MODEL)
            
            response = self.handle_response_stream(stream, run_tts=True)
                
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

            print("\nResponse:\n", response)

        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred while handling the response: {e}")

    def toggle_recording(self):
        """Handle the hotkey press for starting or stopping recording."""
        if self.recorder.recording:
            self.stop_response = False
            self.stop_recording()
        else:
            # If the user has set the config to always include the clipboard text, save it now
            if config.ALWAYS_INCLUDE_CLIPBOARD:# TODO: This should not live in the toggle_recording method
                self.save_clipboard_text()
            self.start_recording()

    def start_main_thread(self):
        """This starts the main thread and keeps a reference to it."""
        if self.main_thread is not None and self.main_thread.is_alive():
            # If the thread is already running, cancel (without playing cancel sound) and start a new one
            self.cancel_all(silent=True)  # the silence is just so you dont hear cancel sound immediately followed by the start sound
            self.main_thread.join()

        self.main_thread = threading.Thread(target=self.toggle_recording)
        self.main_thread.start()

    def save_clipboard_text(self):
        print("Saving clipboard text...")
        self.clipboard_text = read_clipboard()

    def run(self):
        """Run the recorder, setting up hotkeys and entering the main loop."""
        input_handler = get_input_handler(verbose=self.verbose)
        input_handler.double_tap_threshold = config.DOUBLE_TAP_THRESHOLD

        print()
        if config.RECORD_HOTKEY:
            input_handler.add_hotkey(config.RECORD_HOTKEY, pressed=self.start_main_thread,held_release=self.start_main_thread, double_tap=self.save_clipboard_text)
            print(f"Press '{config.RECORD_HOTKEY}' to start recording, press again to stop and transcribe."
                  f"\n\tAlternatively hold it down to record until you release.")

            if "+" in config.RECORD_HOTKEY:
                hotkey_start, hotkey_end = config.RECORD_HOTKEY.rsplit("+", 1)
                print(f"\tHold down '{hotkey_start}' and double tap '{hotkey_end}' to give AlwaysReddy the content currently copied in your clipboard.")
            else:
                print(f"\tDouble tap '{config.RECORD_HOTKEY}' to give AlwaysReddy the content currently copied in your clipboard.")

        if config.CANCEL_HOTKEY:
            input_handler.add_hotkey(config.CANCEL_HOTKEY, pressed=self.cancel_all)
            print(f"Press '{config.CANCEL_HOTKEY}' to cancel recording.")

        if config.CLEAR_HISTORY_HOTKEY:
            input_handler.add_hotkey(config.CLEAR_HISTORY_HOTKEY,pressed=self.new_chat)
            print(f"Press '{config.CLEAR_HISTORY_HOTKEY}' to start a new")

        input_handler.start(blocking=True)

if __name__ == "__main__":
    try:
        AlwaysReddy().run()
    except Exception as e:
        if config.VERBOSE:
            import traceback
            traceback.print_exc()
        else:
            print(f"Failed to start the recorder: {e}")