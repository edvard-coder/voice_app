import os
import sys
import requests
import threading
import queue
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import wave
import time


import signal
import sys


class STTVosk:
    def __init__(self):
        self.model_path = "models/vosk-model-small-ru-0.22"  # Default Russian model
        self.en_model_path = "models/vosk-model-small-en-us-0.15"
        self.model = None
        self.recognizer = None
        self.sample_rate = 16000
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.audio = None
        self.stream = None
        self.is_listening = False
        
        # Language to model mapping
        self.lang_to_model = {
            'ru': self.model_path,
            'en': self.en_model_path,
            'auto': self.model_path  # Default to Russian
        }
        
        # URLs for model downloads
        self.model_urls = {
            'ru': 'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip',
            'en': 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'
        }

    def download_model(self, language='ru'):
        """Download the appropriate model if it doesn't exist"""
        model_path = self.lang_to_model[language]
        
        if os.path.exists(model_path):
            print(f"Model already exists at {model_path}")
            return model_path
            
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        if language not in self.model_urls:
            raise ValueError(f"Unsupported language: {language}")
            
        model_url = self.model_urls[language]
        
        print(f"Downloading model for {language} language...")
        
        try:
            import zipfile
            import urllib.request
            
            # Download the model archive
            zip_path = f"models/vosk-model-{language}.zip"
            urllib.request.urlretrieve(model_url, zip_path)
            
            # Extract the archive
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('models/')
                
            # Remove the zip file after extraction
            os.remove(zip_path)
            
            # Rename extracted folder to the expected name
            extracted_name = os.path.join('models', os.listdir('models')[0])
            os.rename(extracted_name, model_path)
            
            print(f"Model downloaded and extracted to {model_path}")
            return model_path
        except Exception as e:
            print(f"Error downloading model: {e}")
            raise e

    def load_model(self, language='ru'):
        """Load the model for the specified language"""
        model_path = self.lang_to_model.get(language, self.model_path)
        
        # Download model if it doesn't exist
        if not os.path.exists(model_path):
            model_path = self.download_model(language)
            
        # Load the model
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

    def is_microphone_available(self):
        """Check if microphone is available"""
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            
            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    p.terminate()
                    return True
            p.terminate()
            return False
        except Exception:
            return False

    def listen_and_transcribe(self, language='ru', duration=None):
        """Record audio and transcribe it to text"""
        try:
            # Check if microphone is available
            if not self.is_microphone_available():
                raise Exception("Microphone not available")
            
            # Load the appropriate model
            self.load_model(language)
            
            print("Starting recording...")
            
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Open stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            # For real-time recognition, we need to continuously process audio chunks
            text_result = ""
            self.is_listening = True
            
            # Keep recording until is_listening is set to False
            while self.is_listening:
                # Read audio data
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                
                # Process the audio data with Vosk
                if self.recognizer.AcceptWaveform(data):
                    # Get the result
                    result = json.loads(self.recognizer.Result())
                    if 'text' in result and result['text']:
                        text_result += result['text'] + " "
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            if 'text' in final_result and final_result['text']:
                text_result += final_result['text']
            
            # Close stream
            self.stream.stop_stream()
            self.stream.close()
            
            # Terminate PyAudio
            if self.audio:
                self.audio.terminate()
                self.audio = None
            self.stream = None
            
            return text_result.strip()
                
        except Exception as e:
            print(f"Error during recording: {e}")
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
                self.audio = None
            self.stream = None
            raise e

    def stop_listening(self):
        """Stop the listening process"""
        self.is_listening = False


# For testing purposes
if __name__ == "__main__":
    stt = STTVosk()
    text = stt.listen_and_transcribe('ru')
    print(f"Transcribed text: {text}")