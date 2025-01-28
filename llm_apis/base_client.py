# base_client.py

from abc import ABC, abstractmethod

class BaseClient(ABC):
    def __init__(self, verbose=False):
        """
        Initialize the BaseClient.

        Args:
            verbose (bool): Whether to print verbose output.
        """
        self.verbose = verbose

    @abstractmethod
    def stream_completion(self, messages, model, **kwargs):
        """
        Abstract method to stream completion from the API.

        Args:
            messages (list): List of messages.
            model (str): Model identifier.
            **kwargs: Additional keyword arguments.

        Yields:
            str: Generated text from the API.
        """
        pass
