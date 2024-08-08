import time
from config_loader import config
import prompt
from actions.base_action import BaseAction

class AlwaysReddyVoiceAssistant(BaseAction):
    """Action for handling voice assistant functionality."""

    def handle_default_assistant_response(self):
        """Handle the response from the transcription and generate a completion."""
        try:
            recording_filename = self.AR.toggle_recording(self.handle_default_assistant_response)
            if not recording_filename:
                return
            message = self.AR.transcription_manager.transcribe_audio(recording_filename)

            if not self.AR.stop_action and message:
                print("\nTranscript:\n", message)
                
                if len(self.AR.messages) > 0 and self.AR.messages[0]["role"] == "system":
                    self.AR.messages[0]["content"] = prompt.get_system_prompt_message(config.ACTIVE_PROMPT)

                if self.AR.last_message_was_cut_off:
                    message = "--> USER CUT THE ASSISTANTS LAST MESSAGE SHORT <--\n" + message

                if self.AR.clipboard_text and self.AR.clipboard_text != self.AR.last_clipboard_text:
                    message += f"\n\nTHIS IS THE USERS CLIPBOARD CONTENT (ignore if user doesn't mention it):\n```{self.AR.clipboard_text}```"
                    self.AR.last_clipboard_text = self.AR.clipboard_text
                    self.AR.clipboard_text = None
                
                if config.TIMESTAMP_MESSAGES:
                    message += f"\n\nMESSAGE TIMESTAMP:{time.strftime('%I:%M %p')} {time.strftime('%Y-%m-%d (%A)')} "

                self.AR.messages.append({"role": "user", "content": message})

                if self.AR.stop_action:
                    return

                stream = self.AR.completion_client.get_completion(self.AR.messages, model=config.COMPLETION_MODEL)
                response = self.AR.handle_response_stream(stream, run_tts=True)
                    
                while self.AR.tts.running_tts:
                    time.sleep(0.001)

                if not response:
                    if self.AR.verbose:
                        print("No response generated.")
                    self.AR.messages = self.AR.messages[:-1]
                    return

                self.AR.last_message_was_cut_off = False

                if self.AR.stop_action:
                    index = response.rfind(self.AR.tts.last_sentence_spoken)
                    if index != -1:
                        response = response[:index + len(self.AR.tts.last_sentence_spoken)]
                        self.AR.last_message_was_cut_off = True

                self.AR.messages.append({"role": "assistant", "content": response})
                print("\nResponse:\n", response)

        except Exception as e:
            if self.AR.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred while handling the response: {e}")


    def new_chat(self):
        """Clear the message history and start a new chat session."""
        print("Clearing messages and starting a new chat...")
        self.AR.messages = prompt.build_initial_messages(config.ACTIVE_PROMPT)
        self.AR.last_message_was_cut_off = False
        self.AR.last_clipboard_text = None
        print("New chat session started.")