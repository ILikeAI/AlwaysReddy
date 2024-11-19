import importlib
import config


def build_initial_messages_from_prompt_name(prompt_name):
    """
    Get the initial prompt for the given prompt file name.
    
    @param prompt_name: The name of the prompt file to use.
    @return: The initial prompt as a list of dictionaries.
    """
    if not prompt_name:
        return []
    else:
        return [{"role": "system", "content": get_system_prompt_message(prompt_name)}]


def build_initial_messages_from_prompt(prompt):
    """
    Get the initial prompt from a given prompt string.
    
    @param prompt: The prompt string to use.
    @return: The initial prompt as a list of dictionaries.
    """
    if not prompt:
        return []
    else:
        return [{"role": "system", "content": prompt}]


def get_system_prompt_message(prompt_name):
    """
    Get the system prompt message for the given prompt file name.
    
    @param prompt_name: The name of the prompt file to use.
    @return: The system prompt message as a string.
    """
    try:
        # Attempt to import the specified prompt module
        system_prompt = importlib.import_module(f"system_prompts.{prompt_name}")
    except ModuleNotFoundError:
        # Fallback to default prompt if specified prompt not found
        print(f"Error: System prompt '{prompt_name}' not found. Using default prompt.")
        system_prompt = importlib.import_module("system_prompts.default_prompt")

    # Retrieve and clean the main prompt
    prompt = system_prompt.get_prompt().strip()

    # Append additional modules' prompts if any are active
    for module in config.ACTIVE_PROMPT_MODULES:
        module_prompt = importlib.import_module(f"system_prompts.modules.{module}").get_prompt().strip()
        prompt += "\n\n" + module_prompt

    return prompt
