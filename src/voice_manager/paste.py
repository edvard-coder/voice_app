import pyautogui
import time
import pyperclip


def paste_text(text):
    """
    Copy text to clipboard and simulate Ctrl+V to paste it
    """
    # Copy text to clipboard
    pyperclip.copy(text)
    
    # Small delay to ensure clipboard is updated
    time.sleep(0.1)
    
    # Simulate Ctrl+V to paste
    pyautogui.hotkey('ctrl', 'v')