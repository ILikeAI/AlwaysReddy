import re
import clipboard
import tiktoken
import sounddevice as sd
import resampy
import soundfile as sf

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
    clipboard.copy(text)

def count_tokens(messages, model="gpt-3.5-turbo"):
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

def trim_messages(messages, max_tokens):
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
        msg_token_count = count_tokens(messages)
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




def check_supported_sample_rates(device_index):
    """
    Checks the supported sample rates for a given audio input device.

    Args:
    - device_index: int, the index of the audio input device

    Returns:
    - supported_rates: list, a list of supported sample rates
    """
    sample_rates = [8000, 16000, 22050, 32000, 44100, 48000, 96000, 192000]  # Common sample rates
    supported_rates = []

    for rate in sample_rates:
        try:
            # Try to open an InputStream at the specified sample rate
            with sd.InputStream(samplerate=rate, device=device_index, channels=1):
                supported_rates.append(rate)
                print(f"Sample rate {rate} Hz is supported.")
        except Exception as e:
            print(f"Sample rate {rate} Hz is not supported.")

    return supported_rates


def resample(data, orig_sample_rate, target_sample_rate):
    """
    Resamples the audio data to the target sample rate.

    Args:
    - data: numpy array, the audio data to be resampled
    - orig_sample_rate: int, the original sample rate of the audio data
    - target_sample_rate: int, the target sample rate for resampling

    Returns:
    - resampled_data: numpy array, the resampled audio data
    """
    resampled_data = resampy.resample(data, orig_sample_rate, target_sample_rate)
    return resampled_data


def read_and_resample(filename, target_sample_rate):
    """
    Reads an audio file and resamples it to the target sample rate.

    Args:
    - filename: str, the path to the audio file
    - target_sample_rate: int, the target sample rate for resampling

    Returns:
    - resampled_data: numpy array, the resampled audio data
    - original_sample_rate: int, the original sample rate of the audio file
    """
    data, original_sample_rate = sf.read(filename, dtype='float32')
    return resampy.resample(data, original_sample_rate, target_sample_rate), original_sample_rate


def set_default_device_by_name(device_name, kind='output'):
    """
    Sets the default input or output device by its name.

    Args:
    - device_name: str, the name of the input or output device
    - kind: str, 'input' or 'output', specifies the kind of device to set as default
    """
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['name'] == device_name:
            sd.default.device = i
            print(f"Default {kind} device set to: {device_name}")
            return
    print(f"Device '{device_name}' not found or not a {kind} device.")


def print_device_names():
    """
    Prints the available input and output devices.
    """
    devices = sd.query_devices()
    print("Available input devices:")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"  {i}: {dev['name']}")

    print("\nAvailable output devices:")
    for i, dev in enumerate(devices):
        if dev['max_output_channels'] > 0:
            print(f"  {i}: {dev['name']}")




def get_device_name(keyword):
    devices = sd.query_devices()
    for device in devices:
        # Regex pattern to find the keyword in the text
        pattern = rf"\b{re.escape(keyword)}\b"

        # Search for the keyword in the text
        match = re.search(pattern, device["name"])

        if not match:
            continue

        print(f"[Atom] Using device: {device}")
        # Return the part before ", ALSA" if found
        return device["name"]
