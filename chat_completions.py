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
    def __init__(self,parent_client, TTS_client):
        self.parent_client = parent_client
        self.TTS_client = TTS_client
        self.full_response = ""
        self.cancel = False
        if completions_api == "openai":
            self.client = OpenAI(api_key=openai_api_key)
        elif completions_api == "together":
            self.client = OpenAI(
                api_key=os.getenv('TOGETHER_API_KEY'),
                base_url="https://api.together.xyz/v1",
            )
        else:
            raise ValueError("Invalid COMPLETIONS_API value")



    def get_completion(self, messages, together=False, together_model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT", max_tokens=2048):
        """This function streams in the response from a completions API, splits it into sentences and streams the sentences to the TTS client."""
        main_response = ""
        between_symbols = ""
        self.full_response = ""
        
        buffer = ""
        in_start = False
        start_seq = config.START_SEQ
        end_seq = config.END_SEQ

        if together:
            stream = self.client.chat.completions.create(
                model=together_model,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens,
                stream=True
            )
        else:
            stream = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                max_tokens=max_tokens,
                stream=True
                )
            
        self.cancel = False
        self.TTS_client.text_incoming = True
        self.TTS_client.last_played_sentence = ""
        for chunk in stream:
            if self.cancel == True:
                break

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
                    buffer = ""

                if not in_start and any(x in buffer for x in ["!", ". ", "?", "\n"]):
                    # Find the first occurrence of any of the symbols in the buffer
                    split_index = min([buffer.find(x) for x in ["!", ". ", "?", "\n"] if x in buffer])
                    # Split the buffer at the first occurrence of any of these symbols
                    main_response += buffer[:split_index+1]
                    buffer = buffer[split_index+1:]

                    self.TTS_client.run_tts(main_response)

                    main_response = ""


        if self.cancel:            
            print("Cancelling completion...")
            if self.TTS_client.last_played_sentence:
                #The aim of this is to identify what the assisant has spoken aloud so far and only add that to the message thread
                if self.TTS_client.last_played_sentence in self.full_response:
                    # Find the end of the last played sentence in the full response
                    end_index = self.full_response.find(self.TTS_client.last_played_sentence) + len(self.TTS_client.last_played_sentence)
                    # Slice the full response up to and including the last played sentence
                    self.full_response = self.full_response[:end_index]
                else:
                    print(f"Last played sentence not in full response: {self.TTS_client.last_played_sentence}")
                    print(f"Full response: {self.full_response}")
            self.TTS_client.last_played_sentence = ""
            self.cancel = False
            return self.full_response
        
        #If there is still text in the buffer, add it to the main response
        if buffer:
            main_response += buffer

        if main_response and not self.parent_client.is_recording:
            self.TTS_client.run_tts(main_response)

        self.TTS_client.text_incoming = False
        return self.full_response

