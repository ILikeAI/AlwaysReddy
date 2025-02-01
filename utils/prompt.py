import importlib
import config


def build_initial_messages_from_prompt_name(prompt_name : str, messages : list = None):
    """
    Get the initial prompt for the given prompt file name.
    
    @param prompt_name: The name of the prompt file to use.
    @return: The initial prompt as a list of dictionaries.
    """
    if not prompt_name:
        return messages
    else:
        return update_system_prompt_in_messages(prompt_name, messages)

def update_system_prompt_in_messages(prompt_name : str, messages : list = None):
    """
    Update or add the system prompt message to the messages list.
    
    @param prompt_name: The name of the prompt file to use.
    @param messages: List of existing messages to update.
    @return: The updated list of messages with the system prompt.
    """
    try:
        system_prompt = importlib.import_module(f"system_prompts.{prompt_name}")
    except ModuleNotFoundError:
        print(f"Error: System prompt '{prompt_name}' not found. Using default prompt.")
        system_prompt = importlib.import_module("system_prompts.default_prompt")

    prompt = system_prompt.get_prompt().strip()

    for module in config.ACTIVE_PROMPT_MODULES:
        module_prompt = importlib.import_module(f"system_prompts.modules.{module}").get_prompt().strip()
        prompt += "\n\n" + module_prompt

    system_message = {"role": "system", "content": prompt}
    if messages == None:
        messages = []
    for i, message in enumerate(messages):
        if message.get("role") == "system":
            messages[i] = system_message
            break
    else:
        messages.insert(0, system_message)

    return messages


