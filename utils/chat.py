from typing import Union, List, Dict, Callable, Optional, Any
from llm_apis.base_client import BaseClient
import config
from utils import prompt
from utils.utils import maintain_token_limit


class Chat:
    """
    A chat interface to manage conversations with an LLM API.

    Attributes:
        completions_api_client (BaseClient): Client for making LLM completions requests.
        model (str): The model name to use for completions.
        completion_params (dict): Additional parameters to pass to the completions API.
        max_prompt_tokens (int): The maximum number of tokens allowed in the prompt.
        tts_callback (Callable): Optional callback for text-to-speech as responses are generated.
        system_prompt (str): The system prompt content.
        system_prompt_filename (Optional[str]): If provided, used to load a system prompt file.
        messages (List[Dict[str, Union[str, list]]]): Conversation history messages.
        message_callbacks (List[Callable]): A list of callbacks that modify the message list.
            Each callback should accept the current message list as its only parameter and
            return a new message list.
    """

    def __init__(self,
                 completions_api_client: BaseClient,
                 model: str,
                 completion_params: Optional[dict] = None,
                 max_prompt_tokens: int = 8192,
                 tts_callback: Optional[Callable] = None,
                 system_prompt: str = "",
                 system_prompt_filename: Optional[str] = None,
                 message_callbacks: Optional[List[Callable[[List[Dict[str, Union[str, list]]]], 
                                                        List[Dict[str, Union[str, list]]]]]] = None):
        """
        Initialize the Chat object.

        Args:
            completions_api_client (BaseClient): The API client used for completions.
            model (str): The name of the model to use.
            completion_params (dict, optional): Parameters for the completions API (default: {'temperature': 0.7, 'max_tokens': 2048}).
            max_prompt_tokens (int, optional): Maximum tokens allowed in the prompt (default: 8192).
            tts_callback (Callable, optional): Callback function for text-to-speech generation.
            system_prompt (str, optional): The system prompt text.
            system_prompt_filename (str, optional): Filename for the system prompt. If provided, it overwrites system_prompt.
            message_callbacks (List[Callable], optional): A list of functions that will be applied to the message
                list each time a new message is added.
        """
        if completion_params is None:
            completion_params = {'temperature': 0.7, 'max_tokens': 2048}

        self.completions_api_client = completions_api_client
        self.model = model
        self.max_prompt_tokens = max_prompt_tokens
        self.completion_params = completion_params
        self.tts_callback = tts_callback
        self.system_prompt = system_prompt
        self.system_prompt_filename = system_prompt_filename

        # Store the list of callbacks or initialize as an empty list if not provided.
        self.message_callbacks: List[Callable[[List[Dict[str, Union[str, list]]]],
                                              List[Dict[str, Union[str, list]]]]] = message_callbacks or []

        if system_prompt and system_prompt_filename:
            print("Info: Both system_prompt and system_prompt_filename were provided to Chat; using system_prompt_filename")

        if system_prompt_filename:
            # Build initial messages from the prompt file (using the active prompt from config)
            self.messages = prompt.build_initial_messages_from_prompt_name(config.ACTIVE_PROMPT)
        elif system_prompt:
            self.messages = [{"role": "system", "content": system_prompt}]
        else:
            self.messages = []

    def get_completion(self,
                       completions_api_client: Optional[BaseClient] = None,
                       model: Optional[str] = None,
                       max_prompt_tokens: Optional[int] = None,
                       completion_params: Optional[dict] = None,
                       messages: Optional[List[Dict[str, Union[str, list]]]] = None,
                       marker_tuples: List = [],
                       tts_callback: Optional[Callable] = None) -> str:
        """
        Get a completion from the LLM API based on the current conversation context.

        This method ensures that the messages do not exceed the token limit, optionally updates
        the system prompt from a file, and then streams the response from the completions API.

        Args:
            completions_api_client (BaseClient, optional): An override for the completions API client.
            model (str, optional): An override for the model to use.
            max_prompt_tokens (int, optional): An override for the max prompt tokens.
            completion_params (dict, optional): An override for the completions parameters.
            messages (list, optional): An override for the conversation messages.
            marker_tuples (list, optional): Markers used during processing of the text stream.
            tts_callback (Callable, optional): An override for the TTS callback.

        Returns:
            str: The response text from the LLM.
        """
        # Use instance defaults if overrides are not provided.
        tts_callback = tts_callback or self.tts_callback
        completions_api_client = completions_api_client or self.completions_api_client
        model = model or self.model
        max_prompt_tokens = max_prompt_tokens or self.max_prompt_tokens
        completion_params = completion_params or self.completion_params
        messages = messages or self.messages

        # Update system prompt from file if applicable.
        if self.system_prompt_filename:
            prompt.update_system_prompt_in_messages(self.system_prompt_filename)

        # Maintain token limit for the conversation messages.
        messages = maintain_token_limit(self.messages, max_prompt_tokens)

        # Get the stream of completions from the API.
        stream = completions_api_client.get_completion_stream(
            messages,
            model,
            **completion_params
        )

        # Process the streamed response.
        response = completions_api_client.process_text_stream(
            stream,
            marker_tuples=marker_tuples,
            tts_callback=tts_callback
        )
        return response

    def add_message(self, role: str, content: Union[str, list]) -> None:
        """
        Append a message to the conversation history and process the updated message list
        through all registered callbacks.

        Each callback is a function that takes the current message list as input and returns
        a new message list. The updated list from each callback is used as the input for the next.

        Args:
            role (str): The role of the message sender (e.g., 'user', 'assistant', 'system').
            content (Union[str, list]): The content of the message.
        """
        self.messages.append({"role": role, "content": content})

        # Process the messages through each callback sequentially.
        for callback in self.message_callbacks:
            self.messages = callback(self.messages)

    def clear_chat(self) -> None:
        """
        Clear the current conversation history.

        If a system prompt or system prompt file is provided, the conversation history is reset
        with the initial system prompt; otherwise, it is cleared completely.
        """
        if self.system_prompt_filename:
            self.messages = prompt.build_initial_messages_from_prompt_name(config.ACTIVE_PROMPT)
        elif self.system_prompt:
            self.messages = [{"role": "system", "content": self.system_prompt}]
        else:
            self.messages = []
