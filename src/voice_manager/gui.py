import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from .stt_vosk import STTVosk
from .hotkeys import HotkeyManager
from .paste import paste_text
import pyperclip


class VoiceManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Manager")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Initialize components
        self.stt_engine = STTVosk()
        self.hotkey_manager = HotkeyManager()
        
        # State variables
        self.is_recording = False
        self.current_text = ""
        
        # Setup UI
        self.setup_ui()
        
        # Setup hotkey
        self.hotkey_manager.register_hotkey('ctrl+alt+space', self.toggle_recording)
        
        # Start hotkey listener
        self.hotkey_manager.start_listener()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Microphone button
        self.mic_button = ttk.Button(
            main_frame, 
            text="🎙️ Запись", 
            command=self.toggle_recording,
            style='Large.TButton'
        )
        self.mic_button.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Text preview area
        ttk.Label(main_frame, text="Распознанный текст:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.text_preview = scrolledtext.ScrolledText(main_frame, height=8, width=60)
        self.text_preview.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Language selection
        ttk.Label(main_frame, text="Язык распознавания:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.lang_var = tk.StringVar(value="ru")
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(lang_frame, text="Русский", variable=self.lang_var, value="ru").pack(side=tk.LEFT)
        ttk.Radiobutton(lang_frame, text="English", variable=self.lang_var, value="en").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(lang_frame, text="Авто", variable=self.lang_var, value="auto").pack(side=tk.LEFT)
        
        # Insertion mode
        ttk.Label(main_frame, text="Режим вставки:").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        self.insert_mode_var = tk.BooleanVar(value=True)
        insert_frame = ttk.Frame(main_frame)
        insert_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(insert_frame, text="Автовставка в активное окно", variable=self.insert_mode_var).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Готов к записи")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.mic_button.config(text="⏹️ Стоп", state="normal")  # Enable to allow stopping
        self.status_var.set("Запись...")
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        # Stop the STT engine
        self.stt_engine.stop_listening()
        self.mic_button.config(state="normal")
        self.status_var.set("Остановка записи...")

    def _record_audio(self):
        try:
            self.current_text = self.stt_engine.listen_and_transcribe(language=self.lang_var.get())
            
            # Update UI in main thread only if we're still in recording state
            if not self.is_recording:  # Check if still recording after transcribing
                self.root.after(0, self._update_ui_with_text, self.current_text)
        except Exception as e:
            error_msg = f"Ошибка при записи: {str(e)}"
            self.root.after(0, self._show_error, error_msg)

    def _update_ui_with_text(self, text):
        self.text_preview.delete(1.0, tk.END)
        self.text_preview.insert(tk.END, text)
        
        # Update status
        self.status_var.set(f"Распознано: {len(text)} символов")
        
        # Handle insertion if enabled
        if self.insert_mode_var.get() and text.strip():
            try:
                # Copy to clipboard
                pyperclip.copy(text)
                
                # Paste to active window
                paste_text(text)
                self.status_var.set("Текст скопирован и вставлен")
            except Exception as e:
                self.status_var.set(f"Ошибка вставки: {str(e)}")
        
        # Reset button
        self.mic_button.config(text="🎙️ Запись", state="normal")
        self.is_recording = False

    def _show_error(self, error_msg):
        self.text_preview.delete(1.0, tk.END)
        self.text_preview.insert(tk.END, error_msg)
        self.status_var.set(error_msg)
        self.mic_button.config(text="🎙️ Запись", state="normal")
        self.is_recording = False

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.hotkey_manager.stop_listener()
        self.root.destroy()


if __name__ == "__main__":
    app = VoiceManagerGUI()
    app.run()