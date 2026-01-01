import threading
import keyboard
from pynput import keyboard as pynput_keyboard


class HotkeyManager:
    def __init__(self):
        self.hotkeys = {}
        self.listener = None
        self.running = False

    def register_hotkey(self, hotkey, callback):
        """Register a hotkey with its callback function"""
        self.hotkeys[hotkey] = callback

    def _on_press(self, key):
        """Internal method to handle key presses"""
        try:
            # Convert pynput key to string format that matches our registered hotkeys
            if hasattr(key, 'char') and key.char:
                key_str = key.char
            else:
                key_str = str(key).replace("'", "")
                
            # Handle special keys
            if key_str.startswith('Key.'):
                key_str = key_str[4:]  # Remove 'Key.' prefix
                
        except AttributeError:
            # Handle special keys that don't have char attribute
            key_str = str(key).replace("'", "")
            if key_str.startswith('Key.'):
                key_str = key_str[4:]

        return True  # Return True to continue listening

    def start_listener(self):
        """Start the hotkey listener in a separate thread"""
        if self.running:
            return
            
        self.running = True
        self.listener = pynput_keyboard.Listener(on_press=self._on_press)
        self.listener.start()

        # Register hotkeys using the keyboard library
        for hotkey, callback in self.hotkeys.items():
            keyboard.add_hotkey(hotkey, callback)

    def stop_listener(self):
        """Stop the hotkey listener"""
        self.running = False
        if self.listener:
            self.listener.stop()
        # Remove all registered hotkeys
        keyboard.unhook_all()