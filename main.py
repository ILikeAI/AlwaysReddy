import time
import threading
from audio_recorder import AudioRecorder
from transcriber import transcribe_audio
import keyboard
import sound
import chat_completions 
from utils import read_clipboard, to_clipboard, extract_text_between_symbols, count_tokens, trim_messages
import config
from prompt import default_messages

class Recorder:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.is_busy = False
        self.is_recording = False
        self.clipboard_text = None
        self.messages = default_messages.copy()
        self.last_press_time = 0

    def clear_messages(self):
        print("Clearing messages...")
        if self.is_busy or self.is_recording:
            print("Cannot clear messages while recording or busy.")
            return
        self.messages = default_messages.copy()

    def was_double_tapped(self, threshold=0.2):
        current_time = time.time()
        double_tapped = current_time - self.last_press_time < threshold
        self.last_press_time = current_time
        return double_tapped

    def start_recording(self, use_clipboard=False):
        if self.is_busy:
            return

        print(f"USE CLIPBOARD: {use_clipboard}")
        self.timer = None
        if self.is_recording:
            self.stop_recording(use_clipboard)
            return

        self.is_recording = True
        if use_clipboard:
            self.clipboard_text = read_clipboard()
            print("Copied to from clip:"+self.clipboard_text)
        self.recorder.start_recording()
        sound.play_sound("start", volume=config.START_SOUND_VOLUME)
        time.sleep(config.HOTKEY_DELAY)
    

    def stop_recording(self, use_clipboard=False):
        if self.is_recording:
            self.is_busy = True
            sound.play_sound("end", volume=config.END_SOUND_VOLUME)  
            self.recorder.stop_recording()
            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                print("Recording is too short, ignoring...")
                self.is_recording = False
                return
            transcript = transcribe_audio(self.recorder.filename)
            if use_clipboard:
                self.clipboard_text = read_clipboard()
                print("Copied to from clip:"+self.clipboard_text)

            self.handle_transcript(transcript)
            time.sleep(config.HOTKEY_DELAY)
            self.is_recording = False
            self.is_busy = False

    def cancel_recording(self):
        print("cancel recording")
        if self.is_busy:
            sound.play_sound("cancel", volume=config.CANCEL_SOUND_VOLUME)  
            self.recorder.stop_recording(cancel=True)
            print("Recording cancelled.")
            self.is_busy = False

    def handle_transcript(self, transcript):
        if self.clipboard_text:
            self.messages.append({"role": "user", "content": transcript+f"\n\nTHE USER HAS THIS TEXT COPIED TO THEIR CLIPBOARD:\n```{self.clipboard_text}```"})
            self.clipboard_text = None
        else:
            self.messages.append({"role": "user", "content": transcript})
        if count_tokens(self.messages) > config.MAX_TOKENS:
            self.messages = trim_messages(self.messages, config.MAX_TOKENS)
        print("Transcription:\n", transcript)
        self.handle_response(chat_completions.get_completion(self.messages, together=config.USE_TOGETHER_API))

    def handle_response(self, response):
        self.messages.append({"role": "assistant", "content": response})
        print("Response:\n", response)
        text, remaining_text = extract_text_between_symbols(response)
        if text:
            to_clipboard(text)
            print("Text copied to clipboard:", text)
        sound.TTS(remaining_text, voice=config.VOICE)

    def run(self):
        self.timer = None

        def start_recording_wrapper():
            use_clipboard = self.was_double_tapped()
            if self.timer is not None:
                self.timer.cancel()
                self.start_recording(use_clipboard=use_clipboard)
            else:
                self.timer = threading.Timer(0.2, self.start_recording, args=[use_clipboard])
                self.timer.start()

        keyboard.add_hotkey(config.RECORD_HOTKEY, start_recording_wrapper)
        keyboard.add_hotkey(config.CANCEL_HOTKEY, self.cancel_recording)
        keyboard.add_hotkey(config.CLEAR_HISTORY_HOTKEY, self.clear_messages)
        print(f"Press '{config.RECORD_HOTKEY}' to start recording, press again to stop and transcribe.\nDouble tap to give the AI access to your clipboard.\nPress '{config.CANCEL_HOTKEY}' to cancel recording.\nPress '{config.CLEAR_HISTORY_HOTKEY}' to clear the chat history.")

        while True:
            time.sleep(1)

if __name__ == "__main__":
    Recorder().run()