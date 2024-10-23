import re
import clipboard
import tiktoken
import re

def read_clipboard():
    """
    Read the text from the clipboard.

    Returns:
    str: The text read from the clipboard.
    """
    text = clipboard.paste()
    return text

def to_clipboard(text):
    """
    Copy the given text to the clipboard.

    Args:
    text (str): The text to be copied to the clipboard.
    """

    clipboard.copy(extract_code_if_only_code_block(text))

def sanitize_text(text):
    """
    Remove disallowed characters from a string and replace certain symbols with their text equivalents.

    Args:
        text (str): The text to be sanitized.

    Returns:
        str: The sanitized text.
    """
    disallowed_chars = '"<>[]{}|\\~`^*!#$()_;'
    symbol_text_pairs = [
        (' & ', ' and '), 
        (' % ', ' percent '), 
        (' @ ', ' at '), 
        (' = ', ' equals '), 
        (' + ', ' plus '),
        (' / ', ' slash '),
    ]

    sanitized_text = ''.join(filter(lambda x: x not in disallowed_chars, text))
    for symbol, text_equivalent in symbol_text_pairs:
        sanitized_text = sanitized_text.replace(symbol, text_equivalent)
    
    return sanitized_text

def _trim_messages(messages, max_tokens):
    """
    Trim the messages to fit within the maximum token limit.

    Args:
    messages (list): A list of messages to be trimmed.
    max_tokens (int): The maximum number of tokens allowed.

    Returns:
    list: The trimmed list of messages.
    """
    msg_token_count = 0

    while True:
        msg_token_count = _count_tokens(messages)
        if msg_token_count <= max_tokens:
            break
        # Remove the oldest non-system message
        for i in range(len(messages)):
            if messages[i].get('role') != 'system':
                del messages[i]
                break

    # Ensure the first non-system message is from the user
    first_non_system_msg_index = next((i for i, message in enumerate(messages) if message.get('role') != 'system'), None)
    while first_non_system_msg_index is not None and messages[first_non_system_msg_index].get('role') == 'assistant':
        del messages[first_non_system_msg_index]
        first_non_system_msg_index = next((i for i, message in enumerate(messages) if message.get('role') != 'system'), None)

    return messages
           

def _count_tokens(messages, model="gpt-3.5-turbo"):
    """
    Count the tokens in the given messages using the specified model.

    Args:
    messages (list): A list of messages to count tokens from.
    model (str): The model to use for token counting. Defaults to "gpt-3.5-turbo".

    Returns:
    int: The total count of tokens in the messages.
    """
    enc = tiktoken.encoding_for_model(model)
    msg_token_count = 0
    for message in messages:
        for key, value in message.items():
            msg_token_count += len(enc.encode(value))  # Add tokens in set message

    return msg_token_count


def maintain_token_limit(messages, max_tokens):
    """
    Maintain the token limit by trimming messages if the token count exceeds the maximum limit.

    Args:
    messages (list): A list of messages to maintain.
    max_tokens (int): The maximum number of tokens allowed.

    Returns:
    list: The trimmed list of messages.
    """
    if _count_tokens(messages) > max_tokens:
        messages = _trim_messages(messages, max_tokens)
    return messages

def extract_code_if_only_code_block(markdown_text):
    """
    Extracts the code from a markdown text if the text only contains a single code block.

    Args:
        markdown_text (str): The markdown text to extract the code from.

    Returns:
        str: The extracted code if the markdown text only contains a single code block, 
             otherwise the original markdown text.
    """
    
    stripped_text = markdown_text.strip()
    
    # Define the regex pattern
    pattern = r'^```(?:\w+)?\n([\s\S]*?)```$'
    
    # Search for the pattern
    match = re.match(pattern, stripped_text)
    
    if match:
        # Extract and return the code block
        return match.group(1)
    else:
        # Return the original text if it doesn't match the pattern
        return markdown_text