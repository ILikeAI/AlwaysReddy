from openai import OpenAI
import os
from config_loader import config

class TabbyApiClient:
    """Client for interacting with TabbyAPI."""
    def __init__(self, verbose=False):
        key = os.getenv('TABBY_API_KEY')
        self.client = OpenAI(api_key=key if key != "" else None, base_url=config.TABBY_API_BASE_URL)
        self.verbose = verbose

    def stream_completion(self, messages, model, temperature=0.7, max_tokens=2048, **kwargs):
        """Get completion from TabbyAPI.

        Args:
            messages (list): List of messages.
            model (str): Model for completion.
            temperature (float): Temperature for sampling.
            max_tokens (int): Maximum number of tokens to generate.
            **kwargs: Additional keyword arguments.

        Yields:
            str: Text generated by TabbyAPI.
        """
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content != None:
                    yield content
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred streaming completion from TabbyAPI: {e}")
            raise RuntimeError(f"An error occurred streaming completion from TabbyAPI: {e}")