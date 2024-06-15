import importlib


def get_initial_prompt(prompt_name):
    """
    Get the initial prompt for the given prompt file name.
    @param prompt_name: The name of the prompt file to use.
    @return: The initial prompt as a list of dictionaries.
    """
    if prompt_name is None or prompt_name is False:
        return []
    else:
        try:
            active_prompt = importlib.import_module(f"system_prompts.{prompt_name}")
        except ModuleNotFoundError:
            print(f"Error: System prompt '{prompt_name}' not found. Using default prompt.")
            active_prompt = importlib.import_module("system_prompts.default_prompt")

        return [{"role": "system", "content": active_prompt.get_prompt()}]

