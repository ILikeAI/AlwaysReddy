from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

def get_completion(messages, together=False, together_model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT", max_tokens=2048):
    start_time = time.time()
    if together:
        client = OpenAI(
             api_key=os.getenv('TOGETHER_API_KEY'),
            base_url="https://api.together.xyz/v1",
        )
        response = client.chat.completions.create(
            model=together_model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
        )
    else:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            max_tokens=max_tokens,
        )

    print(f"Time taken for completion: {time.time() - start_time} seconds")
    return response.choices[0].message.content

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