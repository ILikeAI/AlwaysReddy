import re
import clipboard
import tiktoken
import io
from PIL import Image, ImageGrab
import base64
import json
import os
import time

def read_clipboard(model_supports_images=True):
    """Read text or image from clipboard."""
    # Try to grab an image from the clipboard
    if model_supports_images:
        try:
            image = ImageGrab.grabclipboard()
            if image:
                processed_image = process_image(image)
                if processed_image:
                    return {'type': 'image', 'content': processed_image}
        except Exception as e:
            print(f"Error processing image from clipboard: {e}")

    # If no image is found, try to get text
    clipboard_content = clipboard.paste()
    if isinstance(clipboard_content, str) and clipboard_content:
        # It's text
        return {'type': 'text', 'content': clipboard_content}
    
    print("No valid content found in clipboard.")
    return None

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
            if isinstance(value, str):
                msg_token_count += len(enc.encode(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if item.get('type') == 'image':
                            msg_token_count += 85  # Approximate token count for an image
                        elif item.get('type') == 'text':
                            msg_token_count += len(enc.encode(item.get('text', '')))
                    elif isinstance(item, str):
                        msg_token_count += len(enc.encode(item))

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

def process_image(image):
    """Resize and encode image for LLM input."""
    try:
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.LANCZOS)
        
        # Convert image to RGB if it's not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85, subsampling=0, progressive=True)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def does_model_support_images(model_name: str) -> bool:
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the JSON file
        json_path = os.path.join(current_dir, 'image_supported_models.json')
        
        # Read the JSON file
        with open(json_path, 'r') as file:
            supported_models = json.load(file)
        
        # Check if the model name is in the supported_models list
        result = model_name in supported_models['supported_models']
        
        return result
    except Exception as e:
        print(f"Error reading or parsing the supported models file: {e}")
        return False

def handle_clipboard_image(AR, message_content):
    """Handle clipboard image and return content if image exists."""
    if hasattr(AR, 'clipboard_image') and AR.clipboard_image:
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",  
                    "data": AR.clipboard_image.replace('\n', '')
                }
            },
            {
                "type": "text",
                "text": message_content + "\n\nTHE USER HAS GRANTED YOU ACCESS TO AN IMAGE FROM THEIR CLIPBOARD. ANALYZE AND BRIEFLY DESCRIBE THE IMAGE IF RELEVANT TO THE CONVERSATION."
            }
        ]
        AR.clipboard_image = None
        return content
    return None

def handle_clipboard_text(AR, message_content):
    """Append clipboard text to the message content if new clipboard text exists."""
    if AR.clipboard_text and AR.clipboard_text != AR.last_clipboard_text:
        message_content += f"\n\nTHE USER HAS GRANTED YOU ACCESS TO THEIR CLIPBOARD, THIS IS ITS CONTENT (ignore if user doesn't mention it):\n```{AR.clipboard_text}```"
        AR.last_clipboard_text = AR.clipboard_text
        AR.clipboard_text = None
    return message_content

def add_timestamp_to_message(message_content):
    """Add a timestamp to the message content."""
    timestamp = f"\n\nMESSAGE TIMESTAMP:{time.strftime('%I:%M %p')} {time.strftime('%Y-%m-%d (%A)')} "
    if isinstance(message_content, list):
        message_content[-1]['text'] += timestamp
    else:
        message_content += timestamp
    return message_content