import time
import traceback
from typing import Optional

from config_loader import config
from actions.base_action import BaseAction
from utils.utils import (
    to_clipboard,
    handle_clipboard_image,
    handle_clipboard_text,
    add_timestamp_to_message,
)
from completion_manager import CompletionManager
import utils.utils as utils
from utils.chat import Chat


class AlwaysReddyVoiceAssistant(BaseAction):
    """
    Action for handling voice assistant functionality.

    This class sets up hotkeys for voice recording and chat management, handles the
    transcription of recorded audio, manages clipboard content, and communicates with
    a chat manager to generate responses from an LLM.
    """

    def setup(self) -> None:
        """
        Set up the voice assistant by registering hotkeys and initializing the Chat instance.
        """
        self.last_message_was_cut_off = False

        # Setup recording hotkey if configured
        if config.RECORD_HOTKEY:
            self.AR.add_action_hotkey(
                config.RECORD_HOTKEY,
                pressed=self.handle_default_assistant_response,
                held_release=self.handle_default_assistant_response,
                double_tap=self.AR.save_clipboard_text,
            )
            print(
                f"'{config.RECORD_HOTKEY}': Start/stop talking to voice assistant (press to toggle on and off, or hold and release)"
            )

            if "+" in config.RECORD_HOTKEY:
                hotkey_start, hotkey_end = config.RECORD_HOTKEY.rsplit("+", 1)
                print(
                    f"\tHold down '{hotkey_start}' and double tap '{hotkey_end}' to send clipboard content to AlwaysReddy"
                )
            else:
                print(f"\tDouble tap '{config.RECORD_HOTKEY}' to send clipboard content to AlwaysReddy")

        # Setup new chat hotkey if configured
        if config.NEW_CHAT_HOTKEY:
            self.AR.add_action_hotkey(config.NEW_CHAT_HOTKEY, pressed=self.new_chat)
            print(f"'{config.NEW_CHAT_HOTKEY}': New chat for voice assistant")

        # Initialize Chat with the configured parameters and completion manager
        self.chat = Chat(
            completions_api_client=CompletionManager(
                verbose=config.VERBOSE, completions_api=config.COMPLETIONS_API
            ),
            completion_params=config.COMPLETION_PARAMS,
            model=config.COMPLETION_MODEL,
            max_prompt_tokens=config.MAX_PROMPT_TOKENS,
            tts_callback=self.AR.tts.run_tts,
            system_prompt_filename=config.ACTIVE_PROMPT
        )

    def handle_default_assistant_response(self) -> None:
        """
        Handle the process of recording, transcribing, and generating a response from the voice assistant.

        This method toggles recording, transcribes the audio if available, processes any clipboard content
        (images or text), adds a timestamp if configured, and then generates a completion using the Chat instance.
        It also handles the situation where the assistant's last message was cut off.
        """
        try:
            recording_filename = self.AR.toggle_recording(self.handle_default_assistant_response)
            if not recording_filename:
                return

            # Transcribe the recorded audio file
            message = self.AR.transcription_manager.transcribe_audio(recording_filename)
            if not self.AR.stop_action and message:
                print("\nTranscript:\n", message)

                # Flag if the user cut off the assistant's previous message
                if self.last_message_was_cut_off:
                    message = "--> USER CUT THE ASSISTANT'S LAST MESSAGE SHORT <--\n" + message

                # Process clipboard image if available; otherwise, process clipboard text
                clipboard_image_content = handle_clipboard_image(self.AR, message)
                if clipboard_image_content:
                    message = clipboard_image_content
                else:
                    message = handle_clipboard_text(self.AR, message)

                # Optionally add a timestamp to the message
                if config.TIMESTAMP_MESSAGES:
                    message = add_timestamp_to_message(message)

                # Append the user's message to the chat history
                self.chat.add_message("user", message)

                # If the action was stopped during processing, exit early
                if self.AR.stop_action:
                    return

                # Generate a completion response from the chat manager
                response = self.chat.get_completion(marker_tuples=[(config.CLIPBOARD_TEXT_START_SEQ, config.CLIPBOARD_TEXT_END_SEQ, to_clipboard)],)
                # Text found between the start and end markers is passed to the callback function

                # Wait until any running text-to-speech (TTS) has finished
                while self.AR.tts.running_tts:
                    time.sleep(0.001)

                # If no response was generated, remove the last user message to avoid consecutive user messages
                if not response:
                    if self.AR.verbose:
                        print("No response generated.")
                    self.chat.messages = self.chat.messages[:-1]
                    return

                self.last_message_was_cut_off = False

                # Check if the action was stopped and adjust the response accordingly
                if self.AR.stop_action:
                    index = response.rfind(self.AR.tts.last_sentence_spoken)
                    if index != -1:
                        response = response[: index + len(self.AR.tts.last_sentence_spoken)]
                        self.last_message_was_cut_off = True

                # Add the assistant's response to the chat history and print it
                self.chat.add_message("assistant", response)
                print("\nResponse:\n", response)

        except Exception as e:
            print(f"An error occurred in handle_default_assistant_response: {e}")
            if self.AR.verbose:
                traceback.print_exc()

    def new_chat(self) -> None:
        self.chat.clear_chat()
        self.last_message_was_cut_off = False
        self.AR.last_clipboard_text = None
        print("New chat session started.")
