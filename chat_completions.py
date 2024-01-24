from openai import OpenAI
import os
from dotenv import load_dotenv

client = OpenAI()
# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY') or os.environ['OPENAI_API_KEY']


def get_completion(messages, together=False, together_model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT"):
    if together:
        client = OpenAI(
             api_key=os.getenv('TOGETHER_API_KEY') or os.environ['TOGETHER_API_KEY'],
            base_url="https://api.together.xyz/v1",
        )
        response = client.chat.completions.create(
            model=together_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
    else:

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages
        )
    print(response)
    return response.choices[0].message.content

def main():
    messages = [
        {
            "role": "user",
            "content": "Hello, I'm a human"
        },
        {
            "role": "assistant",
            "content": "Hello, I'm an AI"
        }
    ]
    completion = get_completion(messages, together=True)
    print(completion)

if __name__ == "__main__":
    main()
    

