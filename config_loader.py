import os
import importlib.util
import re

class ConfigLoader:
    """
    Config class to load and merge default and user-specific configuration settings.

    This class imports the default configuration settings from `config_default.py`
    and overrides them with any user-specific settings defined in `config.py` if it exists.
    The merged configuration settings are available as attributes of the Config instance.

    If new configuration items are found in the default config that are not in the user's
    config, they are automatically appended to the top of the user's config.py file,
    or under an existing "New configuration items" section if present.

    Usage:
        # Import the config object
        from config_loader import config

        # Access configuration settings
        print(config.VERBOSE)
        print(config.USE_GPU)
        print(config.COMPLETIONS_API)
    """

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_config_path = os.path.join(script_dir, 'config_default.py')
        user_config_path = os.path.join(script_dir, 'config.py')

        # Import the default configuration
        default_config = self._import_config(default_config_path)

        # Try to import the user-specific configuration
        user_config = self._import_config(user_config_path)

        # Find new keys in default config that are not in user config
        new_keys = set(default_config.__dict__.keys()) - set(user_config.__dict__.keys())
        new_keys = [key for key in new_keys if not key.startswith('__')]

        # If there are new keys, append them to the user's config file
        if new_keys:
            self._append_new_keys(user_config_path, default_config, new_keys)
            # Reload the user config to include the new keys
            user_config = self._import_config(user_config_path)

        # Load configurations
        for key, value in default_config.__dict__.items():
            if not key.startswith('__'):
                setattr(self, key, getattr(user_config, key, value))

        for key, value in user_config.__dict__.items():
            if not key.startswith('__') and key not in default_config.__dict__:
                setattr(self, key, value)

    def _import_config(self, config_path):
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config

    def _append_new_keys(self, config_path, default_config, new_keys):
        with open(config_path, 'r') as f:
            content = f.read()

        new_section_pattern = re.compile(r'# New configuration items\n(.*?)\n# Existing configuration', re.DOTALL)
        new_section_match = new_section_pattern.search(content)

        if new_section_match:
            # If "New configuration items" section exists, add new keys there
            new_section = new_section_match.group(1)
            for key in new_keys:
                if key not in new_section:
                    value = getattr(default_config, key)
                    new_section += f'{key} = {repr(value)}\n'
            updated_content = new_section_pattern.sub(f'# New configuration items\n{new_section}\n# Existing configuration', content)
        else:
            # If no "New configuration items" section, create it at the top
            new_section = '# New configuration items\n'
            for key in new_keys:
                value = getattr(default_config, key)
                new_section += f'{key} = {repr(value)}\n'
            new_section += '\n# Existing configuration\n'
            updated_content = new_section + content

        with open(config_path, 'w') as f:
            f.write(updated_content)

# Create a global config object
config = ConfigLoader()

# Usage example
if __name__ == "__main__":
    # Now you can use the configuration variables as attributes of config
    print(config.VERBOSE)
    print(config.USE_GPU)
    print(config.COMPLETIONS_API)