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

def get_completion(messages, TTS_func, together=False, together_model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT", max_tokens=2048):
    
    main_response = ""
    between_symbols = ""
    full_response = ""
    buffer = ""
    in_start = False
    start_seq = config.START_SEQ
    end_seq = config.END_SEQ

    if together:
        client = OpenAI(
             api_key=os.getenv('TOGETHER_API_KEY'),
            base_url="https://api.together.xyz/v1",
        )
        stream = client.chat.completions.create(
            model=together_model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
            stream=True
        )
    else:
        client = OpenAI()
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            max_tokens=max_tokens,
            stream=True
            )
        
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
            full_response += content
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

            if not in_start and any(x in buffer for x in ["!", ".", "?", "\n"]):
                main_response += buffer
                
                TTS_func(main_response)
                buffer = ""
                main_response = ""

    # Check if there's any remaining content in the buffer
    if buffer:
        main_response += buffer

    if main_response:
        TTS_func(main_response)

    return full_response


def main():
    messages = [
        {
            "role": "user",
            "content": "Hello write me an essay about Spain"
        },
    ]
    completion = get_completion(messages, together=True,max_tokens = 1)
    #print(completion)

if __name__ == "__main__":
    for i in range(5):
    
        main()