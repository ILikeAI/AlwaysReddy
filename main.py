import time
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
        self.clipboard_text = None
        self.messages = default_messages.copy()

    def start_recording(self, use_clipboard=False):
        if not self.is_busy:
            self.is_busy = True
            if use_clipboard:
                self.clipboard_text = read_clipboard()
                print("Copied to from clip:"+self.clipboard_text)
            self.recorder.start_recording()
            sound.play_sound("start", volume=config.START_SOUND_VOLUME)
            time.sleep(config.HOTKEY_DELAY)

    def stop_recording(self):
        if self.is_busy:
            sound.play_sound("end", volume=config.END_SOUND_VOLUME)  
            self.recorder.stop_recording()
            if self.recorder.duration < config.MIN_RECORDING_DURATION:
                print("Recording is too short, ignoring...")
                self.is_busy = False
                return
            transcript = transcribe_audio(self.recorder.filename)
            self.handle_transcript(transcript)
            self.is_busy = False
            time.sleep(config.HOTKEY_DELAY)

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
        keyboard.add_hotkey(config.DEFAULT_HOTKEY, lambda: self.start_recording(use_clipboard=False) if not self.is_busy else self.stop_recording(), suppress=True)
        keyboard.add_hotkey(config.DEFAULT_CLIP_HOTKEY, lambda: self.start_recording(use_clipboard=True) if not self.is_busy else self.stop_recording(), suppress=True)
        keyboard.add_hotkey(config.CANCEL_HOTKEY, lambda: self.start_recording(use_clipboard=True) if not self.is_busy else self.stop_recording(), suppress=True)
        print("Press 'Ctrl + Spacebar' to start recording, press again to stop and transcribe")
        keyboard.wait('esc')

if __name__ == "__main__":
    Recorder().run()