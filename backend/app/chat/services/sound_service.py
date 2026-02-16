import pyttsx3

class SoundService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9) 
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id) 
    def text_to_speech(self, text: str, filename: str = None):
        self.engine.say(text)
        if filename:
            self.engine.save_to_file(text, filename)
        self.engine.runAndWait()
    
