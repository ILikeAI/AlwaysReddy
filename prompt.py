import importlib
from config_loader import config

if config.ACTIVE_PROMPT is None or config.ACTIVE_PROMPT is False:
    prompts = []
else:
    try:
        active_prompt = importlib.import_module(f"system_prompts.{config.ACTIVE_PROMPT}")
    except ModuleNotFoundError:
        print(f"Error: System prompt '{config.ACTIVE_PROMPT}' not found. Using default prompt.")
        active_prompt = importlib.import_module("system_prompts.default_prompt")

    prompts = [{"role": "system", "content": active_prompt.get_prompt()}]

