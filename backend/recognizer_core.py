import speech_recognition as sr

class RecognizerCore:
    def __init__(self):
        self.r = sr.Recognizer()

    def transcribe_wav_file(self, wav_path):
        with sr.AudioFile(wav_path) as source:
            audio = self.r.record(source)
        try:
            return self.r.recognize_google(audio)
        except sr.UnknownValueError:
            return ''
        except sr.RequestError as e:
            raise RuntimeError('Speech API request failed: ' + str(e))
