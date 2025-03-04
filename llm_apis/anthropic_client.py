# anthropic_client.py

from llm_apis.base_client import BaseClient
from anthropic import Anthropic
import anthropic.types
import os
import base64
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

MAX_RETRIES = 5

class AnthropicRateLimitError(Exception):
    """Exception raised for rate limit errors."""
    def __init__(self, message, retry_after):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)

class AnthropicOverloadError(Exception):
    """Exception raised for overloaded errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AnthropicClient(BaseClient):
    def __init__(self, verbose=False):
        """Initialize the Anthropic client with the API key."""
        super().__init__(verbose)
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=(retry_if_exception_type(AnthropicRateLimitError) |
               retry_if_exception_type(AnthropicOverloadError))
    )
    def _make_api_call(self, api_args):
        """Make an API call with retry mechanism."""
        try:
            return self.client.messages.create(**api_args)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('retry-after', 60))
                raise AnthropicRateLimitError(
                    f"Rate limit exceeded. {str(e)}", retry_after)
            elif e.response.status_code == 529:
                raise AnthropicOverloadError(
                    f"Anthropic API overloaded: {str(e)}")
            raise
        except anthropic.APIStatusError as e:
            error_data = e.args[0]
            if error_data['error']['type'] == 'overloaded_error':
                raise AnthropicOverloadError(
                    f"Anthropic API overloaded: {error_data['error']['message']}")
            raise

    def stream_completion(self, messages, model, **kwargs):
        """Stream completion from the Anthropic API with retry logic.

        Args:
            messages (list): List of messages.
            model (str): Model for completion.
            **kwargs: Additional keyword arguments, including max_tokens if specified.

        Yields:
            str: Text generated by the Anthropic API.
        """
        system_messages = [msg['content'] for msg in messages
                           if msg['role'] == 'system']
        system_message = system_messages[0] if system_messages else None

        messages = [msg for msg in messages
                    if msg['role'] != 'system']

        api_args = {
            "model": model,
            "max_tokens": kwargs.get('max_tokens', 1000),
            "stream": True,
            **kwargs
        }

        if system_message:
            api_args["system"] = system_message

        processed_messages = []
        for message in messages:
            if 'image' in message:
                processed_content = [{
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": message['image'].replace('\n', '')
                    }
                }]

                if 'content' in message and message['content']:
                    processed_content.append({
                        "type": "text",
                        "text": message['content']
                    })

                processed_messages.append({
                    "role": message['role'],
                    "content": processed_content
                })
            else:
                processed_messages.append({
                    "role": message['role'],
                    "content": message['content']
                })

        if not processed_messages:
            raise ValueError(
                f"No messages to send. Original messages: {messages}")

        api_args["messages"] = processed_messages

        try:
            stream = self._make_api_call(api_args)
            for message in stream:
                if message.type == "content_block_delta":
                    yield message.delta.text
        except AnthropicRateLimitError as e:
            if self.verbose:
                print(f"Rate limit error: {e.message}. Retry after {e.retry_after} seconds.")
            raise
        except AnthropicOverloadError as e:
            if self.verbose:
                print(f"Overload error: {e.message}")
            raise
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            print(f"An error occurred streaming completion from Anthropic API: {e}")
            raise RuntimeError(
                f"An error occurred streaming completion from Anthropic API: {e}")

# Test the AnthropicClient
if __name__ == "__main__":
    client = AnthropicClient(verbose=True)

    # Test text only
    messages = [
        {
            "role": "system",
            "content": "Be precise and concise."
        },
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
    model = "claude-3-sonnet-20240229"

    print("Text-only Response:")
    try:
        for chunk in client.stream_completion(messages, model):
            print(chunk, end='', flush=True)
        print()
    except AnthropicRateLimitError as e:
        print(f"\nRate limit error: {e.message}. Retry after {e.retry_after} seconds.")
    except AnthropicOverloadError as e:
        print(f"\nOverload error: {e.message}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

    # Test multimodal
    image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
    image_media_type = "image/jpeg"
    try:
        image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
    except httpx.RequestError as e:
        print(f"An error occurred while fetching the image: {e}")
        exit()

    messages = [
        {
            "role": "system",
            "content": "Respond only in rhyming couplets."
        },
        {
            "role": "user",
            "content": "Should I eat this?"
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_data,
                    },
                }
            ],
        }
    ]

    print("\nMultimodal Response:")
    try:
        for chunk in client.stream_completion(messages, model):
            print(chunk, end='', flush=True)
        print()
    except AnthropicRateLimitError as e:
        print(f"\nRate limit error: {e.message}. Retry after {e.retry_after} seconds.")
    except AnthropicOverloadError as e:
        print(f"\nOverload error: {e.message}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
