from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import config
from utils import to_clipboard

# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

completions_api = config.COMPLETIONS_API

class ChatCompletion:
    def __init__(self, parent_client, TTS_client):
        """
        Initializes the ChatCompletion class with the parent client and TTS client.
        
        Args:
            parent_client: The client that is using this ChatCompletion instance.
            TTS_client: The Text-to-Speech client to stream responses to.
        
        Raises:
            ValueError: If the COMPLETIONS_API value is invalid.
        """
        self.parent_client = parent_client
        self.TTS_client = TTS_client
        self.full_response = ""
        if completions_api == "openai":
            self.client = OpenAI(api_key=openai_api_key)
            self.model = config.OPENAI_MODEL
        elif completions_api == "together":
            self.client = OpenAI(
                api_key=os.getenv('TOGETHER_API_KEY'),
                base_url="https://api.together.xyz/v1",
            )
            self.model = config.TOGETHER_MODEL
        else:
            raise ValueError("Invalid COMPLETIONS_API value")

    def get_completion(self, messages, max_tokens=2048):
        """
        Retrieves a completion from the configured API and streams it to the TTS client.
        
        Args:
            messages: A list of message objects to send to the completions API.
            max_tokens: The maximum number of tokens to generate.
        
        Returns:
            The full response from the completions API as a string.
        
        Raises:
            RuntimeError: If an error occurs during the streaming of completions.
        """
        main_response = ""
        between_symbols = ""
        self.full_response = ""
        
        buffer = ""
        in_start = False
        start_seq = config.START_SEQ
        end_seq = config.END_SEQ
        retries = 2

        while retries > 0:
            try:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=max_tokens,
                    stream=True
                )

                for chunk in stream:
                    if self.parent_client.is_recording:
                        return self.full_response
                    
                    content = chunk.choices[0].delta.content

                    if content is not None:
                        self.full_response += content
                        buffer += content

                        if not in_start and start_seq in buffer:
                            buffer = buffer[buffer.find(start_seq) + len(start_seq):]
                            in_start = True

                        if in_start and end_seq in buffer:
                            between_symbols += buffer[:buffer.find(end_seq)]
                            buffer = buffer[buffer.find(end_seq) + len(end_seq):]
                            in_start = False
                            to_clipboard(between_symbols)
                            between_symbols = ""
                            buffer = ""

                        if not in_start and any(x in buffer for x in ["!", ". ", "?", "\n"]):
                            # Find the first occurrence of any of the symbols in the buffer
                            split_index = min([buffer.find(x) for x in ["!", ". ", "?", "\n"] if x in buffer])
                            # Split the buffer at the first occurrence of any of these symbols
                            main_response += buffer[:split_index+1]
                            buffer = buffer[split_index+1:]

                            self.TTS_client.run_tts(main_response)
                            main_response = ""

                # If there is still text in the buffer, add it to the main response
                if buffer:
                    main_response += buffer

                if main_response and not self.parent_client.is_recording:
                    self.TTS_client.run_tts(main_response)

                # Set waiting for TTS to false this should be done in the TTS class but sometimes the completion does not have any text to pass to TTS
                # meaning that flag is never set back to false.

                break  # Break out of the retry loop on success

            except Exception as e:
                retries -= 1
                if retries == 0:
                    raise RuntimeError(f"An error occurred during the streaming of completions: {e}")
                else:
                    print(f"An error occurred getting completions, retrying... ({retries} retries left)")
                    time.sleep(1)

        return self.full_response
