from openai import OpenAI
import os

class TogetherAIClient:
    """Client for interacting with the TogetherAI API."""
    def __init__(self, verbose=False):
        """Initialize the TogetherAI client with the API key and base URL."""
        self.client = OpenAI(
            api_key=os.environ.get("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
        )
        self.verbose = verbose

    def stream_completion(self, messages, model, temperature=0.7, max_tokens=2048, **kwargs):
        """Get completion from the TogetherAI API.

        Args:
            messages (list): List of messages.
            model (str): Model for completion.
            temperature (float): Temperature for sampling.
            max_tokens (int): Maximum number of tokens to generate.
            **kwargs: Additional keyword arguments.

        Yields:
            str: Text generated by the TogetherAI API.
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
                if content is not None:
                    yield content
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred streaming completion from TogetherAI API: {e}")
            raise RuntimeError(f"An error occurred streaming completion from TogetherAI API: {e}")