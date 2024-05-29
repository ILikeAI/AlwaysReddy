from openai import OpenAI

class LM_StudioClient:
    """Client for interacting with LM studio using a local server and openai lib."""
    def __init__(self, base_url="http://localhost:1234/v1", verbose=False):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.verbose = verbose

    def stream_completion(self, messages, model, temperature=0.7, max_tokens=2048, **kwargs):
        """Get completion from LM studio API.

        Args:
            messages (list): List of messages.
            model (str): Model for completion, this for now is alway "local-model"
            temperature (float): Temperature for sampling.
            max_tokens (int): Maximum number of tokens to generate.
            **kwargs: Additional keyword arguments.

        Yields:
            str: Text generated.
        """
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"An error occurred streaming completion from LM studio: {e}")
            raise RuntimeError(f"An error occurred streaming completion from LM studio: {e}")

# # Example usage
# if __name__ == "__main__":
#     client = LM_StudioClient(base_url="http://localhost:1234/v1", verbose=True)
#     messages = [
#         {"role": "system", "content": "Always answer in rhymes."},
#         {"role": "user", "content": "Introduce yourself."}
#     ]
#     model = "local-model"
#     for content in client.stream_completion(messages, model):
#         print(content)