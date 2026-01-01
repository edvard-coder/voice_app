"""
Voice Manager - Main entry point module
Allows running as `python -m src.voice_manager`
"""
from .gui import VoiceManagerGUI


def main():
    app = VoiceManagerGUI()
    app.run()


if __name__ == "__main__":
    main()