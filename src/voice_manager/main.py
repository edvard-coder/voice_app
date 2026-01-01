"""
Voice Manager - Voice input to text and paste functionality
Main entry point
"""
from .gui import VoiceManagerGUI


def main():
    app = VoiceManagerGUI()
    app.run()


if __name__ == "__main__":
    main()