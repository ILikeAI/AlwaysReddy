import time
import threading
from audio_recorder import AudioRecorder
from transcriber import transcribe_audio
import keyboard
import sound
from chat_completions import ChatCompletion

from utils import read_clipboard, count_tokens, trim_messages
import config
from prompt import default_messages

class Recorder:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.clipboard_text = None
        self.messages = default_messages.copy()
        self.last_press_time = 0
        self.tts = sound.TTS(parent_client=self) 
        self.recording_timeout_timer = None
        self.waiting_for_tts = False
        self.completion_client = ChatCompletion(parent_client=self, TTS_client=self.tts)
        self.tts.completion_client = self.completion_client
        self.recording_stop_time = None


    def clear_messages(self):
        print("Clearing messages...")
        self.messages = default_messages.copy()

    # Check if the hotkey was double tapped
    def was_double_tapped(self, threshold=0.2):
        current_time = time.time()
        double_tapped = current_time - self.last_press_time < threshold
        self.last_press_time = current_time
        return double_tapped


    def start_recording(self):
        print("Starting recording...")
        self.is_recording = True
        self.recorder.start_recording()


        sound.play_sound_FX("start", volume=config.START_SOUND_VOLUME)
        time.sleep(config.HOTKEY_DELAY)
 
        # To stop us from recording for ages in the background without the user knowing, we set a timer to stop the recording after a certain amount of time
        self.recording_timeout_timer = threading.Timer(config.MAX_RECORDING_DURATION, self.stop_recording)
        self.recording_timeout_timer.start()

    def stop_recording(self):
        print("Stopping recording...")

        # Cancel the timer if it's still running
        if self.recording_timeout_timer and self.recording_timeout_timer.is_alive():
            self.recording_timeout_timer.cancel()
        
        if self.is_recording:
            sound.play_sound_FX("end", volume=config.END_SOUND_VOLUME)
            self.is_recording = False  
            self.waiting_for_tts = True
            self.recorder.stop_recording()
            self.recording_stop_time = time.time()#Just so we can track time between now and when the TTS starts

            #if recording is too short, ignore it
            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                print("Recording is too short, ignoring...")
                self.waiting_for_tts = False
                return
            
            
            transcript = transcribe_audio(self.recorder.filename)
            self.handle_response(transcript)
            time.sleep(config.HOTKEY_DELAY)


    def how_long_to_speak_first_word(self,first_word_time):
        """This is mostly for testing, it prints how long it has taken between the recording the users voice and the first word of the response being played"""
        if self.recording_stop_time:
            print(f"Response delay for first word: {self.recording_stop_time-first_word_time} seconds")
            self.recording_stop_time=None

    def cancel_recording(self):
        # If we're already recording, stop the recording and return
        if self.is_recording:
            print("Cancelling recording...")
            sound.play_sound_FX("cancel", volume=config.CANCEL_SOUND_VOLUME)  
            self.recorder.stop_recording(cancel=True)
            print("Recording cancelled.")
            self.is_recording = False

        # Stop the text-to-speech if it's running
        if self.tts.running_tts:
            print("Stopping text-to-speech...")
            self.tts.stop()
            print("Text-to-speech cancelled.")

    def handle_response(self, transcript):
        
        if self.clipboard_text:
            self.messages.append({"role": "user", "content":f"\n\nTHE USER HAS THIS TEXT COPIED TO THEIR CLIPBOARD:\n```{self.clipboard_text}```"})

            self.messages.append({"role": "user", "content": transcript})
            self.clipboard_text = None
        else:
            self.messages.append({"role": "user", "content": transcript})
        if count_tokens(self.messages) > config.MAX_TOKENS:
            self.messages = trim_messages(self.messages, config.MAX_TOKENS)
        print("Transcription:\n", transcript)
        response = self.completion_client.get_completion(self.messages)

        self.messages.append({"role": "assistant", "content": response})
        print("Response:\n", response)

    def handle_hotkey(self):
        if self.waiting_for_tts:
            # If we're waiting for the TTS to finish, don't start a new recording
            return
        
        if self.tts.running_tts:
            print("TTS is running, stopping...")
            # If the TTS is still running, cut it off and start a new recording
            self.tts.stop()

        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def run(self):
        self.timer = None

        def handle_hotkey_wrapper():
            # If the hotkey is pressed again within 0.2 seconds, we'll use the clipboard
            # This just checks if the hotkey was double tapped
            use_clipboard = self.was_double_tapped()
            print("use_clipboard:",use_clipboard)
            if use_clipboard:
                self.clipboard_text = read_clipboard()
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
                self.handle_hotkey()
                

            else:
                self.timer = threading.Timer(0.2, self.handle_hotkey)
                self.timer.start()


        keyboard.add_hotkey(config.RECORD_HOTKEY, handle_hotkey_wrapper)
        keyboard.add_hotkey(config.CANCEL_HOTKEY, self.cancel_recording)
        keyboard.add_hotkey(config.CLEAR_HISTORY_HOTKEY, self.clear_messages)
        print(f"Press '{config.RECORD_HOTKEY}' to start recording, press again to stop and transcribe.\nDouble tap to give the AI access to read your clipboard.\nPress '{config.CANCEL_HOTKEY}' to cancel recording.\nPress '{config.CLEAR_HISTORY_HOTKEY}' to clear the chat history.")

        while True:
            time.sleep(1)

if __name__ == "__main__":
    Recorder().run()