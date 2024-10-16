import importlib
import config


def build_initial_messages(prompt_name):
    """
    Get the initial prompt for the given prompt file name.
    @param prompt_name: The name of the prompt file to use.
    @return: The initial prompt as a list of dictionaries.
    """
    if prompt_name is None or prompt_name is False:
        return []
    else:
        return [{"role": "system", "content": get_system_prompt_message(prompt_name)}]


def get_system_prompt_message(prompt_name):
    """
    Get the system prompt message for the given prompt file name.
    @param prompt_name: The name of the prompt file to use.
    @return: The system prompt message as a string.
    """
    if prompt_name is None or prompt_name is False:
        return ""
    else:
        try:
            system_prompt = importlib.import_module(f"system_prompts.{prompt_name}")
        except ModuleNotFoundError:
            print(f"Error: System prompt '{prompt_name}' not found. Using default prompt.")
            system_prompt = importlib.import_module("system_prompts.default_prompt")

        prompt = system_prompt.get_prompt().strip()

        for module in config.ACTIVE_PROMPT_MODULES:
            prompt += "\n\n" + importlib.import_module(f"system_prompts.modules.{module}").get_prompt().strip()

        return prompt
