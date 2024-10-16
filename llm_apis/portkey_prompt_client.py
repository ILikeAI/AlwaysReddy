import os
from portkey_ai import Portkey
from dotenv import load_dotenv

class PortkeyPromptClient:
    def __init__(self, verbose=False):
        """Initialize the Portkey client with the API key."""
        api_key = os.getenv('PORTKEY_API_KEY')
        if not api_key:
            raise ValueError(
                "PORTKEY_API_KEY environment variable is not set. "
                "Please set it before initializing PortkeyPromptClient. "
                "You can find or create your API key at https://app.portkey.ai/"
            )
        self.client = Portkey(api_key=api_key)
        self.verbose = verbose

    def stream_completion(self, messages, **kwargs):
        """
        Stream a completion from the Portkey API.
        
        Args:
            messages (list): The messages to send to the API.
            **kwargs: Additional keyword arguments to pass to the API.
        
        Returns:
            An iterable of response chunks from the API.
        """
        try:
            return self.client.chat.completions.create(
                messages=messages,
                stream=True,
                **kwargs
            )
        except Exception as e:
            if self.verbose:
                print(f"Error in stream_completion: {e}")
            return None

# Test the PortkeyPromptClient
if __name__ == "__main__":
    load_dotenv()  # Move this here to ensure environment variables are loaded
    client = PortkeyPromptClient(verbose=True)
    messages = {"role":"user","content":"Hello, how are you?"}

    print("Response:")
    for chunk in client.stream_completion(messages):
        print(chunk, end='', flush=True)
    print()  # Add a newline at the end
