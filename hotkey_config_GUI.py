import tkinter as tk
from tkinter import Label, Button, Frame
import re
import keyboard

CONFIG_FILE_PATH = "config.py"

def load_hotkeys():
    hotkeys = {}
    try:
        with open(CONFIG_FILE_PATH, "r") as file:
            lines = file.readlines()
            for line in lines:
                if re.match(r"^\w+_HOTKEY = '.+'$", line):
                    key, value = line.split(" = ")
                    hotkeys[key.strip()] = value.strip().strip("'")
    except FileNotFoundError:
        pass  # Handle case where config file does not exist yet
    return hotkeys

def save_hotkeys(hotkeys):
    with open(CONFIG_FILE_PATH, "r") as file:
        lines = file.readlines()

    with open(CONFIG_FILE_PATH, "w") as file:
        for line in lines:
            # Check if this line contains a hotkey setting
            match = re.match(r"^(\w+_HOTKEY) = '.*'$", line)
            if match and match.group(1) in hotkeys:
                # If it's a hotkey line, replace it with the updated value
                file.write(f"{match.group(1)} = '{hotkeys[match.group(1)]}'\n")
            else:
                # Otherwise, write the line unchanged
                file.write(line)


def start_listening_for_hotkey(root, button, label, hotkey_name, hotkeys):
    current_keys = set()

    def on_key_event(event):
        if event.event_type == 'down':
            if event.name.isalpha():  # Check if the event name is alphabetic
                current_keys.add(event.name.lower())  # Add as lowercase
            else:
                current_keys.add(event.name)  # Add non-alphabetic keys as is
        elif event.event_type == 'up' and event.name in current_keys:
            # Process and display the hotkey
            hotkey_str = '+'.join(sorted(current_keys))
            label.config(text=f"{hotkey_name}: {hotkey_str}")
            hotkeys[hotkey_name] = hotkey_str
            save_hotkeys(hotkeys)
            keyboard.unhook_all()
            button.config(text="Set", state="normal")


    button.config(text="Listening...", state="disabled")
    keyboard.hook(on_key_event)

def load_interface(root, hotkeys):
    for widget in root.winfo_children():
        widget.destroy()

    for hotkey_name, hotkey_value in hotkeys.items():
        frame = Frame(root)
        frame.pack(pady=5)
        label = Label(frame, text=f"{hotkey_name}: {hotkey_value}")
        label.pack(side=tk.LEFT)
        button = Button(frame, text="Set")
        button.pack(side=tk.LEFT)
        # Fix: Pass the current button, label, and hotkey_name as default arguments to lambda
        button['command'] = lambda b=button, l=label, n=hotkey_name: start_listening_for_hotkey(root, b, l, n, hotkeys)


def main():
    root = tk.Tk()
    root.title("Hotkey Configuration")
    hotkeys = load_hotkeys()
    load_interface(root, hotkeys)
    root.mainloop()

if __name__ == "__main__":
    main()
