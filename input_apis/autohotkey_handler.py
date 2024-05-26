from input_apis.input_handler import InputHandler
import config
from ahk import AHK

class AutohotkeyHandler(InputHandler):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.ahk = AHK()
        self.held_hotkeys = {}

    pynput_modifier_remap = {
        'shift': '+',
        'ctrl': '^',
        'alt': '!',
        'win': '#',
        'cmd': '#',
    }

    def convert_to_autohotkey_format(self, hotkey):
        parts = hotkey.lower().split('+')
        modifiers = [part for part in parts if part in self.pynput_modifier_remap]
        non_modifiers = [part for part in parts if part not in self.pynput_modifier_remap]

        if len(non_modifiers) > 1:
            print("\nToo many non-modifiers in hotkey: " + hotkey)
            print("More than one non-modifier is not supported.")
            return

        translated_hotkey = ''

        for i, modifier in enumerate(modifiers):
            if len(non_modifiers) > 0 or i < len(modifiers) - 1:
                translated_hotkey += self.pynput_modifier_remap[modifier]
            else:
                translated_hotkey += modifier

        if len(non_modifiers) > 0:
            translated_hotkey += non_modifiers[0]

        return translated_hotkey

    def add_hotkey(self, hotkey, callback):
        hotkey = self.convert_to_autohotkey_format(hotkey)
        self.ahk.add_hotkey(hotkey, callback)

    def add_held_hotkey(self, hotkey, callback):
        hotkey = self.convert_to_autohotkey_format(hotkey)
        self.held_hotkeys[hotkey] = False
        self.ahk.add_hotkey(hotkey, lambda: self.handle_held_callback(hotkey, callback, is_pressed=True))
        self.ahk.add_hotkey(hotkey + " Up", lambda: self.handle_held_callback(hotkey, callback, is_pressed=False))

    def handle_held_callback(self, hotkey, callback, is_pressed):
        if is_pressed != self.held_hotkeys[hotkey]:
            callback(is_pressed=is_pressed)
            self.held_hotkeys[hotkey] = is_pressed

    def start(self):
        self.ahk.start_hotkeys()
        self.ahk.block_forever()
