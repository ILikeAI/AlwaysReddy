import time
import threading
from audio_recorder import AudioRecorder
from transcriber import transcribe_audio
import keyboard
import TTS
from chat_completions import CompletionManager
from soundfx import play_sound_FX
from utils import read_clipboard, count_tokens, trim_messages
import config
from prompt import prompts

class Recorder:
    def __init__(self):
        """Initialize the Recorder with default settings and objects."""
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.clipboard_text = None
        self.messages = prompts[config.ACTIVE_PROMPT]["messages"].copy()
        self.last_press_time = 0
        self.tts = TTS.TTS(parent_client=self) 
        self.recording_timeout_timer = None
        self.completion_client = CompletionManager(TTS_client=self.tts,parent_client=self)
        self.tts.completion_client = self.completion_client
        self.recording_stop_time = None
        self.timer = None
        self.main_thread = None
        self.stop_response = False

    def clear_messages(self):
        """Clear the message history."""
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
        print("Starting recording...")
        self.is_recording = True
        self.recorder.start_recording()

        play_sound_FX("start", volume=config.START_SOUND_VOLUME)
        time.sleep(config.HOTKEY_DELAY)
 
        self.recording_timeout_timer = threading.Timer(config.MAX_RECORDING_DURATION, self.stop_recording)
        self.recording_timeout_timer.start()

    def stop_recording(self):
        """Stop the audio recording process and handle the recorded audio."""
        print("Stopping recording...")

        if self.recording_timeout_timer and self.recording_timeout_timer.is_alive():
            self.recording_timeout_timer.cancel()
            
        if self.is_recording:
            play_sound_FX("end", volume=config.END_SOUND_VOLUME)
            self.is_recording = False  
            self.recorder.stop_recording()
            self.recording_stop_time = time.time()

            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                print("Recording is too short or file does not exist, ignoring...")
                return
            
            try:
                transcript = transcribe_audio(self.recorder.filename)
                self.handle_response(transcript)

            except Exception as e:
                print(f"An error occurred during transcription: {e}")
            finally:
                time.sleep(config.HOTKEY_DELAY)

    def how_long_to_speak_first_word(self, first_word_time):
        """
        Calculate and print the delay between the end of recording and the first word spoken by TTS.

        Args:
            first_word_time (float): The timestamp of the first word spoken by TTS.
        """
        if self.recording_stop_time:
            print(f"Response delay for first word: {first_word_time - self.recording_stop_time} seconds")
            self.recording_stop_time = None

    def cancel_recording(self):
        """Cancel the current recording """
        if self.is_recording:
            print("Cancelling recording...")
            self.recorder.stop_recording(cancel=True)
            print("Recording cancelled.")
            self.is_recording = False

    def cancel_tts(self):
        """Cancel the current TTS """

        print("Stopping text-to-speech...")
        self.tts.stop()
        print("Text-to-speech cancelled.")

    def cancel_all(self):
        """Cancel the current recording and TTS """
        if self.main_thread is not None and self.main_thread.is_alive():
            play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME) 
            self.stop_response = True
            self.cancel_tts()

        elif self.is_recording:
            play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME) 
            self.cancel_recording()

    


    def handle_response(self, transcript):
        """
        Handle the response from the transcription and generate a completion.

        Args:
            transcript (str): The transcribed text from the audio recording.
        """
        try:
            
            if self.clipboard_text:
                self.messages.append({"role": "user", "content": transcript+f"\n\nTHE USER HAS THIS TEXT COPIED TO THEIR CLIPBOARD:\n```{self.clipboard_text}```"})
                self.clipboard_text = None
            else:
                self.messages.append({"role": "user", "content": transcript})

            if count_tokens(self.messages) > config.MAX_TOKENS:
                self.messages = trim_messages(self.messages, config.MAX_TOKENS)

            print("Transcription:\n", transcript)
            if self.stop_response:
                self.messages = self.messages[:-1]
                return
            
            response = self.completion_client.get_completion(self.messages,model=config.COMPLETION_MODEL)

            if not response:
                print("No response generated.")
                self.messages = self.messages[:-1]
                return

            if self.stop_response:
                # If the assistant was cut off while speaking, find the last sentence spoken and cut off the response there
                index = response.rfind(self.tts.last_sentence_spoken)

                # If the last sentence spoken was found, cut off the response there
                if index != -1:
                    # Add a message to indicate the user cut off the response
                    response = response[:index + len(self.tts.last_sentence_spoken)] + "--> USER CUT OFF RESPONSE <--"
                
            
            self.messages.append({"role": "assistant", "content": response})
            print("Response:\n", response)

        except Exception as e:
            print(f"An error occurred while handling the response: {e}")

    def handle_hotkey(self):
        """Handle the hotkey press for starting or stopping recording."""
        #reset flags
        self.stop_response = False

        if self.tts.running_tts:
            print("TTS is running, stopping...")
            self.tts.stop()

        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()


    def start_main_thread(self):
        """This starts the main thread and keeps a refrence to it"""
        self.timer = None
        if self.main_thread is not None and self.main_thread.is_alive():
            self.cancel_all()
            self.main_thread.join()
        else:
            self.main_thread = threading.Thread(target=self.handle_hotkey)
            self.main_thread.start()

        

    def handle_hotkey_wrapper(self):
        """
        Wrapper for the hotkey handler to include double tap detection for clipboard usage.
        """

        use_clipboard = self.was_double_tapped()
        print("use_clipboard:", use_clipboard)
        if use_clipboard:
            try:
                self.clipboard_text = read_clipboard()
            except Exception as e:
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
        keyboard.add_hotkey(config.RECORD_HOTKEY, self.handle_hotkey_wrapper)
        keyboard.add_hotkey(config.CANCEL_HOTKEY, self.cancel_all)
        keyboard.add_hotkey(config.CLEAR_HISTORY_HOTKEY, self.clear_messages)
        print(f"Press '{config.RECORD_HOTKEY}' to start recording, press again to stop and transcribe.\nDouble tap to give the AI access to read your clipboard.\nPress '{config.CANCEL_HOTKEY}' to cancel recording.\nPress '{config.CLEAR_HISTORY_HOTKEY}' to clear the chat history.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Recorder stopped by user.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        Recorder().run()
    except Exception as e:
        print(f"Failed to start the recorder: {e}")
