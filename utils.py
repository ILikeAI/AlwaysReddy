import re
import clipboard

def read_clipboard():
    text = clipboard.paste()
    return text

def to_clipboard(text):
    clipboard.copy(text)

def extract_text_between_symbols(text, symbol="&&&"):
    # Define the regex pattern
    pattern = r'{}(.*?){}'.format(symbol, symbol)

    # Search for the pattern
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # Separate the matched text and the remaining text
        separated_text = match.group(1).strip()
        remaining_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()

        return separated_text, remaining_text
    else:
        return None, text

