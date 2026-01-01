"""
Build script for creating executable with PyInstaller
"""
import os
import sys
from PyInstaller.__main__ import run as pyinstaller_run

def build_executable():
    # Define the build options
    build_options = [
        '--name=VoiceManager',
        '--windowed',  # Remove this if you want console window
        '--onefile',
        '--add-data=src/voice_manager;voice_manager',
        '--hidden-import=vosk',
        '--hidden-import=pyaudio',
        '--hidden-import=keyboard',
        '--hidden-import=pynput',
        '--hidden-import=pyautogui',
        '--hidden-import=pyperclip',
        'src/voice_manager/__main__.py'
    ]
    
    # Run PyInstaller
    pyinstaller_run(build_options)
    
    print("Build completed! Executable is in the 'dist' folder.")

if __name__ == "__main__":
    build_executable()