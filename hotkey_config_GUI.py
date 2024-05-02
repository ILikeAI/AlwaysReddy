import tkinter as tk
from tkinter import ttk  # Importing ttk for better styling options
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
            match = re.match(r"^(\w+_HOTKEY) = '.*'$", line)
            if match and match.group(1) in hotkeys:
                file.write(f"{match.group(1)} = '{hotkeys[match.group(1)]}'\n")
            else:
                file.write(line)

def start_listening_for_hotkey(root, button, label, hotkey_name, hotkeys):
    current_keys = set()

    def on_key_event(event):
        if event.event_type == 'down':
            current_keys.add(event.name.lower())
        elif event.event_type == 'up' and event.name.lower() in current_keys:
            hotkey_str = '+'.join(sorted(current_keys))
            label.config(text=f"{hotkey_name}: {hotkey_str}")
            hotkeys[hotkey_name] = hotkey_str
            save_hotkeys(hotkeys)
            keyboard.unhook_all()
            button.config(text="Set", state="normal")

    button.config(text="Listening...", state="disabled")
    keyboard.hook(on_key_event)

def load_interface(root, hotkeys):
    style = ttk.Style()
    style.theme_use('clam')  # Using clam theme for better button styling

    # Define style for buttons
    style.configure('TButton', background='#88C0D0', foreground='white', borderwidth=1)
    style.map('TButton', 
              background=[('active', '#81A1C1')], 
              foreground=[('active', 'white')])

    for widget in root.winfo_children():
        widget.destroy()

    for hotkey_name, hotkey_value in hotkeys.items():
        frame = ttk.Frame(root, padding=5)
        frame.pack(pady=5, padx=10, fill=tk.X)
        label = ttk.Label(frame, text=f"{hotkey_name}: {hotkey_value}")
        label.pack(side=tk.LEFT, padx=10)
        button = ttk.Button(frame, text="Set", style='TButton')
        button.pack(side=tk.LEFT, padx=10)
        button['command'] = lambda b=button, l=label, n=hotkey_name: start_listening_for_hotkey(root, b, l, n, hotkeys)

def main():
    root = tk.Tk()
    root.title("Hotkey Configuration")
    root.configure(bg='#ECEFF4')
    hotkeys = load_hotkeys()
    load_interface(root, hotkeys)
    root.mainloop()

if __name__ == "__main__":
    main()
