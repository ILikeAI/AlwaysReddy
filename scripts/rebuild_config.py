import os
import shutil

def main():
    # Define the paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    config_default_path = os.path.join(parent_dir, 'config_default.py')
    config_path = os.path.join(parent_dir, 'config.py')
    
    # Warning message to the user
    warning_message = f"Warning: This will replace your existing 'config.py' with the latest 'config_default.py'.\nDo you want to continue? (yes/no): "
    user_response = input(warning_message).strip().lower()

    if user_response in ['yes', 'y']:
        try:
            # Copy config_default.py to config.py
            shutil.copyfile(config_default_path, config_path)
            print(f"Successfully copied '{config_default_path}' to '{config_path}'")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Operation cancelled by the user.")

if __name__ == "__main__":
    main()
