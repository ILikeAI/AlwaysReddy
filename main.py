import time
from audio_recorder import AudioRecorder
from transcriber import transcribe_audio
import keyboard
import sound
import chat_completions 
from utils import read_clipboard, to_clipboard, extract_text_between_symbols
from config import START_SOUND_VOLUME, END_SOUND_VOLUME, MIN_RECORDING_DURATION, HOTKEY_DELAY, USE_TOGETHER_API,VOICE
from prompt import messages


def main():

    
    recorder = AudioRecorder() 
    is_busy = False  
    clipboard_text = None 


    # Function to start recording
    def start_recording(use_clipboard=False):
        if not (keyboard.is_pressed('ctrl') and keyboard.is_pressed('space')):
            return
        nonlocal is_busy, clipboard_text
        if is_busy:  
            return
        is_busy = True  
        if use_clipboard:
            clipboard_text = read_clipboard()  # Read from clipboard
            print("Copied to from clip:"+clipboard_text)
        recorder.start_recording() 
        sound.play_sound("start", volume=START_SOUND_VOLUME)  
        time.sleep(HOTKEY_DELAY) 




    # Function to stop recording
    def stop_recording():
        if not (keyboard.is_pressed('ctrl') and keyboard.is_pressed('space')):
            return
        nonlocal is_busy, clipboard_text 

        #if not busy, return
        if not is_busy:  
            return
        recorder.stop_recording() 
        sound.play_sound("end", volume=END_SOUND_VOLUME)


        # Check if the recording is less than the minimum duration
        if recorder.duration < MIN_RECORDING_DURATION:
            print("Recording is too short, ignoring...")
            is_busy = False  # Reset the flag
            return
        
        # Transcribe the audio
        transcript = transcribe_audio(recorder.filename)  


        #prepare the messages 
        #if clipboard_text clipboard hotkey was used, add the clipboard text to the transcript
        if clipboard_text:
            messages.append({"role": "user", "content": transcript+f"\n\nTHE USER HAS THIS TEXT COPPIED:\n{clipboard_text}"})
            clipboard_text = None  
        else:
            messages.append({"role": "user", "content": transcript})

        print("Transcription:\n", transcript)
        

        # Get the response from the chat completions
        response = chat_completions.get_completion(messages,together=USE_TOGETHER_API)  # Get the response from the chat completions
        messages.append({"role": "assistant", "content": response})  # Add the response to the messages
        print("Response:\n", response)

        #check if there is text to be copied to the clipboard, and if so, copy it
        text, remaining_text = extract_text_between_symbols(response)
        if text:
            to_clipboard(text)  # Copy the text to clipboard
            print("Text copied to clipboard:", text)


        #play the TTS
        sound.TTS(remaining_text,voice=VOICE)  # Text to speech for the remaining text
        is_busy = False 
        time.sleep(HOTKEY_DELAY) 


    keyboard.add_hotkey('ctrl + space', lambda: start_recording(use_clipboard=False) if not is_busy else stop_recording())
    keyboard.add_hotkey('ctrl + shift + space', lambda: start_recording(use_clipboard=True) if not is_busy else stop_recording(), suppress=True)
    print("Press 'Ctrl + Spacebar' to start recording, press again to stop and transcribe")
    keyboard.wait('esc')  # Wait for 'esc' key to exit

if __name__ == "__main__":
    main() 