class ConfigLoader:
    """
    Config class to load and merge default and user-specific configuration settings.

    This class imports the default configuration settings from `config_default.py`
    and overrides them with any user-specific settings defined in `config.py` if it exists.
    The merged configuration settings are available as attributes of the Config instance.

    Additionally, it prints which configuration items are using default values because
    they were not found in the user-specific configuration.

    Usage:
        # Import the config object
        from config_loader import config

        # Access configuration settings
        print(config.VERBOSE)
        print(config.USE_GPU)
        print(config.COMPLETIONS_API)
    """

    def __init__(self):
        # Import the default configuration
        import config_default as default_config
        # Try to import the user-specific configuration
        try:
            import config as user_config
        except ImportError:
            user_config = None

        # Load default configurations
        default_keys = set(default_config.__dict__.keys())
        user_keys = set(user_config.__dict__.keys()) if user_config else set()
        
        missing_keys = default_keys - user_keys

        for key, value in default_config.__dict__.items():
            if not key.startswith("__"):
                setattr(self, key, value)

        # Override with user-specific configurations if they exist
        if user_config:
            for key, value in user_config.__dict__.items():
                if not key.startswith("__"):
                    setattr(self, key, value)

        # Print missing keys
        if missing_keys:
            print("The following configuration items are missing from 'config.py' and are using default values, run the rebuild_config.py file in the `scripts` folder to rebuild your config file:")
            for key in missing_keys:
                if not key.startswith("__"):
                    print(f"  - {key}")

# Create a global config object
config = ConfigLoader()

# Usage example
if __name__ == "__main__":
    # Now you can use the configuration variables as attributes of config
    print(config.VERBOSE)
    print(config.USE_GPU)
    print(config.COMPLETIONS_API)
